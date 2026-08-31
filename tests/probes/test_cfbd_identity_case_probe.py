from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "probes" / "cfbd_identity_case_probe.py"
SPEC = importlib.util.spec_from_file_location("cfbd_identity_case_probe", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class CFBDIdentityCaseProbeTests(unittest.TestCase):
    def test_contract_version(self) -> None:
        self.assertEqual(
            probe.CONTRACT_VERSION,
            "DAILY_NCAAF_PHASE_B2_CFBD_IDENTITY_CASE_PROBE_V1",
        )

    def test_normalize_name_ignores_case_spaces_and_punctuation(self) -> None:
        self.assertEqual(probe.normalize_name("Kalen DeBoer"), "kalendeboer")
        self.assertEqual(probe.normalize_name(" Kalen-DeBoer "), "kalendeboer")

    def test_candidate_rows_requires_full_normalized_name_match(self) -> None:
        rows = [
            {"name": "Dillon Gabriel", "id": "1"},
            {"name": "Dillon A. Gabriel", "id": "2"},
            {"name": "Gabriel Dillon", "id": "3"},
        ]
        matches = probe.candidate_rows(rows, "Dillon Gabriel")
        self.assertEqual([row["id"] for row in matches], ["1"])

    def test_summarize_roster_identity_detects_stable_provider_id(self) -> None:
        observations = [
            {
                "summary": {
                    "candidate_rows": 1,
                    "candidate_identifiers": ["123"],
                }
            },
            {
                "summary": {
                    "candidate_rows": 1,
                    "candidate_identifiers": ["123"],
                }
            },
        ]
        summary = probe.summarize_roster_identity(observations, "Player One")
        self.assertEqual(summary["distinct_roster_identifiers"], ["123"])
        self.assertEqual(summary["identity_interpretation"], "STABLE_PROVIDER_ID")

    def test_summarize_roster_identity_flags_multiple_ids(self) -> None:
        observations = [
            {"summary": {"candidate_rows": 1, "candidate_identifiers": ["123"]}},
            {"summary": {"candidate_rows": 1, "candidate_identifiers": ["456"]}},
        ]
        summary = probe.summarize_roster_identity(observations, "Player One")
        self.assertEqual(summary["distinct_roster_identifier_count"], 2)
        self.assertEqual(
            summary["identity_interpretation"],
            "MULTIPLE_PROVIDER_IDS_REQUIRES_RECONCILIATION",
        )

    def test_summarize_recruit_link_detects_direct_provider_link(self) -> None:
        recruit_summary = {
            "candidate_rows": 1,
            "candidates": [{"athleteId": "123", "resolved_name": "Player One"}],
        }
        summary = probe.summarize_recruit_link(recruit_summary, ["123"])
        self.assertTrue(summary["direct_match_to_roster"])
        self.assertEqual(summary["identity_interpretation"], "DIRECT_PROVIDER_LINK")

    def test_candidate_without_identifier_remains_context_only(self) -> None:
        rows = [
            {
                "firstName": "Caleb",
                "lastName": "Downs",
                "origin": "Alabama",
                "destination": "Ohio State",
                "transferDate": "2024-01-20",
            }
        ]
        summary = probe.summarize_candidate_set(rows, "Caleb Downs")
        self.assertEqual(summary["candidate_rows"], 1)
        self.assertEqual(summary["candidate_identifiers"], [])
        self.assertEqual(
            summary["identity_interpretation"], "NAME_CONTEXT_CANDIDATE_ONLY"
        )

    def test_summarize_coach_rows_keeps_one_id_across_multiple_teams(self) -> None:
        rows = [
            {
                "id": 9,
                "firstName": "Kalen",
                "lastName": "DeBoer",
                "seasons": [
                    {"year": 2021, "school": "Fresno State"},
                    {"year": 2022, "school": "Washington"},
                    {"year": 2024, "school": "Alabama"},
                ],
            }
        ]
        summary = probe.summarize_coach_rows(rows, "Kalen DeBoer")
        self.assertEqual(summary["provider_ids"], ["9"])
        self.assertEqual(
            summary["observed_teams"], ["Alabama", "Fresno State", "Washington"]
        )
        self.assertEqual(
            summary["identity_interpretation"], "STABLE_PROVIDER_COACH_ID_CANDIDATE"
        )

    def test_build_report_without_key_is_explicit_skip(self) -> None:
        report = probe.build_report(
            None,
            ["jalen_milroe"],
            ["nick_saban"],
            request_delay_seconds=0,
            max_429_retries=0,
        )
        self.assertEqual(report["status"], "SKIPPED_NO_CFBD_API_KEY")
        self.assertNotIn("players", report)
        self.assertNotIn("coaches", report)


if __name__ == "__main__":
    unittest.main()
