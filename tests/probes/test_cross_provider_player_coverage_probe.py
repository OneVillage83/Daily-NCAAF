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

import cross_provider_player_coverage_probe as probe


class CrossProviderPlayerCoverageProbeTests(unittest.TestCase):
    def test_contract_version(self) -> None:
        self.assertEqual(
            probe.CONTRACT_VERSION,
            "DAILY_NCAAF_PHASE_B2C_PLAYER_CROSS_PROVIDER_COVERAGE_V1",
        )

    def test_sample_is_unique_and_bounded(self) -> None:
        keys = probe.sample_keys()
        self.assertEqual(len(keys), 13)
        self.assertEqual(len(keys), len(set(keys)))
        self.assertTrue(all(item["classification"] == "fbs" for item in probe.BREADTH_SLICES))

    def test_classify_complete_exact_match(self) -> None:
        state = probe.classify_slice(
            {
                "cfbd_unique_athlete_ids": 100,
                "espn_unique_athlete_ids": 100,
                "cfbd_only_athlete_id_count": 0,
                "espn_only_athlete_id_count": 0,
                "cfbd_exact_id_overlap_rate": 1.0,
                "espn_exact_id_overlap_rate": 1.0,
            }
        )
        self.assertEqual(state, "COMPLETE_EXACT_ID_SET_MATCH")

    def test_classify_high_overlap(self) -> None:
        state = probe.classify_slice(
            {
                "cfbd_unique_athlete_ids": 100,
                "espn_unique_athlete_ids": 101,
                "cfbd_only_athlete_id_count": 2,
                "espn_only_athlete_id_count": 3,
                "cfbd_exact_id_overlap_rate": 0.98,
                "espn_exact_id_overlap_rate": 0.970297,
            }
        )
        self.assertEqual(state, "HIGH_EXACT_ID_OVERLAP")

    def test_classify_partial_overlap(self) -> None:
        state = probe.classify_slice(
            {
                "cfbd_unique_athlete_ids": 100,
                "espn_unique_athlete_ids": 100,
                "cfbd_only_athlete_id_count": 10,
                "espn_only_athlete_id_count": 10,
                "cfbd_exact_id_overlap_rate": 0.90,
                "espn_exact_id_overlap_rate": 0.90,
            }
        )
        self.assertEqual(state, "PARTIAL_EXACT_ID_OVERLAP")

    def test_classify_zero_espn_rows(self) -> None:
        state = probe.classify_slice(
            {
                "cfbd_unique_athlete_ids": 100,
                "espn_unique_athlete_ids": 0,
            }
        )
        self.assertEqual(state, "NO_ESPN_TEAM_ROWS")

    def test_classify_zero_cfbd_rows(self) -> None:
        state = probe.classify_slice(
            {
                "cfbd_unique_athlete_ids": 0,
                "espn_unique_athlete_ids": 100,
            }
        )
        self.assertEqual(state, "NO_CFBD_TEAM_ROWS")

    def test_aggregate_weighted_overlap_and_provider_only_counts(self) -> None:
        results = {
            "2024:A": {
                "coverage_state": "COMPLETE_EXACT_ID_SET_MATCH",
                "comparison": {
                    "cfbd_unique_athlete_ids": 100,
                    "espn_unique_athlete_ids": 100,
                    "exact_shared_athlete_ids": 100,
                    "cfbd_only_athlete_id_count": 0,
                    "espn_only_athlete_id_count": 0,
                    "cfbd_exact_id_overlap_rate": 1.0,
                    "espn_exact_id_overlap_rate": 1.0,
                    "duplicate_cfbd_athlete_ids": [],
                    "duplicate_espn_athlete_ids": [],
                },
            },
            "2024:B": {
                "coverage_state": "HIGH_EXACT_ID_OVERLAP",
                "comparison": {
                    "cfbd_unique_athlete_ids": 100,
                    "espn_unique_athlete_ids": 100,
                    "exact_shared_athlete_ids": 98,
                    "cfbd_only_athlete_id_count": 2,
                    "espn_only_athlete_id_count": 2,
                    "cfbd_exact_id_overlap_rate": 0.98,
                    "espn_exact_id_overlap_rate": 0.98,
                    "duplicate_cfbd_athlete_ids": [],
                    "duplicate_espn_athlete_ids": [],
                },
            },
        }
        summary = probe.aggregate_slice_results(results)
        self.assertEqual(summary["exact_shared_athlete_ids_total"], 198)
        self.assertEqual(summary["cfbd_only_athlete_ids_total"], 2)
        self.assertEqual(summary["espn_only_athlete_ids_total"], 2)
        self.assertEqual(summary["weighted_cfbd_exact_id_overlap_rate"], 0.99)
        self.assertEqual(summary["weighted_espn_exact_id_overlap_rate"], 0.99)
        self.assertEqual(summary["complete_exact_id_set_match_slice_count"], 1)

    def test_aggregate_retains_zero_coverage_and_duplicate_slices(self) -> None:
        results = {
            "2024:A": {
                "coverage_state": "NO_ESPN_TEAM_ROWS",
                "comparison": {
                    "cfbd_unique_athlete_ids": 100,
                    "espn_unique_athlete_ids": 0,
                    "duplicate_cfbd_athlete_ids": ["1"],
                    "duplicate_espn_athlete_ids": [],
                },
            }
        }
        summary = probe.aggregate_slice_results(results)
        self.assertEqual(summary["zero_espn_team_row_slices"], ["2024:A"])
        self.assertEqual(summary["duplicate_id_slices"], ["2024:A"])
        self.assertEqual(summary["compared_nonempty_slice_count"], 0)

    def test_build_report_without_key_is_explicit_skip(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            report = probe.build_report()
        self.assertEqual(report["status"], "SKIPPED_NO_API_KEY")
        self.assertNotIn("api_key", report)


if __name__ == "__main__":
    unittest.main()
