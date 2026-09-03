#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2-B CFBD college-native family probe.

Research/audit tooling only. It performs bounded read-only CFBD requests for
college-native identity/state families. It is not production acquisition.

The CFBD_API_KEY is read from the environment and is never emitted.
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

CONTRACT_VERSION = "DAILY_NCAAF_PHASE_B2_CFBD_NATIVE_FAMILY_PROBE_V1"
CFBD_BASE = "https://api.collegefootballdata.com"
USER_AGENT = "Daily-NCAAF-Phase-B2B-native-family-probe/1.0"

DEFAULT_SEASONS = (2014, 2018, 2024, 2026)
DEFAULT_TEAMS = ("Alabama", "Michigan", "Notre Dame", "Boise State")
DEFAULT_LINE_WEEK = 1

FAMILIES = (
    "teams",
    "conferences",
    "rosters",
    "recruiting",
    "portal",
    "returning",
    "coaches",
    "talent",
    "rankings",
    "ratings",
    "lines",
)

SummaryFn = Callable[[list[dict[str, Any]]], dict[str, Any]]


def parse_csv(raw: str) -> list[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("at least one value is required")
    return values


def parse_int_list(raw: str) -> list[int]:
    return [int(value) for value in parse_csv(raw)]


def null_count(rows: list[dict[str, Any]], field: str) -> int:
    return sum(1 for row in rows if row.get(field) is None)


def list_result_summary(
    rows: list[dict[str, Any]], id_field: str | None = None
) -> dict[str, Any]:
    summary: dict[str, Any] = {"rows": len(rows)}
    if id_field:
        ids = [row.get(id_field) for row in rows if row.get(id_field) is not None]
        summary.update(
            {
                "id_field": id_field,
                "non_null_ids": len(ids),
                "unique_ids": len(set(ids)),
                "duplicate_id_rows": len(ids) - len(set(ids)),
                "id_null_rows": len(rows) - len(ids),
            }
        )
    return summary


def fetch_json(
    path: str,
    params: dict[str, Any],
    key: str,
    timeout: float = 30.0,
) -> dict[str, Any]:
    query = urllib.parse.urlencode(
        {name: value for name, value in params.items() if value is not None}
    )
    url = f"{CFBD_BASE}{path}"
    if query:
        url += f"?{query}"

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
            "Authorization": f"Bearer {key}",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
            return {
                "http_status": response.status,
                "data": json.loads(payload),
            }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed: Any = json.loads(body)
        except json.JSONDecodeError:
            parsed = body[:1000]
        return {
            "http_status": exc.code,
            "error": parsed,
        }


def run_list_probe(
    path: str,
    params: dict[str, Any],
    key: str,
    summarizer: SummaryFn,
) -> dict[str, Any]:
    result = fetch_json(path, params, key)
    if result.get("http_status") != 200 or not isinstance(result.get("data"), list):
        return {
            "http_status": result.get("http_status"),
            "error": result.get("error", result.get("data")),
        }

    rows = result["data"]
    return {
        "http_status": 200,
        "summary": summarizer(rows),
    }


def summarize_teams(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out = list_result_summary(rows, "id")
    out.update(
        {
            "school_null_rows": null_count(rows, "school"),
            "conference_null_rows": null_count(rows, "conference"),
            "classification_counts": Counter(
                str(row.get("classification"))
                for row in rows
                if row.get("classification") is not None
            ).most_common(),
        }
    )
    return out


def summarize_affiliations(rows: list[dict[str, Any]]) -> dict[str, Any]:
    team_ids = [row.get("teamId") for row in rows if row.get("teamId") is not None]
    return {
        "rows": len(rows),
        "unique_team_ids": len(set(team_ids)),
        "team_id_null_rows": len(rows) - len(team_ids),
        "conference_null_rows": null_count(rows, "conference"),
        "open_ended_rows": null_count(rows, "endYear"),
        "classification_counts": Counter(
            str(row.get("classification"))
            for row in rows
            if row.get("classification") is not None
        ).most_common(),
    }


def summarize_roster(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out = list_result_summary(rows, "id")
    out.update(
        {
            "team_count": len({row.get("team") for row in rows if row.get("team")}),
            "position_null_rows": null_count(rows, "position"),
            "jersey_null_rows": null_count(rows, "jersey"),
            "height_null_rows": null_count(rows, "height"),
            "weight_null_rows": null_count(rows, "weight"),
            "recruit_ids_null_rows": null_count(rows, "recruitIds"),
            "recruit_ids_nonempty_rows": sum(
                1
                for row in rows
                if isinstance(row.get("recruitIds"), list) and len(row["recruitIds"]) > 0
            ),
        }
    )
    return out


def summarize_recruits(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out = list_result_summary(rows, "id")
    out.update(
        {
            "athlete_id_null_rows": null_count(rows, "athleteId"),
            "committed_to_null_rows": null_count(rows, "committedTo"),
            "ranking_null_rows": null_count(rows, "ranking"),
            "rating_null_rows": null_count(rows, "rating"),
            "stars_null_rows": null_count(rows, "stars"),
            "position_null_rows": null_count(rows, "position"),
        }
    )
    return out


def summarize_portal(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "rows": len(rows),
        "destination_null_rows": null_count(rows, "destination"),
        "transfer_date_null_rows": null_count(rows, "transferDate"),
        "rating_null_rows": null_count(rows, "rating"),
        "stars_null_rows": null_count(rows, "stars"),
        "eligibility_counts": Counter(
            str(row.get("eligibility"))
            for row in rows
            if row.get("eligibility") is not None
        ).most_common(),
        "unique_origins": len({row.get("origin") for row in rows if row.get("origin")}),
        "unique_destinations": len(
            {row.get("destination") for row in rows if row.get("destination")}
        ),
    }


def summarize_returning(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "rows": len(rows),
        "unique_teams": len({row.get("team") for row in rows if row.get("team")}),
        "conference_null_rows": null_count(rows, "conference"),
        "total_ppa_null_rows": null_count(rows, "totalPPA"),
        "percent_ppa_null_rows": null_count(rows, "percentPPA"),
        "usage_null_rows": null_count(rows, "usage"),
    }


def summarize_coaches(rows: list[dict[str, Any]], year: int) -> dict[str, Any]:
    out = list_result_summary(rows, "id")
    career_season_entries = 0
    queried_year_matches = 0

    for row in rows:
        seasons = row.get("seasons")
        if not isinstance(seasons, list):
            continue
        career_season_entries += len(seasons)
        if any(
            isinstance(season, dict) and season.get("year") == year
            for season in seasons
        ):
            queried_year_matches += 1

    out.update(
        {
            "rows_with_queried_year_in_seasons": queried_year_matches,
            "career_season_entries": career_season_entries,
            "hire_date_null_rows": null_count(rows, "hireDate"),
        }
    )
    return out


def summarize_talent(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "rows": len(rows),
        "unique_teams": len({row.get("team") for row in rows if row.get("team")}),
        "talent_null_rows": null_count(rows, "talent"),
    }


def summarize_rankings(rows: list[dict[str, Any]]) -> dict[str, Any]:
    weeks: Counter[str] = Counter()
    poll_names: Counter[str] = Counter()
    rank_rows = 0

    for row in rows:
        if row.get("week") is not None:
            weeks[str(row.get("week"))] += 1
        polls = row.get("polls")
        if not isinstance(polls, list):
            continue
        for poll in polls:
            if not isinstance(poll, dict):
                continue
            poll_name = poll.get("poll")
            if poll_name is not None:
                poll_names[str(poll_name)] += 1
            ranks = poll.get("ranks")
            if isinstance(ranks, list):
                rank_rows += len(ranks)

    return {
        "snapshot_rows": len(rows),
        "week_counts": weeks.most_common(),
        "poll_snapshot_counts": poll_names.most_common(),
        "nested_rank_rows": rank_rows,
    }


def summarize_rating(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "rows": len(rows),
        "unique_teams": len({row.get("team") for row in rows if row.get("team")}),
        "conference_null_rows": null_count(rows, "conference"),
    }


def summarize_lines(rows: list[dict[str, Any]]) -> dict[str, Any]:
    providers: Counter[str] = Counter()
    observations = 0
    games_with_lines = 0
    spread_null = 0
    over_under_null = 0
    spread_open_null = 0
    over_under_open_null = 0
    home_ml_null = 0
    away_ml_null = 0

    for row in rows:
        lines = row.get("lines")
        if not isinstance(lines, list) or not lines:
            continue
        games_with_lines += 1
        for line in lines:
            if not isinstance(line, dict):
                continue
            observations += 1
            provider = line.get("provider")
            if provider is not None:
                providers[str(provider)] += 1
            spread_null += int(line.get("spread") is None)
            over_under_null += int(line.get("overUnder") is None)
            spread_open_null += int(line.get("spreadOpen") is None)
            over_under_open_null += int(line.get("overUnderOpen") is None)
            home_ml_null += int(line.get("homeMoneyline") is None)
            away_ml_null += int(line.get("awayMoneyline") is None)

    return {
        "game_rows": len(rows),
        "games_with_lines": games_with_lines,
        "line_observations": observations,
        "provider_counts": providers.most_common(),
        "spread_null_observations": spread_null,
        "over_under_null_observations": over_under_null,
        "spread_open_null_observations": spread_open_null,
        "over_under_open_null_observations": over_under_open_null,
        "home_moneyline_null_observations": home_ml_null,
        "away_moneyline_null_observations": away_ml_null,
    }


def probe_season(
    year: int,
    teams: list[str],
    line_week: int,
    families: set[str],
    key: str,
) -> dict[str, Any]:
    out: dict[str, Any] = {}

    if "teams" in families:
        out["teams"] = run_list_probe(
            "/teams/fbs", {"year": year}, key, summarize_teams
        )

    if "conferences" in families:
        out["conference_affiliations"] = run_list_probe(
            "/conferences/affiliations",
            {"year": year, "classification": "fbs"},
            key,
            summarize_affiliations,
        )

    if "rosters" in families:
        out["rosters"] = {}
        for team in teams:
            out["rosters"][team] = run_list_probe(
                "/roster",
                {"year": year, "team": team, "classification": "fbs"},
                key,
                summarize_roster,
            )

    if "recruiting" in families:
        out["recruiting_players"] = run_list_probe(
            "/recruiting/players",
            {"year": year, "classification": "HighSchool"},
            key,
            summarize_recruits,
        )

    if "portal" in families:
        out["transfer_portal"] = run_list_probe(
            "/player/portal", {"year": year}, key, summarize_portal
        )

    if "returning" in families:
        out["returning_production"] = run_list_probe(
            "/player/returning", {"year": year}, key, summarize_returning
        )

    if "coaches" in families:
        out["coaches"] = run_list_probe(
            "/coaches",
            {"year": year},
            key,
            lambda rows: summarize_coaches(rows, year),
        )

    if "talent" in families:
        out["talent"] = run_list_probe(
            "/talent", {"year": year}, key, summarize_talent
        )

    if "rankings" in families:
        out["rankings"] = run_list_probe(
            "/rankings",
            {"year": year, "seasonType": "both"},
            key,
            summarize_rankings,
        )

    if "ratings" in families:
        out["ratings"] = {}
        rating_paths = {
            "elo": "/ratings/elo",
            "srs": "/ratings/srs",
            "sp": "/ratings/sp",
            "fpi": "/ratings/fpi",
            "core": "/ratings/core",
        }
        for name, path in rating_paths.items():
            out["ratings"][name] = run_list_probe(
                path, {"year": year}, key, summarize_rating
            )

    if "lines" in families:
        out["lines_week"] = {
            "week": line_week,
            **run_list_probe(
                "/lines",
                {"year": year, "week": line_week, "seasonType": "regular"},
                key,
                summarize_lines,
            ),
        }

    return out


def build_report(
    seasons: list[int],
    teams: list[str],
    line_week: int,
    families: set[str],
    key: str | None,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "research_only": True,
        "secret_policy": "CFBD_API_KEY is read from the environment only and never emitted",
        "seasons": seasons,
        "teams": teams,
        "line_week": line_week,
        "families": sorted(families),
    }

    if not key:
        report["status"] = "SKIPPED_NO_CFBD_API_KEY"
        return report

    report["status"] = "RAN"
    report["results"] = {
        str(year): probe_season(year, teams, line_week, families, key)
        for year in seasons
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seasons",
        default=",".join(str(value) for value in DEFAULT_SEASONS),
        help="comma-separated season years",
    )
    parser.add_argument(
        "--teams",
        default=",".join(DEFAULT_TEAMS),
        help="comma-separated representative teams for roster probes",
    )
    parser.add_argument(
        "--families",
        default=",".join(FAMILIES),
        help=f"comma-separated subset of: {','.join(FAMILIES)}",
    )
    parser.add_argument("--line-week", type=int, default=DEFAULT_LINE_WEEK)
    parser.add_argument("--output", help="optional JSON output path; stdout if omitted")
    args = parser.parse_args()

    seasons = parse_int_list(args.seasons)
    teams = parse_csv(args.teams)
    requested = set(parse_csv(args.families))
    unknown = sorted(requested - set(FAMILIES))
    if unknown:
        parser.error(f"unknown families: {','.join(unknown)}")

    report = build_report(
        seasons,
        teams,
        args.line_week,
        requested,
        os.getenv("CFBD_API_KEY"),
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
