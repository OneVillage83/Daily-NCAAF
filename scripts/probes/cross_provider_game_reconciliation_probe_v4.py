#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2-C cross-provider game reconciliation probe V4.

Research/audit tooling only.

V4 keeps V3's exact-event, participant-aligned and freshness-aware behavior, and
adds one final conservative orientation rule:

When an exact game ID is already shared by both providers, one participant may
anchor the two-participant orientation by elimination if:
- that participant has strong display-identity evidence on one orientation;
- the opposite orientation has no competing strong participant evidence; and
- the event still contains exactly the provider home/away participant pair.

This resolves provider aliases such as CFBD `Saint Francis` versus ESPN
`St. Francis (PA) Red Flash` without introducing a global hard-coded name alias.
The alignment basis remains explicit in output so anchored evidence is auditable.

CFBD_API_KEY is read from the environment and is never emitted.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROBE_DIR = Path(__file__).resolve().parent
if str(PROBE_DIR) not in sys.path:
    sys.path.insert(0, str(PROBE_DIR))

import cross_provider_game_reconciliation_probe_v3 as v3

CONTRACT_VERSION = "DAILY_NCAAF_PHASE_B2C_CROSS_PROVIDER_GAME_RECONCILIATION_V4"
DEFAULT_SEASONS = v3.DEFAULT_SEASONS
DEFAULT_REQUEST_DELAY_SECONDS = v3.DEFAULT_REQUEST_DELAY_SECONDS
DEFAULT_MAX_429_RETRIES = v3.DEFAULT_MAX_429_RETRIES
MAX_EXAMPLES = v3.MAX_EXAMPLES

# Preserve originals before patching V3's module globals. V3 functions resolve
# their helper names dynamically, allowing V4 to reuse the proven transport,
# asset, comparison and report plumbing without copying it.
_V3_COMPARE_MATCHED_GAME = v3.compare_matched_game
_V3_COMPARE_SEASON = v3.compare_season


def parse_int_list(raw: str) -> list[int]:
    return v3.parse_int_list(raw)


def display_identity_strength(cfbd_name: Any, espn_name: Any) -> int:
    return v3.display_identity_strength(cfbd_name, espn_name)


def orientation_evidence(cfbd: dict[str, Any], espn: dict[str, Any]) -> dict[str, Any]:
    """Return orientation plus the evidence basis used to reach it.

    Display-name evidence orients participants only after exact event-ID equality
    has already established the event candidate. A one-participant anchor never
    creates an event match by itself.
    """
    ch = cfbd.get("homeTeam")
    ca = cfbd.get("awayTeam")
    eh = v3.v2.espn_home_name(espn)
    ea = v3.v2.espn_away_name(espn)

    hh = display_identity_strength(ch, eh)
    aa = display_identity_strength(ca, ea)
    ha = display_identity_strength(ch, ea)
    ah = display_identity_strength(ca, eh)

    same_score = hh + aa
    swapped_score = ha + ah

    # Retain V3's strongest two-participant rule first.
    if same_score >= 4 and same_score > swapped_score:
        return {
            "orientation": "SAME_SIDE",
            "basis": "TWO_PARTICIPANT_DISPLAY_EVIDENCE",
            "strengths": {"home_home": hh, "away_away": aa, "home_away": ha, "away_home": ah},
        }
    if swapped_score >= 4 and swapped_score > same_score:
        return {
            "orientation": "SWAPPED_SIDES",
            "basis": "TWO_PARTICIPANT_DISPLAY_EVIDENCE",
            "strengths": {"home_home": hh, "away_away": aa, "home_away": ha, "away_home": ah},
        }
    if same_score >= 4 and swapped_score >= 4 and same_score == swapped_score:
        return {
            "orientation": "AMBIGUOUS",
            "basis": "COMPETING_TWO_PARTICIPANT_DISPLAY_EVIDENCE",
            "strengths": {"home_home": hh, "away_away": aa, "home_away": ha, "away_home": ah},
        }

    # Exact event ID + one strong participant + no competing opposite-orientation
    # anchor is sufficient to orient a two-participant event by elimination.
    same_anchor_count = int(hh >= 2) + int(aa >= 2)
    swapped_anchor_count = int(ha >= 2) + int(ah >= 2)

    if same_anchor_count >= 1 and swapped_anchor_count == 0:
        return {
            "orientation": "SAME_SIDE",
            "basis": "ONE_PARTICIPANT_EXACT_EVENT_COUNTERPART_ANCHOR",
            "strengths": {"home_home": hh, "away_away": aa, "home_away": ha, "away_home": ah},
        }
    if swapped_anchor_count >= 1 and same_anchor_count == 0:
        return {
            "orientation": "SWAPPED_SIDES",
            "basis": "ONE_PARTICIPANT_EXACT_EVENT_COUNTERPART_ANCHOR",
            "strengths": {"home_home": hh, "away_away": aa, "home_away": ha, "away_home": ah},
        }

    if same_anchor_count >= 1 and swapped_anchor_count >= 1:
        return {
            "orientation": "AMBIGUOUS",
            "basis": "COMPETING_ONE_PARTICIPANT_ANCHORS",
            "strengths": {"home_home": hh, "away_away": aa, "home_away": ha, "away_home": ah},
        }

    return {
        "orientation": "UNRESOLVED",
        "basis": "INSUFFICIENT_PARTICIPANT_DISPLAY_EVIDENCE",
        "strengths": {"home_home": hh, "away_away": aa, "home_away": ha, "away_home": ah},
    }


def infer_side_orientation(cfbd: dict[str, Any], espn: dict[str, Any]) -> str:
    return str(orientation_evidence(cfbd, espn)["orientation"])


def compare_matched_game(cfbd: dict[str, Any], espn: dict[str, Any]) -> dict[str, Any]:
    result = _V3_COMPARE_MATCHED_GAME(cfbd, espn)
    evidence = orientation_evidence(cfbd, espn)
    result["participant_alignment_basis"] = evidence["basis"]
    result["participant_alignment_strengths"] = evidence["strengths"]
    return result


def compare_season(cfbd_rows: list[dict[str, Any]], espn_rows: list[dict[str, Any]]) -> dict[str, Any]:
    result = _V3_COMPARE_SEASON(cfbd_rows, espn_rows)

    cfbd_index, _, _ = v3.v2.build_id_index(
        cfbd_rows, lambda row: v3.normalize_id(row.get("id"))
    )
    espn_index, _, _ = v3.v2.build_id_index(espn_rows, v3.v2.schedule_game_id)
    matched_ids = sorted(set(cfbd_index) & set(espn_index))
    matched = [compare_matched_game(cfbd_index[i], espn_index[i]) for i in matched_ids]

    agreement = result["matched_field_agreement"]
    agreement["participant_alignment_basis_counts"] = v3.state_counts(
        matched, "participant_alignment_basis"
    )
    agreement["counterpart_anchor_examples"] = [
        item
        for item in matched
        if item.get("participant_alignment_basis")
        == "ONE_PARTICIPANT_EXACT_EVENT_COUNTERPART_ANCHOR"
    ][:MAX_EXAMPLES]
    agreement["participant_alignment_note"] = (
        "one-participant counterpart anchoring is allowed only inside an exact-ID matched "
        "two-participant event when the opposite orientation has no competing strong identity evidence"
    )
    return result


# Patch the imported V3 module so its existing derive_team_crosswalk,
# derive_espn_fbs_ids, compare_season callers, build_report and CLI all use V4
# orientation semantics while retaining the proven V3 plumbing.
v3.CONTRACT_VERSION = CONTRACT_VERSION
v3.infer_side_orientation = infer_side_orientation
v3.compare_matched_game = compare_matched_game
v3.compare_season = compare_season

# Public aliases used by tests and callers.
aligned_espn_side = v3.aligned_espn_side
derive_team_crosswalk = v3.derive_team_crosswalk
derive_espn_fbs_ids = v3.derive_espn_fbs_ids
kickoff_bucket_counts = v3.kickoff_bucket_counts
select_schedule_asset = v3.select_schedule_asset
build_report = v3.build_report
main = v3.main


if __name__ == "__main__":
    main()
