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

import cross_provider_context_reconciliation_probe as probe


class CrossProviderContextReconciliationProbeTests(unittest.TestCase):
    def test_contract_version(self) -> None:
        self.assertEqual(
            probe.CONTRACT_VERSION,
            "DAILY_NCAAF_PHASE_B2C_CONTEXT_RECONCILIATION_V1",
        )

    def test_compare_id_normalizes_csv_float_suffix(self) -> None:
        self.assertEqual(probe.compare_id(123, "123.0"), "MATCH")
        self.assertEqual(probe.compare_id(123, "124"), "MISMATCH")
        self.assertEqual(probe.compare_id(None, "124"), "UNAVAILABLE")

    def test_compare_text_exact_normalized_mismatch(self) -> None:
        self.assertEqual(probe.compare_text("Ohio State", "Ohio State"), "EXACT")
        self.assertEqual(probe.compare_text("ACC", "A.C.C."), "NORMALIZED")
        self.assertEqual(probe.compare_text("SEC", "Big Ten"), "MISMATCH")
        self.assertEqual(probe.compare_text(None, "SEC"), "UNAVAILABLE")

    def test_compare_bool(self) -> None:
        self.assertEqual(probe.compare_bool(True, "true"), "MATCH")
        self.assertEqual(probe.compare_bool(False, "1"), "MISMATCH")
        self.assertEqual(probe.compare_bool(None, "true"), "UNAVAILABLE")

    def test_aligned_espn_field_same_side(self) -> None:
        row = {"home_conference": "SEC", "away_conference": "ACC"}
        self.assertEqual(
            probe.aligned_espn_field(
                row,
                "home",
                "SAME_SIDE",
                ("home_conference",),
                ("away_conference",),
            ),
            "SEC",
        )

    def test_aligned_espn_field_swapped_side(self) -> None:
        row = {"home_conference": "SEC", "away_conference": "ACC"}
        self.assertEqual(
            probe.aligned_espn_field(
                row,
                "home",
                "SWAPPED_SIDES",
                ("home_conference",),
                ("away_conference",),
            ),
            "ACC",
        )

    def test_compare_event_context_complete_match(self) -> None:
        cfbd = {
            "id": 1,
            "homeTeam": "Georgia",
            "awayTeam": "Clemson",
            "venueId": 100,
            "venue": "Example Stadium",
            "neutralSite": False,
            "conferenceGame": False,
            "homeConference": "SEC",
            "awayConference": "ACC",
            "homeClassification": "fbs",
            "awayClassification": "fbs",
        }
        espn = {
            "game_id": "1",
            "home_team": "Georgia Bulldogs",
            "away_team": "Clemson Tigers",
            "venue_id": "100",
            "venue": "Example Stadium",
            "neutral_site": "false",
            "conference_competition": "false",
            "home_conference": "SEC",
            "away_conference": "ACC",
            "home_division": "fbs",
            "away_division": "fbs",
        }
        result = probe.compare_event_context(cfbd, espn)
        self.assertEqual(result["side_orientation"], "SAME_SIDE")
        self.assertEqual(result["venue_id_state"], "MATCH")
        self.assertEqual(result["venue_name_state"], "EXACT")
        self.assertEqual(result["neutral_site_state"], "MATCH")
        self.assertEqual(result["home_conference_state"], "EXACT")
        self.assertEqual(result["away_conference_state"], "EXACT")
        self.assertEqual(result["home_division_state"], "EXACT")
        self.assertEqual(result["conference_game_flag_state"], "MATCH")

    def test_compare_event_context_swapped_participants(self) -> None:
        cfbd = {
            "id": 2,
            "homeTeam": "USC",
            "awayTeam": "Texas A&M",
            "venueId": 200,
            "venue": "Bowl Stadium",
            "neutralSite": True,
            "conferenceGame": False,
            "homeConference": "Big Ten",
            "awayConference": "SEC",
            "homeClassification": "fbs",
            "awayClassification": "fbs",
        }
        espn = {
            "game_id": "2",
            "home_team": "Texas A&M Aggies",
            "away_team": "USC Trojans",
            "venue_id": "200",
            "venue": "Bowl Stadium",
            "neutral_site": "true",
            "conference_competition": "false",
            "home_conference": "SEC",
            "away_conference": "Big Ten",
            "home_division": "fbs",
            "away_division": "fbs",
        }
        result = probe.compare_event_context(cfbd, espn)
        self.assertEqual(result["side_orientation"], "SWAPPED_SIDES")
        self.assertEqual(result["home_conference_state"], "EXACT")
        self.assertEqual(result["away_conference_state"], "EXACT")

    def test_conference_flag_mismatch_remains_separate(self) -> None:
        cfbd = {
            "id": 3,
            "homeTeam": "Notre Dame",
            "awayTeam": "Clemson",
            "conferenceGame": False,
        }
        espn = {
            "game_id": "3",
            "home_team": "Notre Dame Fighting Irish",
            "away_team": "Clemson Tigers",
            "conference_competition": "true",
        }
        result = probe.compare_event_context(cfbd, espn)
        self.assertEqual(result["conference_game_flag_state"], "MISMATCH")

    def test_summarize_context_counts_and_examples(self) -> None:
        rows = [
            {
                "side_orientation": "SAME_SIDE",
                "venue_id_state": "MATCH",
                "venue_name_state": "EXACT",
                "neutral_site_state": "MATCH",
                "home_conference_state": "EXACT",
                "away_conference_state": "EXACT",
                "home_division_state": "EXACT",
                "away_division_state": "EXACT",
                "conference_game_flag_state": "MATCH",
            },
            {
                "side_orientation": "SAME_SIDE",
                "venue_id_state": "MISMATCH",
                "venue_name_state": "MISMATCH",
                "neutral_site_state": "MISMATCH",
                "home_conference_state": "MISMATCH",
                "away_conference_state": "EXACT",
                "home_division_state": "EXACT",
                "away_division_state": "MISMATCH",
                "conference_game_flag_state": "MISMATCH",
            },
        ]
        summary = probe.summarize_context(rows)
        self.assertEqual(summary["state_counts"]["venue_id_state"]["MISMATCH"], 1)
        self.assertEqual(len(summary["examples"]["venue_id_mismatch_examples"]), 1)
        self.assertEqual(
            len(summary["examples"]["conference_game_flag_mismatch_examples"]), 1
        )

    def test_build_report_without_key_is_explicit_skip(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            report = probe.build_report(seasons=[2024], request_delay_seconds=0)
        self.assertEqual(report["status"], "SKIPPED_NO_API_KEY")
        self.assertNotIn("CFBD_API_KEY", str(report.get("secret_policy", "")).split("=")[-1])


if __name__ == "__main__":
    unittest.main()
