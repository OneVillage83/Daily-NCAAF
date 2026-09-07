from __future__ import annotations

import importlib.util
import os
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "probes" / "cross_provider_transfer_event_probe.py"
SPEC = importlib.util.spec_from_file_location("cross_provider_transfer_event_probe", SCRIPT)
assert SPEC and SPEC.loader
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class CrossProviderTransferEventProbeTests(unittest.TestCase):
    def test_contract_version(self) -> None:
        self.assertEqual(
            probe.CONTRACT_VERSION,
            "DAILY_NCAAF_PHASE_B2C_TRANSFER_EVENT_RECONCILIATION_V1",
        )

    def test_target_cases_are_unique_and_bounded(self) -> None:
        self.assertEqual(len(probe.TRANSFER_CASES), 4)
        self.assertEqual(len(set(probe.TRANSFER_CASES)), 4)

    def test_portal_candidates_require_name_origin_destination(self) -> None:
        case = probe.TRANSFER_CASES["caleb_downs_alabama_to_ohio_state"]
        rows = [
            {"firstName": "Caleb", "lastName": "Downs", "origin": "Alabama", "destination": "Ohio State"},
            {"firstName": "Caleb", "lastName": "Downs", "origin": "Alabama", "destination": "Georgia"},
        ]
        matches = probe.portal_candidates(rows, case)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["destination"], "Ohio State")

    def test_portal_record_hash_is_stable(self) -> None:
        left = {"origin": "Alabama", "destination": "Ohio State", "firstName": "Caleb"}
        right = {"firstName": "Caleb", "destination": "Ohio State", "origin": "Alabama"}
        self.assertEqual(probe.portal_record_hash(left), probe.portal_record_hash(right))

    def test_classify_direct_shared_stint(self) -> None:
        cfbd = [{"id": 4870706, "name": "Caleb Downs"}]
        espn = [{"team_id": "333", "athlete_id": "4870706", "full_name": "Caleb Downs"}]
        result = probe.classify_stint(
            expected_id="4870706", cfbd_rows=cfbd, espn_season_rows=espn, team_id="333"
        )
        self.assertEqual(result["state"], "DIRECT_SHARED_PROVIDER_ID")

    def test_classify_zero_espn_team_rows(self) -> None:
        cfbd = [{"id": 4685415, "name": "Travis Hunter"}]
        result = probe.classify_stint(
            expected_id="4685415", cfbd_rows=cfbd, espn_season_rows=[], team_id="2296"
        )
        self.assertEqual(result["state"], "NO_ESPN_TEAM_ROWS")

    def test_reconcile_two_sided_direct_bracket(self) -> None:
        side = {"state": "DIRECT_SHARED_PROVIDER_ID", "cfbd_expected_id_present": True}
        self.assertEqual(
            probe.reconcile_event(portal_candidate_count=1, origin=side, destination=side),
            "TWO_SIDED_DIRECT_SHARED_ID_BRACKET",
        )

    def test_reconcile_partial_direct_bracket(self) -> None:
        origin = {"state": "NO_ESPN_TEAM_ROWS", "cfbd_expected_id_present": True}
        destination = {"state": "DIRECT_SHARED_PROVIDER_ID", "cfbd_expected_id_present": True}
        self.assertEqual(
            probe.reconcile_event(portal_candidate_count=1, origin=origin, destination=destination),
            "PARTIAL_DIRECT_SHARED_ID_BRACKET",
        )

    def test_portal_ambiguity_and_missing_remain_explicit(self) -> None:
        side = {"state": "DIRECT_SHARED_PROVIDER_ID", "cfbd_expected_id_present": True}
        self.assertEqual(
            probe.reconcile_event(portal_candidate_count=0, origin=side, destination=side),
            "PORTAL_CONTEXT_NOT_FOUND",
        )
        self.assertEqual(
            probe.reconcile_event(portal_candidate_count=2, origin=side, destination=side),
            "PORTAL_CONTEXT_AMBIGUOUS",
        )

    def test_build_report_without_key_is_explicit_skip(self) -> None:
        original = os.environ.pop("CFBD_API_KEY", None)
        try:
            result = probe.build_report()
            self.assertEqual(result["status"], "SKIPPED_NO_API_KEY")
        finally:
            if original is not None:
                os.environ["CFBD_API_KEY"] = original


if __name__ == "__main__":
    unittest.main()
