#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2-C C5-D compact conference/context classification probe.

Research/audit tooling only.

V3 proved the American Athletic / American Conference naming case but exposed
additional FCS-side conference differences. V4 does two things:

1. adds one more explicitly verified naming equivalence for the Coastal Athletic
   Association (CFBD ``Coastal Athletic`` vs ESPN-native ``Coastal Athletic
   Association`` / ``CAA``); and
2. aggregates *every* residual mismatch signature across the full compared set,
   instead of relying on the V2/V3 example cap.

Residual mismatch signatures are classified conservatively. Big South/OVC joint
association labels are kept as association-model differences rather than forced
aliases. UAC-vs-Southland is retained as a temporal-affiliation conflict candidate.
Unknown signatures remain UNCLASSIFIED.

The full evidence report is written when --output is supplied, while stdout prints
only a compact summary so local review does not require dumping the entire JSON.

CFBD_API_KEY is read from the environment only by the inherited V2 builder and is
never emitted.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROBE_DIR = Path(__file__).resolve().parent
if str(PROBE_DIR) not in sys.path:
    sys.path.insert(0, str(PROBE_DIR))

import cross_provider_context_reconciliation_probe_v2 as v2
import cross_provider_context_reconciliation_probe_v3 as v3
import cross_provider_game_reconciliation_probe_v2 as game_v2

CONTRACT_VERSION = "DAILY_NCAAF_PHASE_B2C_CONTEXT_RECONCILIATION_V4"
DEFAULT_SEASONS = v3.DEFAULT_SEASONS
DEFAULT_REQUEST_DELAY_SECONDS = v3.DEFAULT_REQUEST_DELAY_SECONDS
DEFAULT_MAX_429_RETRIES = v3.DEFAULT_MAX_429_RETRIES

# Preserve the underlying V2 summarizer before build_report() monkey-patches the
# module global. summarize_with_signatures() must call this stable base function,
# not the live v2.summarize attribute, or it recurses into itself.
BASE_V2_SUMMARIZE = v2.summarize

# Explicit, evidence-backed naming equivalence only. This is not a fuzzy matcher.
CONFERENCE_SEMANTIC_EQUIVALENCE: dict[str, str] = {
    **v3.CONFERENCE_SEMANTIC_EQUIVALENCE,
    "coastalathletic": "coastal_athletic_association",
    "coastalathleticassociation": "coastal_athletic_association",
    "caa": "coastal_athletic_association",
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


def residual_mismatch_class(
    cfbd_conference: Any,
    espn_aliases: list[Any] | tuple[Any, ...],
    espn_conference_id: Any,
) -> str:
    """Classify only measured residual patterns; unknowns remain explicit."""
    left = v2.normalize_conference(cfbd_conference)
    right = {
        v2.normalize_conference(value)
        for value in espn_aliases
        if value not in (None, "")
    }
    conference_id = game_v2.normalize_id(espn_conference_id)

    if conference_id == "179" and left in {
        "bigsouthovc",
        "ovcbigsouth",
        "bigsouth",
    } and ({"ohiovalley", "ovc"} & right):
        return "CONFERENCE_ASSOCIATION_MODEL_DIFFERENCE"

    if conference_id == "30" and left == "uac" and ({"southland", "land"} & right):
        return "TEMPORAL_AFFILIATION_CONFLICT_CANDIDATE"

    return "UNCLASSIFIED"


def mismatch_signature(side: dict[str, Any]) -> str:
    aliases = side.get("espn_conference_aliases") or []
    alias_text = " | ".join(str(value) for value in aliases)
    return (
        f"CFBD={side.get('cfbd_conference')} :: "
        f"ESPN_ID={side.get('espn_conference_id')} :: ESPN={alias_text}"
    )


def summarize_with_signatures(rows: list[dict[str, Any]]) -> dict[str, Any]:
    base = BASE_V2_SUMMARIZE(rows)
    signature_counts: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()
    signature_classes: dict[str, str] = {}

    for row in rows:
        for side_name in ("home", "away"):
            side = row.get(side_name, {})
            if side.get("conference_state") != "MISMATCH":
                continue
            signature = mismatch_signature(side)
            classification = residual_mismatch_class(
                side.get("cfbd_conference"),
                side.get("espn_conference_aliases") or [],
                side.get("espn_conference_id"),
            )
            signature_counts[signature] += 1
            class_counts[classification] += 1
            signature_classes[signature] = classification

    base["conference_mismatch_signature_counts"] = dict(sorted(signature_counts.items()))
    base["conference_mismatch_signature_classes"] = {
        key: signature_classes[key] for key in sorted(signature_classes)
    }
    base["conference_mismatch_class_counts"] = dict(sorted(class_counts.items()))
    base["conference_mismatch_total"] = sum(signature_counts.values())
    base["conference_mismatch_unclassified_count"] = class_counts.get("UNCLASSIFIED", 0)
    return base


def compact_summary(report: dict[str, Any]) -> dict[str, Any]:
    seasons: dict[str, Any] = {}
    total_classes: Counter[str] = Counter()
    total_signatures: Counter[str] = Counter()
    total_unclassified = 0

    for season, result in (report.get("season_results") or {}).items():
        context = result.get("context_reconciliation") or {}
        counts = context.get("state_counts") or {}
        classes = context.get("conference_mismatch_class_counts") or {}
        signatures = context.get("conference_mismatch_signature_counts") or {}
        total_classes.update({str(k): int(v) for k, v in classes.items()})
        total_signatures.update({str(k): int(v) for k, v in signatures.items()})
        total_unclassified += int(
            context.get("conference_mismatch_unclassified_count") or 0
        )
        seasons[str(season)] = {
            "status": result.get("status"),
            "exact_id_matches": (result.get("id_reconciliation") or {}).get(
                "exact_id_matches"
            ),
            "cfbd_exact_id_coverage_rate": (result.get("id_reconciliation") or {}).get(
                "cfbd_exact_id_coverage_rate"
            ),
            "missing_referenced_team_metadata_count": (
                result.get("espn_team_season_metadata") or {}
            ).get("missing_referenced_team_metadata_count"),
            "side_orientation": counts.get("side_orientation", {}),
            "home_external_team_id_state": counts.get(
                "home_external_team_id_state", {}
            ),
            "away_external_team_id_state": counts.get(
                "away_external_team_id_state", {}
            ),
            "home_division_state": counts.get("home_division_state", {}),
            "away_division_state": counts.get("away_division_state", {}),
            "home_conference_state": counts.get("home_conference_state", {}),
            "away_conference_state": counts.get("away_conference_state", {}),
            "conference_mismatch_class_counts": classes,
            "conference_mismatch_signature_counts": signatures,
            "conference_mismatch_unclassified_count": context.get(
                "conference_mismatch_unclassified_count", 0
            ),
        }

    return {
        "contract_version": report.get("contract_version"),
        "status": report.get("status"),
        "seasons": seasons,
        "aggregate": {
            "conference_mismatch_class_counts": dict(sorted(total_classes.items())),
            "conference_mismatch_signature_counts": dict(
                sorted(total_signatures.items())
            ),
            "conference_mismatch_unclassified_count": total_unclassified,
        },
        "freeze_gate": (
            "C5 may freeze only if external team IDs/divisions remain conflict-free, "
            "referenced team metadata is complete, and every residual conference mismatch "
            "signature is explicitly classified; classified source-semantic or historical-"
            "metadata conflicts are retained as evidence rather than coerced into equality."
        ),
    }


def build_report(
    *,
    seasons: list[int] | tuple[int, ...] = DEFAULT_SEASONS,
    request_delay_seconds: float = DEFAULT_REQUEST_DELAY_SECONDS,
    max_429_retries: int = DEFAULT_MAX_429_RETRIES,
) -> dict[str, Any]:
    original_compare = v2.compare_conference_alias
    original_summarize = v2.summarize
    try:
        v2.compare_conference_alias = compare_conference_alias
        v2.summarize = summarize_with_signatures
        report = v2.build_report(
            seasons=seasons,
            request_delay_seconds=request_delay_seconds,
            max_429_retries=max_429_retries,
        )
    finally:
        v2.compare_conference_alias = original_compare
        v2.summarize = original_summarize

    report["contract_version"] = CONTRACT_VERSION
    report["conference_semantic_alias_policy"] = {
        "mode": "EXPLICIT_ENUMERATED_EQUIVALENCE_ONLY",
        "equivalence_groups": {
            "american_athletic": [
                "American Athletic",
                "American Conference",
                "American",
            ],
            "coastal_athletic_association": [
                "Coastal Athletic",
                "Coastal Athletic Association",
                "CAA",
            ],
        },
        "rule": "no fuzzy matching; residual differences remain mismatches",
    }
    report["residual_mismatch_classification_policy"] = {
        "CONFERENCE_ASSOCIATION_MODEL_DIFFERENCE": (
            "Big South/OVC joint-association label versus ESPN OVC umbrella metadata"
        ),
        "TEMPORAL_AFFILIATION_CONFLICT_CANDIDATE": (
            "season-specific affiliation differs from ESPN team-season metadata and must not be aliased"
        ),
        "UNCLASSIFIED": "no measured rule applies; blocks C5 freeze",
    }
    report["compact_summary"] = compact_summary(report)
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
    parser.add_argument(
        "--max-429-retries", type=int, default=DEFAULT_MAX_429_RETRIES
    )
    args = parser.parse_args()

    report = build_report(
        seasons=parse_int_list(args.seasons),
        request_delay_seconds=args.request_delay_seconds,
        max_429_retries=args.max_429_retries,
    )
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(
        json.dumps(
            report.get("compact_summary", compact_summary(report)),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
