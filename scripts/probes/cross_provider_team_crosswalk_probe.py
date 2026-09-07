#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2-C C2 program/team provider crosswalk probe.

Research/audit tooling only.

This probe builds on the frozen C1 V4 event/participant reconciliation contract.
For completed seasons it compares CFBD /teams/fbs provider team IDs against ESPN
team IDs independently derived from participant-aligned exact-event schedule
matches, then measures cross-season ID/name stability and FBS membership changes.

CFBD_API_KEY is read from the environment and is never emitted.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
from collections import defaultdict
from pathlib import Path
from typing import Any

PROBE_DIR = Path(__file__).resolve().parent
if str(PROBE_DIR) not in sys.path:
    sys.path.insert(0, str(PROBE_DIR))

import cross_provider_game_reconciliation_probe_v2 as v2
import cross_provider_game_reconciliation_probe_v4 as v4

CONTRACT_VERSION = "DAILY_NCAAF_PHASE_B2C_PROGRAM_TEAM_CROSSWALK_V1"
DEFAULT_SEASONS = (2023, 2024, 2025)
DEFAULT_REQUEST_DELAY_SECONDS = 0.8
DEFAULT_MAX_429_RETRIES = 3
MAX_EXAMPLES = 25


def parse_int_list(raw: str) -> list[int]:
    return v2.parse_int_list(raw)


def normalize_id(value: Any) -> str | None:
    return v2.normalize_id(value)


def cfbd_fbs_teams(season: int, key: str, max_429_retries: int) -> dict[str, Any]:
    query = urllib.parse.urlencode({"year": season})
    return v2.fetch_json(
        f"{v2.CFBD_BASE}/teams/fbs?{query}",
        bearer=key,
        max_429_retries=max_429_retries,
    )


def extract_team_records(rows: Any) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []
    result: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        school = row.get("school")
        if school is None or not str(school).strip():
            continue
        result.append(
            {
                "school": str(school).strip(),
                "cfbd_team_id": normalize_id(row.get("id")),
                "conference": row.get("conference"),
                "classification": row.get("classification"),
            }
        )
    return result


def duplicate_values(values: list[str | None]) -> list[str]:
    counts: dict[str, int] = {}
    for value in values:
        if value is None:
            continue
        counts[value] = counts.get(value, 0) + 1
    return sorted(value for value, count in counts.items() if count > 1)


def analyze_season_team_crosswalk(
    season: int,
    team_records: list[dict[str, Any]],
    c1_season_result: dict[str, Any],
) -> dict[str, Any]:
    comparison = c1_season_result.get("comparison", {})
    provider_crosswalk = comparison.get("provider_team_crosswalk", {})
    crosswalk = provider_crosswalk.get("crosswalk", {})
    if not isinstance(crosswalk, dict):
        crosswalk = {}

    school_names = [record["school"] for record in team_records]
    cfbd_ids = [record.get("cfbd_team_id") for record in team_records]

    mapped: list[dict[str, Any]] = []
    missing: list[str] = []
    direct_id_state_counts: dict[str, int] = defaultdict(int)
    direct_id_mismatch_examples: list[dict[str, Any]] = []
    multiple_espn_ids_examples: list[dict[str, Any]] = []
    espn_to_names: dict[str, set[str]] = defaultdict(set)

    for record in team_records:
        school = record["school"]
        cfbd_id = record.get("cfbd_team_id")
        entry = crosswalk.get(school)
        if not isinstance(entry, dict):
            missing.append(school)
            direct_id_state_counts["MISSING_SCHEDULE_CROSSWALK"] += 1
            continue

        raw_espn_ids = entry.get("espn_ids")
        espn_ids = sorted(
            {
                identifier
                for identifier in (normalize_id(value) for value in (raw_espn_ids or []))
                if identifier is not None
            }
        )
        displays = sorted(
            str(value)
            for value in (entry.get("espn_display_names") or [])
            if value not in (None, "")
        )

        if len(espn_ids) == 0:
            state = "MISSING_ESPN_ID"
        elif len(espn_ids) > 1:
            state = "MULTIPLE_ESPN_IDS"
            multiple_espn_ids_examples.append(
                {"school": school, "cfbd_team_id": cfbd_id, "espn_ids": espn_ids}
            )
        elif cfbd_id is None:
            state = "CFBD_ID_UNAVAILABLE"
        else:
            state = "MATCH" if cfbd_id == espn_ids[0] else "MISMATCH"
            if state == "MISMATCH":
                direct_id_mismatch_examples.append(
                    {
                        "school": school,
                        "cfbd_team_id": cfbd_id,
                        "derived_espn_team_id": espn_ids[0],
                        "espn_display_names": displays,
                    }
                )

        direct_id_state_counts[state] += 1
        for espn_id in espn_ids:
            espn_to_names[espn_id].add(school)

        mapped.append(
            {
                "school": school,
                "cfbd_team_id": cfbd_id,
                "derived_espn_team_ids": espn_ids,
                "espn_display_names": displays,
                "observations": entry.get("observations"),
                "direct_provider_id_state": state,
            }
        )

    reverse_conflicts = [
        {"espn_team_id": espn_id, "cfbd_school_names": sorted(names)}
        for espn_id, names in sorted(espn_to_names.items())
        if len(names) > 1
    ]

    id_reconciliation = comparison.get("id_reconciliation", {})
    normalized_universe = comparison.get("normalized_event_universe", {})

    return {
        "season": season,
        "fbs_membership": {
            "rows_with_school": len(team_records),
            "unique_school_names": len(set(school_names)),
            "unique_non_null_cfbd_team_ids": len({value for value in cfbd_ids if value is not None}),
            "duplicate_school_names": duplicate_values(school_names),
            "duplicate_cfbd_team_ids": duplicate_values(cfbd_ids),
        },
        "schedule_crosswalk_coverage": {
            "mapped_fbs_school_count": len(mapped),
            "missing_fbs_school_count": len(missing),
            "missing_fbs_schools": sorted(missing),
            "coverage_rate": round(len(mapped) / len(team_records), 6) if team_records else None,
        },
        "direct_provider_team_id_comparison": {
            "state_counts": dict(sorted(direct_id_state_counts.items())),
            "mismatch_examples": direct_id_mismatch_examples[:MAX_EXAMPLES],
            "multiple_espn_ids_examples": multiple_espn_ids_examples[:MAX_EXAMPLES],
            "within_season_espn_id_to_multiple_cfbd_name_conflict_count": len(reverse_conflicts),
            "within_season_espn_id_conflict_examples": reverse_conflicts[:MAX_EXAMPLES],
        },
        "event_reconciliation_context": {
            "exact_shared_event_ids": id_reconciliation.get("exact_id_matches"),
            "normalized_exact_overlap": normalized_universe.get("exact_overlap_with_cfbd"),
            "normalized_cfbd_only": normalized_universe.get(
                "cfbd_only_after_normalization_at_acquisition"
            ),
            "normalized_espn_only": normalized_universe.get(
                "espn_only_after_normalization_at_acquisition"
            ),
            "team_crosswalk_conflicts_from_c1": {
                "cfbd_name_to_multiple_espn_ids": provider_crosswalk.get(
                    "cfbd_name_to_multiple_espn_id_conflict_count"
                ),
                "espn_id_to_multiple_cfbd_names": provider_crosswalk.get(
                    "espn_id_to_multiple_cfbd_name_conflict_count"
                ),
            },
        },
        "mapped_fbs_teams": mapped,
    }


def aggregate_cross_season(season_reports: list[dict[str, Any]]) -> dict[str, Any]:
    by_name: dict[str, dict[str, Any]] = {}
    by_espn_id: dict[str, dict[str, Any]] = {}
    by_cfbd_id: dict[str, dict[str, Any]] = {}

    for report in season_reports:
        season = report["season"]
        for item in report.get("mapped_fbs_teams", []):
            school = item["school"]
            cfbd_id = item.get("cfbd_team_id")
            espn_ids = item.get("derived_espn_team_ids") or []
            displays = item.get("espn_display_names") or []

            name_entry = by_name.setdefault(
                school,
                {
                    "seasons": set(),
                    "cfbd_team_ids": set(),
                    "espn_team_ids": set(),
                    "espn_display_names": set(),
                },
            )
            name_entry["seasons"].add(season)
            if cfbd_id is not None:
                name_entry["cfbd_team_ids"].add(cfbd_id)
            name_entry["espn_team_ids"].update(espn_ids)
            name_entry["espn_display_names"].update(displays)

            if cfbd_id is not None:
                cfbd_entry = by_cfbd_id.setdefault(
                    cfbd_id, {"seasons": set(), "cfbd_school_names": set(), "espn_team_ids": set()}
                )
                cfbd_entry["seasons"].add(season)
                cfbd_entry["cfbd_school_names"].add(school)
                cfbd_entry["espn_team_ids"].update(espn_ids)

            for espn_id in espn_ids:
                espn_entry = by_espn_id.setdefault(
                    espn_id,
                    {"seasons": set(), "cfbd_school_names": set(), "cfbd_team_ids": set()},
                )
                espn_entry["seasons"].add(season)
                espn_entry["cfbd_school_names"].add(school)
                if cfbd_id is not None:
                    espn_entry["cfbd_team_ids"].add(cfbd_id)

    rendered_by_name: dict[str, Any] = {}
    same_name_multiple_provider_ids: list[dict[str, Any]] = []
    for school, entry in sorted(by_name.items()):
        cfbd_ids = sorted(entry["cfbd_team_ids"])
        espn_ids = sorted(entry["espn_team_ids"])
        rendered = {
            "seasons": sorted(entry["seasons"]),
            "cfbd_team_ids": cfbd_ids,
            "espn_team_ids": espn_ids,
            "espn_display_names": sorted(entry["espn_display_names"]),
        }
        rendered_by_name[school] = rendered
        if len(cfbd_ids) > 1 or len(espn_ids) > 1:
            same_name_multiple_provider_ids.append({"school": school, **rendered})

    espn_name_evolution_candidates = [
        {
            "espn_team_id": espn_id,
            "seasons": sorted(entry["seasons"]),
            "cfbd_school_names": sorted(entry["cfbd_school_names"]),
            "cfbd_team_ids": sorted(entry["cfbd_team_ids"]),
        }
        for espn_id, entry in sorted(by_espn_id.items())
        if len(entry["cfbd_school_names"]) > 1
    ]

    cfbd_name_evolution_candidates = [
        {
            "cfbd_team_id": cfbd_id,
            "seasons": sorted(entry["seasons"]),
            "cfbd_school_names": sorted(entry["cfbd_school_names"]),
            "espn_team_ids": sorted(entry["espn_team_ids"]),
        }
        for cfbd_id, entry in sorted(by_cfbd_id.items())
        if len(entry["cfbd_school_names"]) > 1
    ]

    return {
        "unique_fbs_school_names_across_window": len(rendered_by_name),
        "unique_espn_team_ids_across_window": len(by_espn_id),
        "unique_cfbd_team_ids_across_window": len(by_cfbd_id),
        "same_cfbd_name_to_multiple_provider_ids_count": len(same_name_multiple_provider_ids),
        "same_cfbd_name_to_multiple_provider_ids_examples": same_name_multiple_provider_ids[
            :MAX_EXAMPLES
        ],
        "same_espn_id_to_multiple_cfbd_names_count": len(espn_name_evolution_candidates),
        "same_espn_id_to_multiple_cfbd_names_examples": espn_name_evolution_candidates[:MAX_EXAMPLES],
        "same_cfbd_id_to_multiple_cfbd_names_count": len(cfbd_name_evolution_candidates),
        "same_cfbd_id_to_multiple_cfbd_names_examples": cfbd_name_evolution_candidates[:MAX_EXAMPLES],
        "by_cfbd_school_name": rendered_by_name,
    }


def membership_transitions(season_reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(season_reports, key=lambda item: item["season"])
    result: list[dict[str, Any]] = []
    for previous, current in zip(ordered, ordered[1:]):
        prev_names = {
            item["school"] for item in previous.get("mapped_fbs_teams", [])
        } | set(previous.get("schedule_crosswalk_coverage", {}).get("missing_fbs_schools", []))
        curr_names = {
            item["school"] for item in current.get("mapped_fbs_teams", [])
        } | set(current.get("schedule_crosswalk_coverage", {}).get("missing_fbs_schools", []))
        result.append(
            {
                "from_season": previous["season"],
                "to_season": current["season"],
                "entered_fbs": sorted(curr_names - prev_names),
                "exited_fbs": sorted(prev_names - curr_names),
            }
        )
    return result


def build_report(
    seasons: list[int],
    key: str | None,
    *,
    request_delay_seconds: float = DEFAULT_REQUEST_DELAY_SECONDS,
    max_429_retries: int = DEFAULT_MAX_429_RETRIES,
) -> dict[str, Any]:
    if not key:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "SKIPPED_NO_CFBD_API_KEY",
            "secret_policy": "CFBD_API_KEY is read from the environment only and never emitted",
            "seasons": seasons,
            "research_only": True,
        }

    c1_report = v4.build_report(
        seasons,
        key,
        request_delay_seconds=request_delay_seconds,
        max_429_retries=max_429_retries,
    )
    if c1_report.get("status") != "RAN":
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "C1_BASE_REPORT_FAILED",
            "secret_policy": "CFBD_API_KEY is read from the environment only and never emitted",
            "seasons": seasons,
            "research_only": True,
            "c1_status": c1_report.get("status"),
        }

    season_reports: list[dict[str, Any]] = []
    raw_results = c1_report.get("results", {})

    for index, season in enumerate(seasons):
        if index and request_delay_seconds > 0:
            time.sleep(request_delay_seconds)
        response = cfbd_fbs_teams(season, key, max_429_retries)
        rows = response.get("data")
        c1_season = raw_results.get(str(season), raw_results.get(season, {}))

        if response.get("http_status") != 200 or not isinstance(rows, list):
            season_reports.append(
                {
                    "season": season,
                    "status": "CFBD_TEAMS_REQUEST_FAILED",
                    "cfbd_teams_http_status": response.get("http_status"),
                    "cfbd_teams_attempts": response.get("attempts"),
                }
            )
            continue

        analyzed = analyze_season_team_crosswalk(
            season,
            extract_team_records(rows),
            c1_season,
        )
        analyzed["status"] = "COMPARED"
        analyzed["cfbd_teams_source"] = {
            "endpoint": "/teams/fbs",
            "year": season,
            "http_status": response.get("http_status"),
            "attempts": response.get("attempts"),
        }
        sportsdataverse = c1_season.get("sportsdataverse", {})
        analyzed["sportsdataverse_source"] = {
            "asset_name": sportsdataverse.get("asset_name"),
            "asset_updated_at": sportsdataverse.get("asset_updated_at"),
            "sha256": sportsdataverse.get("sha256"),
            "advertised_digest_matches": sportsdataverse.get("advertised_digest_matches"),
            "acquired_at": sportsdataverse.get("acquired_at"),
        }
        season_reports.append(analyzed)

    comparable = [item for item in season_reports if item.get("status") == "COMPARED"]
    return {
        "contract_version": CONTRACT_VERSION,
        "status": "RAN",
        "research_only": True,
        "secret_policy": "CFBD_API_KEY is read from the environment only and never emitted",
        "seasons": seasons,
        "comparison_policy": (
            "C1 V4 exact-event participant alignment derives ESPN team IDs; "
            "CFBD /teams/fbs IDs are then compared directly; provider IDs remain crosswalks"
        ),
        "season_results": {str(item["season"]): item for item in season_reports},
        "cross_season": aggregate_cross_season(comparable),
        "membership_transitions": membership_transitions(comparable),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--seasons",
        default=",".join(str(value) for value in DEFAULT_SEASONS),
        help="comma-separated completed seasons",
    )
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--request-delay-seconds",
        type=float,
        default=DEFAULT_REQUEST_DELAY_SECONDS,
    )
    parser.add_argument(
        "--max-429-retries",
        type=int,
        default=DEFAULT_MAX_429_RETRIES,
    )
    args = parser.parse_args()

    report = build_report(
        parse_int_list(args.seasons),
        os.environ.get("CFBD_API_KEY"),
        request_delay_seconds=args.request_delay_seconds,
        max_429_retries=args.max_429_retries,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
