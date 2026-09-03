#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2-C C5-B team-season context reconciliation probe.

Research/audit tooling only.

C5-A proved that the ESPN-native schedule CSV does not expose event venue_id or
participant conference/division columns. C5-B therefore joins exact-ID matched
schedule participants to the ESPN-native portions of the published espn_cfb_teams
season table.

Important provenance rule: espn_cfb_teams contains explicitly backported CFBD
columns in addition to ESPN-native columns. This probe whitelists only documented
ESPN-native fields and never treats cfbd_conference/classification or other
backported CFBD fields as ESPN evidence.

The team-season venue_id is a HOME-VENUE observation, not a direct event-venue
observation. It is used only as a conservative standard-home-venue anchor.

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
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

PROBE_DIR = Path(__file__).resolve().parent
if str(PROBE_DIR) not in sys.path:
    sys.path.insert(0, str(PROBE_DIR))

import cross_provider_context_reconciliation_probe as c5a
import cross_provider_game_reconciliation_probe_v2 as v2
import cross_provider_game_reconciliation_probe_v3 as v3
import cross_provider_game_reconciliation_probe_v4 as v4

CONTRACT_VERSION = "DAILY_NCAAF_PHASE_B2C_CONTEXT_RECONCILIATION_V2"
DEFAULT_SEASONS = (2023, 2024, 2025)
DEFAULT_REQUEST_DELAY_SECONDS = 0.8
DEFAULT_MAX_429_RETRIES = 3
MAX_EXAMPLES = 25

TEAMS_RELEASE_API = (
    "https://api.github.com/repos/sportsdataverse/sportsdataverse-data/"
    "releases/tags/espn_cfb_teams"
)

# Only documented ESPN-native columns may be projected into evidence.
ESPN_NATIVE_TEAM_FIELDS = (
    "season",
    "team_id",
    "uid",
    "guid",
    "slug",
    "abbreviation",
    "display_name",
    "short_display_name",
    "name",
    "nickname",
    "location",
    "color",
    "alternate_color",
    "is_active",
    "is_all_star",
    "is_exhibition",
    "division",
    "is_fbs",
    "team_group_id",
    "team_group_name",
    "conference_id",
    "conference_name",
    "conference_short_name",
    "conference_abbreviation",
    "conference_midsize_name",
    "conference_slug",
    "conference_is_conference",
    "conference_parent_id",
    "team_logo",
    "team_logo_dark",
    "conference_logo",
    "venue_id",
    "venue_name",
    "venue_city",
    "venue_state",
    "venue_indoor",
    "venue_grass",
)

FORBIDDEN_BACKPORTED_FIELDS = {
    "cfbd_conference",
    "classification",
    "school",
    "mascot",
    "alt_name1",
    "alt_name2",
    "alt_name3",
    "city",
    "state",
    "country_code",
    "timezone",
    "latitude",
    "longitude",
    "elevation",
    "capacity",
    "dome",
    "grass",
}


def utc_now() -> str:
    return v2.utc_now()


def parse_int_list(raw: str) -> list[int]:
    return v2.parse_int_list(raw)


def decode_csv_asset(raw: bytes, asset_name: str) -> list[dict[str, str]]:
    if asset_name.endswith(".csv.gz"):
        payload = gzip.decompress(raw)
    elif asset_name.endswith(".csv"):
        payload = raw
    else:
        raise ValueError(f"unsupported CSV asset format: {asset_name}")
    return list(csv.DictReader(io.StringIO(payload.decode("utf-8-sig"))))


def asset_rank(name: str) -> int:
    if name.endswith(".csv.gz"):
        return 0
    if name.endswith(".csv"):
        return 1
    return 99


def select_csv_asset(
    manifest: dict[str, Any], prefix: str
) -> dict[str, Any] | None:
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        return None
    candidates = [
        item
        for item in assets
        if isinstance(item, dict)
        and str(item.get("name", "")).startswith(prefix)
        and asset_rank(str(item.get("name", ""))) < 99
        and item.get("browser_download_url")
    ]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda item: (
            v3.asset_timestamp(item),
            -asset_rank(str(item.get("name", ""))),
            str(item.get("name", "")),
        ),
        reverse=True,
    )[0]


def project_espn_native_team_row(row: dict[str, Any]) -> dict[str, Any]:
    """Return only documented ESPN-native fields from the mixed published row."""
    return {field: row.get(field) for field in ESPN_NATIVE_TEAM_FIELDS if field in row}


def team_id(row: dict[str, Any]) -> str | None:
    return v2.normalize_id(row.get("team_id"))


def build_team_index(
    rows: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], int, int, int]:
    index: dict[str, dict[str, Any]] = {}
    non_null = 0
    duplicates = 0
    fbs_rows = 0
    for raw in rows:
        row = project_espn_native_team_row(raw)
        identifier = team_id(row)
        if identifier is None:
            continue
        non_null += 1
        if v2.parse_bool(row.get("is_fbs")) is True:
            fbs_rows += 1
        if identifier in index:
            duplicates += 1
            continue
        index[identifier] = row
    return index, non_null, duplicates, fbs_rows


def normalize_conference(value: Any) -> str | None:
    if value in (None, ""):
        return None
    token = re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())
    if token.endswith("conference"):
        token = token[: -len("conference")]
    return token or None


def conference_aliases(team_row: dict[str, Any] | None) -> list[str]:
    if not team_row:
        return []
    fields = (
        "conference_name",
        "conference_short_name",
        "conference_abbreviation",
        "conference_midsize_name",
    )
    out: list[str] = []
    seen: set[str] = set()
    for field in fields:
        value = team_row.get(field)
        if value in (None, ""):
            continue
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def compare_conference_alias(
    cfbd_value: Any, team_row: dict[str, Any] | None
) -> tuple[str, list[str]]:
    if team_row is None:
        return "UNAVAILABLE_TEAM_METADATA", []
    aliases = conference_aliases(team_row)
    if not aliases:
        return "UNAVAILABLE_ESPN_CONFERENCE", []
    cfbd_text = None if cfbd_value in (None, "") else str(cfbd_value).strip()
    if cfbd_text is None:
        return "UNAVAILABLE_CFBD_CONFERENCE", aliases
    if any(cfbd_text == alias for alias in aliases):
        return "EXACT_ALIAS_MATCH", aliases
    target = normalize_conference(cfbd_text)
    if target and any(normalize_conference(alias) == target for alias in aliases):
        return "NORMALIZED_ALIAS_MATCH", aliases
    return "MISMATCH", aliases


def compare_division(
    cfbd_value: Any, team_row: dict[str, Any] | None
) -> tuple[str, Any]:
    if team_row is None:
        return "UNAVAILABLE_TEAM_METADATA", None
    espn_value = team_row.get("division")
    if cfbd_value in (None, "") or espn_value in (None, ""):
        return "UNAVAILABLE", espn_value
    left = str(cfbd_value).strip().lower()
    right = str(espn_value).strip().lower()
    return ("MATCH" if left == right else "MISMATCH"), espn_value


def participant_result(
    cfbd: dict[str, Any],
    espn_schedule: dict[str, Any],
    team_index: dict[str, dict[str, Any]],
    side: str,
    orientation: str,
) -> dict[str, Any]:
    if side not in {"home", "away"}:
        raise ValueError("side must be home or away")
    if orientation not in {"SAME_SIDE", "SWAPPED_SIDES"}:
        return {
            "side": side,
            "state": "UNRESOLVED_ORIENTATION",
            "external_team_id_state": "UNRESOLVED_ORIENTATION",
            "division_state": "UNRESOLVED_ORIENTATION",
            "conference_state": "UNRESOLVED_ORIENTATION",
        }

    cfbd_id = v2.normalize_id(cfbd.get("homeId" if side == "home" else "awayId"))
    aligned = v3.aligned_espn_side(espn_schedule, side, orientation)
    espn_id = v2.normalize_id(aligned.get("id"))
    metadata = team_index.get(espn_id or "")
    metadata_id = team_id(metadata or {})

    if cfbd_id is None or espn_id is None:
        external_id_state = "UNAVAILABLE"
    elif cfbd_id != espn_id:
        external_id_state = "MISMATCH"
    elif metadata is None:
        external_id_state = "MATCH_NO_TEAM_METADATA"
    elif metadata_id == espn_id:
        external_id_state = "MATCH"
    else:
        external_id_state = "MISMATCH_TEAM_METADATA_ID"

    cfbd_division = cfbd.get(
        "homeClassification" if side == "home" else "awayClassification"
    )
    division_state, espn_division = compare_division(cfbd_division, metadata)

    cfbd_conference = cfbd.get("homeConference" if side == "home" else "awayConference")
    conference_state, aliases = compare_conference_alias(cfbd_conference, metadata)

    return {
        "side": side,
        "external_team_id_state": external_id_state,
        "cfbd_team_id": cfbd_id,
        "espn_schedule_team_id": espn_id,
        "espn_team_metadata_present": metadata is not None,
        "cfbd_team": cfbd.get("homeTeam" if side == "home" else "awayTeam"),
        "espn_schedule_team": aligned.get("name"),
        "cfbd_division": cfbd_division,
        "espn_division": espn_division,
        "division_state": division_state,
        "cfbd_conference": cfbd_conference,
        "espn_conference_aliases": aliases,
        "conference_state": conference_state,
        "espn_conference_id": None if metadata is None else metadata.get("conference_id"),
    }


def home_venue_anchor(
    cfbd: dict[str, Any],
    espn_schedule: dict[str, Any],
    team_index: dict[str, dict[str, Any]],
    orientation: str,
) -> dict[str, Any]:
    cfbd_neutral = v2.parse_bool(cfbd.get("neutralSite"))
    espn_neutral = v2.parse_bool(espn_schedule.get("neutral_site"))
    cfbd_home_id = v2.normalize_id(cfbd.get("homeId"))
    espn_home_id = v2.espn_home_id(espn_schedule)

    if (
        orientation != "SAME_SIDE"
        or cfbd_neutral is not False
        or espn_neutral is not False
        or cfbd_home_id is None
        or espn_home_id is None
        or cfbd_home_id != espn_home_id
    ):
        return {
            "state": "NOT_APPLICABLE_CONTEXT",
            "cfbd_event_venue_id": v2.normalize_id(cfbd.get("venueId")),
            "espn_team_home_venue_id": None,
        }

    metadata = team_index.get(espn_home_id)
    if metadata is None:
        return {
            "state": "UNAVAILABLE_TEAM_METADATA",
            "cfbd_event_venue_id": v2.normalize_id(cfbd.get("venueId")),
            "espn_team_home_venue_id": None,
        }

    cfbd_venue_id = v2.normalize_id(cfbd.get("venueId"))
    espn_home_venue_id = v2.normalize_id(metadata.get("venue_id"))
    if cfbd_venue_id is None or espn_home_venue_id is None:
        state = "UNAVAILABLE"
    elif cfbd_venue_id == espn_home_venue_id:
        state = "MATCH"
    else:
        state = "DIFFERENT_FROM_TEAM_HOME_VENUE"

    return {
        "state": state,
        "cfbd_event_venue_id": cfbd_venue_id,
        "cfbd_event_venue": cfbd.get("venue"),
        "espn_team_home_venue_id": espn_home_venue_id,
        "espn_team_home_venue": metadata.get("venue_name"),
        "home_team_id": espn_home_id,
        "home_team": metadata.get("display_name") or metadata.get("location"),
    }


def compare_game(
    cfbd: dict[str, Any],
    espn_schedule: dict[str, Any],
    team_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    orientation = v4.infer_side_orientation(cfbd, espn_schedule)
    home = participant_result(cfbd, espn_schedule, team_index, "home", orientation)
    away = participant_result(cfbd, espn_schedule, team_index, "away", orientation)
    venue = home_venue_anchor(cfbd, espn_schedule, team_index, orientation)
    return {
        "game_id": v2.normalize_id(cfbd.get("id")),
        "side_orientation": orientation,
        "home": home,
        "away": away,
        "home_venue_anchor": venue,
    }


def count_nested(rows: list[dict[str, Any]], side: str, field: str) -> dict[str, int]:
    return dict(
        sorted(Counter(str(row.get(side, {}).get(field)) for row in rows).items())
    )


def example_nested(
    rows: list[dict[str, Any]], side: str, field: str, bad_states: set[str]
) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if str(row.get(side, {}).get(field)) in bad_states
    ][:MAX_EXAMPLES]


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "state_counts": {
            "side_orientation": dict(
                sorted(Counter(str(row.get("side_orientation")) for row in rows).items())
            ),
            "home_external_team_id_state": count_nested(
                rows, "home", "external_team_id_state"
            ),
            "away_external_team_id_state": count_nested(
                rows, "away", "external_team_id_state"
            ),
            "home_division_state": count_nested(rows, "home", "division_state"),
            "away_division_state": count_nested(rows, "away", "division_state"),
            "home_conference_state": count_nested(rows, "home", "conference_state"),
            "away_conference_state": count_nested(rows, "away", "conference_state"),
            "home_venue_anchor_state": dict(
                sorted(
                    Counter(
                        str(row.get("home_venue_anchor", {}).get("state")) for row in rows
                    ).items()
                )
            ),
        },
        "examples": {
            "external_team_id_problem_examples": (
                example_nested(
                    rows,
                    "home",
                    "external_team_id_state",
                    {"MISMATCH", "MISMATCH_TEAM_METADATA_ID", "MATCH_NO_TEAM_METADATA"},
                )
                + example_nested(
                    rows,
                    "away",
                    "external_team_id_state",
                    {"MISMATCH", "MISMATCH_TEAM_METADATA_ID", "MATCH_NO_TEAM_METADATA"},
                )
            )[:MAX_EXAMPLES],
            "division_mismatch_examples": (
                example_nested(rows, "home", "division_state", {"MISMATCH"})
                + example_nested(rows, "away", "division_state", {"MISMATCH"})
            )[:MAX_EXAMPLES],
            "conference_mismatch_examples": (
                example_nested(rows, "home", "conference_state", {"MISMATCH"})
                + example_nested(rows, "away", "conference_state", {"MISMATCH"})
            )[:MAX_EXAMPLES],
            "conference_unavailable_examples": (
                example_nested(
                    rows,
                    "home",
                    "conference_state",
                    {"UNAVAILABLE_TEAM_METADATA", "UNAVAILABLE_ESPN_CONFERENCE"},
                )
                + example_nested(
                    rows,
                    "away",
                    "conference_state",
                    {"UNAVAILABLE_TEAM_METADATA", "UNAVAILABLE_ESPN_CONFERENCE"},
                )
            )[:MAX_EXAMPLES],
            "different_home_venue_examples": [
                row
                for row in rows
                if row.get("home_venue_anchor", {}).get("state")
                == "DIFFERENT_FROM_TEAM_HOME_VENUE"
            ][:MAX_EXAMPLES],
        },
    }


def asset_evidence(
    asset: dict[str, Any], raw: bytes, rows: list[dict[str, Any]], result: dict[str, Any]
) -> dict[str, Any]:
    digest = hashlib.sha256(raw).hexdigest()
    advertised = str(asset.get("digest") or "")
    advertised_value = (
        advertised.split(":", 1)[1] if advertised.startswith("sha256:") else None
    )
    return {
        "http_status": result.get("http_status"),
        "attempts": result.get("attempts"),
        "asset_name": asset.get("name"),
        "asset_updated_at": asset.get("updated_at"),
        "source_url": asset.get("browser_download_url"),
        "byte_count": len(raw),
        "sha256": digest,
        "advertised_digest": advertised or None,
        "advertised_digest_matches": advertised_value == digest if advertised_value else None,
        "rows": len(rows),
        "columns": list(rows[0].keys()) if rows else [],
        "acquired_at": utc_now(),
    }


def fetch_manifest(url: str, max_429_retries: int) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    result = v2.fetch_json(url, max_429_retries=max_429_retries)
    data = result.get("data")
    evidence = {
        "source_url": url,
        "http_status": result.get("http_status"),
        "attempts": result.get("attempts"),
        "release_updated_at": data.get("updated_at") if isinstance(data, dict) else None,
        "asset_count": len(data.get("assets", []))
        if isinstance(data, dict) and isinstance(data.get("assets"), list)
        else None,
        "acquired_at": utc_now(),
    }
    return (data if result.get("http_status") == 200 and isinstance(data, dict) else None), evidence


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
            "ESPN-native team fields are whitelisted from the mixed espn_cfb_teams release; "
            "backported CFBD fields are excluded from second-path evidence"
        ),
        "team_field_origin_policy": {
            "allowed_espn_native_fields": list(ESPN_NATIVE_TEAM_FIELDS),
            "forbidden_backported_fields": sorted(FORBIDDEN_BACKPORTED_FIELDS),
        },
        "venue_policy": (
            "team-season venue_id is a home-venue observation and is never substituted for "
            "direct event-venue identity"
        ),
        "seasons": [int(value) for value in seasons],
    }
    if not key:
        base["status"] = "SKIPPED_NO_API_KEY"
        return base

    schedule_manifest, schedule_manifest_evidence = fetch_manifest(
        v2.SPORTSDATAVERSE_RELEASE_API, max_429_retries
    )
    teams_manifest, teams_manifest_evidence = fetch_manifest(
        TEAMS_RELEASE_API, max_429_retries
    )
    base["sportsdataverse_schedule_manifest"] = schedule_manifest_evidence
    base["sportsdataverse_teams_manifest"] = teams_manifest_evidence

    if schedule_manifest is None:
        base["status"] = "SCHEDULE_MANIFEST_FETCH_FAILED"
        return base
    if teams_manifest is None:
        base["status"] = "TEAMS_MANIFEST_FETCH_FAILED"
        return base

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
            }
            continue

        schedule_asset = v3.select_schedule_asset(schedule_manifest, season)
        teams_asset = select_csv_asset(teams_manifest, f"cfb_teams_{season}.")
        if schedule_asset is None or teams_asset is None:
            season_results[str(season)] = {
                "status": "SOURCE_ASSET_NOT_FOUND",
                "schedule_asset_found": schedule_asset is not None,
                "teams_asset_found": teams_asset is not None,
            }
            continue

        schedule_result = v2.fetch_bytes(
            str(schedule_asset["browser_download_url"]),
            max_429_retries=max_429_retries,
        )
        teams_result = v2.fetch_bytes(
            str(teams_asset["browser_download_url"]),
            max_429_retries=max_429_retries,
        )
        schedule_raw = schedule_result.get("data", b"")
        teams_raw = teams_result.get("data", b"")
        if schedule_result.get("http_status") != 200 or teams_result.get("http_status") != 200:
            season_results[str(season)] = {
                "status": "SOURCE_ASSET_FETCH_FAILED",
                "schedule_http_status": schedule_result.get("http_status"),
                "teams_http_status": teams_result.get("http_status"),
            }
            continue

        try:
            schedule_rows = v2.decode_schedule_asset(
                bytes(schedule_raw), str(schedule_asset["name"])
            )
            team_rows = decode_csv_asset(bytes(teams_raw), str(teams_asset["name"]))
        except Exception as exc:
            season_results[str(season)] = {
                "status": "SOURCE_ASSET_DECODE_FAILED",
                "error": str(exc),
            }
            continue

        cfbd_index, cfbd_non_null, cfbd_duplicates = v2.build_id_index(
            cfbd_rows, lambda row: v2.normalize_id(row.get("id"))
        )
        schedule_index, schedule_non_null, schedule_duplicates = v2.build_id_index(
            schedule_rows, v2.schedule_game_id
        )
        teams_index, teams_non_null, team_duplicates, fbs_team_rows = build_team_index(team_rows)

        matched_ids = sorted(set(cfbd_index) & set(schedule_index))
        compared = [
            compare_game(cfbd_index[game_id], schedule_index[game_id], teams_index)
            for game_id in matched_ids
        ]

        referenced_ids: set[str] = set()
        for row in compared:
            for side in ("home", "away"):
                identifier = row.get(side, {}).get("espn_schedule_team_id")
                if identifier:
                    referenced_ids.add(str(identifier))
        missing_team_metadata_ids = sorted(identifier for identifier in referenced_ids if identifier not in teams_index)

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
                **asset_evidence(
                    schedule_asset, bytes(schedule_raw), schedule_rows, schedule_result
                ),
                "non_null_game_ids": schedule_non_null,
                "duplicate_game_id_rows": schedule_duplicates,
            },
            "espn_team_season_metadata": {
                **asset_evidence(teams_asset, bytes(teams_raw), team_rows, teams_result),
                "non_null_team_ids": teams_non_null,
                "unique_team_ids": len(teams_index),
                "duplicate_team_id_rows": team_duplicates,
                "is_fbs_true_rows": fbs_team_rows,
                "referenced_schedule_team_ids": len(referenced_ids),
                "missing_referenced_team_metadata_count": len(missing_team_metadata_ids),
                "missing_referenced_team_metadata_ids": missing_team_metadata_ids[:MAX_EXAMPLES],
            },
            "id_reconciliation": {
                "exact_id_matches": len(matched_ids),
                "cfbd_only_count": len(set(cfbd_index) - set(schedule_index)),
                "espn_only_count_raw": len(set(schedule_index) - set(cfbd_index)),
                "cfbd_exact_id_coverage_rate": round(len(matched_ids) / len(cfbd_index), 6)
                if cfbd_index
                else None,
            },
            "context_reconciliation": summarize(compared),
        }

    base["season_results"] = season_results
    base["status"] = "RAN"
    return base


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seasons",
        default=",".join(str(value) for value in DEFAULT_SEASONS),
        help="comma-separated seasons",
    )
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--request-delay-seconds", type=float, default=DEFAULT_REQUEST_DELAY_SECONDS
    )
    parser.add_argument("--max-429-retries", type=int, default=DEFAULT_MAX_429_RETRIES)
    args = parser.parse_args()

    report = build_report(
        seasons=parse_int_list(args.seasons),
        request_delay_seconds=args.request_delay_seconds,
        max_429_retries=args.max_429_retries,
    )
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output is None:
        print(rendered)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
