from __future__ import annotations

import gzip
import importlib.util
import os
import sys
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "probes" / "cross_provider_player_identity_probe.py"
SPEC = importlib.util.spec_from_file_location("cross_provider_player_identity_probe", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load probe")
probe = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = probe
SPEC.loader.exec_module(probe)


class CrossProviderPlayerIdentityProbeTests(unittest.TestCase):
    def test_contract_version(self) -> None:
        self.assertEqual(
            probe.CONTRACT_VERSION,
            "DAILY_NCAAF_PHASE_B2C_PLAYER_CROSS_PROVIDER_IDENTITY_V1",
        )

    def test_select_roster_asset_uses_newest_supported(self) -> None:
        manifest = {
            "assets": [
                {
                    "name": "cfb_rosters_2024.csv.gz",
                    "updated_at": "2026-09-01T08:00:00Z",
                    "browser_download_url": "https://example/gz",
                },
                {
                    "name": "cfb_rosters_2024.csv",
                    "updated_at": "2026-09-01T09:00:00Z",
                    "browser_download_url": "https://example/csv",
                },
                {
                    "name": "cfb_rosters_2024.parquet",
                    "updated_at": "2026-09-01T10:00:00Z",
                    "browser_download_url": "https://example/parquet",
                },
            ]
        }
        selected = probe.select_roster_asset(manifest, 2024)
        self.assertIsNotNone(selected)
        self.assertEqual(selected["name"], "cfb_rosters_2024.csv")

    def test_decode_gzip_csv(self) -> None:
        text = "season,team_id,athlete_id,full_name\n2024,333,1,Player One\n"
        rows, columns = probe.decode_roster_rows("cfb_rosters_2024.csv.gz", gzip.compress(text.encode()))
        self.assertEqual(columns, ["season", "team_id", "athlete_id", "full_name"])
        self.assertEqual(rows[0]["athlete_id"], "1")

    def test_compare_roster_slice_complete_overlap(self) -> None:
        cfbd_rows = [
            {"id": "1", "firstName": "A", "lastName": "One"},
            {"id": "2", "firstName": "B", "lastName": "Two"},
        ]
        espn_rows = [
            {"team_id": "333", "athlete_id": "1", "full_name": "A One"},
            {"team_id": "333", "athlete_id": "2", "full_name": "B Two"},
        ]
        result = probe.compare_roster_slice(cfbd_rows, espn_rows, "333")
        self.assertEqual(result["exact_shared_athlete_ids"], 2)
        self.assertEqual(result["cfbd_only_athlete_id_count"], 0)
        self.assertEqual(result["espn_only_athlete_id_count"], 0)
        self.assertEqual(result["cfbd_exact_id_overlap_rate"], 1.0)

    def test_compare_roster_slice_provider_only_ids_explicit(self) -> None:
        cfbd_rows = [{"id": "1"}, {"id": "2"}]
        espn_rows = [
            {"team_id": "333", "athlete_id": "2"},
            {"team_id": "333", "athlete_id": "3"},
        ]
        result = probe.compare_roster_slice(cfbd_rows, espn_rows, "333")
        self.assertEqual(result["cfbd_only_athlete_id_examples"], ["1"])
        self.assertEqual(result["espn_only_athlete_id_examples"], ["3"])

    def test_duplicate_espn_ids_are_surfaced(self) -> None:
        result = probe.compare_roster_slice(
            [{"id": "1"}],
            [
                {"team_id": "333", "athlete_id": "1"},
                {"team_id": "333", "athlete_id": "1"},
            ],
            "333",
        )
        self.assertEqual(result["duplicate_espn_athlete_ids"], ["1"])

    def test_target_direct_shared_provider_id(self) -> None:
        result = probe.classify_target_observation(
            "Jalen Milroe",
            "4432734",
            [{"id": "4432734", "firstName": "Jalen", "lastName": "Milroe"}],
            [{"athlete_id": "4432734", "full_name": "Jalen Milroe"}],
        )
        self.assertEqual(result["state"], "DIRECT_SHARED_PROVIDER_ID")

    def test_target_identifier_disagreement_is_not_name_repaired(self) -> None:
        result = probe.classify_target_observation(
            "Example Player",
            "100",
            [{"id": "101", "firstName": "Example", "lastName": "Player"}],
            [{"athlete_id": "202", "full_name": "Example Player"}],
        )
        self.assertEqual(result["state"], "IDENTIFIER_DISAGREEMENT")

    def test_ambiguous_name_candidates_remain_ambiguous(self) -> None:
        result = probe.classify_target_observation(
            "Alex Smith",
            "999",
            [
                {"id": "1", "firstName": "Alex", "lastName": "Smith"},
                {"id": "2", "firstName": "Alex", "lastName": "Smith"},
            ],
            [],
        )
        self.assertEqual(result["state"], "AMBIGUOUS_NAME_CANDIDATES")

    def test_case_summary_transfer_continuity(self) -> None:
        case = {"name": "Transfer Player", "expected_athlete_id": "42"}
        observations = [
            {
                "team_id": "1",
                "target_identity": {"state": "DIRECT_SHARED_PROVIDER_ID"},
            },
            {
                "team_id": "2",
                "target_identity": {"state": "DIRECT_SHARED_PROVIDER_ID"},
            },
        ]
        result = probe.summarize_case("transfer", case, observations)
        self.assertEqual(
            result["continuity_state"],
            "DIRECT_SHARED_PROVIDER_ID_ACROSS_ALL_MEASURED_STINTS",
        )
        self.assertEqual(result["external_team_ids_observed"], ["1", "2"])

    def test_build_report_without_key_is_explicit_skip(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            report = probe.build_report()
        self.assertEqual(report["status"], "SKIPPED_NO_API_KEY")
        self.assertNotIn("CFBD_API_KEY", str(report.get("secret_policy", "")).replace("CFBD_API_KEY", ""))


if __name__ == "__main__":
    unittest.main()
