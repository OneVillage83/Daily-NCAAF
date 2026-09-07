#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2-C C5 venue/conference/context reconciliation probe.

Research/audit tooling only.

Compares CFBD game-context observations with the ESPN-native SportsDataverse
schedule artifact only after exact event identity and C1 participant orientation
have already been established.

This is delivery-path reconciliation inside an ESPN-origin ecosystem, not
independent-source corroboration.

CFBD_API_KEY is read from the environment only and is never emitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

PROBE_DIR = Path(__file__).resolve().parent
if str(PROBE_DIR) not in sys.path:
    sys.path.insert(0, str(PROBE_DIR))

import cross_provider_game_reconciliation_probe_v2 as v2
import cross_provider_game_reconciliation_probe_v3 as v3
import cross_provider_game_reconciliation_probe_v4 as v4

CONTRACT_VERSION = "DAILY_NCAAF_PHASE_B2C_CONTEXT_RECONCILIATION_V1"
DEFAULT_SEASONS = (2023, 2024, 2025)
DEFAULT_REQUEST_DELAY_SECONDS = 0.8
DEFAULT_MAX_429_RETRIES = 3
MAX_EXAMPLES = 25


def utc_now() -> str:
    return v2.utc_now()


def parse_int_list(raw: str) -> list[int]:
    return v2.parse_int_list(raw)


def normalize_text(value: Any) -> str | None:
    if value in (None, ""):
        return None
    token = re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())
    return token or None


def compare_id(left: Any, right: Any) -> str:
    a = v2.normalize_id(left)
    b = v2.normalize_id(right)
    if a is None or b is None:
        return "UNAVAILABLE"
    return "MATCH" if a == b else "MISMATCH"


def compare_bool(left: Any, right: Any) -> str:
    a = v2.parse_bool(left)
    b = v2.parse_bool(right)
    if a is None or b is None:
        return "UNAVAILABLE"
    return "MATCH" if a == b else "MISMATCH"


def compare_text(left: Any, right: Any) -> str:
    if left in (None, "") or right in (None, ""):
        return "UNAVAILABLE"
    if str(left).strip() == str(right).strip():
        return "EXACT"
    a = normalize_text(left)
    b = normalize_text(right)
    if a is not None and a == b:
        return "NORMALIZED"
    return "MISMATCH"


def aligned_espn_field(
    espn: dict[str, Any],
    cfbd_side: str,
    orientation: str,
    home_fields: tuple[str, ...],
    away_fields: tuple[str, ...],
) -> Any:
    if orientation == "SAME_SIDE":
        source_side = cfbd_side
    elif orientation == "SWAPPED_SIDES":
        source_side = "away" if cfbd_side == "home" else "home"
    else:
        return None
    return v2.first_value(espn, home_fields if source_side == "home" else away_fields)


def compare_participant_text(
    cfbd_value: Any,
    espn: dict[str, Any],
    cfbd_side: str,
    orientation: str,
    home_fields: tuple[str, ...],
    away_fields: tuple[str, ...],
) -> tuple[str, Any]:
    if orientation not in {"SAME_SIDE", "SWAPPED_SIDES"}:
        return "UNRESOLVED_ORIENTATION", None
    espn_value = aligned_espn_field(
        espn, cfbd_side, orientation, home_fields, away_fields
    )
    return compare_text(cfbd_value, espn_value), espn_value


def compare_event_context(cfbd: dict[str, Any], espn: dict[str, Any]) -> dict[str, Any]:
    orientation = v4.infer_side_orientation(cfbd, espn)

    home_conference_state, espn_home_conference = compare_participant_text(
        cfbd.get("homeConference"),
        espn,
        "home",
        orientation,
        ("home_conference", "homeConference"),
        ("away_conference", "awayConference"),
    )
    away_conference_state, espn_away_conference = compare_participant_text(
        cfbd.get("awayConference"),
        espn,
        "away",
        orientation,
        ("home_conference", "homeConference"),
        ("away_conference", "awayConference"),
    )
    home_division_state, espn_home_division = compare_participant_text(
        cfbd.get("homeClassification"),
        espn,
        "home",
        orientation,
        ("home_division", "home_classification", "homeClassification"),
        ("away_division", "away_classification", "awayClassification"),
    )
    away_division_state, espn_away_division = compare_participant_text(
        cfbd.get("awayClassification"),
        espn,
        "away",
        orientation,
        ("home_division", "home_classification", "homeClassification"),
        ("away_division", "away_classification", "awayClassification"),
    )

    espn_venue_id = v2.first_value(espn, ("venue_id", "venueId"))
    espn_venue = v2.first_value(espn, ("venue", "venue_name", "venueName"))
    espn_neutral = v2.first_value(espn, ("neutral_site", "neutralSite"))
    espn_conference_competition = v2.first_value(
        espn,
        ("conference_competition", "conferenceCompetition", "conference_game"),
    )

    return {
        "game_id": v2.normalize_id(cfbd.get("id")),
        "side_orientation": orientation,
        "venue_id_state": compare_id(cfbd.get("venueId"), espn_venue_id),
        "venue_name_state": compare_text(cfbd.get("venue"), espn_venue),
        "neutral_site_state": compare_bool(cfbd.get("neutralSite"), espn_neutral),
        "home_conference_state": home_conference_state,
        "away_conference_state": away_conference_state,
        "home_division_state": home_division_state,
        "away_division_state": away_division_state,
        "conference_game_flag_state": compare_bool(
            cfbd.get("conferenceGame"), espn_conference_competition
        ),
        "cfbd": {
            "home_team": cfbd.get("homeTeam"),
            "away_team": cfbd.get("awayTeam"),
            "venue_id": cfbd.get("venueId"),
            "venue": cfbd.get("venue"),
            "neutral_site": cfbd.get("neutralSite"),
            "conference_game": cfbd.get("conferenceGame"),
            "home_conference": cfbd.get("homeConference"),
            "away_conference": cfbd.get("awayConference"),
            "home_division": cfbd.get("homeClassification"),
            "away_division": cfbd.get("awayClassification"),
        },
        "espn": {
            "home_team": v2.espn_home_name(espn),
            "away_team": v2.espn_away_name(espn),
            "venue_id": espn_venue_id,
            "venue": espn_venue,
            "neutral_site": espn_neutral,
            "conference_competition": espn_conference_competition,
            "aligned_home_conference": espn_home_conference,
            "aligned_away_conference": espn_away_conference,
            "aligned_home_division": espn_home_division,
            "aligned_away_division": espn_away_division,
        },
    }


def state_counts(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row.get(field)) for row in rows).items()))


def problem_examples(
    rows: list[dict[str, Any]], field: str, bad_states: set[str]
) -> list[dict[str, Any]]:
    return [row for row in rows if str(row.get(field)) in bad_states][:MAX_EXAMPLES]


def summarize_context(rows: list[dict[str, Any]]) -> dict[str, Any]:
    fields = (
        "side_orientation",
        "venue_id_state",
        "venue_name_state",
        "neutral_site_state",
        "home_conference_state",
        "away_conference_state",
        "home_division_state",
        "away_division_state",
        "conference_game_flag_state",
    )
    counts = {field: state_counts(rows, field) for field in fields}
    examples = {
        "orientation_problem_examples": problem_examples(
            rows, "side_orientation", {"UNRESOLVED", "AMBIGUOUS"}
        ),
        "venue_id_mismatch_examples": problem_examples(
            rows, "venue_id_state", {"MISMATCH"}
        ),
        "venue_name_mismatch_examples": problem_examples(
            rows, "venue_name_state", {"MISMATCH"}
        ),
        "neutral_site_mismatch_examples": problem_examples(
            rows, "neutral_site_state", {"MISMATCH"}
        ),
        "home_conference_mismatch_examples": problem_examples(
            rows, "home_conference_state", {"MISMATCH"}
        ),
        "away_conference_mismatch_examples": problem_examples(
            rows, "away_conference_state", {"MISMATCH"}
        ),
        "home_division_mismatch_examples": problem_examples(
            rows, "home_division_state", {"MISMATCH"}
        ),
        "away_division_mismatch_examples": problem_examples(
            rows, "away_division_state", {"MISMATCH"}
        ),
        "conference_game_flag_mismatch_examples": problem_examples(
            rows, "conference_game_flag_state", {"MISMATCH"}
        ),
    }
    return {"state_counts": counts, "examples": examples}


def build_report(
    *,
    seasons: list[int] | tuple[int, ...] = DEFAULT_SEASONS,
    request_delay_seconds: float = DEFAULT_REQUEST_DELAY_SECONDS,
    max_429_retries: int = DEFAULT_MAX_429_RETRIES,
) -> dict[str, Any]:
    key = os.environ.get("CFBD_API_KEY", "").strip()
    base: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "generated_at": utc_now(),
        "research_only": True,
        "secret_policy": "CFBD_API_KEY is read from the environment only and never emitted",
        "provenance_policy": (
            "CFBD /games and ESPN-native SportsDataverse schedule are reconciled as "
            "separate delivery paths in an ESPN-origin ecosystem; agreement is not "
            "independent-source corroboration"
        ),
        "comparison_policy": (
            "exact game ID first; C1 participant orientation second; context fields third"
        ),
        "seasons": [int(value) for value in seasons],
    }
    if not key:
        base["status"] = "SKIPPED_NO_API_KEY"
        return base

    manifest_result = v2.fetch_json(
        v2.SPORTSDATAVERSE_RELEASE_API,
        max_429_retries=max_429_retries,
    )
    manifest = manifest_result.get("data")
    if manifest_result.get("http_status") != 200 or not isinstance(manifest, dict):
        base["status"] = "SCHEDULE_MANIFEST_FETCH_FAILED"
        base["sportsdataverse_manifest"] = {
            "http_status": manifest_result.get("http_status"),
            "attempts": manifest_result.get("attempts"),
        }
        return base

    base["sportsdataverse_manifest"] = {
        "source_url": v2.SPORTSDATAVERSE_RELEASE_API,
        "http_status": 200,
        "attempts": manifest_result.get("attempts"),
        "release_updated_at": manifest.get("updated_at"),
        "asset_count": len(manifest.get("assets", []))
        if isinstance(manifest.get("assets"), list)
        else None,
        "acquired_at": utc_now(),
    }

    season_results: dict[str, Any] = {}
    for index, season in enumerate(int(value) for value in seasons):
        if index and request_delay_seconds > 0:
            time.sleep(request_delay_seconds)

        cfbd_result = v2.cfbd_games(season, key, max_429_retries)
        cfbd_rows = cfbd_result.get("data")
        if cfbd_result.get("http_status") != 200 or not isinstance(cfbd_rows, list):
            season_results[str(season)] = {
                "status": "CFBD_FETCH_FAILED",
                "cfbd_http_status": cfbd_result.get("http_status"),
                "cfbd_attempts": cfbd_result.get("attempts"),
            }
            continue

        asset = v3.select_schedule_asset(manifest, season)
        if asset is None:
            season_results[str(season)] = {
                "status": "ESPN_ASSET_NOT_FOUND",
                "cfbd_rows": len(cfbd_rows),
            }
            continue

        asset_result = v2.fetch_bytes(
            str(asset["browser_download_url"]),
            max_429_retries=max_429_retries,
        )
        payload = asset_result.get("data", b"")
        if asset_result.get("http_status") != 200 or not isinstance(
            payload, (bytes, bytearray)
        ):
            season_results[str(season)] = {
                "status": "ESPN_ASSET_FETCH_FAILED",
                "cfbd_rows": len(cfbd_rows),
                "asset_name": asset.get("name"),
                "espn_http_status": asset_result.get("http_status"),
            }
            continue

        try:
            espn_rows = v2.decode_schedule_asset(bytes(payload), str(asset["name"]))
        except Exception as exc:
            season_results[str(season)] = {
                "status": "ESPN_ASSET_DECODE_FAILED",
                "error": str(exc),
                "asset_name": asset.get("name"),
            }
            continue

        cfbd_index, cfbd_non_null, cfbd_duplicates = v2.build_id_index(
            cfbd_rows, lambda row: v2.normalize_id(row.get("id"))
        )
        espn_index, espn_non_null, espn_duplicates = v2.build_id_index(
            espn_rows, v2.schedule_game_id
        )
        matched_ids = sorted(set(cfbd_index) & set(espn_index))
        compared = [
            compare_event_context(cfbd_index[game_id], espn_index[game_id])
            for game_id in matched_ids
        ]

        advertised = str(asset.get("digest") or "")
        advertised_value = (
            advertised.split(":", 1)[1] if advertised.startswith("sha256:") else None
        )
        digest = hashlib.sha256(bytes(payload)).hexdigest()

        season_results[str(season)] = {
            "status": "COMPARED",
            "cfbd": {
                "http_status": cfbd_result.get("http_status"),
                "attempts": cfbd_result.get("attempts"),
                "rows": len(cfbd_rows),
                "non_null_game_ids": cfbd_non_null,
                "duplicate_game_id_rows": cfbd_duplicates,
            },
            "espn_native_schedule": {
                "http_status": asset_result.get("http_status"),
                "attempts": asset_result.get("attempts"),
                "rows": len(espn_rows),
                "non_null_game_ids": espn_non_null,
                "duplicate_game_id_rows": espn_duplicates,
                "asset_name": asset.get("name"),
                "asset_updated_at": asset.get("updated_at"),
                "source_url": asset.get("browser_download_url"),
                "byte_count": len(payload),
                "sha256": digest,
                "advertised_digest": advertised or None,
                "advertised_digest_matches": advertised_value == digest
                if advertised_value
                else None,
                "columns": list(espn_rows[0].keys()) if espn_rows else [],
                "acquired_at": utc_now(),
            },
            "id_reconciliation": {
                "exact_id_matches": len(matched_ids),
                "cfbd_exact_id_coverage_rate": round(
                    len(matched_ids) / len(cfbd_index), 6
                )
                if cfbd_index
                else None,
                "cfbd_only_count": len(set(cfbd_index) - set(espn_index)),
                "espn_only_count_raw": len(set(espn_index) - set(cfbd_index)),
            },
            "context_reconciliation": summarize_context(compared),
        }

    base["season_results"] = season_results
    base["status"] = "RAN"
    return base


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seasons", default=",".join(str(v) for v in DEFAULT_SEASONS))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--request-delay", type=float, default=DEFAULT_REQUEST_DELAY_SECONDS)
    parser.add_argument("--max-429-retries", type=int, default=DEFAULT_MAX_429_RETRIES)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    report = build_report(
        seasons=parse_int_list(args.seasons),
        request_delay_seconds=args.request_delay,
        max_429_retries=args.max_429_retries,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
