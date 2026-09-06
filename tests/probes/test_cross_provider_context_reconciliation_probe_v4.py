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

import cross_provider_context_reconciliation_probe_v4 as probe


class CrossProviderContextReconciliationProbeV4Tests(unittest.TestCase):
    def test_contract_version(self) -> None:
        self.assertEqual(
            probe.CONTRACT_VERSION,
            "DAILY_NCAAF_PHASE_B2C_CONTEXT_RECONCILIATION_V4",
        )

    def test_existing_american_semantic_alias_still_matches(self) -> None:
        state, _ = probe.compare_conference_alias(
            "American Athletic",
            {"conference_name": "American Conference", "conference_short_name": "American"},
        )
        self.assertEqual(state, "SEMANTIC_ALIAS_MATCH")

    def test_coastal_athletic_semantic_alias_matches(self) -> None:
        state, _ = probe.compare_conference_alias(
            "Coastal Athletic",
            {"conference_name": "Coastal Athletic Association", "conference_abbreviation": "CAA"},
        )
        self.assertEqual(state, "SEMANTIC_ALIAS_MATCH")

    def test_unrelated_conferences_remain_mismatch(self) -> None:
        state, _ = probe.compare_conference_alias(
            "UAC",
            {"conference_name": "Southland Conference", "conference_short_name": "Southland"},
        )
        self.assertEqual(state, "MISMATCH")

    def test_big_south_ovc_is_association_model_difference(self) -> None:
        state = probe.residual_mismatch_class(
            "Big South-OVC", ["Ohio Valley Conference", "OVC"], "179"
        )
        self.assertEqual(state, "CONFERENCE_ASSOCIATION_MODEL_DIFFERENCE")

    def test_ovc_big_south_is_association_model_difference(self) -> None:
        state = probe.residual_mismatch_class(
            "OVC-Big South", ["Ohio Valley Conference", "OVC"], 179
        )
        self.assertEqual(state, "CONFERENCE_ASSOCIATION_MODEL_DIFFERENCE")

    def test_uac_southland_is_temporal_conflict_candidate(self) -> None:
        state = probe.residual_mismatch_class(
            "UAC", ["Southland Conference", "Southland", "land"], "30"
        )
        self.assertEqual(state, "TEMPORAL_AFFILIATION_CONFLICT_CANDIDATE")

    def test_unknown_signature_is_unclassified(self) -> None:
        state = probe.residual_mismatch_class("Mystery", ["Other"], "999")
        self.assertEqual(state, "UNCLASSIFIED")

    def test_summary_counts_all_residual_signatures(self) -> None:
        rows = [
            {
                "side_orientation": "SAME_SIDE",
                "home": {
                    "external_team_id_state": "MATCH",
                    "division_state": "MATCH",
                    "conference_state": "EXACT_ALIAS_MATCH",
                },
                "away": {
                    "external_team_id_state": "MATCH",
                    "division_state": "MATCH",
                    "conference_state": "MISMATCH",
                    "cfbd_conference": "Big South-OVC",
                    "espn_conference_aliases": ["Ohio Valley Conference", "OVC"],
                    "espn_conference_id": "179",
                },
                "home_venue_anchor": {"state": "MATCH"},
            },
            {
                "side_orientation": "SAME_SIDE",
                "home": {
                    "external_team_id_state": "MATCH",
                    "division_state": "MATCH",
                    "conference_state": "EXACT_ALIAS_MATCH",
                },
                "away": {
                    "external_team_id_state": "MATCH",
                    "division_state": "MATCH",
                    "conference_state": "MISMATCH",
                    "cfbd_conference": "UAC",
                    "espn_conference_aliases": ["Southland Conference", "Southland"],
                    "espn_conference_id": "30",
                },
                "home_venue_anchor": {"state": "MATCH"},
            },
        ]
        summary = probe.summarize_with_signatures(rows)
        self.assertEqual(summary["conference_mismatch_total"], 2)
        self.assertEqual(summary["conference_mismatch_unclassified_count"], 0)
        self.assertEqual(
            summary["conference_mismatch_class_counts"][
                "CONFERENCE_ASSOCIATION_MODEL_DIFFERENCE"
            ],
            1,
        )
        self.assertEqual(
            summary["conference_mismatch_class_counts"][
                "TEMPORAL_AFFILIATION_CONFLICT_CANDIDATE"
            ],
            1,
        )

    def test_build_report_without_key_restores_v2_functions(self) -> None:
        import cross_provider_context_reconciliation_probe_v2 as v2

        before_compare = v2.compare_conference_alias
        before_summarize = v2.summarize
        with patch.dict(os.environ, {}, clear=True):
            report = probe.build_report(seasons=[2024], request_delay_seconds=0)
        self.assertEqual(report["status"], "SKIPPED_NO_API_KEY")
        self.assertEqual(report["contract_version"], probe.CONTRACT_VERSION)
        self.assertIs(v2.compare_conference_alias, before_compare)
        self.assertIs(v2.summarize, before_summarize)


if __name__ == "__main__":
    unittest.main()
