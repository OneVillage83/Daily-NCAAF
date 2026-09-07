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

import cross_provider_play_reconciliation_probe as probe


class CrossProviderPlayReconciliationProbeTests(unittest.TestCase):
    def test_contract_version(self) -> None:
        self.assertEqual(
            probe.CONTRACT_VERSION,
            "DAILY_NCAAF_PHASE_B2C_SELECTED_PLAY_RECONCILIATION_V1",
        )

    def test_parse_int_list(self) -> None:
        self.assertEqual(probe.parse_int_list("1, 2,3"), [1, 2, 3])

    def test_normalize_id_handles_numeric_string(self) -> None:
        self.assertEqual(probe.normalize_id("401.0"), "401")
        self.assertEqual(probe.normalize_id(401), "401")
        self.assertIsNone(probe.normalize_id(None))

    def test_parse_clock_seconds(self) -> None:
        self.assertEqual(probe.parse_clock_seconds({"minutes": 12, "seconds": 34}), 754)
        self.assertEqual(probe.parse_clock_seconds({"displayValue": "1:05"}), 65)
        self.assertEqual(probe.parse_clock_seconds("0:09"), 9)
        self.assertIsNone(probe.parse_clock_seconds(None))

    def test_extract_espn_plays_previous_and_current(self) -> None:
        summary = {
            "drives": {
                "previous": [
                    {"id": "d1", "plays": [{"id": "p1"}, {"id": "p2"}]}
                ],
                "current": {"id": "d2", "plays": [{"id": "p3"}]},
            }
        }
        self.assertEqual(
            [row["id"] for row in probe.extract_espn_plays(summary)],
            ["p1", "p2", "p3"],
        )

    def test_scalar_state_preserves_unavailable(self) -> None:
        self.assertEqual(probe.scalar_state(None, None), "UNAVAILABLE_BOTH")
        self.assertEqual(probe.scalar_state(1, None), "UNAVAILABLE_ONE_SIDE")
        self.assertEqual(probe.scalar_state(1, 1), "MATCH")
        self.assertEqual(probe.scalar_state(1, 2), "MISMATCH")

    def test_text_state_exact_normalized_and_mismatch(self) -> None:
        self.assertEqual(probe.text_state("Pass", "Pass"), "EXACT")
        self.assertEqual(probe.text_state("Pass, complete!", "pass complete"), "NORMALIZED")
        self.assertEqual(probe.text_state("rush", "pass"), "MISMATCH")

    def test_compare_shared_play_core_fields(self) -> None:
        cfbd = {
            "period": 2,
            "clock": {"minutes": 3, "seconds": 21},
            "down": 3,
            "distance": 7,
            "yardsToGoal": 44,
            "scoring": False,
            "playType": "Rush",
            "playText": "Runner for 4 yards",
        }
        espn = {
            "period": {"number": 2},
            "clock": {"displayValue": "3:21"},
            "start": {"down": 3, "distance": 7, "yardsToEndzone": 44},
            "scoringPlay": False,
            "type": {"text": "Rush"},
            "text": "Runner for 4 yards",
        }
        states, _ = probe.compare_shared_play(cfbd, espn)
        self.assertTrue(all(value in {"MATCH", "EXACT"} for value in states.values()))

    def test_reconcile_game_plays_exact_and_provider_only(self) -> None:
        cfbd = [
            {"id": "1", "period": 1},
            {"id": "2", "period": 1},
            {"id": "3", "period": 1},
        ]
        espn = [
            {"id": "2", "period": {"number": 1}},
            {"id": "3", "period": {"number": 1}},
            {"id": "4", "period": {"number": 1}},
        ]
        result = probe.reconcile_game_plays(cfbd, espn)
        self.assertEqual(result["exact_shared_play_ids"], 2)
        self.assertEqual(result["cfbd_only_play_ids_count"], 1)
        self.assertEqual(result["espn_only_play_ids_count"], 1)
        self.assertAlmostEqual(result["cfbd_exact_id_overlap_rate"], 2 / 3)
        self.assertAlmostEqual(result["espn_exact_id_overlap_rate"], 2 / 3)

    def test_duplicate_play_ids_are_surfaced(self) -> None:
        result = probe.reconcile_game_plays(
            [{"id": "1"}, {"id": "1"}],
            [{"id": "1"}, {"id": "1"}],
        )
        self.assertEqual(result["cfbd_duplicate_play_ids"], ["1"])
        self.assertEqual(result["espn_duplicate_play_ids"], ["1"])

    def test_semantic_mismatch_does_not_change_identity_count(self) -> None:
        result = probe.reconcile_game_plays(
            [{"id": "1", "down": 1}],
            [{"id": "1", "start": {"down": 2}}],
        )
        self.assertEqual(result["exact_shared_play_ids"], 1)
        self.assertEqual(result["field_state_counts"]["down"]["MISMATCH"], 1)

    def test_build_report_without_key_is_explicit_skip(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            report = probe.build_report(game_ids=[401628339], request_delay_seconds=0)
        self.assertEqual(report["status"], "SKIPPED_NO_API_KEY")
        self.assertEqual(report["contract_version"], probe.CONTRACT_VERSION)
        self.assertIn("environment only", report["secret_policy"])
        self.assertNotIn("Authorization", str(report))


if __name__ == "__main__":
    unittest.main()
