#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2-C CFBD <-> ESPN/cfbfastR game reconciliation probe.

Research/audit tooling only. The probe compares CFBD's FBS-involved game
response with the public SportsDataverse `espn_cfb_schedules` season asset.
It tests direct game-ID overlap and matched-event field agreement without
creating canonical identities or treating raw provider-universe differences as
missing data.

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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "DAILY_NCAAF_PHASE_B2C_CROSS_PROVIDER_GAME_RECONCILIATION_V1"
CFBD_BASE = "https://api.collegefootballdata.com"
SPORTSDATAVERSE_SCHEDULE_URL = (
    "https://github.com/sportsdataverse/sportsdataverse-data/releases/download/"
    "espn_cfb_schedules/cfb_schedule_{season}.csv.gz"
)
USER_AGENT = "Daily-NCAAF-Phase-B2C-game-reconciliation/1.0"
DEFAULT_SEASONS = (2024, 2026)
DEFAULT_REQUEST_DELAY_SECONDS = 0.8
DEFAULT_MAX_429_RETRIES = 3
MAX_EXAMPLES = 25


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
    if value is None or value == "":
        return None
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return None


def parse_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def parse_bool(value: Any) -> bool | None:
    if value is None or value == "":
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
    if value is None or value == "":
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


def is_fbs_label(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    text = re.sub(r"[^a-z0-9]+", "", str(value).lower())
    if text in {"fbs", "footballbowlsubdivision", "ia", "divisionia"}:
        return True
    if text in {"fcs", "footballchampionshipsubdivision", "iaa", "divisioniaa"}:
        return False
    return None


def sleep_backoff(attempt: int, retry_after: str | None) -> None:
    if retry_after:
        try:
            seconds = float(retry_after)
        except ValueError:
            seconds = 0.0
        if seconds > 0:
            time.sleep(seconds)
            return
    time.sleep(min(2.0 ** attempt, 8.0))


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


def decode_schedule_asset(raw: bytes) -> list[dict[str, str]]:
    payload = gzip.decompress(raw)
    text = payload.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def schedule_game_id(row: dict[str, Any]) -> str | None:
    return normalize_id(first_value(row, ("game_id", "id", "gameId")))


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


def espn_completed(row: dict[str, Any]) -> bool | None:
    return parse_bool(first_value(row, ("completed", "is_completed", "status_completed")))


def espn_division_pair(row: dict[str, Any]) -> tuple[bool | None, bool | None]:
    home = first_value(
        row,
        (
            "home_division",
            "home_team_division",
            "home_classification",
            "home_team_classification",
        ),
    )
    away = first_value(
        row,
        (
            "away_division",
            "away_team_division",
            "away_classification",
            "away_team_classification",
        ),
    )
    return is_fbs_label(home), is_fbs_label(away)


def build_id_index(rows: list[dict[str, Any]], id_fn: Any) -> tuple[dict[str, dict[str, Any]], int, int]:
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


def compare_team_names(cfbd_value: Any, espn_value: Any) -> str:
    if cfbd_value is None or espn_value is None:
        return "UNAVAILABLE"
    if str(cfbd_value) == str(espn_value):
        return "EXACT"
    if normalize_name(cfbd_value) == normalize_name(espn_value):
        return "NORMALIZED"
    return "MISMATCH"


def compare_matched_game(cfbd: dict[str, Any], espn: dict[str, Any]) -> dict[str, Any]:
    home_state = compare_team_names(cfbd.get("homeTeam"), espn_home_name(espn))
    away_state = compare_team_names(cfbd.get("awayTeam"), espn_away_name(espn))

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
        "home_team_state": home_state,
        "away_team_state": away_state,
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
            "home_team": espn_home_name(espn),
            "away_team": espn_away_name(espn),
            "home_score": sd_home_score,
            "away_score": sd_away_score,
            "completed": sd_completed,
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
    home_fbs, away_fbs = espn_division_pair(row)
    return {
        "game_id": schedule_game_id(row),
        "week": espn_week(row),
        "start_date": first_value(row, ("game_date", "start_date", "startDate", "date")),
        "home_team": espn_home_name(row),
        "away_team": espn_away_name(row),
        "home_fbs_label": home_fbs,
        "away_fbs_label": away_fbs,
    }


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

    espn_division_available = False
    espn_fbs_involved_ids: set[str] = set()
    for identifier, row in espn_index.items():
        home_fbs, away_fbs = espn_division_pair(row)
        if home_fbs is not None or away_fbs is not None:
            espn_division_available = True
        if home_fbs is True or away_fbs is True:
            espn_fbs_involved_ids.add(identifier)

    normalized_universe: dict[str, Any]
    if espn_division_available:
        normalized_universe = {
            "status": "MEASURED_FROM_ESPN_DIVISION_FIELDS",
            "espn_fbs_involved_ids": len(espn_fbs_involved_ids),
            "exact_overlap_with_cfbd": len(cfbd_ids & espn_fbs_involved_ids),
            "cfbd_only_after_normalization": len(cfbd_ids - espn_fbs_involved_ids),
            "espn_only_after_normalization": len(espn_fbs_involved_ids - cfbd_ids),
        }
    else:
        normalized_universe = {
            "status": "UNIVERSE_UNNORMALIZED",
            "reason": "no recognized ESPN division/classification columns were populated",
        }

    mismatch_examples = [
        item
        for item in matched
        if "MISMATCH"
        in {
            item["home_team_state"],
            item["away_team_state"],
            item["week_state"],
            item["kickoff_state"],
            item["score_state"],
            item["lifecycle_state"],
        }
    ][:MAX_EXAMPLES]

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
            "raw_espn_extra_interpretation": "UNIVERSE_DIFFERENCE_UNTIL_NORMALIZED",
        },
        "matched_field_agreement": {
            "matched_games": len(matched),
            "home_team_state_counts": state_counts(matched, "home_team_state"),
            "away_team_state_counts": state_counts(matched, "away_team_state"),
            "week_state_counts": state_counts(matched, "week_state"),
            "kickoff_state_counts": state_counts(matched, "kickoff_state"),
            "score_state_counts": state_counts(matched, "score_state"),
            "lifecycle_state_counts": state_counts(matched, "lifecycle_state"),
            "mismatch_examples": mismatch_examples,
        },
        "normalized_event_universe": normalized_universe,
    }


def build_report(
    seasons: list[int],
    key: str | None,
    *,
    request_delay_seconds: float,
    max_429_retries: int,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "research_only": True,
        "secret_policy": "CFBD_API_KEY is read from the environment only and never emitted",
        "seasons": seasons,
        "request_delay_seconds": request_delay_seconds,
        "max_429_retries": max_429_retries,
        "comparison_policy": (
            "exact provider game IDs are tested first; raw provider-universe differences "
            "are not classified as missing data without universe normalization"
        ),
    }
    if not key:
        report["status"] = "SKIPPED_NO_CFBD_API_KEY"
        return report

    report["status"] = "RAN"
    report["results"] = {}

    for index, season in enumerate(seasons):
        season_entry: dict[str, Any] = {}
        cfbd_acquired_at = datetime.now(timezone.utc).isoformat()
        cfbd = cfbd_games(season, key, max_429_retries)
        season_entry["cfbd"] = {
            "http_status": cfbd.get("http_status"),
            "attempts": cfbd.get("attempts"),
            "acquired_at": cfbd_acquired_at,
            "query_scope": {"year": season, "seasonType": "both", "classification": "fbs"},
        }

        if request_delay_seconds > 0:
            time.sleep(request_delay_seconds)

        source_url = SPORTSDATAVERSE_SCHEDULE_URL.format(season=season)
        sd_acquired_at = datetime.now(timezone.utc).isoformat()
        sd = fetch_bytes(source_url, max_429_retries=max_429_retries)
        raw_asset = sd.get("data", b"")
        season_entry["sportsdataverse"] = {
            "http_status": sd.get("http_status"),
            "attempts": sd.get("attempts"),
            "acquired_at": sd_acquired_at,
            "source_url": source_url,
            "byte_count": len(raw_asset),
            "sha256": hashlib.sha256(raw_asset).hexdigest() if raw_asset else None,
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
            espn_rows = decode_schedule_asset(raw_asset)
        except (OSError, UnicodeDecodeError, csv.Error) as exc:
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
