#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2-C C5-C conference-semantic reconciliation probe.

Research/audit tooling only.

C5-B measured perfect participant external-ID and division agreement across the
2023-2025 completed-season window, but every emitted conference mismatch example
was the same naming-semantic case: CFBD ``American Athletic`` versus ESPN-native
``American Conference`` / ``American`` for conference id 151.

V3 preserves the V2 source/provenance/venue rules and adds one explicit semantic
conference-equivalence layer so a known provider naming difference is not counted
as an affiliation conflict. The layer is deliberately tiny and enumerated; it is
not a fuzzy matcher and it does not silently collapse unknown labels.

CFBD_API_KEY is still read from the environment only by the V2 report builder and
is never emitted.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROBE_DIR = Path(__file__).resolve().parent
if str(PROBE_DIR) not in sys.path:
    sys.path.insert(0, str(PROBE_DIR))

import cross_provider_context_reconciliation_probe_v2 as v2

CONTRACT_VERSION = "DAILY_NCAAF_PHASE_B2C_CONTEXT_RECONCILIATION_V3"
DEFAULT_SEASONS = v2.DEFAULT_SEASONS
DEFAULT_REQUEST_DELAY_SECONDS = v2.DEFAULT_REQUEST_DELAY_SECONDS
DEFAULT_MAX_429_RETRIES = v2.DEFAULT_MAX_429_RETRIES

# Explicit semantic equivalence only. Do not expand this table without measured
# evidence and a documented reason.
CONFERENCE_SEMANTIC_EQUIVALENCE: dict[str, str] = {
    "americanathletic": "american_athletic",
    "americanconference": "american_athletic",
    "american": "american_athletic",
}


def parse_int_list(raw: str) -> list[int]:
    return v2.parse_int_list(raw)


def canonical_conference_token(value: Any) -> str | None:
    token = v2.normalize_conference(value)
    if token is None:
        return None
    return CONFERENCE_SEMANTIC_EQUIVALENCE.get(token, token)


def compare_conference_alias(
    cfbd_value: Any, team_row: dict[str, Any] | None
) -> tuple[str, list[str]]:
    """Compare conference labels with exact, normalized, then explicit semantic aliases."""
    if team_row is None:
        return "UNAVAILABLE_TEAM_METADATA", []

    aliases = v2.conference_aliases(team_row)
    if not aliases:
        return "UNAVAILABLE_ESPN_CONFERENCE", []

    cfbd_text = None if cfbd_value in (None, "") else str(cfbd_value).strip()
    if cfbd_text is None:
        return "UNAVAILABLE_CFBD_CONFERENCE", aliases

    if any(cfbd_text == alias for alias in aliases):
        return "EXACT_ALIAS_MATCH", aliases

    normalized_target = v2.normalize_conference(cfbd_text)
    if normalized_target and any(
        v2.normalize_conference(alias) == normalized_target for alias in aliases
    ):
        return "NORMALIZED_ALIAS_MATCH", aliases

    semantic_target = canonical_conference_token(cfbd_text)
    if semantic_target and any(
        canonical_conference_token(alias) == semantic_target for alias in aliases
    ):
        return "SEMANTIC_ALIAS_MATCH", aliases

    return "MISMATCH", aliases


def build_report(
    *,
    seasons: list[int] | tuple[int, ...] = DEFAULT_SEASONS,
    request_delay_seconds: float = DEFAULT_REQUEST_DELAY_SECONDS,
    max_429_retries: int = DEFAULT_MAX_429_RETRIES,
) -> dict[str, Any]:
    """Run the V2 report with only the conference comparison function overridden."""
    original_compare = v2.compare_conference_alias
    try:
        v2.compare_conference_alias = compare_conference_alias
        report = v2.build_report(
            seasons=seasons,
            request_delay_seconds=request_delay_seconds,
            max_429_retries=max_429_retries,
        )
    finally:
        v2.compare_conference_alias = original_compare

    report["contract_version"] = CONTRACT_VERSION
    report["conference_semantic_alias_policy"] = {
        "mode": "EXPLICIT_ENUMERATED_EQUIVALENCE_ONLY",
        "equivalence_groups": {
            "american_athletic": [
                "American Athletic",
                "American Conference",
                "American",
            ]
        },
        "rule": (
            "semantic aliases are measured provider-label equivalences only; "
            "unknown labels remain mismatches and no fuzzy matching is allowed"
        ),
    }
    return report


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
