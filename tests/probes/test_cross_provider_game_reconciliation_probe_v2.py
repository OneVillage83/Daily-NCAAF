import gzip
import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "probes" / "cross_provider_game_reconciliation_probe_v2.py"
SPEC = importlib.util.spec_from_file_location("cross_provider_game_reconciliation_probe_v2", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CrossProviderGameReconciliationProbeV2Tests(unittest.TestCase):
    def test_contract_version(self):
        self.assertEqual(
            MODULE.CONTRACT_VERSION,
            "DAILY_NCAAF_PHASE_B2C_CROSS_PROVIDER_GAME_RECONCILIATION_V2",
        )

    def test_parse_int_list(self):
        self.assertEqual(MODULE.parse_int_list("2024, 2026"), [2024, 2026])

    def test_normalize_id_removes_csv_float_suffix(self):
        self.assertEqual(MODULE.normalize_id("401628319.0"), "401628319")

    def test_select_schedule_asset_prefers_csv_gz(self):
        manifest = {
            "assets": [
                {
                    "name": "cfb_schedule_2024.csv",
                    "browser_download_url": "https://example/csv",
                },
                {
                    "name": "cfb_schedule_2024.csv.gz",
                    "browser_download_url": "https://example/gz",
                },
                {
                    "name": "cfb_schedule_2024.parquet",
                    "browser_download_url": "https://example/parquet",
                },
            ]
        }
        selected = MODULE.select_schedule_asset(manifest, 2024)
        self.assertEqual(selected["name"], "cfb_schedule_2024.csv.gz")

    def test_select_schedule_asset_falls_back_to_plain_csv(self):
        manifest = {
            "assets": [
                {
                    "name": "cfb_schedule_2026.csv",
                    "browser_download_url": "https://example/csv",
                },
                {
                    "name": "cfb_schedule_2026.parquet",
                    "browser_download_url": "https://example/parquet",
                },
            ]
        }
        selected = MODULE.select_schedule_asset(manifest, 2026)
        self.assertEqual(selected["name"], "cfb_schedule_2026.csv")

    def test_decode_plain_csv(self):
        raw = b"game_id,home_team,away_team\n1,Alabama,Georgia\n"
        rows = MODULE.decode_schedule_asset(raw, "cfb_schedule_2026.csv")
        self.assertEqual(rows[0]["game_id"], "1")

    def test_decode_gzip_csv(self):
        raw = gzip.compress(b"game_id,home_team,away_team\n1,Alabama,Georgia\n")
        rows = MODULE.decode_schedule_asset(raw, "cfb_schedule_2024.csv.gz")
        self.assertEqual(rows[0]["home_team"], "Alabama")

    def test_display_name_prefix_is_not_generic_mismatch(self):
        self.assertEqual(
            MODULE.compare_display_names("Alabama", "Alabama Crimson Tide"),
            "CFBD_NAME_PREFIX_OF_ESPN_DISPLAY",
        )

    def test_espn_completed_uses_status(self):
        self.assertTrue(MODULE.espn_completed({"status": "STATUS_FINAL"}))
        self.assertFalse(MODULE.espn_completed({"status": "STATUS_SCHEDULED"}))

    def test_team_crosswalk_detects_no_conflict_for_repeated_pair(self):
        cfbd_index = {
            "1": {"homeTeam": "Alabama", "awayTeam": "Georgia"},
            "2": {"homeTeam": "Alabama", "awayTeam": "Auburn"},
        }
        espn_index = {
            "1": {"home_id": "333", "home_team": "Alabama Crimson Tide", "away_id": "61", "away_team": "Georgia Bulldogs"},
            "2": {"home_id": "333", "home_team": "Alabama Crimson Tide", "away_id": "2", "away_team": "Auburn Tigers"},
        }
        report = MODULE.derive_team_crosswalk(cfbd_index, espn_index, ["1", "2"])
        self.assertEqual(report["cfbd_name_to_multiple_espn_id_conflict_count"], 0)
        self.assertEqual(report["crosswalk"]["Alabama"]["espn_ids"], ["333"])

    def test_derived_fbs_universe_uses_matched_side_ids(self):
        cfbd_rows = [
            {
                "id": 1,
                "homeTeam": "Alabama",
                "awayTeam": "Georgia",
                "homeClassification": "fbs",
                "awayClassification": "fbs",
                "week": 1,
                "startDate": "2024-08-31T16:00:00Z",
                "homePoints": 20,
                "awayPoints": 10,
                "completed": True,
            }
        ]
        espn_rows = [
            {
                "game_id": "1",
                "home_id": "333",
                "away_id": "61",
                "home_team": "Alabama Crimson Tide",
                "away_team": "Georgia Bulldogs",
                "week": "1",
                "game_date": "2024-08-31T16:00Z",
                "home_score": "20",
                "away_score": "10",
                "status": "STATUS_FINAL",
            },
            {
                "game_id": "2",
                "home_id": "333",
                "away_id": "999",
                "home_team": "Alabama Crimson Tide",
                "away_team": "Other",
                "week": "2",
                "game_date": "2024-09-07T16:00Z",
                "status": "STATUS_SCHEDULED",
            },
            {
                "game_id": "3",
                "home_id": "888",
                "away_id": "999",
                "home_team": "FCS A",
                "away_team": "FCS B",
                "week": "2",
                "game_date": "2024-09-07T17:00Z",
                "status": "STATUS_SCHEDULED",
            },
        ]
        result = MODULE.compare_season(cfbd_rows, espn_rows)
        normalized = result["normalized_event_universe"]
        self.assertEqual(normalized["espn_fbs_involved_event_ids"], 2)
        self.assertEqual(normalized["espn_only_after_normalization"], 1)

    def test_field_specific_kickoff_mismatch_is_exposed(self):
        cfbd_rows = [
            {
                "id": 1,
                "homeTeam": "Alabama",
                "awayTeam": "Georgia",
                "homeClassification": "fbs",
                "awayClassification": "fbs",
                "week": 1,
                "startDate": "2024-08-31T16:00:00Z",
                "homePoints": 20,
                "awayPoints": 10,
                "completed": True,
            }
        ]
        espn_rows = [
            {
                "game_id": "1",
                "home_id": "333",
                "away_id": "61",
                "home_team": "Alabama Crimson Tide",
                "away_team": "Georgia Bulldogs",
                "week": "1",
                "game_date": "2024-08-31T17:00Z",
                "home_score": "20",
                "away_score": "10",
                "status": "STATUS_FINAL",
            }
        ]
        result = MODULE.compare_season(cfbd_rows, espn_rows)
        examples = result["matched_field_agreement"]["kickoff_mismatch_examples"]
        self.assertEqual(len(examples), 1)
        self.assertEqual(examples[0]["kickoff_delta_seconds"], 3600.0)

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
