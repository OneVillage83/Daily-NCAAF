import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "probes" / "cross_provider_game_reconciliation_probe_v3.py"
SPEC = importlib.util.spec_from_file_location("cross_provider_game_reconciliation_probe_v3", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CrossProviderGameReconciliationProbeV3Tests(unittest.TestCase):
    def test_contract_version(self):
        self.assertEqual(
            MODULE.CONTRACT_VERSION,
            "DAILY_NCAAF_PHASE_B2C_CROSS_PROVIDER_GAME_RECONCILIATION_V3",
        )

    def test_parse_int_list(self):
        self.assertEqual(MODULE.parse_int_list("2024, 2026"), [2024, 2026])

    def test_select_schedule_asset_prefers_newer_plain_csv_over_old_gzip(self):
        manifest = {
            "assets": [
                {
                    "name": "cfb_schedule_2024.csv.gz",
                    "browser_download_url": "https://example/old-gz",
                    "updated_at": "2026-07-18T13:43:29Z",
                },
                {
                    "name": "cfb_schedule_2024.csv",
                    "browser_download_url": "https://example/new-csv",
                    "updated_at": "2026-09-01T03:26:59Z",
                },
            ]
        }
        selected = MODULE.select_schedule_asset(manifest, 2024)
        self.assertEqual(selected["name"], "cfb_schedule_2024.csv")

    def test_select_schedule_asset_uses_format_as_tie_breaker(self):
        manifest = {
            "assets": [
                {
                    "name": "cfb_schedule_2024.csv",
                    "browser_download_url": "https://example/csv",
                    "updated_at": "2026-09-01T03:26:59Z",
                },
                {
                    "name": "cfb_schedule_2024.csv.gz",
                    "browser_download_url": "https://example/gz",
                    "updated_at": "2026-09-01T03:26:59Z",
                },
            ]
        }
        selected = MODULE.select_schedule_asset(manifest, 2024)
        self.assertEqual(selected["name"], "cfb_schedule_2024.csv.gz")

    def test_infer_same_side_orientation(self):
        cfbd = {"homeTeam": "Alabama", "awayTeam": "Georgia"}
        espn = {
            "home_team": "Alabama Crimson Tide",
            "away_team": "Georgia Bulldogs",
        }
        self.assertEqual(MODULE.infer_side_orientation(cfbd, espn), "SAME_SIDE")

    def test_infer_swapped_side_orientation(self):
        cfbd = {"homeTeam": "Coastal Carolina", "awayTeam": "UTSA"}
        espn = {
            "home_team": "UTSA Roadrunners",
            "away_team": "Coastal Carolina Chanticleers",
        }
        self.assertEqual(MODULE.infer_side_orientation(cfbd, espn), "SWAPPED_SIDES")

    def test_swapped_side_score_compares_by_participant(self):
        cfbd = {
            "id": 1,
            "homeTeam": "Coastal Carolina",
            "awayTeam": "UTSA",
            "homePoints": 15,
            "awayPoints": 44,
            "week": 1,
            "startDate": "2024-12-23T16:00:00Z",
            "completed": True,
        }
        espn = {
            "game_id": "1",
            "home_id": "2636",
            "home_team": "UTSA Roadrunners",
            "home_score": "44",
            "away_id": "324",
            "away_team": "Coastal Carolina Chanticleers",
            "away_score": "15",
            "week": "1",
            "game_date": "2024-12-23T16:00Z",
            "status": "STATUS_FINAL",
        }
        result = MODULE.compare_matched_game(cfbd, espn)
        self.assertEqual(result["side_orientation"], "SWAPPED_SIDES")
        self.assertEqual(result["score_state"], "MATCH")
        self.assertEqual(result["aligned_participants"]["cfbd_home_to_espn"]["id"], "324")
        self.assertEqual(result["aligned_participants"]["cfbd_away_to_espn"]["id"], "2636")

    def test_swapped_event_does_not_create_team_crosswalk_conflict(self):
        cfbd_index = {
            "1": {"homeTeam": "UTSA", "awayTeam": "Rice"},
            "2": {"homeTeam": "Coastal Carolina", "awayTeam": "UTSA"},
        }
        espn_index = {
            "1": {
                "home_id": "2636",
                "home_team": "UTSA Roadrunners",
                "away_id": "242",
                "away_team": "Rice Owls",
            },
            "2": {
                "home_id": "2636",
                "home_team": "UTSA Roadrunners",
                "away_id": "324",
                "away_team": "Coastal Carolina Chanticleers",
            },
        }
        report = MODULE.derive_team_crosswalk(cfbd_index, espn_index, ["1", "2"])
        self.assertEqual(report["cfbd_name_to_multiple_espn_id_conflict_count"], 0)
        self.assertEqual(report["crosswalk"]["UTSA"]["espn_ids"], ["2636"])
        self.assertEqual(report["crosswalk"]["Coastal Carolina"]["espn_ids"], ["324"])

    def test_fbs_derivation_respects_swapped_orientation(self):
        cfbd_index = {
            "1": {
                "homeTeam": "Coastal Carolina",
                "awayTeam": "UTSA",
                "homeClassification": "fbs",
                "awayClassification": "fbs",
            }
        }
        espn_index = {
            "1": {
                "home_id": "2636",
                "home_team": "UTSA Roadrunners",
                "away_id": "324",
                "away_team": "Coastal Carolina Chanticleers",
            }
        }
        self.assertEqual(MODULE.derive_espn_fbs_ids(cfbd_index, espn_index, ["1"]), {"2636", "324"})

    def test_current_strict_subset_is_labeled_snapshot_relation(self):
        cfbd_rows = [
            {
                "id": 1,
                "homeTeam": "Alabama",
                "awayTeam": "Georgia",
                "homeClassification": "fbs",
                "awayClassification": "fbs",
                "week": 1,
                "startDate": "2026-08-29T16:00:00Z",
                "completed": True,
                "homePoints": 20,
                "awayPoints": 10,
            },
            {
                "id": 2,
                "homeTeam": "Texas",
                "awayTeam": "Oklahoma",
                "homeClassification": "fbs",
                "awayClassification": "fbs",
                "week": 2,
                "startDate": "2026-09-05T16:00:00Z",
                "completed": False,
            },
        ]
        espn_rows = [
            {
                "game_id": "1",
                "home_id": "333",
                "home_team": "Alabama Crimson Tide",
                "away_id": "61",
                "away_team": "Georgia Bulldogs",
                "week": "1",
                "game_date": "2026-08-29T16:00Z",
                "home_score": "20",
                "away_score": "10",
                "status": "STATUS_FINAL",
            }
        ]
        result = MODULE.compare_season(cfbd_rows, espn_rows)
        self.assertEqual(
            result["snapshot_relation"]["state"],
            "ESPN_EVENT_SET_STRICT_SUBSET_OF_CFBD_AT_ACQUISITION",
        )

    def test_lifecycle_lag_is_exposed_without_identity_failure(self):
        cfbd = {
            "id": 1,
            "homeTeam": "Stanford",
            "awayTeam": "Hawai'i",
            "homePoints": 37,
            "awayPoints": 27,
            "week": 1,
            "startDate": "2026-08-29T23:00:00Z",
            "completed": True,
        }
        espn = {
            "game_id": "1",
            "home_id": "24",
            "home_team": "Stanford Cardinal",
            "home_score": "23",
            "away_id": "62",
            "away_team": "Hawai'i Rainbow Warriors",
            "away_score": "7",
            "week": "1",
            "game_date": "2026-08-29T23:00Z",
            "status": "STATUS_IN_PROGRESS",
        }
        result = MODULE.compare_matched_game(cfbd, espn)
        self.assertEqual(result["side_orientation"], "SAME_SIDE")
        self.assertEqual(result["lifecycle_state"], "MISMATCH")
        self.assertEqual(result["score_state"], "MISMATCH")

    def test_kickoff_bucket_counts(self):
        items = [
            {"kickoff_delta_seconds": 0.0},
            {"kickoff_delta_seconds": 300.0},
            {"kickoff_delta_seconds": 600.0},
            {"kickoff_delta_seconds": 3600.0},
            {"kickoff_delta_seconds": 8700.0},
        ]
        counts = MODULE.kickoff_bucket_counts(items)
        self.assertEqual(counts["LE_60S"], 1)
        self.assertEqual(counts["GT_60S_LE_5M"], 1)
        self.assertEqual(counts["GT_5M_LE_30M"], 1)
        self.assertEqual(counts["GT_30M_LE_2H"], 1)
        self.assertEqual(counts["GT_2H"], 1)

    def test_unresolved_orientation_does_not_force_score_mismatch(self):
        cfbd = {
            "id": 1,
            "homeTeam": "Alpha",
            "awayTeam": "Beta",
            "homePoints": 10,
            "awayPoints": 20,
            "week": 1,
            "startDate": "2024-08-31T16:00:00Z",
            "completed": True,
        }
        espn = {
            "game_id": "1",
            "home_team": "Gamma",
            "away_team": "Delta",
            "home_score": "10",
            "away_score": "20",
            "week": "1",
            "game_date": "2024-08-31T16:00Z",
            "status": "STATUS_FINAL",
        }
        result = MODULE.compare_matched_game(cfbd, espn)
        self.assertEqual(result["side_orientation"], "UNRESOLVED")
        self.assertEqual(result["score_state"], "UNRESOLVED_ORIENTATION")

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
