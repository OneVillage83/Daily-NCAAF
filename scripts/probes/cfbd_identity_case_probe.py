#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2-B targeted CFBD identity case probe.

Research/audit tooling only. This script measures provider identity continuity for
bounded player/transfer/coach cases. Name matching is used only to find
candidates and is never promoted to canonical identity.

The CFBD_API_KEY is read from the environment and is never emitted.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "DAILY_NCAAF_PHASE_B2_CFBD_IDENTITY_CASE_PROBE_V1"
CFBD_BASE = "https://api.collegefootballdata.com"
USER_AGENT = "Daily-NCAAF-Phase-B2B-identity-case-probe/1.0"
DEFAULT_REQUEST_DELAY_SECONDS = 0.8
DEFAULT_MAX_429_RETRIES = 3

PLAYER_CASES: dict[str, dict[str, Any]] = {
    "jalen_milroe": {
        "name": "Jalen Milroe",
        "recruit_year": 2021,
        "roster_stints": [
            {"year": 2021, "team": "Alabama", "classification": "fbs"},
            {"year": 2022, "team": "Alabama", "classification": "fbs"},
            {"year": 2023, "team": "Alabama", "classification": "fbs"},
            {"year": 2024, "team": "Alabama", "classification": "fbs"},
        ],
        "portal_years": [],
    },
    "dillon_gabriel": {
        "name": "Dillon Gabriel",
        "recruit_year": 2019,
        "roster_stints": [
            {"year": 2019, "team": "UCF", "classification": "fbs"},
            {"year": 2020, "team": "UCF", "classification": "fbs"},
            {"year": 2021, "team": "UCF", "classification": "fbs"},
            {"year": 2022, "team": "Oklahoma", "classification": "fbs"},
            {"year": 2023, "team": "Oklahoma", "classification": "fbs"},
            {"year": 2024, "team": "Oregon", "classification": "fbs"},
        ],
        "portal_years": [2022, 2024],
    },
    "travis_hunter": {
        "name": "Travis Hunter",
        "recruit_year": 2022,
        "roster_stints": [
            {"year": 2022, "team": "Jackson State", "classification": "fcs"},
            {"year": 2023, "team": "Colorado", "classification": "fbs"},
            {"year": 2024, "team": "Colorado", "classification": "fbs"},
        ],
        "portal_years": [2023],
    },
    "caleb_downs": {
        "name": "Caleb Downs",
        "recruit_year": 2023,
        "roster_stints": [
            {"year": 2023, "team": "Alabama", "classification": "fbs"},
            {"year": 2024, "team": "Ohio State", "classification": "fbs"},
            {"year": 2025, "team": "Ohio State", "classification": "fbs"},
        ],
        "portal_years": [2024],
    },
}

COACH_CASES: dict[str, dict[str, str]] = {
    "nick_saban": {"first_name": "Nick", "last_name": "Saban"},
    "kalen_deboer": {"first_name": "Kalen", "last_name": "DeBoer"},
    "curt_cignetti": {"first_name": "Curt", "last_name": "Cignetti"},
}

CANDIDATE_FIELDS = (
    "id",
    "athleteId",
    "athlete_id",
    "name",
    "firstName",
    "lastName",
    "first_name",
    "last_name",
    "team",
    "position",
    "jersey",
    "year",
    "classification",
    "origin",
    "destination",
    "transferDate",
    "eligibility",
    "rating",
    "stars",
    "committedTo",
)


def parse_csv(raw: str) -> list[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("at least one value is required")
    return values


def normalize_name(value: str | None) -> str:
    if not value:
        return ""
    return "".join(character.lower() for character in value if character.isalnum())


def row_name(row: dict[str, Any]) -> str:
    direct = row.get("name")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    first = row.get("firstName") or row.get("first_name")
    last = row.get("lastName") or row.get("last_name")
    parts = [str(value).strip() for value in (first, last) if value]
    return " ".join(parts)


def candidate_rows(rows: list[dict[str, Any]], target_name: str) -> list[dict[str, Any]]:
    target = normalize_name(target_name)
    return [row for row in rows if normalize_name(row_name(row)) == target]


def provider_identifier(row: dict[str, Any]) -> str | None:
    for field_name in ("athleteId", "athlete_id", "id"):
        value = row.get(field_name)
        if value is not None and str(value).strip():
            return str(value)
    return None


def candidate_view(row: dict[str, Any]) -> dict[str, Any]:
    view = {
        key: row.get(key)
        for key in CANDIDATE_FIELDS
        if key in row and row.get(key) is not None
    }
    view["resolved_name"] = row_name(row)
    view["schema_keys"] = sorted(row.keys())
    return view


def summarize_candidate_set(
    rows: list[dict[str, Any]], target_name: str
) -> dict[str, Any]:
    matches = candidate_rows(rows, target_name)
    identifiers = [
        value for value in (provider_identifier(row) for row in matches) if value is not None
    ]
    return {
        "source_rows": len(rows),
        "candidate_rows": len(matches),
        "candidate_identifiers": sorted(set(identifiers)),
        "candidates": [candidate_view(row) for row in matches],
        "identity_interpretation": (
            "DIRECT_PROVIDER_IDENTIFIER_PRESENT"
            if identifiers
            else "NAME_CONTEXT_CANDIDATE_ONLY"
        ),
    }


def summarize_roster_identity(
    observations: list[dict[str, Any]], target_name: str
) -> dict[str, Any]:
    ids: list[str] = []
    observed_stints = 0
    for observation in observations:
        summary = observation.get("summary")
        if not isinstance(summary, dict):
            continue
        if summary.get("candidate_rows", 0) > 0:
            observed_stints += 1
        ids.extend(str(value) for value in summary.get("candidate_identifiers", []))

    unique_ids = sorted(set(ids))
    if observed_stints == 0:
        interpretation = "UNRESOLVED"
    elif len(unique_ids) == 1:
        interpretation = "STABLE_PROVIDER_ID"
    elif len(unique_ids) > 1:
        interpretation = "MULTIPLE_PROVIDER_IDS_REQUIRES_RECONCILIATION"
    else:
        interpretation = "NAME_CONTEXT_CANDIDATE_ONLY"

    return {
        "target_name": target_name,
        "observed_roster_stints": observed_stints,
        "distinct_roster_identifiers": unique_ids,
        "distinct_roster_identifier_count": len(unique_ids),
        "identity_interpretation": interpretation,
    }


def summarize_recruit_link(
    recruit_summary: dict[str, Any] | None,
    roster_identifiers: list[str],
) -> dict[str, Any]:
    if not recruit_summary:
        return {
            "direct_athlete_ids": [],
            "direct_match_to_roster": False,
            "identity_interpretation": "UNRESOLVED",
        }

    direct_ids: set[str] = set()
    for candidate in recruit_summary.get("candidates", []):
        if not isinstance(candidate, dict):
            continue
        value = candidate.get("athleteId") or candidate.get("athlete_id")
        if value is not None:
            direct_ids.add(str(value))

    roster_set = {str(value) for value in roster_identifiers}
    matched = bool(direct_ids & roster_set)
    if matched:
        interpretation = "DIRECT_PROVIDER_LINK"
    elif direct_ids:
        interpretation = "DIRECT_ID_PRESENT_BUT_NOT_ROSTER_MATCH"
    elif recruit_summary.get("candidate_rows", 0) > 0:
        interpretation = "NAME_CONTEXT_CANDIDATE_ONLY"
    else:
        interpretation = "UNRESOLVED"

    return {
        "direct_athlete_ids": sorted(direct_ids),
        "direct_match_to_roster": matched,
        "identity_interpretation": interpretation,
    }


@dataclass
class CFBDClient:
    key: str
    request_delay_seconds: float = DEFAULT_REQUEST_DELAY_SECONDS
    max_429_retries: int = DEFAULT_MAX_429_RETRIES
    timeout_seconds: float = 30.0
    _cache: dict[tuple[str, tuple[tuple[str, str], ...]], dict[str, Any]] = field(
        default_factory=dict
    )
    _last_request_at: float = 0.0

    def _cache_key(
        self, path: str, params: dict[str, Any]
    ) -> tuple[str, tuple[tuple[str, str], ...]]:
        normalized = tuple(
            sorted(
                (str(key), str(value))
                for key, value in params.items()
                if value is not None
            )
        )
        return path, normalized

    def get_json(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        cache_key = self._cache_key(path, params)
        cached = self._cache.get(cache_key)
        if cached is not None:
            copied = dict(cached)
            copied["cache_hit"] = True
            return copied

        query = urllib.parse.urlencode(
            {name: value for name, value in params.items() if value is not None}
        )
        url = f"{CFBD_BASE}{path}"
        if query:
            url += f"?{query}"

        attempts = 0
        result: dict[str, Any] = {}
        while attempts <= self.max_429_retries:
            attempts += 1
            elapsed = time.monotonic() - self._last_request_at
            if self._last_request_at and elapsed < self.request_delay_seconds:
                time.sleep(self.request_delay_seconds - elapsed)

            request = urllib.request.Request(
                url,
                headers={
                    "Accept": "application/json",
                    "User-Agent": USER_AGENT,
                    "Authorization": f"Bearer {self.key}",
                },
                method="GET",
            )

            try:
                with urllib.request.urlopen(
                    request, timeout=self.timeout_seconds
                ) as response:
                    self._last_request_at = time.monotonic()
                    payload = response.read().decode("utf-8")
                    result = {
                        "http_status": response.status,
                        "attempts": attempts,
                        "data": json.loads(payload),
                    }
                    break
            except urllib.error.HTTPError as exc:
                self._last_request_at = time.monotonic()
                body = exc.read().decode("utf-8", errors="replace")
                try:
                    parsed: Any = json.loads(body)
                except json.JSONDecodeError:
                    parsed = body[:1000]

                result = {
                    "http_status": exc.code,
                    "attempts": attempts,
                    "error": parsed,
                }
                if exc.code != 429 or attempts > self.max_429_retries:
                    break

                retry_after = exc.headers.get("Retry-After")
                try:
                    retry_seconds = float(retry_after) if retry_after else 0.0
                except (TypeError, ValueError):
                    retry_seconds = 0.0
                backoff = max(retry_seconds, self.request_delay_seconds * (2 ** attempts))
                time.sleep(backoff)

        self._cache[cache_key] = dict(result)
        return result

    def get_list(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        result = self.get_json(path, params)
        if result.get("http_status") != 200 or not isinstance(result.get("data"), list):
            return {
                "http_status": result.get("http_status"),
                "attempts": result.get("attempts"),
                "cache_hit": result.get("cache_hit", False),
                "error": result.get("error", result.get("data")),
            }
        return {
            "http_status": 200,
            "attempts": result.get("attempts"),
            "cache_hit": result.get("cache_hit", False),
            "rows": result["data"],
        }


def probe_list_candidates(
    client: CFBDClient,
    path: str,
    params: dict[str, Any],
    target_name: str,
) -> dict[str, Any]:
    result = client.get_list(path, params)
    if result.get("http_status") != 200:
        return {
            "http_status": result.get("http_status"),
            "attempts": result.get("attempts"),
            "cache_hit": result.get("cache_hit", False),
            "error": result.get("error"),
        }
    summary = summarize_candidate_set(result["rows"], target_name)
    return {
        "http_status": 200,
        "attempts": result.get("attempts"),
        "cache_hit": result.get("cache_hit", False),
        "summary": summary,
    }


def probe_player_case(
    client: CFBDClient, case_name: str, case: dict[str, Any]
) -> dict[str, Any]:
    target_name = str(case["name"])
    out: dict[str, Any] = {
        "case": case_name,
        "target_name": target_name,
        "matching_policy": "normalized-name matching finds candidates only; it never establishes canonical identity",
    }

    out["player_search"] = probe_list_candidates(
        client,
        "/player/search",
        {"searchTerm": target_name},
        target_name,
    )

    roster_observations: list[dict[str, Any]] = []
    for stint in case["roster_stints"]:
        observation = {
            "year": stint["year"],
            "team": stint["team"],
            "classification": stint["classification"],
        }
        result = probe_list_candidates(
            client,
            "/roster",
            {
                "year": stint["year"],
                "team": stint["team"],
                "classification": stint["classification"],
            },
            target_name,
        )
        observation.update(result)
        roster_observations.append(observation)

    out["roster_observations"] = roster_observations
    roster_identity = summarize_roster_identity(roster_observations, target_name)
    out["roster_identity"] = roster_identity

    recruit_year = int(case["recruit_year"])
    out["recruiting"] = {
        "year": recruit_year,
        **probe_list_candidates(
            client,
            "/recruiting/players",
            {"year": recruit_year, "classification": "HighSchool"},
            target_name,
        ),
    }
    recruit_summary = out["recruiting"].get("summary")
    out["recruit_to_roster_link"] = summarize_recruit_link(
        recruit_summary if isinstance(recruit_summary, dict) else None,
        roster_identity["distinct_roster_identifiers"],
    )

    portal_observations: list[dict[str, Any]] = []
    for year in case["portal_years"]:
        observation = {
            "year": year,
            **probe_list_candidates(
                client,
                "/player/portal",
                {"year": year},
                target_name,
            ),
        }
        portal_observations.append(observation)
    out["portal_observations"] = portal_observations

    portal_explicit_ids: set[str] = set()
    portal_candidate_rows = 0
    for observation in portal_observations:
        summary = observation.get("summary")
        if not isinstance(summary, dict):
            continue
        portal_candidate_rows += int(summary.get("candidate_rows", 0))
        portal_explicit_ids.update(
            str(value) for value in summary.get("candidate_identifiers", [])
        )

    out["portal_identity"] = {
        "candidate_rows": portal_candidate_rows,
        "explicit_provider_identifiers": sorted(portal_explicit_ids),
        "identity_interpretation": (
            "DIRECT_PROVIDER_IDENTIFIER_PRESENT"
            if portal_explicit_ids
            else (
                "NAME_CONTEXT_CANDIDATE_ONLY"
                if portal_candidate_rows
                else "UNRESOLVED"
            )
        ),
    }
    return out


def summarize_coach_rows(rows: list[dict[str, Any]], target_name: str) -> dict[str, Any]:
    matches = candidate_rows(rows, target_name)
    ids = sorted(
        {
            str(row.get("id"))
            for row in matches
            if row.get("id") is not None and str(row.get("id")).strip()
        }
    )
    season_entries = 0
    teams: set[str] = set()
    years: set[int] = set()
    candidate_payloads: list[dict[str, Any]] = []

    for row in matches:
        seasons = row.get("seasons")
        if isinstance(seasons, list):
            season_entries += len(seasons)
            for season in seasons:
                if not isinstance(season, dict):
                    continue
                team = season.get("school") or season.get("team")
                if team:
                    teams.add(str(team))
                year = season.get("year")
                if isinstance(year, int):
                    years.add(year)
        candidate_payloads.append(
            {
                "id": row.get("id"),
                "resolved_name": row_name(row),
                "schema_keys": sorted(row.keys()),
                "seasons": seasons if isinstance(seasons, list) else None,
            }
        )

    if len(ids) == 1:
        interpretation = "STABLE_PROVIDER_COACH_ID_CANDIDATE"
    elif len(ids) > 1:
        interpretation = "MULTIPLE_PROVIDER_COACH_IDS_REQUIRES_RECONCILIATION"
    elif matches:
        interpretation = "NAME_CONTEXT_CANDIDATE_ONLY"
    else:
        interpretation = "UNRESOLVED"

    return {
        "source_rows": len(rows),
        "candidate_rows": len(matches),
        "provider_ids": ids,
        "nested_season_entries": season_entries,
        "observed_teams": sorted(teams),
        "observed_years": sorted(years),
        "identity_interpretation": interpretation,
        "candidates": candidate_payloads,
    }


def probe_coach_case(
    client: CFBDClient, case_name: str, case: dict[str, str]
) -> dict[str, Any]:
    target_name = f"{case['first_name']} {case['last_name']}"
    result = client.get_list(
        "/coaches",
        {"firstName": case["first_name"], "lastName": case["last_name"]},
    )
    if result.get("http_status") != 200:
        return {
            "case": case_name,
            "target_name": target_name,
            "http_status": result.get("http_status"),
            "attempts": result.get("attempts"),
            "error": result.get("error"),
        }
    return {
        "case": case_name,
        "target_name": target_name,
        "http_status": 200,
        "attempts": result.get("attempts"),
        "summary": summarize_coach_rows(result["rows"], target_name),
    }


def build_report(
    key: str | None,
    player_case_names: list[str],
    coach_case_names: list[str],
    request_delay_seconds: float = DEFAULT_REQUEST_DELAY_SECONDS,
    max_429_retries: int = DEFAULT_MAX_429_RETRIES,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "research_only": True,
        "secret_policy": "CFBD_API_KEY is read from the environment only and never emitted",
        "matching_policy": "name matching discovers candidates only; provider-independent canonical identity is not assigned by this probe",
        "request_delay_seconds": request_delay_seconds,
        "max_429_retries": max_429_retries,
        "player_cases": player_case_names,
        "coach_cases": coach_case_names,
    }

    if not key:
        report["status"] = "SKIPPED_NO_CFBD_API_KEY"
        return report

    client = CFBDClient(
        key=key,
        request_delay_seconds=request_delay_seconds,
        max_429_retries=max_429_retries,
    )
    report["status"] = "RAN"
    report["players"] = {
        case_name: probe_player_case(client, case_name, PLAYER_CASES[case_name])
        for case_name in player_case_names
    }
    report["coaches"] = {
        case_name: probe_coach_case(client, case_name, COACH_CASES[case_name])
        for case_name in coach_case_names
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--player-cases",
        default=",".join(PLAYER_CASES),
        help=f"comma-separated subset of: {','.join(PLAYER_CASES)}",
    )
    parser.add_argument(
        "--coach-cases",
        default=",".join(COACH_CASES),
        help=f"comma-separated subset of: {','.join(COACH_CASES)}",
    )
    parser.add_argument(
        "--request-delay-seconds",
        type=float,
        default=DEFAULT_REQUEST_DELAY_SECONDS,
    )
    parser.add_argument(
        "--max-429-retries",
        type=int,
        default=DEFAULT_MAX_429_RETRIES,
    )
    parser.add_argument("--output", help="optional JSON output path; stdout if omitted")
    args = parser.parse_args()

    requested_players = parse_csv(args.player_cases)
    requested_coaches = parse_csv(args.coach_cases)
    unknown_players = sorted(set(requested_players) - set(PLAYER_CASES))
    unknown_coaches = sorted(set(requested_coaches) - set(COACH_CASES))
    if unknown_players:
        parser.error(f"unknown player cases: {','.join(unknown_players)}")
    if unknown_coaches:
        parser.error(f"unknown coach cases: {','.join(unknown_coaches)}")
    if args.request_delay_seconds < 0:
        parser.error("--request-delay-seconds must be >= 0")
    if args.max_429_retries < 0:
        parser.error("--max-429-retries must be >= 0")

    report = build_report(
        os.getenv("CFBD_API_KEY"),
        requested_players,
        requested_coaches,
        request_delay_seconds=args.request_delay_seconds,
        max_429_retries=args.max_429_retries,
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
