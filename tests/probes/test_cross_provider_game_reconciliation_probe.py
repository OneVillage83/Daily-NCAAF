from __future__ import annotations

import gzip
import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "probes"
    / "cross_provider_game_reconciliation_probe.py"
)
SPEC = importlib.util.spec_from_file_location("cross_provider_game_reconciliation_probe", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class CrossProviderGameReconciliationProbeTests(unittest.TestCase):
    def test_contract_version(self) -> None:
        self.assertEqual(
            probe.CONTRACT_VERSION,
            "DAILY_NCAAF_PHASE_B2C_CROSS_PROVIDER_GAME_RECONCILIATION_V1",
        )

    def test_parse_int_list(self) -> None:
        self.assertEqual(probe.parse_int_list("2024, 2026"), [2024, 2026])

    def test_normalize_id_removes_csv_float_suffix(self) -> None:
        self.assertEqual(probe.normalize_id("401234567.0"), "401234567")
        self.assertEqual(probe.normalize_id(401234567), "401234567")

    def test_decode_schedule_asset(self) -> None:
        payload = (
            "game_id,week,home_team,away_team\n"
            "401,1,Alabama,Georgia\n"
        ).encode("utf-8")
        rows = probe.decode_schedule_asset(gzip.compress(payload))
        self.assertEqual(rows[0]["game_id"], "401")
        self.assertEqual(rows[0]["home_team"], "Alabama")

    def test_compare_team_names_distinguishes_normalized_match(self) -> None:
        self.assertEqual(probe.compare_team_names("Miami (FL)", "Miami FL"), "NORMALIZED")
        self.assertEqual(probe.compare_team_names("Alabama", "Alabama"), "EXACT")
        self.assertEqual(probe.compare_team_names("USC", "Southern California"), "MISMATCH")

    def test_compare_season_measures_exact_id_overlap(self) -> None:
        cfbd_rows = [
            {
                "id": 401,
                "week": 1,
                "startDate": "2024-08-31T19:30:00Z",
                "homeTeam": "Alabama",
                "awayTeam": "Georgia",
                "homePoints": 30,
                "awayPoints": 20,
                "completed": True,
                "homeClassification": "fbs",
                "awayClassification": "fbs",
            },
            {
                "id": 402,
                "week": 1,
                "startDate": "2024-08-31T22:00:00Z",
                "homeTeam": "Team C",
                "awayTeam": "Team D",
                "homeClassification": "fbs",
                "awayClassification": "fcs",
            },
        ]
        espn_rows = [
            {
                "game_id": "401",
                "week": "1",
                "game_date": "2024-08-31T19:30:00Z",
                "home_team": "Alabama",
                "away_team": "Georgia",
                "home_score": "30",
                "away_score": "20",
                "completed": "true",
            },
            {
                "game_id": "999",
                "week": "1",
                "home_team": "FCS A",
                "away_team": "FCS B",
            },
        ]
        result = probe.compare_season(cfbd_rows, espn_rows)
        ids = result["id_reconciliation"]
        self.assertEqual(ids["exact_id_matches"], 1)
        self.assertEqual(ids["cfbd_only_count"], 1)
        self.assertEqual(ids["espn_only_count"], 1)
        self.assertEqual(ids["cfbd_exact_id_coverage_rate"], 0.5)

    def test_compare_season_normalizes_espn_fbs_universe_when_fields_exist(self) -> None:
        cfbd_rows = [
            {"id": 401, "homeTeam": "A", "awayTeam": "B"},
        ]
        espn_rows = [
            {
                "game_id": "401",
                "home_team": "A",
                "away_team": "B",
                "home_division": "FBS",
                "away_division": "FCS",
            },
            {
                "game_id": "999",
                "home_team": "C",
                "away_team": "D",
                "home_division": "FCS",
                "away_division": "FCS",
            },
        ]
        result = probe.compare_season(cfbd_rows, espn_rows)
        normalized = result["normalized_event_universe"]
        self.assertEqual(normalized["status"], "MEASURED_FROM_ESPN_DIVISION_FIELDS")
        self.assertEqual(normalized["espn_fbs_involved_ids"], 1)
        self.assertEqual(normalized["exact_overlap_with_cfbd"], 1)
        self.assertEqual(normalized["espn_only_after_normalization"], 0)

    def test_compare_matched_game_detects_kickoff_mismatch(self) -> None:
        cfbd = {
            "id": 401,
            "week": 1,
            "startDate": "2024-08-31T19:30:00Z",
            "homeTeam": "Alabama",
            "awayTeam": "Georgia",
        }
        espn = {
            "game_id": "401",
            "week": "1",
            "game_date": "2024-08-31T20:00:00Z",
            "home_team": "Alabama",
            "away_team": "Georgia",
        }
        result = probe.compare_matched_game(cfbd, espn)
        self.assertEqual(result["kickoff_state"], "MISMATCH")
        self.assertEqual(result["kickoff_delta_seconds"], 1800.0)

    def test_build_report_without_key_is_explicit_skip(self) -> None:
        report = probe.build_report(
            [2024],
            None,
            request_delay_seconds=0,
            max_429_retries=0,
        )
        self.assertEqual(report["status"], "SKIPPED_NO_CFBD_API_KEY")
        self.assertNotIn("results", report)


if __name__ == "__main__":
    unittest.main()
