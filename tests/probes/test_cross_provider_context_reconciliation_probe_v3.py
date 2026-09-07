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

import cross_provider_context_reconciliation_probe_v2 as v2
import cross_provider_context_reconciliation_probe_v3 as probe


class CrossProviderContextReconciliationProbeV3Tests(unittest.TestCase):
    def test_contract_version(self) -> None:
        self.assertEqual(
            probe.CONTRACT_VERSION,
            "DAILY_NCAAF_PHASE_B2C_CONTEXT_RECONCILIATION_V3",
        )

    def test_american_semantic_tokens_collapse(self) -> None:
        expected = "american_athletic"
        self.assertEqual(probe.canonical_conference_token("American Athletic"), expected)
        self.assertEqual(probe.canonical_conference_token("American Conference"), expected)
        self.assertEqual(probe.canonical_conference_token("American"), expected)

    def test_american_provider_names_are_semantic_alias_match(self) -> None:
        team = {
            "conference_name": "American Conference",
            "conference_short_name": "American",
            "conference_id": "151",
        }
        state, aliases = probe.compare_conference_alias("American Athletic", team)
        self.assertEqual(state, "SEMANTIC_ALIAS_MATCH")
        self.assertIn("American Conference", aliases)

    def test_existing_exact_match_remains_exact(self) -> None:
        team = {
            "conference_name": "Southeastern Conference",
            "conference_short_name": "SEC",
            "conference_abbreviation": "SEC",
        }
        state, _ = probe.compare_conference_alias("SEC", team)
        self.assertEqual(state, "EXACT_ALIAS_MATCH")

    def test_existing_normalized_match_remains_normalized(self) -> None:
        team = {"conference_name": "Mid-American Conference"}
        state, _ = probe.compare_conference_alias("Mid-American", team)
        self.assertEqual(state, "NORMALIZED_ALIAS_MATCH")

    def test_unrelated_conferences_remain_mismatch(self) -> None:
        team = {"conference_name": "Big Ten Conference", "conference_short_name": "Big Ten"}
        state, _ = probe.compare_conference_alias("SEC", team)
        self.assertEqual(state, "MISMATCH")

    def test_missing_metadata_remains_unavailable(self) -> None:
        state, aliases = probe.compare_conference_alias("SEC", None)
        self.assertEqual(state, "UNAVAILABLE_TEAM_METADATA")
        self.assertEqual(aliases, [])

    def test_build_report_without_key_is_v3_and_restores_v2_function(self) -> None:
        original = v2.compare_conference_alias
        with patch.dict(os.environ, {}, clear=True):
            report = probe.build_report(seasons=[2024], request_delay_seconds=0)
        self.assertEqual(report["status"], "SKIPPED_NO_API_KEY")
        self.assertEqual(report["contract_version"], probe.CONTRACT_VERSION)
        self.assertIs(v2.compare_conference_alias, original)
        self.assertEqual(
            report["conference_semantic_alias_policy"]["mode"],
            "EXPLICIT_ENUMERATED_EQUIVALENCE_ONLY",
        )


if __name__ == "__main__":
    unittest.main()
