import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "probes" / "cross_provider_team_crosswalk_probe.py"
SPEC = importlib.util.spec_from_file_location("cross_provider_team_crosswalk_probe", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CrossProviderTeamCrosswalkProbeTests(unittest.TestCase):
    def test_contract_version(self):
        self.assertEqual(
            MODULE.CONTRACT_VERSION,
            "DAILY_NCAAF_PHASE_B2C_PROGRAM_TEAM_CROSSWALK_V1",
        )

    def test_parse_int_list(self):
        self.assertEqual(MODULE.parse_int_list("2023, 2024,2025"), [2023, 2024, 2025])

    def test_extract_team_records(self):
        rows = [
            {"id": 333, "school": "Alabama", "conference": "SEC"},
            {"id": "61", "school": "Georgia", "conference": "SEC"},
            {"id": 1, "school": "   "},
            None,
        ]
        self.assertEqual(
            MODULE.extract_team_records(rows),
            [
                {
                    "school": "Alabama",
                    "cfbd_team_id": "333",
                    "conference": "SEC",
                    "classification": None,
                },
                {
                    "school": "Georgia",
                    "cfbd_team_id": "61",
                    "conference": "SEC",
                    "classification": None,
                },
            ],
        )

    def test_direct_provider_team_ids_match(self):
        records = [
            {"school": "Alabama", "cfbd_team_id": "333", "conference": "SEC", "classification": None},
            {"school": "Georgia", "cfbd_team_id": "61", "conference": "SEC", "classification": None},
        ]
        c1 = {
            "comparison": {
                "provider_team_crosswalk": {
                    "crosswalk": {
                        "Alabama": {"espn_ids": ["333"], "espn_display_names": ["Alabama Crimson Tide"], "observations": 13},
                        "Georgia": {"espn_ids": ["61"], "espn_display_names": ["Georgia Bulldogs"], "observations": 14},
                    },
                    "cfbd_name_to_multiple_espn_id_conflict_count": 0,
                    "espn_id_to_multiple_cfbd_name_conflict_count": 0,
                },
                "id_reconciliation": {"exact_id_matches": 2},
                "normalized_event_universe": {
                    "exact_overlap_with_cfbd": 2,
                    "cfbd_only_after_normalization_at_acquisition": 0,
                    "espn_only_after_normalization_at_acquisition": 0,
                },
            }
        }
        result = MODULE.analyze_season_team_crosswalk(2024, records, c1)
        self.assertEqual(result["schedule_crosswalk_coverage"]["coverage_rate"], 1.0)
        self.assertEqual(result["direct_provider_team_id_comparison"]["state_counts"], {"MATCH": 2})

    def test_direct_provider_team_id_mismatch_is_surfaced(self):
        records = [
            {"school": "Alabama", "cfbd_team_id": "999", "conference": "SEC", "classification": None}
        ]
        c1 = {
            "comparison": {
                "provider_team_crosswalk": {
                    "crosswalk": {
                        "Alabama": {"espn_ids": ["333"], "espn_display_names": ["Alabama Crimson Tide"], "observations": 1}
                    }
                }
            }
        }
        result = MODULE.analyze_season_team_crosswalk(2024, records, c1)
        self.assertEqual(result["direct_provider_team_id_comparison"]["state_counts"]["MISMATCH"], 1)
        self.assertEqual(result["direct_provider_team_id_comparison"]["mismatch_examples"][0]["derived_espn_team_id"], "333")

    def test_missing_fbs_crosswalk_is_explicit(self):
        records = [
            {"school": "Alabama", "cfbd_team_id": "333", "conference": "SEC", "classification": None},
            {"school": "Georgia", "cfbd_team_id": "61", "conference": "SEC", "classification": None},
        ]
        c1 = {
            "comparison": {
                "provider_team_crosswalk": {
                    "crosswalk": {
                        "Alabama": {"espn_ids": ["333"], "espn_display_names": [], "observations": 1}
                    }
                }
            }
        }
        result = MODULE.analyze_season_team_crosswalk(2024, records, c1)
        self.assertEqual(result["schedule_crosswalk_coverage"]["missing_fbs_schools"], ["Georgia"])
        self.assertEqual(result["direct_provider_team_id_comparison"]["state_counts"]["MISSING_SCHEDULE_CROSSWALK"], 1)

    def test_within_season_reverse_collision_is_surfaced(self):
        records = [
            {"school": "Alpha", "cfbd_team_id": "1", "conference": None, "classification": None},
            {"school": "Beta", "cfbd_team_id": "2", "conference": None, "classification": None},
        ]
        c1 = {
            "comparison": {
                "provider_team_crosswalk": {
                    "crosswalk": {
                        "Alpha": {"espn_ids": ["10"], "espn_display_names": [], "observations": 1},
                        "Beta": {"espn_ids": ["10"], "espn_display_names": [], "observations": 1},
                    }
                }
            }
        }
        result = MODULE.analyze_season_team_crosswalk(2024, records, c1)
        self.assertEqual(
            result["direct_provider_team_id_comparison"]["within_season_espn_id_to_multiple_cfbd_name_conflict_count"],
            1,
        )

    def test_cross_season_stable_name_and_id(self):
        reports = [
            {
                "season": 2023,
                "mapped_fbs_teams": [
                    {"school": "Alabama", "cfbd_team_id": "333", "derived_espn_team_ids": ["333"], "espn_display_names": ["Alabama Crimson Tide"]}
                ],
            },
            {
                "season": 2024,
                "mapped_fbs_teams": [
                    {"school": "Alabama", "cfbd_team_id": "333", "derived_espn_team_ids": ["333"], "espn_display_names": ["Alabama Crimson Tide"]}
                ],
            },
        ]
        result = MODULE.aggregate_cross_season(reports)
        self.assertEqual(result["same_cfbd_name_to_multiple_provider_ids_count"], 0)
        self.assertEqual(result["by_cfbd_school_name"]["Alabama"]["seasons"], [2023, 2024])

    def test_same_espn_id_multiple_names_is_name_evolution_candidate(self):
        reports = [
            {
                "season": 2023,
                "mapped_fbs_teams": [
                    {"school": "Old Name", "cfbd_team_id": "50", "derived_espn_team_ids": ["50"], "espn_display_names": ["Old Name Mascot"]}
                ],
            },
            {
                "season": 2024,
                "mapped_fbs_teams": [
                    {"school": "New Name", "cfbd_team_id": "50", "derived_espn_team_ids": ["50"], "espn_display_names": ["New Name Mascot"]}
                ],
            },
        ]
        result = MODULE.aggregate_cross_season(reports)
        self.assertEqual(result["same_espn_id_to_multiple_cfbd_names_count"], 1)
        self.assertEqual(result["same_cfbd_id_to_multiple_cfbd_names_count"], 1)

    def test_membership_transitions(self):
        reports = [
            {
                "season": 2023,
                "mapped_fbs_teams": [{"school": "Alpha"}, {"school": "Beta"}],
                "schedule_crosswalk_coverage": {"missing_fbs_schools": []},
            },
            {
                "season": 2024,
                "mapped_fbs_teams": [{"school": "Beta"}, {"school": "Gamma"}],
                "schedule_crosswalk_coverage": {"missing_fbs_schools": []},
            },
        ]
        result = MODULE.membership_transitions(reports)
        self.assertEqual(result[0]["entered_fbs"], ["Gamma"])
        self.assertEqual(result[0]["exited_fbs"], ["Alpha"])

    def test_build_report_without_key_is_explicit_skip(self):
        report = MODULE.build_report([2023, 2024, 2025], None, request_delay_seconds=0.0, max_429_retries=0)
        self.assertEqual(report["status"], "SKIPPED_NO_CFBD_API_KEY")


if __name__ == "__main__":
    unittest.main()
