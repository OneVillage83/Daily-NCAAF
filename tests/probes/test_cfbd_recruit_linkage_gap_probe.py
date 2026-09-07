from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "probes" / "cfbd_recruit_linkage_gap_probe.py"
SPEC = importlib.util.spec_from_file_location("cfbd_recruit_linkage_gap_probe", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class CFBDRecruitLinkageGapProbeTests(unittest.TestCase):
    def test_contract_version(self) -> None:
        self.assertEqual(
            probe.CONTRACT_VERSION,
            "DAILY_NCAAF_PHASE_B2_CFBD_RECRUIT_LINKAGE_GAP_PROBE_V1",
        )

    def test_normalize_name(self) -> None:
        self.assertEqual(probe.normalize_name(" D'Andre-Smith Jr. "), "dandresmithjr")

    def test_missing_link_candidates_require_null_athlete_and_fbs_commit(self) -> None:
        rows = [
            {"id": "1", "name": "A Player", "athleteId": None, "committedTo": "Alabama", "ranking": 2},
            {"id": "2", "name": "B Player", "athleteId": "p2", "committedTo": "Alabama", "ranking": 1},
            {"id": "3", "name": "C Player", "athleteId": None, "committedTo": "FCS School", "ranking": 3},
        ]
        candidates = probe.missing_link_candidates(rows, {"Alabama"})
        self.assertEqual([str(row["id"]) for row in candidates], ["1"])

    def test_collision_examples_surface_same_normalized_name(self) -> None:
        rows = [
            {"id": "1", "name": "John Smith", "committedTo": "A"},
            {"id": "2", "name": "John-Smith", "committedTo": "B"},
            {"id": "3", "name": "Jane Doe", "committedTo": "C"},
        ]
        collisions = probe.recruit_collision_examples(rows)
        self.assertEqual(len(collisions), 1)
        self.assertEqual(collisions[0]["normalized_name"], "johnsmith")
        self.assertEqual(collisions[0]["row_count"], 2)

    def test_roster_lookup_detects_direct_recruit_id_link(self) -> None:
        rows = [
            {
                "id": "p1",
                "firstName": "Alex",
                "lastName": "Player",
                "team": "Alabama",
                "recruitIds": ["r1", "r9"],
            }
        ]
        summary = probe.summarize_roster_lookup(rows, "Alex Player", "r1")
        self.assertEqual(summary["candidate_identifiers"], ["p1"])
        self.assertEqual(summary["direct_recruit_id_match_identifiers"], ["p1"])

    def test_assess_case_prefers_direct_roster_recruit_link(self) -> None:
        recruit = {"id": "r1", "name": "Alex Player", "committedTo": "Alabama"}
        observations = [
            {
                "summary": {
                    "candidate_identifiers": ["p1"],
                    "direct_recruit_id_match_identifiers": ["p1"],
                }
            }
        ]
        summary = probe.assess_missing_link_case(recruit, observations)
        self.assertEqual(summary["identity_interpretation"], "DIRECT_ROSTER_RECRUIT_ID_LINK")

    def test_assess_case_keeps_name_only_contextual(self) -> None:
        recruit = {"id": "r1", "name": "Alex Player", "committedTo": "Alabama"}
        observations = [
            {
                "summary": {
                    "candidate_identifiers": ["p1"],
                    "direct_recruit_id_match_identifiers": [],
                }
            }
        ]
        summary = probe.assess_missing_link_case(recruit, observations)
        self.assertEqual(
            summary["identity_interpretation"],
            "NAME_CONTEXT_ONLY_STABLE_ROSTER_CANDIDATE",
        )

    def test_assess_case_flags_multiple_roster_ids_as_ambiguous(self) -> None:
        recruit = {"id": "r1", "name": "Alex Player", "committedTo": "Alabama"}
        observations = [
            {
                "summary": {
                    "candidate_identifiers": ["p1", "p2"],
                    "direct_recruit_id_match_identifiers": [],
                }
            }
        ]
        summary = probe.assess_missing_link_case(recruit, observations)
        self.assertEqual(summary["identity_interpretation"], "AMBIGUOUS_NAME_COLLISION")

    def test_build_report_without_key_is_explicit_skip(self) -> None:
        report = probe.build_report(
            None,
            [2024],
            2,
            request_delay_seconds=0,
            max_429_retries=0,
        )
        self.assertEqual(report["status"], "SKIPPED_NO_CFBD_API_KEY")
        self.assertNotIn("results", report)


if __name__ == "__main__":
    unittest.main()
