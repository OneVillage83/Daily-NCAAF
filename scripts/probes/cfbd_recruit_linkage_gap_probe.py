#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2-B missing recruit-linkage / name-collision probe.

Research/audit tooling only. The probe samples CFBD recruiting records whose
`athleteId` is null, checks bounded roster observations for explicit `recruitIds`
recovery, and surfaces normalized-name collisions. Name matching discovers
candidates only and never assigns canonical identity.

CFBD_API_KEY is read from the environment and is never emitted.
"""

from __future__ import annotations

import argparse
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
from typing import Any

CONTRACT_VERSION = "DAILY_NCAAF_PHASE_B2_CFBD_RECRUIT_LINKAGE_GAP_PROBE_V1"
CFBD_BASE = "https://api.collegefootballdata.com"
USER_AGENT = "Daily-NCAAF-Phase-B2B-recruit-linkage-gap-probe/1.0"
DEFAULT_YEARS = (2021, 2022, 2023, 2024)
DEFAULT_MAX_CASES_PER_YEAR = 3
DEFAULT_REQUEST_DELAY_SECONDS = 0.8
DEFAULT_MAX_429_RETRIES = 3


def parse_csv(raw: str) -> list[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("at least one value is required")
    return values


def parse_int_list(raw: str) -> list[int]:
    return [int(value) for value in parse_csv(raw)]


def normalize_name(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]", "", value.lower())


def resolved_name(row: dict[str, Any]) -> str:
    name = row.get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    first = str(row.get("firstName") or "").strip()
    last = str(row.get("lastName") or "").strip()
    return " ".join(part for part in (first, last) if part)


class CFBDClient:
    def __init__(
        self,
        key: str,
        request_delay_seconds: float,
        max_429_retries: int,
        timeout: float = 30.0,
    ) -> None:
        self.key = key
        self.request_delay_seconds = max(0.0, request_delay_seconds)
        self.max_429_retries = max(0, max_429_retries)
        self.timeout = timeout
        self.cache: dict[tuple[str, tuple[tuple[str, str], ...]], dict[str, Any]] = {}
        self._last_request_at: float | None = None

    def _cache_key(
        self, path: str, params: dict[str, Any]
    ) -> tuple[str, tuple[tuple[str, str], ...]]:
        normalized = tuple(
            sorted(
                (name, str(value))
                for name, value in params.items()
                if value is not None
            )
        )
        return path, normalized

    def _pace(self) -> None:
        if self._last_request_at is None or self.request_delay_seconds <= 0:
            return
        elapsed = time.monotonic() - self._last_request_at
        remaining = self.request_delay_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)

    def get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        cache_key = self._cache_key(path, params)
        cached = self.cache.get(cache_key)
        if cached is not None:
            replay = dict(cached)
            replay["cache_hit"] = True
            return replay

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
            self._pace()
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
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    self._last_request_at = time.monotonic()
                    payload = response.read().decode("utf-8")
                    result = {
                        "http_status": response.status,
                        "data": json.loads(payload),
                        "attempts": attempts,
                        "cache_hit": False,
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
                    "error": parsed,
                    "attempts": attempts,
                    "cache_hit": False,
                }
                if exc.code != 429 or attempts > self.max_429_retries:
                    break

                retry_after = exc.headers.get("Retry-After")
                try:
                    delay = float(retry_after) if retry_after else 1.5 * attempts
                except ValueError:
                    delay = 1.5 * attempts
                time.sleep(max(delay, self.request_delay_seconds))

        self.cache[cache_key] = dict(result)
        return result


def extract_fbs_names(rows: list[dict[str, Any]]) -> set[str]:
    return {
        str(row.get("school")).strip()
        for row in rows
        if row.get("school") is not None and str(row.get("school")).strip()
    }


def missing_link_candidates(
    recruit_rows: list[dict[str, Any]], fbs_names: set[str]
) -> list[dict[str, Any]]:
    candidates = []
    for row in recruit_rows:
        if row.get("athleteId") is not None:
            continue
        if row.get("id") is None:
            continue
        name = resolved_name(row)
        committed = row.get("committedTo")
        if not name or not isinstance(committed, str) or committed not in fbs_names:
            continue
        candidates.append(row)

    def sort_key(row: dict[str, Any]) -> tuple[float, str, str]:
        ranking = row.get("ranking")
        rank_value = float(ranking) if isinstance(ranking, (int, float)) else 1e12
        return rank_value, normalize_name(resolved_name(row)), str(row.get("id"))

    return sorted(candidates, key=sort_key)


def recruit_collision_examples(
    recruit_rows: list[dict[str, Any]], limit: int = 10
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in recruit_rows:
        key = normalize_name(resolved_name(row))
        if key:
            grouped[key].append(row)

    collisions = []
    for key in sorted(grouped):
        rows = grouped[key]
        if len(rows) < 2:
            continue
        collisions.append(
            {
                "normalized_name": key,
                "row_count": len(rows),
                "records": [
                    {
                        "id": row.get("id"),
                        "name": resolved_name(row),
                        "committedTo": row.get("committedTo"),
                        "position": row.get("position"),
                        "athleteId": row.get("athleteId"),
                    }
                    for row in rows[:5]
                ],
            }
        )
        if len(collisions) >= limit:
            break
    return collisions


def summarize_roster_lookup(
    rows: list[dict[str, Any]], target_name: str, recruit_id: str
) -> dict[str, Any]:
    target = normalize_name(target_name)
    matches = [row for row in rows if normalize_name(resolved_name(row)) == target]
    candidate_ids = sorted(
        {str(row.get("id")) for row in matches if row.get("id") is not None}
    )
    direct_ids = sorted(
        {
            str(row.get("id"))
            for row in matches
            if row.get("id") is not None
            and isinstance(row.get("recruitIds"), list)
            and recruit_id in {str(value) for value in row.get("recruitIds", [])}
        }
    )
    return {
        "candidate_rows": len(matches),
        "candidate_identifiers": candidate_ids,
        "direct_recruit_id_match_identifiers": direct_ids,
        "candidates": [
            {
                "id": row.get("id"),
                "resolved_name": resolved_name(row),
                "team": row.get("team"),
                "position": row.get("position"),
                "jersey": row.get("jersey"),
                "recruitIds": row.get("recruitIds"),
                "provider_year_field": row.get("year"),
            }
            for row in matches[:5]
        ],
    }


def assess_missing_link_case(
    recruit: dict[str, Any], roster_observations: list[dict[str, Any]]
) -> dict[str, Any]:
    recruit_id = str(recruit.get("id"))
    candidate_ids: set[str] = set()
    direct_ids: set[str] = set()

    for observation in roster_observations:
        summary = observation.get("summary")
        if not isinstance(summary, dict):
            continue
        candidate_ids.update(str(value) for value in summary.get("candidate_identifiers", []))
        direct_ids.update(
            str(value)
            for value in summary.get("direct_recruit_id_match_identifiers", [])
        )

    if direct_ids:
        interpretation = "DIRECT_ROSTER_RECRUIT_ID_LINK"
    elif len(candidate_ids) == 1:
        interpretation = "NAME_CONTEXT_ONLY_STABLE_ROSTER_CANDIDATE"
    elif len(candidate_ids) > 1:
        interpretation = "AMBIGUOUS_NAME_COLLISION"
    else:
        interpretation = "UNRESOLVED"

    return {
        "recruit_id": recruit_id,
        "target_name": resolved_name(recruit),
        "committed_to": recruit.get("committedTo"),
        "candidate_roster_identifiers": sorted(candidate_ids),
        "direct_recruit_id_match_identifiers": sorted(direct_ids),
        "identity_interpretation": interpretation,
    }


def probe_year(
    client: CFBDClient,
    year: int,
    max_cases_per_year: int,
) -> dict[str, Any]:
    fbs_result = client.get("/teams/fbs", {"year": year})
    recruit_result = client.get(
        "/recruiting/players", {"year": year, "classification": "HighSchool"}
    )

    out: dict[str, Any] = {
        "fbs_http_status": fbs_result.get("http_status"),
        "fbs_attempts": fbs_result.get("attempts"),
        "recruiting_http_status": recruit_result.get("http_status"),
        "recruiting_attempts": recruit_result.get("attempts"),
    }

    fbs_rows = fbs_result.get("data")
    recruit_rows = recruit_result.get("data")
    if not isinstance(fbs_rows, list) or not isinstance(recruit_rows, list):
        out["error"] = {
            "fbs": fbs_result.get("error"),
            "recruiting": recruit_result.get("error"),
        }
        return out

    fbs_names = extract_fbs_names(fbs_rows)
    candidates = missing_link_candidates(recruit_rows, fbs_names)
    selected = candidates[: max(0, max_cases_per_year)]

    out.update(
        {
            "fbs_unique_programs": len(fbs_names),
            "recruit_rows": len(recruit_rows),
            "athlete_id_null_rows": sum(
                1 for row in recruit_rows if row.get("athleteId") is None
            ),
            "fbs_committed_athlete_id_null_rows": len(candidates),
            "normalized_name_collision_examples": recruit_collision_examples(
                recruit_rows
            ),
            "selected_cases": [],
        }
    )

    for recruit in selected:
        target_name = resolved_name(recruit)
        committed = str(recruit.get("committedTo"))
        recruit_id = str(recruit.get("id"))
        observations = []
        for roster_year in (year, year + 1):
            result = client.get(
                "/roster",
                {
                    "year": roster_year,
                    "team": committed,
                    "classification": "fbs",
                },
            )
            observation: dict[str, Any] = {
                "year": roster_year,
                "team": committed,
                "http_status": result.get("http_status"),
                "attempts": result.get("attempts"),
                "cache_hit": result.get("cache_hit", False),
            }
            rows = result.get("data")
            if isinstance(rows, list):
                observation["summary"] = summarize_roster_lookup(
                    rows, target_name, recruit_id
                )
            else:
                observation["error"] = result.get("error")
            observations.append(observation)

        case = {
            "recruit": {
                "id": recruit.get("id"),
                "name": target_name,
                "committedTo": recruit.get("committedTo"),
                "position": recruit.get("position"),
                "ranking": recruit.get("ranking"),
                "rating": recruit.get("rating"),
                "stars": recruit.get("stars"),
                "athleteId": recruit.get("athleteId"),
            },
            "roster_observations": observations,
        }
        case["linkage_summary"] = assess_missing_link_case(recruit, observations)
        out["selected_cases"].append(case)

    return out


def build_report(
    key: str | None,
    years: list[int],
    max_cases_per_year: int,
    request_delay_seconds: float,
    max_429_retries: int,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "research_only": True,
        "secret_policy": "CFBD_API_KEY is read from the environment only and never emitted",
        "matching_policy": "name matching discovers candidates only; canonical identity is never assigned by this probe",
        "years": years,
        "max_cases_per_year": max_cases_per_year,
        "request_delay_seconds": request_delay_seconds,
        "max_429_retries": max_429_retries,
    }

    if not key:
        report["status"] = "SKIPPED_NO_CFBD_API_KEY"
        return report

    client = CFBDClient(key, request_delay_seconds, max_429_retries)
    report["status"] = "RAN"
    report["results"] = {
        str(year): probe_year(client, year, max_cases_per_year) for year in years
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--years",
        default=",".join(str(value) for value in DEFAULT_YEARS),
        help="comma-separated recruiting years",
    )
    parser.add_argument(
        "--max-cases-per-year", type=int, default=DEFAULT_MAX_CASES_PER_YEAR
    )
    parser.add_argument(
        "--request-delay-seconds",
        type=float,
        default=DEFAULT_REQUEST_DELAY_SECONDS,
    )
    parser.add_argument(
        "--max-429-retries", type=int, default=DEFAULT_MAX_429_RETRIES
    )
    parser.add_argument("--output", help="optional JSON output path; stdout if omitted")
    args = parser.parse_args()

    report = build_report(
        os.getenv("CFBD_API_KEY"),
        parse_int_list(args.years),
        args.max_cases_per_year,
        args.request_delay_seconds,
        args.max_429_retries,
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
