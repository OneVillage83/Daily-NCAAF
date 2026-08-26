from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "probes" / "provider_coverage_probe.py"
SPEC = importlib.util.spec_from_file_location("provider_coverage_probe", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class ProviderCoverageProbeTests(unittest.TestCase):
    def test_parse_int_list(self) -> None:
        self.assertEqual(probe.parse_int_list("2004, 2010,2024"), [2004, 2010, 2024])

    def test_select_season_asset_prefers_parquet(self) -> None:
        assets = [
            {"name": "play_by_play_2024.csv", "size": 100},
            {"name": "play_by_play_2024.rds", "size": 80},
            {"name": "play_by_play_2024.parquet", "size": 50},
        ]
        selected = probe.select_season_asset(assets, 2024)
        self.assertIsNotNone(selected)
        self.assertEqual(selected["name"], "play_by_play_2024.parquet")

    def test_select_season_asset_missing(self) -> None:
        self.assertIsNone(probe.select_season_asset([], 2024))

    def test_summarize_games(self) -> None:
        rows = [
            {
                "id": 1,
                "completed": True,
                "neutralSite": False,
                "homeConference": "SEC",
                "awayConference": "ACC",
            },
            {
                "id": 2,
                "completed": False,
                "neutralSite": True,
                "homeConference": "Big Ten",
                "awayConference": None,
            },
            {
                "id": 2,
                "completed": False,
                "neutralSite": True,
                "homeConference": "Big Ten",
                "awayConference": None,
            },
        ]
        summary = probe.summarize_games(rows)
        self.assertEqual(summary["rows"], 3)
        self.assertEqual(summary["unique_game_ids"], 2)
        self.assertEqual(summary["duplicate_game_id_rows"], 1)
        self.assertEqual(summary["completed_rows"], 1)
        self.assertEqual(summary["neutral_site_rows"], 2)
        self.assertEqual(summary["away_conference_null_rows"], 2)

    def test_summarize_plays(self) -> None:
        rows = [
            {
                "id": 10,
                "gameId": 1,
                "wallclock": "2024-09-01T00:00:00Z",
                "ppa": 0.1,
                "playText": "Run",
                "playType": "Rush",
            },
            {
                "id": 11,
                "gameId": 1,
                "wallclock": None,
                "ppa": None,
                "playText": None,
                "playType": "Pass Reception",
            },
            {
                "id": 11,
                "gameId": 1,
                "wallclock": None,
                "ppa": None,
                "playText": None,
                "playType": "Pass Reception",
            },
        ]
        summary = probe.summarize_plays(rows)
        self.assertEqual(summary["rows"], 3)
        self.assertEqual(summary["unique_game_ids"], 1)
        self.assertEqual(summary["unique_play_ids"], 2)
        self.assertEqual(summary["duplicate_play_id_rows"], 1)
        self.assertEqual(summary["wallclock_null_rows"], 2)
        self.assertEqual(summary["ppa_null_rows"], 2)
        self.assertEqual(summary["play_text_null_rows"], 2)

    def test_cfbd_without_key_is_explicit_skip(self) -> None:
        result = probe.cfbd_probe([2024], [1], None)
        self.assertEqual(result["status"], "SKIPPED_NO_CFBD_API_KEY")
        self.assertNotIn("seasons", result)

    def test_known_lookahead_fields_are_locked(self) -> None:
        self.assertIn("lead_text", probe.KNOWN_CFBFASTR_LOOKAHEAD_FIELDS)
        self.assertIn("lead_scoringPlay", probe.KNOWN_CFBFASTR_LOOKAHEAD_FIELDS)


if __name__ == "__main__":
    unittest.main()
