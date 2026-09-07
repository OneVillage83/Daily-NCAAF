#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2-C C4 transfer-event reconciliation probe.

Research/audit tooling only.

CFBD portal rows measured in B.2-B do not carry a direct athlete identifier.
This probe therefore treats portal rows as contextual transfer observations and
brackets them with frozen C3 external athlete-ID evidence in surrounding CFBD
and ESPN-derived SportsDataverse rosters.

CFBD_API_KEY is read from the environment only and is never emitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROBE_DIR = Path(__file__).resolve().parent
if str(PROBE_DIR) not in sys.path:
    sys.path.insert(0, str(PROBE_DIR))

import cfbd_identity_case_probe as cfbd_identity
import cross_provider_player_identity_probe as player_probe

CONTRACT_VERSION = "DAILY_NCAAF_PHASE_B2C_TRANSFER_EVENT_RECONCILIATION_V1"
DEFAULT_REQUEST_DELAY_SECONDS = 0.8
DEFAULT_MAX_429_RETRIES = 3
MAX_EXAMPLES = 20

TRANSFER_CASES: dict[str, dict[str, Any]] = {
    "dillon_gabriel_ucf_to_oklahoma": {
        "name": "Dillon Gabriel",
        "expected_athlete_id": "4427238",
        "portal_season": 2022,
        "expected_transfer_date": "2021-11-27T07:07:00.000Z",
        "origin": {"season": 2021, "team": "UCF", "classification": "fbs", "team_id": "2116"},
        "destination": {"season": 2022, "team": "Oklahoma", "classification": "fbs", "team_id": "201"},
    },
    "dillon_gabriel_oklahoma_to_oregon": {
        "name": "Dillon Gabriel",
        "expected_athlete_id": "4427238",
        "portal_season": 2024,
        "expected_transfer_date": "2023-12-04T14:01:00.000Z",
        "origin": {"season": 2023, "team": "Oklahoma", "classification": "fbs", "team_id": "201"},
        "destination": {"season": 2024, "team": "Oregon", "classification": "fbs", "team_id": "2483"},
    },
    "travis_hunter_jackson_state_to_colorado": {
        "name": "Travis Hunter",
        "expected_athlete_id": "4685415",
        "portal_season": 2023,
        "expected_transfer_date": "2022-12-19T04:36:00.000Z",
        "origin": {"season": 2022, "team": "Jackson State", "classification": "fcs", "team_id": "2296"},
        "destination": {"season": 2023, "team": "Colorado", "classification": "fbs", "team_id": "38"},
    },
    "caleb_downs_alabama_to_ohio_state": {
        "name": "Caleb Downs",
        "expected_athlete_id": "4870706",
        "portal_season": 2024,
        "expected_transfer_date": "2024-01-17T15:39:00.000Z",
        "origin": {"season": 2023, "team": "Alabama", "classification": "fbs", "team_id": "333"},
        "destination": {"season": 2024, "team": "Ohio State", "classification": "fbs", "team_id": "194"},
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_name(value: Any) -> str:
    return player_probe.normalize_name(value)


def portal_name(row: dict[str, Any]) -> str:
    first = row.get("firstName") or row.get("first_name")
    last = row.get("lastName") or row.get("last_name")
    parts = [str(value).strip() for value in (first, last) if value not in (None, "")]
    if parts:
        return " ".join(parts)
    value = row.get("name")
    return str(value).strip() if value not in (None, "") else ""


def normalize_program(value: Any) -> str:
    return normalize_name(value)


def portal_candidates(rows: list[dict[str, Any]], case: dict[str, Any]) -> list[dict[str, Any]]:
    target_name = normalize_name(case["name"])
    origin = normalize_program(case["origin"]["team"])
    destination = normalize_program(case["destination"]["team"])
    out: list[dict[str, Any]] = []
    for row in rows:
        if normalize_name(portal_name(row)) != target_name:
            continue
        if normalize_program(row.get("origin")) != origin:
            continue
        if normalize_program(row.get("destination")) != destination:
            continue
        out.append(row)
    return out


def portal_record_hash(row: dict[str, Any]) -> str:
    payload = json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def portal_view(row: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "season",
        "firstName",
        "lastName",
        "position",
        "origin",
        "destination",
        "transferDate",
        "rating",
        "stars",
        "eligibility",
    )
    return {
        "provider_record_hash": portal_record_hash(row),
        "resolved_name": portal_name(row),
        "schema_keys": sorted(row.keys()),
        **{field: row.get(field) for field in fields if field in row},
    }


def espn_rows_for_team(rows: list[dict[str, Any]], team_id: str) -> list[dict[str, Any]]:
    return [row for row in rows if player_probe.espn_team_id(row) == str(team_id)]


def classify_stint(
    *,
    expected_id: str,
    cfbd_rows: list[dict[str, Any]],
    espn_season_rows: list[dict[str, Any]],
    team_id: str,
) -> dict[str, Any]:
    espn_rows = espn_rows_for_team(espn_season_rows, team_id)
    cfbd_expected = any(player_probe.cfbd_athlete_id(row) == expected_id for row in cfbd_rows)
    espn_expected = any(player_probe.espn_athlete_id(row) == expected_id for row in espn_rows)

    if not cfbd_rows:
        state = "NO_CFBD_TEAM_ROWS"
    elif not espn_rows and cfbd_expected:
        state = "NO_ESPN_TEAM_ROWS"
    elif cfbd_expected and espn_expected:
        state = "DIRECT_SHARED_PROVIDER_ID"
    elif cfbd_expected and not espn_expected:
        state = "CFBD_ONLY_IDENTIFIER"
    elif espn_expected and not cfbd_expected:
        state = "ESPN_ONLY_IDENTIFIER"
    else:
        cfbd_name_ids = player_probe.candidate_ids_by_name(cfbd_rows, "", source="cfbd") if False else []
        state = "UNRESOLVED"

    return {
        "state": state,
        "expected_athlete_id": expected_id,
        "cfbd_team_rows": len(cfbd_rows),
        "espn_team_rows": len(espn_rows),
        "cfbd_expected_id_present": cfbd_expected,
        "espn_expected_id_present": espn_expected,
    }


def reconcile_event(
    *,
    portal_candidate_count: int,
    origin: dict[str, Any],
    destination: dict[str, Any],
) -> str:
    if portal_candidate_count == 0:
        return "PORTAL_CONTEXT_NOT_FOUND"
    if portal_candidate_count > 1:
        return "PORTAL_CONTEXT_AMBIGUOUS"

    origin_state = str(origin.get("state"))
    destination_state = str(destination.get("state"))

    if origin_state == "ESPN_ONLY_IDENTIFIER" or destination_state == "ESPN_ONLY_IDENTIFIER":
        return "IDENTIFIER_CONFLICT"

    origin_cfbd = bool(origin.get("cfbd_expected_id_present"))
    destination_cfbd = bool(destination.get("cfbd_expected_id_present"))
    if not (origin_cfbd and destination_cfbd):
        return "UNRESOLVED"

    direct_count = sum(
        state == "DIRECT_SHARED_PROVIDER_ID" for state in (origin_state, destination_state)
    )
    if direct_count == 2:
        return "TWO_SIDED_DIRECT_SHARED_ID_BRACKET"
    if direct_count == 1:
        return "PARTIAL_DIRECT_SHARED_ID_BRACKET"
    return "CFBD_ONLY_TWO_SIDED_ID_BRACKET"


def transfer_date_state(candidate: dict[str, Any] | None, expected: str | None) -> str:
    if candidate is None or expected is None:
        return "UNAVAILABLE"
    observed = candidate.get("transferDate")
    if observed in (None, ""):
        return "UNAVAILABLE"
    return "MATCH" if str(observed) == str(expected) else "DIFFERENT_OBSERVATION"


def required_seasons() -> list[int]:
    seasons: set[int] = set()
    for case in TRANSFER_CASES.values():
        seasons.add(int(case["origin"]["season"]))
        seasons.add(int(case["destination"]["season"]))
    return sorted(seasons)


def load_roster_assets(
    manifest: dict[str, Any],
    *,
    max_429_retries: int,
) -> tuple[dict[int, dict[str, Any]], dict[int, list[dict[str, str]]]]:
    metadata: dict[int, dict[str, Any]] = {}
    rows_by_season: dict[int, list[dict[str, str]]] = {}
    for season in required_seasons():
        asset = player_probe.select_roster_asset(manifest, season)
        if asset is None:
            metadata[season] = {"status": "ASSET_NOT_FOUND"}
            rows_by_season[season] = []
            continue
        result = player_probe.transport.fetch_bytes(
            str(asset["browser_download_url"]), max_429_retries=max_429_retries
        )
        payload = result.get("data", b"")
        if result.get("http_status") != 200 or not isinstance(payload, (bytes, bytearray)):
            metadata[season] = {
                "status": "ASSET_FETCH_FAILED",
                "asset_name": asset.get("name"),
                "http_status": result.get("http_status"),
                "attempts": result.get("attempts"),
            }
            rows_by_season[season] = []
            continue
        digest = hashlib.sha256(bytes(payload)).hexdigest()
        advertised = str(asset.get("digest") or "")
        advertised_value = advertised.split(":", 1)[1] if advertised.startswith("sha256:") else None
        try:
            rows, columns = player_probe.decode_roster_rows(str(asset["name"]), bytes(payload))
        except Exception as exc:
            metadata[season] = {
                "status": "DECODE_FAILED",
                "asset_name": asset.get("name"),
                "error": str(exc),
            }
            rows_by_season[season] = []
            continue
        rows_by_season[season] = rows
        metadata[season] = {
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
    return metadata, rows_by_season


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
        "portal_identity_policy": "portal rows are contextual transfer observations; surrounding direct athlete IDs provide the identity bracket",
        "target_cases": sorted(TRANSFER_CASES),
    }
    if not key:
        base["status"] = "SKIPPED_NO_API_KEY"
        return base

    manifest_result = player_probe.transport.fetch_json(
        player_probe.ROSTER_RELEASE_API,
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
        "source_url": player_probe.ROSTER_RELEASE_API,
        "http_status": 200,
        "attempts": manifest_result.get("attempts"),
        "release_updated_at": manifest.get("updated_at"),
        "asset_count": len(manifest.get("assets", [])) if isinstance(manifest.get("assets"), list) else None,
        "acquired_at": utc_now(),
    }

    asset_metadata, rows_by_season = load_roster_assets(
        manifest, max_429_retries=max_429_retries
    )

    client = cfbd_identity.CFBDClient(
        key=key,
        request_delay_seconds=request_delay_seconds,
        max_429_retries=max_429_retries,
    )

    portal_cache: dict[int, dict[str, Any]] = {}
    roster_cache: dict[tuple[int, str, str], dict[str, Any]] = {}
    results: dict[str, Any] = {}
    state_counter: Counter[str] = Counter()

    for case_name, case in TRANSFER_CASES.items():
        portal_season = int(case["portal_season"])
        if portal_season not in portal_cache:
            portal_cache[portal_season] = client.get_list(
                "/player/portal", {"year": portal_season}
            )
        portal_result = portal_cache[portal_season]
        portal_rows = portal_result.get("rows", []) if portal_result.get("http_status") == 200 else []
        candidates = portal_candidates(portal_rows, case)

        stint_outputs: dict[str, Any] = {}
        for side in ("origin", "destination"):
            stint = case[side]
            cache_key = (
                int(stint["season"]),
                str(stint["team"]),
                str(stint["classification"]),
            )
            if cache_key not in roster_cache:
                roster_cache[cache_key] = client.get_list(
                    "/roster",
                    {
                        "year": stint["season"],
                        "team": stint["team"],
                        "classification": stint["classification"],
                    },
                )
            roster_result = roster_cache[cache_key]
            cfbd_rows = roster_result.get("rows", []) if roster_result.get("http_status") == 200 else []
            stint_state = classify_stint(
                expected_id=str(case["expected_athlete_id"]),
                cfbd_rows=cfbd_rows,
                espn_season_rows=rows_by_season.get(int(stint["season"]), []),
                team_id=str(stint["team_id"]),
            )
            stint_outputs[side] = {
                "season": stint["season"],
                "team": stint["team"],
                "classification": stint["classification"],
                "team_id": stint["team_id"],
                "cfbd_http_status": roster_result.get("http_status"),
                **stint_state,
            }

        event_state = reconcile_event(
            portal_candidate_count=len(candidates),
            origin=stint_outputs["origin"],
            destination=stint_outputs["destination"],
        )
        state_counter[event_state] += 1
        one_candidate = candidates[0] if len(candidates) == 1 else None
        results[case_name] = {
            "case": case_name,
            "target_name": case["name"],
            "expected_athlete_id": case["expected_athlete_id"],
            "portal_season": portal_season,
            "portal_http_status": portal_result.get("http_status"),
            "portal_source_rows": len(portal_rows),
            "portal_candidate_count": len(candidates),
            "portal_candidates": [portal_view(row) for row in candidates[:MAX_EXAMPLES]],
            "portal_transfer_date_state": transfer_date_state(
                one_candidate, case.get("expected_transfer_date")
            ),
            "expected_transfer_date": case.get("expected_transfer_date"),
            "origin": stint_outputs["origin"],
            "destination": stint_outputs["destination"],
            "reconciliation_state": event_state,
            "identity_interpretation": (
                "portal context is reconciled to surrounding athlete-ID evidence; the portal row itself is not identity authority"
            ),
        }

    base["sportsdataverse_roster_assets"] = {
        str(season): value for season, value in asset_metadata.items()
    }
    base["transfer_events"] = results
    base["reconciliation_state_counts"] = dict(sorted(state_counter.items()))
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
