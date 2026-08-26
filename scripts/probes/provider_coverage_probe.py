#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2 provider coverage probe.

This is research/audit tooling, not production ingestion. It measures public
SportsDataverse release manifests without credentials and can perform small,
read-only CFBD probes when CFBD_API_KEY is present in the environment.

No secret value is ever written to the report.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

DEFAULT_SEASONS = (2004, 2006, 2010, 2014, 2015, 2018, 2020, 2021, 2023, 2024, 2025, 2026)
DEFAULT_CFBD_WEEKS = (1, 8, 15)

SPORTSDATAVERSE_RELEASES = {
    "schedules": "espn_cfb_schedules",
    "play_by_play": "espn_cfb_pbp",
    "game_rosters": "espn_cfb_game_rosters",
    "play_participants": "espn_cfb_play_participants",
    "betting": "espn_cfb_betting",
    "injuries": "espn_cfb_injuries",
    "power_index": "espn_cfb_power_index",
}

# Verified in cfbfastR-cfb-data DATASETS.md during B.2 public-source inspection.
# These fields describe the NEXT play and therefore are prohibited predictors
# for play-level next-state models.
KNOWN_CFBFASTR_LOOKAHEAD_FIELDS = (
    "lead_text",
    "lead_start_team",
    "lead_start_yardsToEndzone",
    "lead_start_down",
    "lead_start_distance",
    "lead_scoringPlay",
)

GITHUB_RELEASE_BASE = (
    "https://api.github.com/repos/sportsdataverse/sportsdataverse-data/releases/tags/"
)
CFBD_BASE = "https://api.collegefootballdata.com"
USER_AGENT = "Daily-NCAAF-Phase-B2-coverage-probe/1.0"


@dataclass(frozen=True)
class HttpResult:
    status: int
    data: Any
    headers: dict[str, str]


def parse_int_list(raw: str) -> list[int]:
    values: list[int] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        values.append(int(item))
    if not values:
        raise ValueError("at least one integer is required")
    return values


def fetch_json(url: str, *, bearer: str | None = None, timeout: float = 30.0) -> HttpResult:
    headers = {
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
            return HttpResult(
                status=response.status,
                data=json.loads(payload),
                headers={k.lower(): v for k, v in response.headers.items()},
            )
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed: Any = json.loads(body)
        except json.JSONDecodeError:
            parsed = body[:1000]
        return HttpResult(
            status=exc.code,
            data=parsed,
            headers={k.lower(): v for k, v in exc.headers.items()},
        )


def _asset_rank(name: str) -> int:
    if name.endswith(".parquet"):
        return 0
    if name.endswith(".csv.gz"):
        return 1
    if name.endswith(".csv"):
        return 2
    if name.endswith(".rds"):
        return 3
    return 99


def select_season_asset(assets: Iterable[dict[str, Any]], season: int) -> dict[str, Any] | None:
    marker = f"_{season}."
    candidates = [a for a in assets if marker in str(a.get("name", ""))]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda a: (_asset_rank(str(a.get("name", ""))), str(a.get("name", ""))),
    )[0]


def sportsdataverse_manifest_probe(seasons: list[int]) -> dict[str, Any]:
    datasets: dict[str, Any] = {}
    for dataset, tag in SPORTSDATAVERSE_RELEASES.items():
        url = GITHUB_RELEASE_BASE + urllib.parse.quote(tag, safe="")
        result = fetch_json(url)
        entry: dict[str, Any] = {
            "release_tag": tag,
            "http_status": result.status,
            "release_updated_at": None,
            "asset_count": None,
            "seasons": {},
        }
        if result.status != 200 or not isinstance(result.data, dict):
            entry["error"] = result.data
            datasets[dataset] = entry
            continue

        assets = result.data.get("assets", [])
        entry["release_updated_at"] = result.data.get("updated_at")
        entry["asset_count"] = len(assets)
        for season in seasons:
            asset = select_season_asset(assets, season)
            if asset is None:
                entry["seasons"][str(season)] = {"present": False}
                continue
            entry["seasons"][str(season)] = {
                "present": True,
                "name": asset.get("name"),
                "size_bytes": asset.get("size"),
                "created_at": asset.get("created_at"),
                "updated_at": asset.get("updated_at"),
                "digest": asset.get("digest"),
            }
        datasets[dataset] = entry

    return {
        "provider": "SportsDataverse/cfbfastR public releases",
        "probe_type": "release_manifest",
        "datasets": datasets,
        "known_field_guardrails": {
            "cfbfastR_play_level_lookahead_fields": list(KNOWN_CFBFASTR_LOOKAHEAD_FIELDS),
            "rule": "never whitelist an entire provider table as model features",
        },
    }


def cfbd_get(path: str, params: dict[str, Any], key: str) -> HttpResult:
    query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    return fetch_json(f"{CFBD_BASE}{path}?{query}", bearer=key)


def summarize_games(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ids = [row.get("id") for row in rows if row.get("id") is not None]
    home_conf_null = sum(1 for row in rows if row.get("homeConference") is None)
    away_conf_null = sum(1 for row in rows if row.get("awayConference") is None)
    neutral = sum(1 for row in rows if bool(row.get("neutralSite")))
    completed = sum(1 for row in rows if bool(row.get("completed")))
    return {
        "rows": len(rows),
        "unique_game_ids": len(set(ids)),
        "duplicate_game_id_rows": len(ids) - len(set(ids)),
        "completed_rows": completed,
        "neutral_site_rows": neutral,
        "home_conference_null_rows": home_conf_null,
        "away_conference_null_rows": away_conf_null,
    }


def summarize_plays(rows: list[dict[str, Any]]) -> dict[str, Any]:
    game_ids = [row.get("gameId") for row in rows if row.get("gameId") is not None]
    play_ids = [row.get("id") for row in rows if row.get("id") is not None]
    wallclock_null = sum(1 for row in rows if row.get("wallclock") is None)
    ppa_null = sum(1 for row in rows if row.get("ppa") is None)
    play_text_null = sum(1 for row in rows if row.get("playText") is None)
    play_types = Counter(str(row.get("playType")) for row in rows if row.get("playType") is not None)
    return {
        "rows": len(rows),
        "unique_game_ids": len(set(game_ids)),
        "unique_play_ids": len(set(play_ids)),
        "duplicate_play_id_rows": len(play_ids) - len(set(play_ids)),
        "wallclock_null_rows": wallclock_null,
        "ppa_null_rows": ppa_null,
        "play_text_null_rows": play_text_null,
        "top_play_types": play_types.most_common(12),
    }


def cfbd_probe(seasons: list[int], weeks: list[int], key: str | None) -> dict[str, Any]:
    if not key:
        return {
            "provider": "CollegeFootballData",
            "probe_type": "authenticated_read_only",
            "status": "SKIPPED_NO_CFBD_API_KEY",
            "secret_policy": "CFBD_API_KEY is read from the environment only and never emitted",
        }

    output: dict[str, Any] = {
        "provider": "CollegeFootballData",
        "probe_type": "authenticated_read_only",
        "status": "RAN",
        "secret_policy": "key value intentionally omitted",
        "seasons": {},
    }

    for season in seasons:
        season_entry: dict[str, Any] = {"games": {}, "plays_by_week": {}}
        games = cfbd_get(
            "/games",
            {"year": season, "seasonType": "both", "classification": "fbs"},
            key,
        )
        season_entry["games"]["http_status"] = games.status
        if games.status == 200 and isinstance(games.data, list):
            season_entry["games"]["summary"] = summarize_games(games.data)
        else:
            season_entry["games"]["error"] = games.data

        for week in weeks:
            plays = cfbd_get(
                "/plays",
                {
                    "year": season,
                    "week": week,
                    "seasonType": "both",
                    "classification": "fbs",
                },
                key,
            )
            week_entry: dict[str, Any] = {"http_status": plays.status}
            if plays.status == 200 and isinstance(plays.data, list):
                week_entry["summary"] = summarize_plays(plays.data)
            else:
                week_entry["error"] = plays.data
            season_entry["plays_by_week"][str(week)] = week_entry

        output["seasons"][str(season)] = season_entry

    return output


def build_report(mode: str, seasons: list[int], weeks: list[int]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "contract_version": "DAILY_NCAAF_PHASE_B2_PROVIDER_COVERAGE_PROBE_V1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "research_only": True,
        "seasons": seasons,
        "cfbd_weeks": weeks,
        "providers": {},
    }
    if mode in {"public", "all"}:
        report["providers"]["sportsdataverse"] = sportsdataverse_manifest_probe(seasons)
    if mode in {"cfbd", "all"}:
        report["providers"]["cfbd"] = cfbd_probe(seasons, weeks, os.getenv("CFBD_API_KEY"))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("public", "cfbd", "all"), default="all")
    parser.add_argument(
        "--seasons",
        default=",".join(str(v) for v in DEFAULT_SEASONS),
        help="comma-separated season years",
    )
    parser.add_argument(
        "--cfbd-weeks",
        default=",".join(str(v) for v in DEFAULT_CFBD_WEEKS),
        help="comma-separated representative weeks for CFBD PBP probes",
    )
    parser.add_argument("--output", help="optional JSON output path; stdout if omitted")
    args = parser.parse_args()

    seasons = parse_int_list(args.seasons)
    weeks = parse_int_list(args.cfbd_weeks)
    report = build_report(args.mode, seasons, weeks)
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
