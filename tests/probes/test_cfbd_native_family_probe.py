from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "probes" / "cfbd_native_family_probe.py"
SPEC = importlib.util.spec_from_file_location("cfbd_native_family_probe", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class CFBDNativeFamilyProbeTests(unittest.TestCase):
    def test_contract_version(self) -> None:
        self.assertEqual(
            probe.CONTRACT_VERSION,
            "DAILY_NCAAF_PHASE_B2_CFBD_NATIVE_FAMILY_PROBE_V1",
        )

    def test_parse_csv(self) -> None:
        self.assertEqual(
            probe.parse_csv("Alabama, Michigan,Notre Dame"),
            ["Alabama", "Michigan", "Notre Dame"],
        )

    def test_build_report_without_key_is_explicit_skip(self) -> None:
        report = probe.build_report(
            [2024],
            ["Michigan"],
            1,
            {"rosters"},
            None,
        )
        self.assertEqual(report["status"], "SKIPPED_NO_CFBD_API_KEY")
        self.assertNotIn("results", report)

    def test_list_result_summary_detects_duplicates_and_null_id(self) -> None:
        rows = [{"id": "1"}, {"id": "2"}, {"id": "2"}, {"id": None}]
        summary = probe.list_result_summary(rows, "id")
        self.assertEqual(summary["rows"], 4)
        self.assertEqual(summary["unique_ids"], 2)
        self.assertEqual(summary["duplicate_id_rows"], 1)
        self.assertEqual(summary["id_null_rows"], 1)

    def test_summarize_roster_measures_recruit_linkage(self) -> None:
        rows = [
            {
                "id": "1",
                "team": "Michigan",
                "position": "QB",
                "jersey": 7,
                "height": 74,
                "weight": 210,
                "recruitIds": ["r1"],
            },
            {
                "id": "2",
                "team": "Michigan",
                "position": None,
                "jersey": None,
                "height": None,
                "weight": None,
                "recruitIds": None,
            },
        ]
        summary = probe.summarize_roster(rows)
        self.assertEqual(summary["rows"], 2)
        self.assertEqual(summary["recruit_ids_nonempty_rows"], 1)
        self.assertEqual(summary["recruit_ids_null_rows"], 1)
        self.assertEqual(summary["position_null_rows"], 1)

    def test_summarize_recruits_measures_athlete_linkage(self) -> None:
        rows = [
            {
                "id": "r1",
                "athleteId": "p1",
                "committedTo": "Michigan",
                "ranking": 1,
                "rating": 0.99,
                "stars": 5,
                "position": "QB",
            },
            {
                "id": "r2",
                "athleteId": None,
                "committedTo": None,
                "ranking": None,
                "rating": None,
                "stars": None,
                "position": None,
            },
        ]
        summary = probe.summarize_recruits(rows)
        self.assertEqual(summary["athlete_id_null_rows"], 1)
        self.assertEqual(summary["committed_to_null_rows"], 1)
        self.assertEqual(summary["rating_null_rows"], 1)

    def test_summarize_portal_keeps_unknown_destination(self) -> None:
        rows = [
            {
                "origin": "A",
                "destination": "B",
                "transferDate": "2026-01-01T00:00:00Z",
                "rating": 0.9,
                "stars": 4,
                "eligibility": "Immediate",
            },
            {
                "origin": "C",
                "destination": None,
                "transferDate": None,
                "rating": None,
                "stars": None,
                "eligibility": "TBD",
            },
        ]
        summary = probe.summarize_portal(rows)
        self.assertEqual(summary["destination_null_rows"], 1)
        self.assertEqual(summary["transfer_date_null_rows"], 1)
        self.assertEqual(summary["unique_destinations"], 1)

    def test_summarize_lines_counts_nested_provider_observations(self) -> None:
        rows = [
            {
                "lines": [
                    {
                        "provider": "Book A",
                        "spread": -3.5,
                        "spreadOpen": -2.5,
                        "overUnder": 50.5,
                        "overUnderOpen": None,
                        "homeMoneyline": -150,
                        "awayMoneyline": 130,
                    },
                    {
                        "provider": "Book B",
                        "spread": None,
                        "spreadOpen": None,
                        "overUnder": 51.0,
                        "overUnderOpen": 50.0,
                        "homeMoneyline": None,
                        "awayMoneyline": None,
                    },
                ]
            },
            {"lines": []},
        ]
        summary = probe.summarize_lines(rows)
        self.assertEqual(summary["game_rows"], 2)
        self.assertEqual(summary["games_with_lines"], 1)
        self.assertEqual(summary["line_observations"], 2)
        self.assertEqual(summary["spread_null_observations"], 1)
        self.assertEqual(summary["over_under_open_null_observations"], 1)


if __name__ == "__main__":
    unittest.main()
