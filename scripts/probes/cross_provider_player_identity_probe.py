#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2-C C3 targeted cross-provider player identity probe.

Research/audit tooling only.

Compares CFBD roster athlete identifiers with ESPN-derived SportsDataverse
season-roster athlete identifiers for bounded continuity cases and the full
team-season roster slices surrounding those cases.

CFBD_API_KEY is read from the environment only and is never emitted.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROBE_DIR = Path(__file__).resolve().parent
if str(PROBE_DIR) not in sys.path:
    sys.path.insert(0, str(PROBE_DIR))

import cfbd_identity_case_probe as cfbd_identity
import cross_provider_game_reconciliation_probe_v2 as transport

CONTRACT_VERSION = "DAILY_NCAAF_PHASE_B2C_PLAYER_CROSS_PROVIDER_IDENTITY_V1"
ROSTER_RELEASE_API = (
    "https://api.github.com/repos/sportsdataverse/sportsdataverse-data/"
    "releases/tags/espn_cfb_rosters"
)
DEFAULT_REQUEST_DELAY_SECONDS = 0.8
DEFAULT_MAX_429_RETRIES = 3
MAX_EXAMPLES = 20

TARGET_CASES: dict[str, dict[str, Any]] = {
    "jalen_milroe": {
        "name": "Jalen Milroe",
        "expected_athlete_id": "4432734",
        "stints": [
            {"season": 2023, "team": "Alabama", "classification": "fbs", "team_id": "333"},
            {"season": 2024, "team": "Alabama", "classification": "fbs", "team_id": "333"},
        ],
    },
    "dillon_gabriel": {
        "name": "Dillon Gabriel",
        "expected_athlete_id": "4427238",
        "stints": [
            {"season": 2022, "team": "Oklahoma", "classification": "fbs", "team_id": "201"},
            {"season": 2023, "team": "Oklahoma", "classification": "fbs", "team_id": "201"},
            {"season": 2024, "team": "Oregon", "classification": "fbs", "team_id": "2483"},
        ],
    },
    "travis_hunter": {
        "name": "Travis Hunter",
        "expected_athlete_id": "4685415",
        "stints": [
            {"season": 2022, "team": "Jackson State", "classification": "fcs", "team_id": "2296"},
            {"season": 2023, "team": "Colorado", "classification": "fbs", "team_id": "38"},
            {"season": 2024, "team": "Colorado", "classification": "fbs", "team_id": "38"},
        ],
    },
    "caleb_downs": {
        "name": "Caleb Downs",
        "expected_athlete_id": "4870706",
        "stints": [
            {"season": 2023, "team": "Alabama", "classification": "fbs", "team_id": "333"},
            {"season": 2024, "team": "Ohio State", "classification": "fbs", "team_id": "194"},
            {"season": 2025, "team": "Ohio State", "classification": "fbs", "team_id": "194"},
        ],
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_id(value: Any) -> str | None:
    return transport.normalize_id(value)


def normalize_name(value: Any) -> str:
    if value is None:
        return ""
    return "".join(ch.lower() for ch in str(value) if ch.isalnum())


def first_value(row: dict[str, Any], fields: tuple[str, ...]) -> Any:
    for field in fields:
        value = row.get(field)
        if value not in (None, ""):
            return value
    return None


def roster_asset_rank(name: str) -> int:
    if name.endswith(".csv.gz"):
        return 0
    if name.endswith(".csv"):
        return 1
    return 99


def asset_timestamp(asset: dict[str, Any]) -> datetime:
    for field in ("updated_at", "created_at"):
        parsed = transport.parse_datetime(asset.get(field))
        if parsed is not None:
            return parsed
    return datetime.min.replace(tzinfo=timezone.utc)


def select_roster_asset(manifest: dict[str, Any], season: int) -> dict[str, Any] | None:
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        return None
    prefix = f"cfb_rosters_{season}."
    candidates = [
        item
        for item in assets
        if isinstance(item, dict)
        and str(item.get("name", "")).startswith(prefix)
        and roster_asset_rank(str(item.get("name", ""))) < 99
        and item.get("browser_download_url")
    ]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda item: (
            asset_timestamp(item),
            -roster_asset_rank(str(item.get("name", ""))),
            str(item.get("name", "")),
        ),
        reverse=True,
    )[0]


def decode_roster_rows(asset_name: str, payload: bytes) -> tuple[list[dict[str, str]], list[str]]:
    if asset_name.endswith(".csv.gz"):
        raw = gzip.decompress(payload)
    elif asset_name.endswith(".csv"):
        raw = payload
    else:
        raise ValueError(f"unsupported roster asset: {asset_name}")
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    rows = [dict(row) for row in reader]
    return rows, list(reader.fieldnames or [])


def espn_athlete_id(row: dict[str, Any]) -> str | None:
    return normalize_id(first_value(row, ("athlete_id", "athleteId", "id")))


def espn_team_id(row: dict[str, Any]) -> str | None:
    return normalize_id(first_value(row, ("team_id", "teamId")))


def espn_name(row: dict[str, Any]) -> str:
    value = first_value(
        row,
        (
            "full_name",
            "athlete_display_name",
            "display_name",
            "name",
            "athlete_name",
        ),
    )
    return str(value).strip() if value is not None else ""


def espn_position(row: dict[str, Any]) -> str | None:
    value = first_value(
        row,
        (
            "position_abbreviation",
            "position",
            "position_name",
            "position_display_name",
        ),
    )
    return str(value).strip() if value not in (None, "") else None


def cfbd_athlete_id(row: dict[str, Any]) -> str | None:
    return normalize_id(first_value(row, ("id", "athleteId", "athlete_id")))


def cfbd_name(row: dict[str, Any]) -> str:
    return cfbd_identity.row_name(row)


def duplicate_ids(rows: list[dict[str, Any]], getter: Any) -> list[str]:
    counts = Counter(value for row in rows if (value := getter(row)) is not None)
    return sorted(value for value, count in counts.items() if count > 1)


def candidate_ids_by_name(rows: list[dict[str, Any]], target_name: str, *, source: str) -> list[str]:
    target = normalize_name(target_name)
    values: list[str] = []
    for row in rows:
        row_name = cfbd_name(row) if source == "cfbd" else espn_name(row)
        if normalize_name(row_name) != target:
            continue
        identifier = cfbd_athlete_id(row) if source == "cfbd" else espn_athlete_id(row)
        if identifier is not None:
            values.append(identifier)
    return sorted(set(values))


def compare_roster_slice(
    cfbd_rows: list[dict[str, Any]],
    espn_rows: list[dict[str, Any]],
    team_id: str,
) -> dict[str, Any]:
    espn_team_rows = [row for row in espn_rows if espn_team_id(row) == str(team_id)]

    cfbd_ids = {value for row in cfbd_rows if (value := cfbd_athlete_id(row)) is not None}
    espn_ids = {value for row in espn_team_rows if (value := espn_athlete_id(row)) is not None}
    shared = cfbd_ids & espn_ids
    cfbd_only = cfbd_ids - espn_ids
    espn_only = espn_ids - cfbd_ids

    cfbd_by_id = {cfbd_athlete_id(row): row for row in cfbd_rows if cfbd_athlete_id(row) is not None}
    espn_by_id = {espn_athlete_id(row): row for row in espn_team_rows if espn_athlete_id(row) is not None}

    same_id_name_difference_examples: list[dict[str, Any]] = []
    for athlete_id in sorted(shared):
        left = cfbd_by_id.get(athlete_id, {})
        right = espn_by_id.get(athlete_id, {})
        left_name = cfbd_name(left)
        right_name = espn_name(right)
        if normalize_name(left_name) != normalize_name(right_name):
            same_id_name_difference_examples.append(
                {
                    "athlete_id": athlete_id,
                    "cfbd_name": left_name,
                    "espn_name": right_name,
                    "cfbd_position": first_value(left, ("position",)),
                    "espn_position": espn_position(right),
                }
            )
            if len(same_id_name_difference_examples) >= MAX_EXAMPLES:
                break

    return {
        "cfbd_rows": len(cfbd_rows),
        "espn_team_rows": len(espn_team_rows),
        "cfbd_unique_athlete_ids": len(cfbd_ids),
        "espn_unique_athlete_ids": len(espn_ids),
        "exact_shared_athlete_ids": len(shared),
        "cfbd_exact_id_overlap_rate": round(len(shared) / len(cfbd_ids), 6) if cfbd_ids else None,
        "espn_exact_id_overlap_rate": round(len(shared) / len(espn_ids), 6) if espn_ids else None,
        "cfbd_only_athlete_id_count": len(cfbd_only),
        "espn_only_athlete_id_count": len(espn_only),
        "cfbd_only_athlete_id_examples": sorted(cfbd_only)[:MAX_EXAMPLES],
        "espn_only_athlete_id_examples": sorted(espn_only)[:MAX_EXAMPLES],
        "duplicate_cfbd_athlete_ids": duplicate_ids(cfbd_rows, cfbd_athlete_id),
        "duplicate_espn_athlete_ids": duplicate_ids(espn_team_rows, espn_athlete_id),
        "same_id_name_difference_examples": same_id_name_difference_examples,
    }


def classify_target_observation(
    target_name: str,
    expected_id: str,
    cfbd_rows: list[dict[str, Any]],
    espn_team_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    cfbd_name_ids = candidate_ids_by_name(cfbd_rows, target_name, source="cfbd")
    espn_name_ids = candidate_ids_by_name(espn_team_rows, target_name, source="espn")

    cfbd_expected_rows = [row for row in cfbd_rows if cfbd_athlete_id(row) == expected_id]
    espn_expected_rows = [row for row in espn_team_rows if espn_athlete_id(row) == expected_id]

    cfbd_expected_present = bool(cfbd_expected_rows)
    espn_expected_present = bool(espn_expected_rows)

    if cfbd_expected_present and espn_expected_present:
        state = "DIRECT_SHARED_PROVIDER_ID"
    elif cfbd_expected_present and not espn_expected_present:
        state = "CFBD_ONLY_IDENTIFIER"
    elif espn_expected_present and not cfbd_expected_present:
        state = "ESPN_ONLY_IDENTIFIER"
    elif len(cfbd_name_ids) > 1 or len(espn_name_ids) > 1:
        state = "AMBIGUOUS_NAME_CANDIDATES"
    elif cfbd_name_ids and espn_name_ids and set(cfbd_name_ids).isdisjoint(espn_name_ids):
        state = "IDENTIFIER_DISAGREEMENT"
    else:
        state = "UNRESOLVED"

    return {
        "state": state,
        "expected_athlete_id": expected_id,
        "cfbd_expected_id_present": cfbd_expected_present,
        "espn_expected_id_present": espn_expected_present,
        "cfbd_name_candidate_ids": cfbd_name_ids,
        "espn_name_candidate_ids": espn_name_ids,
        "name_matching_role": "candidate discovery/diagnosis only; never identity authority",
    }


def summarize_case(case_name: str, case: dict[str, Any], observations: list[dict[str, Any]]) -> dict[str, Any]:
    states = [str(item.get("target_identity", {}).get("state")) for item in observations]
    shared_count = sum(state == "DIRECT_SHARED_PROVIDER_ID" for state in states)
    expected = str(case["expected_athlete_id"])
    team_ids = sorted({str(item["team_id"]) for item in observations})

    if observations and shared_count == len(observations):
        continuity = "DIRECT_SHARED_PROVIDER_ID_ACROSS_ALL_MEASURED_STINTS"
    elif shared_count > 0:
        continuity = "PARTIAL_DIRECT_SHARED_PROVIDER_ID"
    else:
        continuity = "UNRESOLVED"

    return {
        "case": case_name,
        "target_name": case["name"],
        "expected_athlete_id": expected,
        "measured_stints": len(observations),
        "direct_shared_stints": shared_count,
        "external_team_ids_observed": team_ids,
        "continuity_state": continuity,
        "observations": observations,
    }


def unique_slices() -> list[dict[str, Any]]:
    seen: set[tuple[int, str, str]] = set()
    out: list[dict[str, Any]] = []
    for case in TARGET_CASES.values():
        for stint in case["stints"]:
            key = (int(stint["season"]), str(stint["team"]), str(stint["classification"]))
            if key in seen:
                continue
            seen.add(key)
            out.append(dict(stint))
    return sorted(out, key=lambda item: (int(item["season"]), str(item["team"])))


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
        "comparison_policy": "exact provider athlete IDs are identity evidence; names are diagnostic candidate discovery only",
        "target_cases": sorted(TARGET_CASES),
    }
    if not key:
        base["status"] = "SKIPPED_NO_API_KEY"
        return base

    manifest_result = transport.fetch_json(
        ROSTER_RELEASE_API,
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
        "source_url": ROSTER_RELEASE_API,
        "http_status": 200,
        "attempts": manifest_result.get("attempts"),
        "release_updated_at": manifest.get("updated_at"),
        "asset_count": len(manifest.get("assets", [])) if isinstance(manifest.get("assets"), list) else None,
        "acquired_at": utc_now(),
    }

    seasons = sorted({int(stint["season"]) for case in TARGET_CASES.values() for stint in case["stints"]})
    season_assets: dict[int, dict[str, Any]] = {}
    season_rows: dict[int, list[dict[str, str]]] = {}

    for season in seasons:
        asset = select_roster_asset(manifest, season)
        if asset is None:
            season_assets[season] = {"status": "ASSET_NOT_FOUND"}
            season_rows[season] = []
            continue
        result = transport.fetch_bytes(
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
            rows, columns = decode_roster_rows(str(asset["name"]), bytes(payload))
            status = "LOADED"
        except Exception as exc:  # research harness: retain explicit decode failure
            rows, columns = [], []
            status = "DECODE_FAILED"
            season_assets[season] = {
                "status": status,
                "asset_name": asset.get("name"),
                "error": str(exc),
            }
            season_rows[season] = []
            continue

        season_rows[season] = rows
        season_assets[season] = {
            "status": status,
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

    client = cfbd_identity.CFBDClient(
        key=key,
        request_delay_seconds=request_delay_seconds,
        max_429_retries=max_429_retries,
    )

    slice_results: dict[str, dict[str, Any]] = {}
    cfbd_slice_rows: dict[tuple[int, str], list[dict[str, Any]]] = {}
    for stint in unique_slices():
        season = int(stint["season"])
        team = str(stint["team"])
        classification = str(stint["classification"])
        team_id = str(stint["team_id"])
        key_name = f"{season}:{team}"
        result = client.get_list(
            "/roster",
            {"year": season, "team": team, "classification": classification},
        )
        if result.get("http_status") != 200:
            slice_results[key_name] = {
                "season": season,
                "team": team,
                "classification": classification,
                "team_id": team_id,
                "status": "CFBD_ROSTER_FETCH_FAILED",
                "http_status": result.get("http_status"),
                "attempts": result.get("attempts"),
                "error": result.get("error"),
            }
            cfbd_slice_rows[(season, team)] = []
            continue

        cfbd_rows = result.get("rows", [])
        cfbd_slice_rows[(season, team)] = cfbd_rows
        roster_rows = season_rows.get(season, [])
        comparison = compare_roster_slice(cfbd_rows, roster_rows, team_id)
        slice_results[key_name] = {
            "season": season,
            "team": team,
            "classification": classification,
            "team_id": team_id,
            "status": "COMPARED",
            "cfbd_http_status": 200,
            "cfbd_attempts": result.get("attempts"),
            "sportsdataverse_asset_status": season_assets.get(season, {}).get("status"),
            "comparison": comparison,
        }

    case_results: dict[str, Any] = {}
    state_counter: Counter[str] = Counter()
    for case_name, case in TARGET_CASES.items():
        observations: list[dict[str, Any]] = []
        for stint in case["stints"]:
            season = int(stint["season"])
            team = str(stint["team"])
            team_id = str(stint["team_id"])
            cfbd_rows = cfbd_slice_rows.get((season, team), [])
            espn_rows_for_team = [
                row for row in season_rows.get(season, []) if espn_team_id(row) == team_id
            ]
            identity_result = classify_target_observation(
                str(case["name"]),
                str(case["expected_athlete_id"]),
                cfbd_rows,
                espn_rows_for_team,
            )
            state_counter[identity_result["state"]] += 1
            observations.append(
                {
                    "season": season,
                    "team": team,
                    "classification": stint["classification"],
                    "team_id": team_id,
                    "target_identity": identity_result,
                }
            )
        case_results[case_name] = summarize_case(case_name, case, observations)

    base["sportsdataverse_roster_assets"] = {str(key): value for key, value in season_assets.items()}
    base["team_season_roster_slices"] = slice_results
    base["player_cases"] = case_results
    base["target_identity_state_counts"] = dict(sorted(state_counter.items()))
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
