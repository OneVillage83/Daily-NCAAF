#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2-C C3-B cross-provider player coverage breadth probe.

Research/audit tooling only.

Extends the targeted C3-A player identity evidence with a deterministic breadth
sample across conference, independent, service-academy and recent FBS-entry
contexts. Exact provider athlete IDs are compared directly; names remain
non-authoritative diagnostics.

CFBD_API_KEY is read from the environment only and is never emitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROBE_DIR = Path(__file__).resolve().parent
if str(PROBE_DIR) not in sys.path:
    sys.path.insert(0, str(PROBE_DIR))

import cross_provider_player_identity_probe as c3a

CONTRACT_VERSION = "DAILY_NCAAF_PHASE_B2C_PLAYER_CROSS_PROVIDER_COVERAGE_V1"
DEFAULT_REQUEST_DELAY_SECONDS = c3a.DEFAULT_REQUEST_DELAY_SECONDS
DEFAULT_MAX_429_RETRIES = c3a.DEFAULT_MAX_429_RETRIES

BREADTH_SLICES: tuple[dict[str, Any], ...] = (
    {"season": 2024, "team": "Clemson", "classification": "fbs", "team_id": "228", "stratum": "ACC"},
    {"season": 2024, "team": "Michigan", "classification": "fbs", "team_id": "130", "stratum": "BIG_TEN"},
    {"season": 2024, "team": "Utah", "classification": "fbs", "team_id": "254", "stratum": "BIG_12"},
    {"season": 2024, "team": "Georgia", "classification": "fbs", "team_id": "61", "stratum": "SEC"},
    {"season": 2024, "team": "Army", "classification": "fbs", "team_id": "349", "stratum": "AAC_SERVICE_ACADEMY"},
    {"season": 2024, "team": "Kennesaw State", "classification": "fbs", "team_id": "338", "stratum": "CUSA_RECENT_FBS_ENTRY"},
    {"season": 2024, "team": "Toledo", "classification": "fbs", "team_id": "2649", "stratum": "MAC"},
    {"season": 2024, "team": "Boise State", "classification": "fbs", "team_id": "68", "stratum": "MOUNTAIN_WEST"},
    {"season": 2024, "team": "App State", "classification": "fbs", "team_id": "2026", "stratum": "SUN_BELT"},
    {"season": 2024, "team": "Oregon State", "classification": "fbs", "team_id": "204", "stratum": "PAC_12_REALIGNMENT"},
    {"season": 2024, "team": "Notre Dame", "classification": "fbs", "team_id": "87", "stratum": "INDEPENDENT"},
    {"season": 2025, "team": "Delaware", "classification": "fbs", "team_id": "48", "stratum": "2025_FBS_ENTRY"},
    {"season": 2025, "team": "Missouri State", "classification": "fbs", "team_id": "2623", "stratum": "2025_FBS_ENTRY"},
)


def utc_now() -> str:
    return c3a.utc_now()


def sample_keys() -> list[str]:
    return [f"{int(item['season'])}:{item['team']}" for item in BREADTH_SLICES]


def classify_slice(comparison: dict[str, Any]) -> str:
    cfbd_ids = int(comparison.get("cfbd_unique_athlete_ids") or 0)
    espn_ids = int(comparison.get("espn_unique_athlete_ids") or 0)
    if cfbd_ids == 0 and espn_ids == 0:
        return "UNRESOLVED"
    if cfbd_ids == 0:
        return "NO_CFBD_TEAM_ROWS"
    if espn_ids == 0:
        return "NO_ESPN_TEAM_ROWS"

    cfbd_only = int(comparison.get("cfbd_only_athlete_id_count") or 0)
    espn_only = int(comparison.get("espn_only_athlete_id_count") or 0)
    if cfbd_only == 0 and espn_only == 0:
        return "COMPLETE_EXACT_ID_SET_MATCH"

    left = comparison.get("cfbd_exact_id_overlap_rate")
    right = comparison.get("espn_exact_id_overlap_rate")
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        if left >= 0.95 and right >= 0.95:
            return "HIGH_EXACT_ID_OVERLAP"
    return "PARTIAL_EXACT_ID_OVERLAP"


def aggregate_slice_results(slice_results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    state_counts: Counter[str] = Counter()
    complete_slices = 0
    zero_espn: list[str] = []
    zero_cfbd: list[str] = []
    duplicate_slices: list[str] = []
    compared_nonempty = 0

    cfbd_total = 0
    espn_total = 0
    shared_total = 0
    cfbd_only_total = 0
    espn_only_total = 0
    cfbd_rates: list[float] = []
    espn_rates: list[float] = []

    for key, result in sorted(slice_results.items()):
        state = str(result.get("coverage_state") or result.get("status") or "UNRESOLVED")
        state_counts[state] += 1
        if state == "COMPLETE_EXACT_ID_SET_MATCH":
            complete_slices += 1
        if state == "NO_ESPN_TEAM_ROWS":
            zero_espn.append(key)
        if state == "NO_CFBD_TEAM_ROWS":
            zero_cfbd.append(key)

        comparison = result.get("comparison")
        if not isinstance(comparison, dict):
            continue
        if comparison.get("duplicate_cfbd_athlete_ids") or comparison.get("duplicate_espn_athlete_ids"):
            duplicate_slices.append(key)

        cfbd_ids = int(comparison.get("cfbd_unique_athlete_ids") or 0)
        espn_ids = int(comparison.get("espn_unique_athlete_ids") or 0)
        if cfbd_ids == 0 or espn_ids == 0:
            continue

        compared_nonempty += 1
        cfbd_total += cfbd_ids
        espn_total += espn_ids
        shared_total += int(comparison.get("exact_shared_athlete_ids") or 0)
        cfbd_only_total += int(comparison.get("cfbd_only_athlete_id_count") or 0)
        espn_only_total += int(comparison.get("espn_only_athlete_id_count") or 0)

        left = comparison.get("cfbd_exact_id_overlap_rate")
        right = comparison.get("espn_exact_id_overlap_rate")
        if isinstance(left, (int, float)):
            cfbd_rates.append(float(left))
        if isinstance(right, (int, float)):
            espn_rates.append(float(right))

    return {
        "sample_slice_count": len(slice_results),
        "compared_nonempty_slice_count": compared_nonempty,
        "complete_exact_id_set_match_slice_count": complete_slices,
        "coverage_state_counts": dict(sorted(state_counts.items())),
        "zero_espn_team_row_slices": zero_espn,
        "zero_cfbd_team_row_slices": zero_cfbd,
        "duplicate_id_slices": duplicate_slices,
        "cfbd_unique_athlete_ids_total": cfbd_total,
        "espn_unique_athlete_ids_total": espn_total,
        "exact_shared_athlete_ids_total": shared_total,
        "cfbd_only_athlete_ids_total": cfbd_only_total,
        "espn_only_athlete_ids_total": espn_only_total,
        "weighted_cfbd_exact_id_overlap_rate": round(shared_total / cfbd_total, 6) if cfbd_total else None,
        "weighted_espn_exact_id_overlap_rate": round(shared_total / espn_total, 6) if espn_total else None,
        "minimum_cfbd_slice_overlap_rate": round(min(cfbd_rates), 6) if cfbd_rates else None,
        "minimum_espn_slice_overlap_rate": round(min(espn_rates), 6) if espn_rates else None,
    }


def load_roster_assets(
    manifest: dict[str, Any],
    *,
    max_429_retries: int,
) -> tuple[dict[int, dict[str, Any]], dict[int, list[dict[str, str]]]]:
    season_assets: dict[int, dict[str, Any]] = {}
    season_rows: dict[int, list[dict[str, str]]] = {}
    seasons = sorted({int(item["season"]) for item in BREADTH_SLICES})

    for season in seasons:
        asset = c3a.select_roster_asset(manifest, season)
        if asset is None:
            season_assets[season] = {"status": "ASSET_NOT_FOUND"}
            season_rows[season] = []
            continue

        result = c3a.transport.fetch_bytes(
            str(asset["browser_download_url"]),
            max_429_retries=max_429_retries,
        )
        payload = result.get("data", b"")
        if result.get("http_status") != 200 or not isinstance(payload, (bytes, bytearray)):
            season_assets[season] = {
                "status": "ASSET_FETCH_FAILED",
                "asset_name": asset.get("name"),
                "http_status": result.get("http_status"),
                "attempts": result.get("attempts"),
            }
            season_rows[season] = []
            continue

        digest = hashlib.sha256(bytes(payload)).hexdigest()
        advertised = str(asset.get("digest") or "")
        advertised_value = advertised.split(":", 1)[1] if advertised.startswith("sha256:") else None
        try:
            rows, columns = c3a.decode_roster_rows(str(asset["name"]), bytes(payload))
        except Exception as exc:  # retain research-harness failure evidence
            season_assets[season] = {
                "status": "DECODE_FAILED",
                "asset_name": asset.get("name"),
                "error": str(exc),
            }
            season_rows[season] = []
            continue

        season_rows[season] = rows
        season_assets[season] = {
            "status": "LOADED",
            "asset_name": asset.get("name"),
            "asset_updated_at": asset.get("updated_at"),
            "source_url": asset.get("browser_download_url"),
            "http_status": result.get("http_status"),
            "attempts": result.get("attempts"),
            "byte_count": len(payload),
            "sha256": digest,
            "advertised_digest": advertised or None,
            "advertised_digest_matches": advertised_value == digest if advertised_value else None,
            "columns": columns,
            "rows": len(rows),
            "acquired_at": utc_now(),
        }

    return season_assets, season_rows


def build_report(
    *,
    request_delay_seconds: float = DEFAULT_REQUEST_DELAY_SECONDS,
    max_429_retries: int = DEFAULT_MAX_429_RETRIES,
) -> dict[str, Any]:
    key = os.environ.get("CFBD_API_KEY", "").strip()
    base: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "generated_at": utc_now(),
        "research_only": True,
        "secret_policy": "CFBD_API_KEY is read from the environment only and never emitted",
        "comparison_policy": "exact provider athlete IDs are identity evidence; provider-only rows remain coverage differences; names are diagnostics only",
        "sample_design": [dict(item) for item in BREADTH_SLICES],
    }
    if not key:
        base["status"] = "SKIPPED_NO_API_KEY"
        return base

    manifest_result = c3a.transport.fetch_json(
        c3a.ROSTER_RELEASE_API,
        max_429_retries=max_429_retries,
    )
    if manifest_result.get("http_status") != 200 or not isinstance(manifest_result.get("data"), dict):
        base["status"] = "ROSTER_MANIFEST_FETCH_FAILED"
        base["sportsdataverse_manifest"] = {
            "http_status": manifest_result.get("http_status"),
            "attempts": manifest_result.get("attempts"),
        }
        return base

    manifest = manifest_result["data"]
    base["sportsdataverse_manifest"] = {
        "source_url": c3a.ROSTER_RELEASE_API,
        "http_status": 200,
        "attempts": manifest_result.get("attempts"),
        "release_updated_at": manifest.get("updated_at"),
        "asset_count": len(manifest.get("assets", [])) if isinstance(manifest.get("assets"), list) else None,
        "acquired_at": utc_now(),
    }

    season_assets, season_rows = load_roster_assets(
        manifest,
        max_429_retries=max_429_retries,
    )

    client = c3a.cfbd_identity.CFBDClient(
        key=key,
        request_delay_seconds=request_delay_seconds,
        max_429_retries=max_429_retries,
    )

    slice_results: dict[str, dict[str, Any]] = {}
    for item in BREADTH_SLICES:
        season = int(item["season"])
        team = str(item["team"])
        classification = str(item["classification"])
        team_id = str(item["team_id"])
        key_name = f"{season}:{team}"

        result = client.get_list(
            "/roster",
            {"year": season, "team": team, "classification": classification},
        )
        if result.get("http_status") != 200:
            slice_results[key_name] = {
                **dict(item),
                "status": "CFBD_ROSTER_FETCH_FAILED",
                "http_status": result.get("http_status"),
                "attempts": result.get("attempts"),
                "error": result.get("error"),
                "coverage_state": "UNRESOLVED",
            }
            continue

        comparison = c3a.compare_roster_slice(
            result.get("rows", []),
            season_rows.get(season, []),
            team_id,
        )
        slice_results[key_name] = {
            **dict(item),
            "status": "COMPARED",
            "cfbd_http_status": 200,
            "cfbd_attempts": result.get("attempts"),
            "sportsdataverse_asset_status": season_assets.get(season, {}).get("status"),
            "coverage_state": classify_slice(comparison),
            "comparison": comparison,
        }

    base["sportsdataverse_roster_assets"] = {str(key): value for key, value in season_assets.items()}
    base["team_season_roster_slices"] = slice_results
    base["aggregate"] = aggregate_slice_results(slice_results)
    base["status"] = "RAN"
    return base


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--request-delay", type=float, default=DEFAULT_REQUEST_DELAY_SECONDS)
    parser.add_argument("--max-429-retries", type=int, default=DEFAULT_MAX_429_RETRIES)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    report = build_report(
        request_delay_seconds=args.request_delay,
        max_429_retries=args.max_429_retries,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
