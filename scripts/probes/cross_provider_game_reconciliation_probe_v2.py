#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2-C cross-provider game reconciliation probe V2.

Research/audit tooling only. Compares CFBD's FBS-involved game universe with the
public SportsDataverse/ESPN schedule release while preserving source evidence.

V2 changes from V1:
- discovers the actual season asset from the GitHub release manifest instead of
  fabricating a .csv.gz URL;
- supports .csv.gz and plain .csv schedule assets without extra dependencies;
- derives an ESPN FBS-team-ID set from exact matched-game sides, allowing the
  ESPN-only event set to be normalized even when schedule rows lack division
  columns;
- treats team display-name text as a diagnostic, not identity proof;
- emits field-specific mismatch examples so kickoff/score issues cannot be
  hidden by benign display-name differences;
- parses ESPN schedule status into a coarse completed-state observation where
  defensible.

CFBD_API_KEY is read from the environment and is never emitted.
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
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

CONTRACT_VERSION = "DAILY_NCAAF_PHASE_B2C_CROSS_PROVIDER_GAME_RECONCILIATION_V2"
CFBD_BASE = "https://api.collegefootballdata.com"
SPORTSDATAVERSE_RELEASE_API = (
    "https://api.github.com/repos/sportsdataverse/sportsdataverse-data/"
    "releases/tags/espn_cfb_schedules"
)
USER_AGENT = "Daily-NCAAF-Phase-B2C-game-reconciliation/2.0"
DEFAULT_SEASONS = (2024, 2026)
DEFAULT_REQUEST_DELAY_SECONDS = 0.8
DEFAULT_MAX_429_RETRIES = 3
MAX_EXAMPLES = 25


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_int_list(raw: str) -> list[int]:
    values = [int(item.strip()) for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("at least one season is required")
    return values


def normalize_id(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    return text


def normalize_name(value: Any) -> str | None:
    if value is None:
        return None
    text = re.sub(r"[^a-z0-9]+", "", str(value).lower())
    return text or None


def first_value(row: dict[str, Any], names: tuple[str, ...]) -> Any:
    for name in names:
        if name in row:
            value = row.get(name)
            if value not in (None, ""):
                return value
    return None


def parse_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return None


def parse_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def parse_bool(value: Any) -> bool | None:
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "t", "1", "yes", "y"}:
        return True
    if text in {"false", "f", "0", "no", "n"}:
        return False
    return None


def parse_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def sleep_backoff(attempt: int, retry_after: str | None) -> None:
    if retry_after:
        try:
            seconds = float(retry_after)
        except ValueError:
            seconds = 0.0
        if seconds > 0:
            time.sleep(seconds)
            return
    time.sleep(min(2.0**attempt, 8.0))


def fetch_bytes(
    url: str,
    *,
    bearer: str | None = None,
    timeout: float = 45.0,
    max_429_retries: int = DEFAULT_MAX_429_RETRIES,
) -> dict[str, Any]:
    headers = {"Accept": "*/*", "User-Agent": USER_AGENT}
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
    attempts = 0
    while True:
        attempts += 1
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return {
                    "http_status": response.status,
                    "attempts": attempts,
                    "data": response.read(),
                    "headers": {k.lower(): v for k, v in response.headers.items()},
                }
        except urllib.error.HTTPError as exc:
            body = exc.read()
            if exc.code == 429 and attempts <= max_429_retries:
                sleep_backoff(attempts, exc.headers.get("Retry-After"))
                continue
            return {
                "http_status": exc.code,
                "attempts": attempts,
                "data": body,
                "headers": {k.lower(): v for k, v in exc.headers.items()},
            }


def fetch_json(
    url: str,
    *,
    bearer: str | None = None,
    max_429_retries: int = DEFAULT_MAX_429_RETRIES,
) -> dict[str, Any]:
    result = fetch_bytes(url, bearer=bearer, max_429_retries=max_429_retries)
    raw = result.get("data", b"")
    try:
        parsed: Any = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        parsed = raw[:1000].decode("utf-8", errors="replace")
    return {
        "http_status": result.get("http_status"),
        "attempts": result.get("attempts"),
        "data": parsed,
    }


def cfbd_games(season: int, key: str, max_429_retries: int) -> dict[str, Any]:
    query = urllib.parse.urlencode(
        {"year": season, "seasonType": "both", "classification": "fbs"}
    )
    return fetch_json(
        f"{CFBD_BASE}/games?{query}",
        bearer=key,
        max_429_retries=max_429_retries,
    )


def schedule_asset_rank(name: str) -> int:
    if name.endswith(".csv.gz"):
        return 0
    if name.endswith(".csv"):
        return 1
    return 99


def select_schedule_asset(manifest: dict[str, Any], season: int) -> dict[str, Any] | None:
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        return None
    prefix = f"cfb_schedule_{season}."
    candidates = [
        item
        for item in assets
        if isinstance(item, dict)
        and str(item.get("name", "")).startswith(prefix)
        and schedule_asset_rank(str(item.get("name", ""))) < 99
        and item.get("browser_download_url")
    ]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda item: (
            schedule_asset_rank(str(item.get("name", ""))),
            str(item.get("name", "")),
        ),
    )[0]


def decode_schedule_asset(raw: bytes, asset_name: str) -> list[dict[str, str]]:
    if asset_name.endswith(".csv.gz"):
        payload = gzip.decompress(raw)
    elif asset_name.endswith(".csv"):
        payload = raw
    else:
        raise ValueError(f"unsupported schedule asset format: {asset_name}")
    text = payload.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def schedule_game_id(row: dict[str, Any]) -> str | None:
    return normalize_id(first_value(row, ("game_id", "id", "gameId")))


def espn_home_id(row: dict[str, Any]) -> str | None:
    return normalize_id(first_value(row, ("home_id", "homeId", "home_team_id")))


def espn_away_id(row: dict[str, Any]) -> str | None:
    return normalize_id(first_value(row, ("away_id", "awayId", "away_team_id")))


def espn_home_name(row: dict[str, Any]) -> Any:
    return first_value(
        row,
        ("home_team", "homeTeam", "home_team_name", "homeTeamName", "home_location"),
    )


def espn_away_name(row: dict[str, Any]) -> Any:
    return first_value(
        row,
        ("away_team", "awayTeam", "away_team_name", "awayTeamName", "away_location"),
    )


def espn_week(row: dict[str, Any]) -> int | None:
    return parse_int(first_value(row, ("week", "wk")))


def espn_start(row: dict[str, Any]) -> datetime | None:
    return parse_datetime(first_value(row, ("game_date", "start_date", "startDate", "date")))


def espn_home_score(row: dict[str, Any]) -> float | None:
    return parse_float(first_value(row, ("home_score", "home_points", "homePoints")))


def espn_away_score(row: dict[str, Any]) -> float | None:
    return parse_float(first_value(row, ("away_score", "away_points", "awayPoints")))


def espn_status(row: dict[str, Any]) -> str | None:
    value = first_value(row, ("status", "status_type_name", "status_name"))
    if value in (None, ""):
        return None
    return str(value).strip()


def espn_completed(row: dict[str, Any]) -> bool | None:
    direct = parse_bool(first_value(row, ("completed", "is_completed", "status_completed")))
    if direct is not None:
        return direct
    status = espn_status(row)
    if status is None:
        return None
    token = re.sub(r"[^a-z0-9]+", "", status.lower())
    if "final" in token or "complete" in token:
        return True
    if any(word in token for word in ("scheduled", "pre", "progress", "halftime", "delay", "postpon", "cancel")):
        return False
    return None


def build_id_index(
    rows: list[dict[str, Any]], id_fn: Callable[[dict[str, Any]], str | None]
) -> tuple[dict[str, dict[str, Any]], int, int]:
    index: dict[str, dict[str, Any]] = {}
    non_null = 0
    duplicates = 0
    for row in rows:
        identifier = id_fn(row)
        if identifier is None:
            continue
        non_null += 1
        if identifier in index:
            duplicates += 1
            continue
        index[identifier] = row
    return index, non_null, duplicates


def compare_display_names(cfbd_value: Any, espn_value: Any) -> str:
    if cfbd_value is None or espn_value is None:
        return "UNAVAILABLE"
    if str(cfbd_value) == str(espn_value):
        return "EXACT"
    left = normalize_name(cfbd_value)
    right = normalize_name(espn_value)
    if left == right:
        return "NORMALIZED"
    if left and right and right.startswith(left):
        return "CFBD_NAME_PREFIX_OF_ESPN_DISPLAY"
    return "DIFFERENT_DISPLAY_TEXT"


def compare_matched_game(cfbd: dict[str, Any], espn: dict[str, Any]) -> dict[str, Any]:
    cfbd_week = parse_int(cfbd.get("week"))
    sd_week = espn_week(espn)
    if cfbd_week is None or sd_week is None:
        week_state = "UNAVAILABLE"
    else:
        week_state = "MATCH" if cfbd_week == sd_week else "MISMATCH"

    cfbd_start = parse_datetime(cfbd.get("startDate"))
    sd_start = espn_start(espn)
    kickoff_delta_seconds: float | None = None
    if cfbd_start is None or sd_start is None:
        kickoff_state = "UNAVAILABLE"
    else:
        kickoff_delta_seconds = abs((cfbd_start - sd_start).total_seconds())
        kickoff_state = "MATCH" if kickoff_delta_seconds <= 60 else "MISMATCH"

    cfbd_home_score = parse_float(cfbd.get("homePoints"))
    cfbd_away_score = parse_float(cfbd.get("awayPoints"))
    sd_home_score = espn_home_score(espn)
    sd_away_score = espn_away_score(espn)
    if None in (cfbd_home_score, cfbd_away_score, sd_home_score, sd_away_score):
        score_state = "UNAVAILABLE"
    else:
        score_state = (
            "MATCH"
            if cfbd_home_score == sd_home_score and cfbd_away_score == sd_away_score
            else "MISMATCH"
        )

    cfbd_completed = parse_bool(cfbd.get("completed"))
    sd_completed = espn_completed(espn)
    if cfbd_completed is None or sd_completed is None:
        lifecycle_state = "UNAVAILABLE"
    else:
        lifecycle_state = "MATCH" if cfbd_completed == sd_completed else "MISMATCH"

    return {
        "game_id": normalize_id(cfbd.get("id")),
        "home_display_state": compare_display_names(cfbd.get("homeTeam"), espn_home_name(espn)),
        "away_display_state": compare_display_names(cfbd.get("awayTeam"), espn_away_name(espn)),
        "week_state": week_state,
        "kickoff_state": kickoff_state,
        "kickoff_delta_seconds": kickoff_delta_seconds,
        "score_state": score_state,
        "lifecycle_state": lifecycle_state,
        "cfbd": {
            "week": cfbd_week,
            "start_date": cfbd.get("startDate"),
            "home_team": cfbd.get("homeTeam"),
            "away_team": cfbd.get("awayTeam"),
            "home_points": cfbd.get("homePoints"),
            "away_points": cfbd.get("awayPoints"),
            "completed": cfbd.get("completed"),
            "home_classification": cfbd.get("homeClassification"),
            "away_classification": cfbd.get("awayClassification"),
        },
        "espn": {
            "week": sd_week,
            "start_date": first_value(espn, ("game_date", "start_date", "startDate", "date")),
            "home_id": espn_home_id(espn),
            "away_id": espn_away_id(espn),
            "home_team": espn_home_name(espn),
            "away_team": espn_away_name(espn),
            "home_score": sd_home_score,
            "away_score": sd_away_score,
            "status": espn_status(espn),
            "completed_interpretation": sd_completed,
        },
    }


def state_counts(items: list[dict[str, Any]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(item.get(field))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def compact_cfbd_example(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": normalize_id(row.get("id")),
        "week": row.get("week"),
        "start_date": row.get("startDate"),
        "home_team": row.get("homeTeam"),
        "away_team": row.get("awayTeam"),
        "home_classification": row.get("homeClassification"),
        "away_classification": row.get("awayClassification"),
        "completed": row.get("completed"),
    }


def compact_espn_example(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "game_id": schedule_game_id(row),
        "week": espn_week(row),
        "start_date": first_value(row, ("game_date", "start_date", "startDate", "date")),
        "home_id": espn_home_id(row),
        "away_id": espn_away_id(row),
        "home_team": espn_home_name(row),
        "away_team": espn_away_name(row),
        "status": espn_status(row),
    }


def derive_team_crosswalk(
    cfbd_index: dict[str, dict[str, Any]],
    espn_index: dict[str, dict[str, Any]],
    matched_ids: list[str],
) -> dict[str, Any]:
    cfbd_to_espn: dict[str, dict[str, Any]] = {}
    espn_to_cfbd: dict[str, set[str]] = defaultdict(set)
    observations = 0

    for game_id in matched_ids:
        cfbd = cfbd_index[game_id]
        espn = espn_index[game_id]
        for side in ("home", "away"):
            cfbd_name = cfbd.get("homeTeam" if side == "home" else "awayTeam")
            espn_id = espn_home_id(espn) if side == "home" else espn_away_id(espn)
            espn_name = espn_home_name(espn) if side == "home" else espn_away_name(espn)
            if cfbd_name in (None, "") or espn_id is None:
                continue
            observations += 1
            key = str(cfbd_name)
            entry = cfbd_to_espn.setdefault(
                key,
                {"espn_ids": set(), "espn_display_names": set(), "observations": 0},
            )
            entry["espn_ids"].add(espn_id)
            if espn_name not in (None, ""):
                entry["espn_display_names"].add(str(espn_name))
            entry["observations"] += 1
            espn_to_cfbd[espn_id].add(key)

    cfbd_conflicts = []
    rendered = {}
    for name, entry in sorted(cfbd_to_espn.items()):
        ids = sorted(entry["espn_ids"])
        displays = sorted(entry["espn_display_names"])
        rendered[name] = {
            "espn_ids": ids,
            "espn_display_names": displays,
            "observations": entry["observations"],
        }
        if len(ids) > 1:
            cfbd_conflicts.append({"cfbd_team": name, "espn_ids": ids, "espn_display_names": displays})

    espn_conflicts = [
        {"espn_id": identifier, "cfbd_names": sorted(names)}
        for identifier, names in sorted(espn_to_cfbd.items())
        if len(names) > 1
    ]

    return {
        "derivation": "same-side pairing inside exact matched game IDs",
        "identity_strength": "strong provider crosswalk evidence; not canonical identity",
        "side_observations": observations,
        "unique_cfbd_team_names": len(rendered),
        "unique_espn_team_ids": len(espn_to_cfbd),
        "cfbd_name_to_multiple_espn_id_conflict_count": len(cfbd_conflicts),
        "espn_id_to_multiple_cfbd_name_conflict_count": len(espn_conflicts),
        "cfbd_conflict_examples": cfbd_conflicts[:MAX_EXAMPLES],
        "espn_conflict_examples": espn_conflicts[:MAX_EXAMPLES],
        "crosswalk": rendered,
    }


def derive_espn_fbs_ids_from_matched_sides(
    cfbd_index: dict[str, dict[str, Any]],
    espn_index: dict[str, dict[str, Any]],
    matched_ids: list[str],
) -> set[str]:
    result: set[str] = set()
    for game_id in matched_ids:
        cfbd = cfbd_index[game_id]
        espn = espn_index[game_id]
        if str(cfbd.get("homeClassification", "")).lower() == "fbs":
            identifier = espn_home_id(espn)
            if identifier:
                result.add(identifier)
        if str(cfbd.get("awayClassification", "")).lower() == "fbs":
            identifier = espn_away_id(espn)
            if identifier:
                result.add(identifier)
    return result


def mismatch_examples(items: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    return [item for item in items if item.get(field) == "MISMATCH"][:MAX_EXAMPLES]


def compare_season(cfbd_rows: list[dict[str, Any]], espn_rows: list[dict[str, Any]]) -> dict[str, Any]:
    cfbd_index, cfbd_non_null, cfbd_duplicates = build_id_index(
        cfbd_rows, lambda row: normalize_id(row.get("id"))
    )
    espn_index, espn_non_null, espn_duplicates = build_id_index(espn_rows, schedule_game_id)

    cfbd_ids = set(cfbd_index)
    espn_ids = set(espn_index)
    matched_ids = sorted(cfbd_ids & espn_ids)
    cfbd_only_ids = sorted(cfbd_ids - espn_ids)
    espn_only_ids = sorted(espn_ids - cfbd_ids)

    matched = [compare_matched_game(cfbd_index[i], espn_index[i]) for i in matched_ids]
    crosswalk = derive_team_crosswalk(cfbd_index, espn_index, matched_ids)

    derived_fbs_espn_ids = derive_espn_fbs_ids_from_matched_sides(
        cfbd_index, espn_index, matched_ids
    )
    espn_fbs_involved_ids = {
        identifier
        for identifier, row in espn_index.items()
        if espn_home_id(row) in derived_fbs_espn_ids or espn_away_id(row) in derived_fbs_espn_ids
    }

    return {
        "cfbd": {
            "rows": len(cfbd_rows),
            "non_null_game_ids": cfbd_non_null,
            "unique_game_ids": len(cfbd_index),
            "duplicate_game_id_rows": cfbd_duplicates,
        },
        "espn_cfbfastR": {
            "rows": len(espn_rows),
            "non_null_game_ids": espn_non_null,
            "unique_game_ids": len(espn_index),
            "duplicate_game_id_rows": espn_duplicates,
            "columns": sorted(espn_rows[0].keys()) if espn_rows else [],
        },
        "id_reconciliation": {
            "exact_id_matches": len(matched_ids),
            "cfbd_exact_id_coverage_rate": round(len(matched_ids) / len(cfbd_ids), 6)
            if cfbd_ids
            else None,
            "cfbd_only_count": len(cfbd_only_ids),
            "espn_only_count": len(espn_only_ids),
            "cfbd_only_examples": [compact_cfbd_example(cfbd_index[i]) for i in cfbd_only_ids[:MAX_EXAMPLES]],
            "espn_only_examples": [compact_espn_example(espn_index[i]) for i in espn_only_ids[:MAX_EXAMPLES]],
        },
        "provider_team_crosswalk": crosswalk,
        "normalized_event_universe": {
            "status": "DERIVED_FROM_EXACT_MATCHED_SIDE_CROSSWALK",
            "method": (
                "derive ESPN FBS team IDs from sides labeled FBS by CFBD on exact-ID matched games, "
                "then classify all ESPN schedule events using those ESPN team IDs"
            ),
            "derived_espn_fbs_team_ids": len(derived_fbs_espn_ids),
            "espn_fbs_involved_event_ids": len(espn_fbs_involved_ids),
            "exact_overlap_with_cfbd": len(cfbd_ids & espn_fbs_involved_ids),
            "cfbd_only_after_normalization": len(cfbd_ids - espn_fbs_involved_ids),
            "espn_only_after_normalization": len(espn_fbs_involved_ids - cfbd_ids),
            "espn_only_after_normalization_examples": [
                compact_espn_example(espn_index[i])
                for i in sorted(espn_fbs_involved_ids - cfbd_ids)[:MAX_EXAMPLES]
            ],
        },
        "matched_field_agreement": {
            "matched_games": len(matched),
            "home_display_state_counts": state_counts(matched, "home_display_state"),
            "away_display_state_counts": state_counts(matched, "away_display_state"),
            "week_state_counts": state_counts(matched, "week_state"),
            "kickoff_state_counts": state_counts(matched, "kickoff_state"),
            "score_state_counts": state_counts(matched, "score_state"),
            "lifecycle_state_counts": state_counts(matched, "lifecycle_state"),
            "week_mismatch_examples": mismatch_examples(matched, "week_state"),
            "kickoff_mismatch_examples": mismatch_examples(matched, "kickoff_state"),
            "score_mismatch_examples": mismatch_examples(matched, "score_state"),
            "lifecycle_mismatch_examples": mismatch_examples(matched, "lifecycle_state"),
            "display_text_note": (
                "team display-name states are diagnostics only; provider team identity is measured "
                "through the side-derived ESPN team-ID crosswalk"
            ),
        },
    }


def advertised_digest_matches(asset: dict[str, Any], actual_sha256: str | None) -> bool | None:
    digest = asset.get("digest")
    if not digest or actual_sha256 is None:
        return None
    text = str(digest)
    if not text.startswith("sha256:"):
        return None
    return text.split(":", 1)[1].lower() == actual_sha256.lower()


def build_report(
    seasons: list[int],
    key: str | None,
    *,
    request_delay_seconds: float,
    max_429_retries: int,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "generated_at": utc_now(),
        "research_only": True,
        "secret_policy": "CFBD_API_KEY is read from the environment only and never emitted",
        "seasons": seasons,
        "request_delay_seconds": request_delay_seconds,
        "max_429_retries": max_429_retries,
        "comparison_policy": (
            "exact game IDs first; provider team IDs are derived from exact matched sides; "
            "display-name text is diagnostic only; source assets are discovered from the release manifest"
        ),
    }
    if not key:
        report["status"] = "SKIPPED_NO_CFBD_API_KEY"
        return report

    manifest_acquired_at = utc_now()
    manifest_result = fetch_json(
        SPORTSDATAVERSE_RELEASE_API,
        max_429_retries=max_429_retries,
    )
    manifest = manifest_result.get("data")
    report["sportsdataverse_release_manifest"] = {
        "http_status": manifest_result.get("http_status"),
        "attempts": manifest_result.get("attempts"),
        "acquired_at": manifest_acquired_at,
        "source_url": SPORTSDATAVERSE_RELEASE_API,
        "release_updated_at": manifest.get("updated_at") if isinstance(manifest, dict) else None,
        "asset_count": len(manifest.get("assets", [])) if isinstance(manifest, dict) and isinstance(manifest.get("assets"), list) else None,
    }
    if manifest_result.get("http_status") != 200 or not isinstance(manifest, dict):
        report["status"] = "SPORTSDATAVERSE_MANIFEST_ERROR"
        report["sportsdataverse_release_manifest"]["error"] = manifest
        return report

    report["status"] = "RAN"
    report["results"] = {}

    for index, season in enumerate(seasons):
        season_entry: dict[str, Any] = {}
        cfbd_acquired_at = utc_now()
        cfbd = cfbd_games(season, key, max_429_retries)
        season_entry["cfbd"] = {
            "http_status": cfbd.get("http_status"),
            "attempts": cfbd.get("attempts"),
            "acquired_at": cfbd_acquired_at,
            "query_scope": {"year": season, "seasonType": "both", "classification": "fbs"},
        }

        asset = select_schedule_asset(manifest, season)
        if asset is None:
            season_entry["status"] = "SPORTSDATAVERSE_NO_SUPPORTED_SEASON_ASSET"
            season_entry["sportsdataverse"] = {
                "supported_formats": [".csv.gz", ".csv"],
                "season": season,
            }
            report["results"][str(season)] = season_entry
            continue

        if request_delay_seconds > 0:
            time.sleep(request_delay_seconds)

        source_url = str(asset.get("browser_download_url"))
        asset_name = str(asset.get("name"))
        sd_acquired_at = utc_now()
        sd = fetch_bytes(source_url, max_429_retries=max_429_retries)
        raw_asset = sd.get("data", b"")
        actual_sha = hashlib.sha256(raw_asset).hexdigest() if raw_asset else None
        season_entry["sportsdataverse"] = {
            "http_status": sd.get("http_status"),
            "attempts": sd.get("attempts"),
            "acquired_at": sd_acquired_at,
            "asset_name": asset_name,
            "source_url": source_url,
            "byte_count": len(raw_asset),
            "sha256": actual_sha,
            "advertised_digest": asset.get("digest"),
            "advertised_digest_matches": advertised_digest_matches(asset, actual_sha),
            "asset_created_at": asset.get("created_at"),
            "asset_updated_at": asset.get("updated_at"),
        }

        cfbd_rows = cfbd.get("data")
        if cfbd.get("http_status") != 200 or not isinstance(cfbd_rows, list):
            season_entry["status"] = "CFBD_ERROR"
            season_entry["cfbd"]["error"] = cfbd_rows
            report["results"][str(season)] = season_entry
            continue

        if sd.get("http_status") != 200:
            season_entry["status"] = "SPORTSDATAVERSE_ERROR"
            season_entry["sportsdataverse"]["error_preview"] = raw_asset[:500].decode(
                "utf-8", errors="replace"
            )
            report["results"][str(season)] = season_entry
            continue

        try:
            espn_rows = decode_schedule_asset(raw_asset, asset_name)
        except (OSError, UnicodeDecodeError, csv.Error, ValueError) as exc:
            season_entry["status"] = "SPORTSDATAVERSE_DECODE_ERROR"
            season_entry["sportsdataverse"]["decode_error"] = str(exc)
            report["results"][str(season)] = season_entry
            continue

        season_entry["status"] = "COMPARED"
        season_entry["comparison"] = compare_season(cfbd_rows, espn_rows)
        report["results"][str(season)] = season_entry

        if index + 1 < len(seasons) and request_delay_seconds > 0:
            time.sleep(request_delay_seconds)

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seasons",
        default=",".join(str(value) for value in DEFAULT_SEASONS),
        help="comma-separated season years",
    )
    parser.add_argument(
        "--request-delay-seconds",
        type=float,
        default=DEFAULT_REQUEST_DELAY_SECONDS,
        help="delay between provider requests",
    )
    parser.add_argument(
        "--max-429-retries",
        type=int,
        default=DEFAULT_MAX_429_RETRIES,
        help="bounded retry count for HTTP 429",
    )
    parser.add_argument("--output", help="optional JSON output path; stdout if omitted")
    args = parser.parse_args()

    report = build_report(
        parse_int_list(args.seasons),
        os.getenv("CFBD_API_KEY"),
        request_delay_seconds=max(args.request_delay_seconds, 0.0),
        max_429_retries=max(args.max_429_retries, 0),
    )
    rendered = json.dumps(report, indent=2, sort_keys=True)

    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered + "\n", encoding="utf-8")
        print(path)
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
