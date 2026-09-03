#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2-B CFBD talent-membership scope probe.

Research/audit tooling only. Compares CFBD season-specific `/talent` team names
against `/teams/fbs` membership using bounded authenticated read-only requests.
The API key is read only from the environment and is never emitted.
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "DAILY_NCAAF_PHASE_B2_CFBD_TALENT_SCOPE_PROBE_V1"
CFBD_BASE = "https://api.collegefootballdata.com"
USER_AGENT = "Daily-NCAAF-Phase-B2B-talent-scope-probe/1.0"
DEFAULT_SEASONS = (2023, 2024, 2025, 2026)
DEFAULT_REQUEST_DELAY = 0.75
DEFAULT_MAX_RETRIES = 3


def parse_csv(raw: str) -> list[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("at least one value is required")
    return values


def parse_int_list(raw: str) -> list[int]:
    return [int(value) for value in parse_csv(raw)]


def fetch_json(
    path: str,
    params: dict[str, Any],
    key: str,
    *,
    timeout: float = 30.0,
    max_retries: int = DEFAULT_MAX_RETRIES,
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

    attempt = 0
    while True:
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read().decode("utf-8")
                return {
                    "http_status": response.status,
                    "data": json.loads(payload),
                    "attempts": attempt + 1,
                }
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                parsed: Any = json.loads(body)
            except json.JSONDecodeError:
                parsed = body[:1000]

            if exc.code == 429 and attempt < max_retries:
                retry_after = exc.headers.get("Retry-After")
                if retry_after:
                    try:
                        delay = max(float(retry_after), 0.0)
                    except ValueError:
                        delay = 2.0 ** attempt
                else:
                    delay = 2.0 ** attempt
                time.sleep(delay)
                attempt += 1
                continue

            return {
                "http_status": exc.code,
                "error": parsed,
                "attempts": attempt + 1,
            }


def extract_fbs_names(rows: list[dict[str, Any]]) -> list[str]:
    return [
        str(row["school"]).strip()
        for row in rows
        if row.get("school") is not None and str(row["school"]).strip()
    ]


def extract_talent_names(rows: list[dict[str, Any]]) -> list[str]:
    return [
        str(row["team"]).strip()
        for row in rows
        if row.get("team") is not None and str(row["team"]).strip()
    ]


def duplicate_count(values: list[str]) -> int:
    return len(values) - len(set(values))


def compare_membership(fbs_names: list[str], talent_names: list[str]) -> dict[str, Any]:
    fbs_set = set(fbs_names)
    talent_set = set(talent_names)
    overlap = fbs_set & talent_set
    missing = sorted(fbs_set - talent_set)
    extra = sorted(talent_set - fbs_set)

    return {
        "fbs_rows_with_name": len(fbs_names),
        "fbs_unique_names": len(fbs_set),
        "fbs_duplicate_name_rows": duplicate_count(fbs_names),
        "talent_rows_with_name": len(talent_names),
        "talent_unique_names": len(talent_set),
        "talent_duplicate_name_rows": duplicate_count(talent_names),
        "exact_name_overlap": len(overlap),
        "fbs_missing_from_talent_count": len(missing),
        "fbs_missing_from_talent": missing,
        "talent_outside_fbs_count": len(extra),
        "talent_outside_fbs": extra,
        "exact_membership_match": not missing and not extra,
    }


def probe_season(
    year: int,
    key: str,
    *,
    request_delay: float,
    max_retries: int,
) -> dict[str, Any]:
    fbs_result = fetch_json(
        "/teams/fbs",
        {"year": year},
        key,
        max_retries=max_retries,
    )
    if request_delay > 0:
        time.sleep(request_delay)

    talent_result = fetch_json(
        "/talent",
        {"year": year},
        key,
        max_retries=max_retries,
    )

    out: dict[str, Any] = {
        "fbs_http_status": fbs_result.get("http_status"),
        "fbs_attempts": fbs_result.get("attempts"),
        "talent_http_status": talent_result.get("http_status"),
        "talent_attempts": talent_result.get("attempts"),
    }

    if fbs_result.get("http_status") != 200 or not isinstance(fbs_result.get("data"), list):
        out["fbs_error"] = fbs_result.get("error", fbs_result.get("data"))
        return out

    if talent_result.get("http_status") != 200 or not isinstance(talent_result.get("data"), list):
        out["talent_error"] = talent_result.get("error", talent_result.get("data"))
        return out

    fbs_rows = fbs_result["data"]
    talent_rows = talent_result["data"]
    fbs_names = extract_fbs_names(fbs_rows)
    talent_names = extract_talent_names(talent_rows)

    out["membership"] = compare_membership(fbs_names, talent_names)
    out["raw_row_counts"] = {
        "fbs_rows": len(fbs_rows),
        "talent_rows": len(talent_rows),
    }
    return out


def build_report(
    seasons: list[int],
    key: str | None,
    *,
    request_delay: float,
    max_retries: int,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "research_only": True,
        "secret_policy": "CFBD_API_KEY is read from the environment only and never emitted",
        "comparison": "exact provider team-name membership; mismatches are surfaced, not auto-normalized",
        "seasons": seasons,
        "request_delay_seconds": request_delay,
        "max_429_retries": max_retries,
    }

    if not key:
        report["status"] = "SKIPPED_NO_CFBD_API_KEY"
        return report

    report["status"] = "RAN"
    results: dict[str, Any] = {}
    for index, year in enumerate(seasons):
        results[str(year)] = probe_season(
            year,
            key,
            request_delay=request_delay,
            max_retries=max_retries,
        )
        if request_delay > 0 and index < len(seasons) - 1:
            time.sleep(request_delay)
    report["results"] = results
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seasons",
        default=",".join(str(value) for value in DEFAULT_SEASONS),
        help="comma-separated season years",
    )
    parser.add_argument(
        "--request-delay",
        type=float,
        default=DEFAULT_REQUEST_DELAY,
        help="seconds to pause between requests; default 0.75",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help="maximum retries after HTTP 429; default 3",
    )
    parser.add_argument("--output", help="optional JSON output path; stdout if omitted")
    args = parser.parse_args()

    if args.request_delay < 0:
        parser.error("--request-delay must be >= 0")
    if args.max_retries < 0:
        parser.error("--max-retries must be >= 0")

    report = build_report(
        parse_int_list(args.seasons),
        os.getenv("CFBD_API_KEY"),
        request_delay=args.request_delay,
        max_retries=args.max_retries,
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
