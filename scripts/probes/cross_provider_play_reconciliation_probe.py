#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2-C C6-A selected play-level reconciliation probe.

Research/audit tooling only.

The probe compares CollegeFootballData historical /plays rows with ESPN site-v2
summary play-by-play for a bounded set of already-reconciled game IDs. Exact play
ID equality is measured before any semantic field comparison. Provider-only plays
remain explicit and are never force-paired by row order, clock, or text.

CFBD_API_KEY is read from the environment only and is never emitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "DAILY_NCAAF_PHASE_B2C_SELECTED_PLAY_RECONCILIATION_V1"
CFBD_BASE = "https://api.collegefootballdata.com"
ESPN_SUMMARY_BASE = (
    "https://site.api.espn.com/apis/site/v2/sports/football/"
    "college-football/summary"
)
DEFAULT_GAME_IDS = (
    401520375,
    401628339,
    401628459,
    401677085,
    401677093,
    401754516,
)
DEFAULT_REQUEST_DELAY_SECONDS = 0.8
DEFAULT_MAX_429_RETRIES = 3
MAX_EXAMPLES = 12


class ProbeRequestError(RuntimeError):
    """Raised when a probe HTTP request cannot be completed safely."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_int_list(raw: str) -> list[int]:
    values: list[int] = []
    for piece in str(raw).split(","):
        piece = piece.strip()
        if piece:
            values.append(int(piece))
    return values


def normalize_id(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    if not text:
        return None
    if re.fullmatch(r"-?\d+\.0+", text):
        text = text.split(".", 1)[0]
    return text


def normalize_text(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = unicodedata.normalize("NFKD", str(value)).casefold()
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def parse_clock_seconds(value: Any) -> int | None:
    if value in (None, ""):
        return None
    if isinstance(value, dict):
        minutes = value.get("minutes")
        seconds = value.get("seconds")
        if minutes is not None and seconds is not None:
            try:
                return int(minutes) * 60 + int(seconds)
            except (TypeError, ValueError):
                pass
        for key in ("displayValue", "display_value", "clock"):
            if value.get(key) not in (None, ""):
                return parse_clock_seconds(value.get(key))
        numeric = value.get("value")
        if numeric not in (None, ""):
            try:
                return int(float(numeric))
            except (TypeError, ValueError):
                return None
        return None
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip()
    match = re.fullmatch(r"(\d{1,2}):(\d{2})", text)
    if match:
        return int(match.group(1)) * 60 + int(match.group(2))
    try:
        return int(float(text))
    except ValueError:
        return None


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def request_json(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    max_429_retries: int = DEFAULT_MAX_429_RETRIES,
    request_delay_seconds: float = DEFAULT_REQUEST_DELAY_SECONDS,
) -> tuple[Any, dict[str, Any]]:
    safe_headers = {
        "Accept": "application/json",
        "User-Agent": "Daily-NCAAF-C6-research-probe/1.0",
    }
    if headers:
        safe_headers.update(headers)

    attempts = 0
    while True:
        attempts += 1
        request = urllib.request.Request(url, headers=safe_headers)
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
                status = int(getattr(response, "status", 200))
                payload = json.loads(raw.decode("utf-8"))
                meta = {
                    "url": url,
                    "http_status": status,
                    "attempts": attempts,
                    "acquired_at": utc_now(),
                    "byte_count": len(raw),
                    "sha256": _sha256(raw),
                }
                return payload, meta
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempts <= max_429_retries + 1:
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                try:
                    pause = float(retry_after) if retry_after else request_delay_seconds * attempts
                except ValueError:
                    pause = request_delay_seconds * attempts
                time.sleep(max(pause, 0.0))
                continue
            raise ProbeRequestError(f"HTTP {exc.code} for {url}") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ProbeRequestError(f"request failed for {url}: {type(exc).__name__}") from exc


def cfbd_headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def resolve_cfbd_game(
    game_id: int,
    *,
    api_key: str,
    max_429_retries: int,
    request_delay_seconds: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    url = f"{CFBD_BASE}/games?{urllib.parse.urlencode({'id': game_id})}"
    payload, meta = request_json(
        url,
        headers=cfbd_headers(api_key),
        max_429_retries=max_429_retries,
        request_delay_seconds=request_delay_seconds,
    )
    if not isinstance(payload, list):
        raise ProbeRequestError(f"unexpected CFBD games payload for {game_id}")
    exact = [row for row in payload if normalize_id(row.get("id")) == str(game_id)]
    if len(exact) != 1:
        raise ProbeRequestError(
            f"expected one CFBD game row for {game_id}, found {len(exact)}"
        )
    return exact[0], meta


def game_fetch_key(game: dict[str, Any]) -> tuple[int, int, str]:
    season = int(game.get("season"))
    week = int(game.get("week"))
    season_type = str(game.get("seasonType") or "regular").strip().lower()
    return season, week, season_type


def fetch_cfbd_week_plays(
    *,
    season: int,
    week: int,
    season_type: str,
    api_key: str,
    max_429_retries: int,
    request_delay_seconds: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    query = urllib.parse.urlencode(
        {
            "year": season,
            "week": week,
            "seasonType": season_type,
            "classification": "fbs",
        }
    )
    url = f"{CFBD_BASE}/plays?{query}"
    payload, meta = request_json(
        url,
        headers=cfbd_headers(api_key),
        max_429_retries=max_429_retries,
        request_delay_seconds=request_delay_seconds,
    )
    if not isinstance(payload, list):
        raise ProbeRequestError(
            f"unexpected CFBD plays payload for {season} week {week}"
        )
    rows = [row for row in payload if isinstance(row, dict)]
    meta = {**meta, "rows": len(rows)}
    return rows, meta


def fetch_espn_summary(
    game_id: int,
    *,
    max_429_retries: int,
    request_delay_seconds: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    url = f"{ESPN_SUMMARY_BASE}?{urllib.parse.urlencode({'event': game_id})}"
    payload, meta = request_json(
        url,
        max_429_retries=max_429_retries,
        request_delay_seconds=request_delay_seconds,
    )
    if not isinstance(payload, dict):
        raise ProbeRequestError(f"unexpected ESPN summary payload for {game_id}")
    return payload, meta


def extract_espn_plays(summary: dict[str, Any]) -> list[dict[str, Any]]:
    drives_obj = summary.get("drives")
    drives: list[dict[str, Any]] = []
    if isinstance(drives_obj, dict):
        for key in ("previous", "current"):
            value = drives_obj.get(key)
            if isinstance(value, list):
                drives.extend(item for item in value if isinstance(item, dict))
            elif isinstance(value, dict):
                drives.append(value)
    elif isinstance(drives_obj, list):
        drives.extend(item for item in drives_obj if isinstance(item, dict))

    plays: list[dict[str, Any]] = []
    for drive in drives:
        value = drive.get("plays")
        if isinstance(value, list):
            plays.extend(item for item in value if isinstance(item, dict))

    if not plays and isinstance(summary.get("plays"), list):
        plays.extend(item for item in summary["plays"] if isinstance(item, dict))
    return plays


def index_by_id(rows: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    index: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    for row in rows:
        row_id = normalize_id(row.get("id") if "id" in row else row.get("play_id"))
        if row_id is None:
            continue
        if row_id in index:
            duplicates.append(row_id)
        else:
            index[row_id] = row
    return index, sorted(set(duplicates))


def scalar_state(left: Any, right: Any) -> str:
    if left is None and right is None:
        return "UNAVAILABLE_BOTH"
    if left is None or right is None:
        return "UNAVAILABLE_ONE_SIDE"
    return "MATCH" if left == right else "MISMATCH"


def text_state(left: Any, right: Any) -> str:
    if left in (None, "") and right in (None, ""):
        return "UNAVAILABLE_BOTH"
    if left in (None, "") or right in (None, ""):
        return "UNAVAILABLE_ONE_SIDE"
    left_text = str(left).strip()
    right_text = str(right).strip()
    if left_text == right_text:
        return "EXACT"
    if normalize_text(left_text) == normalize_text(right_text):
        return "NORMALIZED"
    return "MISMATCH"


def nested_value(row: dict[str, Any], *path: str) -> Any:
    value: Any = row
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def espn_period(play: dict[str, Any]) -> int | None:
    raw = play.get("period")
    if isinstance(raw, dict):
        raw = raw.get("number") or raw.get("value")
    try:
        return int(raw) if raw is not None else None
    except (TypeError, ValueError):
        return None


def int_or_none(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def bool_or_none(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().casefold()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def compare_shared_play(
    cfbd: dict[str, Any], espn: dict[str, Any]
) -> tuple[dict[str, str], dict[str, tuple[Any, Any]]]:
    espn_type = nested_value(espn, "type", "text")
    if espn_type is None and isinstance(espn.get("type"), str):
        espn_type = espn.get("type")

    left_right: dict[str, tuple[Any, Any]] = {
        "period": (int_or_none(cfbd.get("period")), espn_period(espn)),
        "clock_seconds": (
            parse_clock_seconds(cfbd.get("clock")),
            parse_clock_seconds(espn.get("clock")),
        ),
        "down": (int_or_none(cfbd.get("down")), int_or_none(nested_value(espn, "start", "down"))),
        "distance": (
            int_or_none(cfbd.get("distance")),
            int_or_none(nested_value(espn, "start", "distance")),
        ),
        "yards_to_goal": (
            int_or_none(cfbd.get("yardsToGoal")),
            int_or_none(nested_value(espn, "start", "yardsToEndzone")),
        ),
        "scoring": (
            bool_or_none(cfbd.get("scoring")),
            bool_or_none(espn.get("scoringPlay")),
        ),
        "play_type": (cfbd.get("playType"), espn_type),
        "play_text": (cfbd.get("playText"), espn.get("text")),
    }
    states: dict[str, str] = {}
    for field, pair in left_right.items():
        if field in {"play_type", "play_text"}:
            states[field] = text_state(*pair)
        else:
            states[field] = scalar_state(*pair)
    return states, left_right


def reconcile_game_plays(
    cfbd_rows: list[dict[str, Any]], espn_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    cfbd_index, cfbd_duplicates = index_by_id(cfbd_rows)
    espn_index, espn_duplicates = index_by_id(espn_rows)
    cfbd_ids = set(cfbd_index)
    espn_ids = set(espn_index)
    shared = sorted(cfbd_ids & espn_ids)
    cfbd_only = sorted(cfbd_ids - espn_ids)
    espn_only = sorted(espn_ids - cfbd_ids)

    field_counts: dict[str, Counter[str]] = {
        field: Counter()
        for field in (
            "period",
            "clock_seconds",
            "down",
            "distance",
            "yards_to_goal",
            "scoring",
            "play_type",
            "play_text",
        )
    }
    mismatch_examples: list[dict[str, Any]] = []

    for play_id in shared:
        states, pairs = compare_shared_play(cfbd_index[play_id], espn_index[play_id])
        for field, state in states.items():
            field_counts[field][state] += 1
            if state == "MISMATCH" and len(mismatch_examples) < MAX_EXAMPLES:
                mismatch_examples.append(
                    {
                        "play_id": play_id,
                        "field": field,
                        "cfbd": pairs[field][0],
                        "espn": pairs[field][1],
                    }
                )

    return {
        "cfbd_rows": len(cfbd_rows),
        "espn_rows": len(espn_rows),
        "cfbd_unique_play_ids": len(cfbd_ids),
        "espn_unique_play_ids": len(espn_ids),
        "cfbd_duplicate_play_ids": cfbd_duplicates,
        "espn_duplicate_play_ids": espn_duplicates,
        "exact_shared_play_ids": len(shared),
        "cfbd_only_play_ids_count": len(cfbd_only),
        "espn_only_play_ids_count": len(espn_only),
        "cfbd_only_play_ids_sample": cfbd_only[:MAX_EXAMPLES],
        "espn_only_play_ids_sample": espn_only[:MAX_EXAMPLES],
        "cfbd_exact_id_overlap_rate": (
            len(shared) / len(cfbd_ids) if cfbd_ids else None
        ),
        "espn_exact_id_overlap_rate": (
            len(shared) / len(espn_ids) if espn_ids else None
        ),
        "field_state_counts": {
            field: dict(sorted(counter.items())) for field, counter in field_counts.items()
        },
        "mismatch_examples": mismatch_examples,
    }


def compact_summary(report: dict[str, Any]) -> dict[str, Any]:
    games: dict[str, Any] = {}
    total_cfbd = 0
    total_espn = 0
    total_shared = 0
    total_cfbd_only = 0
    total_espn_only = 0
    total_duplicate_cfbd = 0
    total_duplicate_espn = 0
    aggregate_fields: dict[str, Counter[str]] = {}

    for game_id, result in (report.get("game_results") or {}).items():
        rec = result.get("play_reconciliation") or {}
        total_cfbd += int(rec.get("cfbd_unique_play_ids") or 0)
        total_espn += int(rec.get("espn_unique_play_ids") or 0)
        total_shared += int(rec.get("exact_shared_play_ids") or 0)
        total_cfbd_only += int(rec.get("cfbd_only_play_ids_count") or 0)
        total_espn_only += int(rec.get("espn_only_play_ids_count") or 0)
        total_duplicate_cfbd += len(rec.get("cfbd_duplicate_play_ids") or [])
        total_duplicate_espn += len(rec.get("espn_duplicate_play_ids") or [])
        for field, states in (rec.get("field_state_counts") or {}).items():
            aggregate_fields.setdefault(field, Counter()).update(
                {str(k): int(v) for k, v in states.items()}
            )
        games[str(game_id)] = {
            "status": result.get("status"),
            "season": (result.get("game") or {}).get("season"),
            "week": (result.get("game") or {}).get("week"),
            "season_type": (result.get("game") or {}).get("season_type"),
            "matchup": (result.get("game") or {}).get("matchup"),
            "cfbd_unique_play_ids": rec.get("cfbd_unique_play_ids"),
            "espn_unique_play_ids": rec.get("espn_unique_play_ids"),
            "exact_shared_play_ids": rec.get("exact_shared_play_ids"),
            "cfbd_only_play_ids_count": rec.get("cfbd_only_play_ids_count"),
            "espn_only_play_ids_count": rec.get("espn_only_play_ids_count"),
            "cfbd_exact_id_overlap_rate": rec.get("cfbd_exact_id_overlap_rate"),
            "espn_exact_id_overlap_rate": rec.get("espn_exact_id_overlap_rate"),
            "cfbd_duplicate_play_ids": rec.get("cfbd_duplicate_play_ids"),
            "espn_duplicate_play_ids": rec.get("espn_duplicate_play_ids"),
            "field_state_counts": rec.get("field_state_counts"),
        }

    return {
        "contract_version": report.get("contract_version"),
        "status": report.get("status"),
        "games": games,
        "aggregate": {
            "cfbd_unique_play_ids": total_cfbd,
            "espn_unique_play_ids": total_espn,
            "exact_shared_play_ids": total_shared,
            "cfbd_only_play_ids_count": total_cfbd_only,
            "espn_only_play_ids_count": total_espn_only,
            "cfbd_exact_id_overlap_rate": total_shared / total_cfbd if total_cfbd else None,
            "espn_exact_id_overlap_rate": total_shared / total_espn if total_espn else None,
            "cfbd_duplicate_play_id_count": total_duplicate_cfbd,
            "espn_duplicate_play_id_count": total_duplicate_espn,
            "field_state_counts": {
                field: dict(sorted(counter.items()))
                for field, counter in sorted(aggregate_fields.items())
            },
        },
        "decision_rule": (
            "Exact play IDs are measured before semantic comparisons. Provider-only plays "
            "remain explicit. If exact-ID overlap is insufficient, use a later bounded "
            "composite-alignment study rather than force-matching C6-A rows."
        ),
    }


def build_report(
    *,
    game_ids: list[int] | tuple[int, ...] = DEFAULT_GAME_IDS,
    request_delay_seconds: float = DEFAULT_REQUEST_DELAY_SECONDS,
    max_429_retries: int = DEFAULT_MAX_429_RETRIES,
) -> dict[str, Any]:
    api_key = os.environ.get("CFBD_API_KEY")
    report: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "generated_at": utc_now(),
        "research_only": True,
        "secret_policy": "CFBD_API_KEY is read from the environment only and never emitted",
        "provenance_policy": (
            "CFBD and ESPN delivery paths are compatibility/reconciliation evidence, not "
            "independent upstream corroboration; cross-delivery agreement does not establish PIT safety"
        ),
        "game_ids": [int(value) for value in game_ids],
        "status": "RAN",
        "game_results": {},
    }
    if not api_key:
        report["status"] = "SKIPPED_NO_API_KEY"
        report["compact_summary"] = compact_summary(report)
        return report

    week_cache: dict[tuple[int, int, str], tuple[list[dict[str, Any]], dict[str, Any]]] = {}

    for raw_game_id in game_ids:
        game_id = int(raw_game_id)
        try:
            game_row, game_meta = resolve_cfbd_game(
                game_id,
                api_key=api_key,
                max_429_retries=max_429_retries,
                request_delay_seconds=request_delay_seconds,
            )
            season, week, season_type = game_fetch_key(game_row)
            fetch_key = (season, week, season_type)
            if fetch_key not in week_cache:
                week_cache[fetch_key] = fetch_cfbd_week_plays(
                    season=season,
                    week=week,
                    season_type=season_type,
                    api_key=api_key,
                    max_429_retries=max_429_retries,
                    request_delay_seconds=request_delay_seconds,
                )
            week_rows, week_meta = week_cache[fetch_key]
            cfbd_game_rows = [
                row for row in week_rows if normalize_id(row.get("gameId")) == str(game_id)
            ]

            espn_summary, espn_meta = fetch_espn_summary(
                game_id,
                max_429_retries=max_429_retries,
                request_delay_seconds=request_delay_seconds,
            )
            espn_game_rows = extract_espn_plays(espn_summary)

            home = game_row.get("homeTeam") or game_row.get("home")
            away = game_row.get("awayTeam") or game_row.get("away")
            report["game_results"][str(game_id)] = {
                "status": "COMPARED",
                "game": {
                    "game_id": game_id,
                    "season": season,
                    "week": week,
                    "season_type": season_type,
                    "matchup": f"{away} at {home}",
                    "completed": game_row.get("completed"),
                },
                "cfbd_game_lookup": game_meta,
                "cfbd_week_plays": {
                    **week_meta,
                    "filtered_game_rows": len(cfbd_game_rows),
                },
                "espn_summary": {
                    **espn_meta,
                    "extracted_play_rows": len(espn_game_rows),
                },
                "play_reconciliation": reconcile_game_plays(
                    cfbd_game_rows, espn_game_rows
                ),
            }
        except Exception as exc:  # research harness: preserve other selected cases
            report["game_results"][str(game_id)] = {
                "status": "ERROR",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }

    if any(value.get("status") == "ERROR" for value in report["game_results"].values()):
        report["status"] = "RAN_WITH_ERRORS"
    report["compact_summary"] = compact_summary(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--game-ids",
        default=",".join(str(value) for value in DEFAULT_GAME_IDS),
        help="comma-separated game IDs",
    )
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--request-delay-seconds", type=float, default=DEFAULT_REQUEST_DELAY_SECONDS
    )
    parser.add_argument("--max-429-retries", type=int, default=DEFAULT_MAX_429_RETRIES)
    args = parser.parse_args()

    report = build_report(
        game_ids=parse_int_list(args.game_ids),
        request_delay_seconds=args.request_delay_seconds,
        max_429_retries=args.max_429_retries,
    )
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps(report.get("compact_summary", compact_summary(report)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
