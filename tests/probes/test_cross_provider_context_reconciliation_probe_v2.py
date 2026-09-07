from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
PROBE_DIR = ROOT / "scripts" / "probes"
if str(PROBE_DIR) not in sys.path:
    sys.path.insert(0, str(PROBE_DIR))

import cross_provider_context_reconciliation_probe_v2 as probe


class CrossProviderContextReconciliationProbeV2Tests(unittest.TestCase):
    def test_contract_version(self) -> None:
        self.assertEqual(
            probe.CONTRACT_VERSION,
            "DAILY_NCAAF_PHASE_B2C_CONTEXT_RECONCILIATION_V2",
        )

    def test_native_projection_excludes_backported_fields(self) -> None:
        row = {
            "team_id": "333",
            "division": "fbs",
            "conference_abbreviation": "SEC",
            "venue_id": "3657",
            "cfbd_conference": "SEC",
            "classification": "fbs",
            "school": "Alabama",
        }
        projected = probe.project_espn_native_team_row(row)
        self.assertEqual(projected["team_id"], "333")
        self.assertEqual(projected["conference_abbreviation"], "SEC")
        self.assertNotIn("cfbd_conference", projected)
        self.assertNotIn("classification", projected)
        self.assertNotIn("school", projected)

    def test_conference_alias_exact_and_normalized(self) -> None:
        team = {
            "conference_name": "Southeastern Conference",
            "conference_short_name": "SEC",
            "conference_abbreviation": "SEC",
            "conference_midsize_name": "Southeastern",
        }
        state, aliases = probe.compare_conference_alias("SEC", team)
        self.assertEqual(state, "EXACT_ALIAS_MATCH")
        self.assertIn("SEC", aliases)

        team2 = {
            "conference_name": "Mid-American Conference",
            "conference_short_name": "Mid-American Conference",
        }
        state2, _ = probe.compare_conference_alias("Mid-American", team2)
        self.assertEqual(state2, "NORMALIZED_ALIAS_MATCH")

    def test_conference_missing_remains_unavailable(self) -> None:
        state, aliases = probe.compare_conference_alias(
            "FBS Independents", {"conference_name": None}
        )
        self.assertEqual(state, "UNAVAILABLE_ESPN_CONFERENCE")
        self.assertEqual(aliases, [])

    def test_division_match_and_mismatch(self) -> None:
        self.assertEqual(
            probe.compare_division("fbs", {"division": "fbs"})[0], "MATCH"
        )
        self.assertEqual(
            probe.compare_division("fcs", {"division": "fbs"})[0], "MISMATCH"
        )
        self.assertEqual(
            probe.compare_division("fbs", None)[0], "UNAVAILABLE_TEAM_METADATA"
        )

    def test_team_index_tracks_duplicates_and_fbs(self) -> None:
        rows = [
            {"team_id": "1", "is_fbs": "true", "division": "fbs"},
            {"team_id": "2", "is_fbs": "false", "division": "fcs"},
            {"team_id": "1", "is_fbs": "true", "division": "fbs"},
        ]
        index, non_null, duplicates, fbs_rows = probe.build_team_index(rows)
        self.assertEqual(non_null, 3)
        self.assertEqual(duplicates, 1)
        self.assertEqual(fbs_rows, 2)
        self.assertEqual(set(index), {"1", "2"})

    def test_participant_result_uses_aligned_team_metadata(self) -> None:
        cfbd = {
            "homeId": 333,
            "homeTeam": "Alabama",
            "homeClassification": "fbs",
            "homeConference": "SEC",
        }
        schedule = {"home_id": "333", "home_team": "Alabama Crimson Tide"}
        teams = {
            "333": {
                "team_id": "333",
                "division": "fbs",
                "conference_abbreviation": "SEC",
                "conference_id": "8",
            }
        }
        result = probe.participant_result(
            cfbd, schedule, teams, "home", "SAME_SIDE"
        )
        self.assertEqual(result["external_team_id_state"], "MATCH")
        self.assertEqual(result["division_state"], "MATCH")
        self.assertEqual(result["conference_state"], "EXACT_ALIAS_MATCH")

    def test_home_venue_anchor_matches_standard_home(self) -> None:
        cfbd = {
            "homeId": 333,
            "venueId": 3657,
            "venue": "Bryant-Denny Stadium",
            "neutralSite": False,
        }
        schedule = {
            "home_id": "333",
            "neutral_site": "false",
        }
        teams = {
            "333": {
                "team_id": "333",
                "venue_id": "3657",
                "venue_name": "Bryant-Denny Stadium",
                "display_name": "Alabama Crimson Tide",
            }
        }
        result = probe.home_venue_anchor(cfbd, schedule, teams, "SAME_SIDE")
        self.assertEqual(result["state"], "MATCH")

    def test_home_venue_anchor_preserves_alternate_site_difference(self) -> None:
        cfbd = {
            "homeId": 333,
            "venueId": 9999,
            "venue": "Alternate Stadium",
            "neutralSite": False,
        }
        schedule = {"home_id": "333", "neutral_site": "false"}
        teams = {
            "333": {
                "team_id": "333",
                "venue_id": "3657",
                "venue_name": "Bryant-Denny Stadium",
            }
        }
        result = probe.home_venue_anchor(cfbd, schedule, teams, "SAME_SIDE")
        self.assertEqual(result["state"], "DIFFERENT_FROM_TEAM_HOME_VENUE")

    def test_home_venue_anchor_not_applicable_for_neutral(self) -> None:
        cfbd = {"homeId": 333, "venueId": 3657, "neutralSite": True}
        schedule = {"home_id": "333", "neutral_site": "true"}
        result = probe.home_venue_anchor(cfbd, schedule, {}, "SAME_SIDE")
        self.assertEqual(result["state"], "NOT_APPLICABLE_CONTEXT")

    def test_summarize_counts_nested_states(self) -> None:
        rows = [
            {
                "side_orientation": "SAME_SIDE",
                "home": {
                    "external_team_id_state": "MATCH",
                    "division_state": "MATCH",
                    "conference_state": "EXACT_ALIAS_MATCH",
                },
                "away": {
                    "external_team_id_state": "MATCH",
                    "division_state": "MATCH",
                    "conference_state": "NORMALIZED_ALIAS_MATCH",
                },
                "home_venue_anchor": {"state": "MATCH"},
            },
            {
                "side_orientation": "SAME_SIDE",
                "home": {
                    "external_team_id_state": "MATCH",
                    "division_state": "MISMATCH",
                    "conference_state": "MISMATCH",
                },
                "away": {
                    "external_team_id_state": "MATCH",
                    "division_state": "MATCH",
                    "conference_state": "UNAVAILABLE_ESPN_CONFERENCE",
                },
                "home_venue_anchor": {"state": "DIFFERENT_FROM_TEAM_HOME_VENUE"},
            },
        ]
        summary = probe.summarize(rows)
        self.assertEqual(summary["state_counts"]["home_division_state"]["MISMATCH"], 1)
        self.assertEqual(summary["state_counts"]["home_conference_state"]["MISMATCH"], 1)
        self.assertEqual(
            summary["state_counts"]["home_venue_anchor_state"][
                "DIFFERENT_FROM_TEAM_HOME_VENUE"
            ],
            1,
        )

    def test_build_report_without_key_is_explicit_skip(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            report = probe.build_report(seasons=[2024], request_delay_seconds=0)
        self.assertEqual(report["status"], "SKIPPED_NO_API_KEY")
        self.assertIn("never emitted", report["secret_policy"])


if __name__ == "__main__":
    unittest.main()
