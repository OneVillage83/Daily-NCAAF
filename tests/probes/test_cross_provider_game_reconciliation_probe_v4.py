import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "probes" / "cross_provider_game_reconciliation_probe_v4.py"
SPEC = importlib.util.spec_from_file_location("cross_provider_game_reconciliation_probe_v4", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CrossProviderGameReconciliationProbeV4Tests(unittest.TestCase):
    def saint_francis_case(self):
        cfbd = {
            "id": 401644732,
            "homeTeam": "Kent State",
            "awayTeam": "Saint Francis",
            "homeClassification": "fbs",
            "awayClassification": "fcs",
            "homePoints": 17,
            "awayPoints": 23,
            "week": 2,
            "startDate": "2024-09-07T18:30:00Z",
            "completed": True,
        }
        espn = {
            "game_id": "401644732",
            "home_id": "2309",
            "home_team": "Kent State Golden Flashes",
            "home_score": "17",
            "away_id": "2598",
            "away_team": "St. Francis (PA) Red Flash",
            "away_score": "23",
            "week": "2",
            "game_date": "2024-09-07T18:30Z",
            "status": "STATUS_FINAL",
        }
        return cfbd, espn

    def test_contract_version(self):
        self.assertEqual(
            MODULE.CONTRACT_VERSION,
            "DAILY_NCAAF_PHASE_B2C_CROSS_PROVIDER_GAME_RECONCILIATION_V4",
        )

    def test_parse_int_list(self):
        self.assertEqual(MODULE.parse_int_list("2024, 2026"), [2024, 2026])

    def test_one_participant_anchor_resolves_same_side_alias(self):
        cfbd, espn = self.saint_francis_case()
        evidence = MODULE.orientation_evidence(cfbd, espn)
        self.assertEqual(evidence["orientation"], "SAME_SIDE")
        self.assertEqual(
            evidence["basis"],
            "ONE_PARTICIPANT_EXACT_EVENT_COUNTERPART_ANCHOR",
        )

    def test_one_participant_anchor_allows_score_comparison(self):
        cfbd, espn = self.saint_francis_case()
        result = MODULE.compare_matched_game(cfbd, espn)
        self.assertEqual(result["side_orientation"], "SAME_SIDE")
        self.assertEqual(result["score_state"], "MATCH")
        self.assertEqual(result["aligned_participants"]["cfbd_away_to_espn"]["id"], "2598")

    def test_one_participant_anchor_adds_alias_to_crosswalk(self):
        cfbd, espn = self.saint_francis_case()
        report = MODULE.derive_team_crosswalk(
            {"401644732": cfbd},
            {"401644732": espn},
            ["401644732"],
        )
        self.assertEqual(report["matched_games_skipped_for_unresolved_orientation"], 0)
        self.assertEqual(report["crosswalk"]["Saint Francis"]["espn_ids"], ["2598"])
        self.assertEqual(report["cfbd_name_to_multiple_espn_id_conflict_count"], 0)

    def test_compare_season_reports_counterpart_anchor_basis(self):
        cfbd, espn = self.saint_francis_case()
        result = MODULE.compare_season([cfbd], [espn])
        counts = result["matched_field_agreement"]["participant_alignment_basis_counts"]
        self.assertEqual(counts["ONE_PARTICIPANT_EXACT_EVENT_COUNTERPART_ANCHOR"], 1)
        self.assertEqual(len(result["matched_field_agreement"]["counterpart_anchor_examples"]), 1)

    def test_competing_one_participant_anchors_remain_ambiguous(self):
        cfbd = {"homeTeam": "Miami", "awayTeam": "Unknown"}
        espn = {
            "home_team": "Miami Hurricanes",
            "away_team": "Miami (OH) RedHawks",
        }
        evidence = MODULE.orientation_evidence(cfbd, espn)
        self.assertEqual(evidence["orientation"], "AMBIGUOUS")
        self.assertEqual(evidence["basis"], "COMPETING_ONE_PARTICIPANT_ANCHORS")

    def test_two_participant_swapped_evidence_still_wins(self):
        cfbd = {"homeTeam": "Coastal Carolina", "awayTeam": "UTSA"}
        espn = {
            "home_team": "UTSA Roadrunners",
            "away_team": "Coastal Carolina Chanticleers",
        }
        evidence = MODULE.orientation_evidence(cfbd, espn)
        self.assertEqual(evidence["orientation"], "SWAPPED_SIDES")
        self.assertEqual(evidence["basis"], "TWO_PARTICIPANT_DISPLAY_EVIDENCE")

    def test_unrelated_names_remain_unresolved(self):
        cfbd = {"homeTeam": "Alpha", "awayTeam": "Beta"}
        espn = {"home_team": "Gamma", "away_team": "Delta"}
        evidence = MODULE.orientation_evidence(cfbd, espn)
        self.assertEqual(evidence["orientation"], "UNRESOLVED")

    def test_build_report_without_key_is_explicit_skip(self):
        report = MODULE.build_report(
            [2024],
            None,
            request_delay_seconds=0.0,
            max_429_retries=0,
        )
        self.assertEqual(report["status"], "SKIPPED_NO_CFBD_API_KEY")


if __name__ == "__main__":
    unittest.main()
