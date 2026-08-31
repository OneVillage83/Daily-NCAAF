from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "probes" / "cfbd_talent_scope_probe.py"
SPEC = importlib.util.spec_from_file_location("cfbd_talent_scope_probe", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class CFBDTalentScopeProbeTests(unittest.TestCase):
    def test_contract_version(self) -> None:
        self.assertEqual(
            probe.CONTRACT_VERSION,
            "DAILY_NCAAF_PHASE_B2_CFBD_TALENT_SCOPE_PROBE_V1",
        )

    def test_parse_int_list(self) -> None:
        self.assertEqual(probe.parse_int_list("2023, 2024,2025"), [2023, 2024, 2025])

    def test_extract_names_ignores_null_and_blank(self) -> None:
        fbs_rows = [{"school": "A"}, {"school": None}, {"school": "  "}, {"school": "B"}]
        talent_rows = [{"team": "A"}, {"team": None}, {"team": " C "}]
        self.assertEqual(probe.extract_fbs_names(fbs_rows), ["A", "B"])
        self.assertEqual(probe.extract_talent_names(talent_rows), ["A", "C"])

    def test_compare_membership_surfaces_mismatches_without_normalizing(self) -> None:
        summary = probe.compare_membership(
            ["A", "B", "C"],
            ["A", "B", "D"],
        )
        self.assertEqual(summary["exact_name_overlap"], 2)
        self.assertEqual(summary["fbs_missing_from_talent"], ["C"])
        self.assertEqual(summary["talent_outside_fbs"], ["D"])
        self.assertFalse(summary["exact_membership_match"])

    def test_compare_membership_detects_duplicate_rows(self) -> None:
        summary = probe.compare_membership(["A", "A", "B"], ["A", "B", "B"])
        self.assertEqual(summary["fbs_duplicate_name_rows"], 1)
        self.assertEqual(summary["talent_duplicate_name_rows"], 1)
        self.assertTrue(summary["exact_membership_match"])

    def test_build_report_without_key_is_explicit_skip(self) -> None:
        report = probe.build_report(
            [2025],
            None,
            request_delay=0.0,
            max_retries=0,
        )
        self.assertEqual(report["status"], "SKIPPED_NO_CFBD_API_KEY")
        self.assertNotIn("results", report)


if __name__ == "__main__":
    unittest.main()
