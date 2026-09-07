#!/usr/bin/env python3
"""Daily-NCAAF Phase B.2-C cross-provider game reconciliation probe V3.

Research/audit tooling only.

V3 corrects two V2 assumptions:
- provider home/away sides are not identity and may be swapped for the same event;
- asset freshness outranks file-format preference when multiple supported season assets exist.

It imports the V2 transport/decoding helpers but performs participant-aligned
identity, score, team-crosswalk, and event-universe reconciliation itself.

CFBD_API_KEY is read from the environment and is never emitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROBE_DIR = Path(__file__).resolve().parent
if str(PROBE_DIR) not in sys.path:
    sys.path.insert(0, str(PROBE_DIR))

import cross_provider_game_reconciliation_probe_v2 as v2

CONTRACT_VERSION = "DAILY_NCAAF_PHASE_B2C_CROSS_PROVIDER_GAME_RECONCILIATION_V3"
DEFAULT_SEASONS = (2024, 2026)
DEFAULT_REQUEST_DELAY_SECONDS = v2.DEFAULT_REQUEST_DELAY_SECONDS
DEFAULT_MAX_429_RETRIES = v2.DEFAULT_MAX_429_RETRIES
MAX_EXAMPLES = v2.MAX_EXAMPLES

IDENTITY_STATES = {
    "EXACT",
    "NORMALIZED",
    "CFBD_NAME_PREFIX_OF_ESPN_DISPLAY",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_int_list(raw: str) -> list[int]:
    return v2.parse_int_list(raw)


def normalize_id(value: Any) -> str | None:
    return v2.normalize_id(value)


def parse_datetime(value: Any) -> datetime | None:
    return v2.parse_datetime(value)


def asset_timestamp(asset: dict[str, Any]) -> datetime:
    for field in ("updated_at", "created_at"):
        parsed = parse_datetime(asset.get(field))
        if parsed is not None:
            return parsed
    return datetime.min.replace(tzinfo=timezone.utc)


def schedule_asset_rank(name: str) -> int:
    if name.endswith(".csv.gz"):
        return 0
    if name.endswith(".csv"):
        return 1
    return 99


def select_schedule_asset(manifest: dict[str, Any], season: int) -> dict[str, Any] | None:
    """Choose the newest supported season asset; format rank breaks timestamp ties."""
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        return None
    prefix = f"cfb_schedule_{season}."
    candidates = [
        item
        for item in assets
        if isinstance(item, dict)
        and str(item.get("name", "")).startswith(prefix)
        and schedule_asset_rank(str(item.get("name", ""))) < 99
        and item.get("browser_download_url")
    ]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda item: (
            asset_timestamp(item),
            -schedule_asset_rank(str(item.get("name", ""))),
            str(item.get("name", "")),
        ),
        reverse=True,
    )[0]


def display_identity_strength(cfbd_name: Any, espn_name: Any) -> int:
    state = v2.compare_display_names(cfbd_name, espn_name)
    if state in {"EXACT", "NORMALIZED"}:
        return 3
    if state == "CFBD_NAME_PREFIX_OF_ESPN_DISPLAY":
        return 2
    return 0


def infer_side_orientation(cfbd: dict[str, Any], espn: dict[str, Any]) -> str:
    """Infer whether provider participant sides are aligned or swapped.

    Exact game-ID equality establishes the event candidate. Display text is used
    only to orient the two participants inside that already matched event; it is
    not used to create a game identity.
    """
    ch = cfbd.get("homeTeam")
    ca = cfbd.get("awayTeam")
    eh = v2.espn_home_name(espn)
    ea = v2.espn_away_name(espn)

    same_score = display_identity_strength(ch, eh) + display_identity_strength(ca, ea)
    swapped_score = display_identity_strength(ch, ea) + display_identity_strength(ca, eh)

    if same_score >= 4 and same_score > swapped_score:
        return "SAME_SIDE"
    if swapped_score >= 4 and swapped_score > same_score:
        return "SWAPPED_SIDES"
    if same_score >= 4 and swapped_score >= 4 and same_score == swapped_score:
        return "AMBIGUOUS"
    return "UNRESOLVED"


def aligned_espn_side(espn: dict[str, Any], cfbd_side: str, orientation: str) -> dict[str, Any]:
    if cfbd_side not in {"home", "away"}:
        raise ValueError("cfbd_side must be home or away")
    if orientation == "SAME_SIDE":
        espn_side = cfbd_side
    elif orientation == "SWAPPED_SIDES":
        espn_side = "away" if cfbd_side == "home" else "home"
    else:
        return {"side": None, "id": None, "name": None, "score": None}

    if espn_side == "home":
        return {
            "side": "home",
            "id": v2.espn_home_id(espn),
            "name": v2.espn_home_name(espn),
            "score": v2.espn_home_score(espn),
        }
    return {
        "side": "away",
        "id": v2.espn_away_id(espn),
        "name": v2.espn_away_name(espn),
        "score": v2.espn_away_score(espn),
    }


def compare_matched_game(cfbd: dict[str, Any], espn: dict[str, Any]) -> dict[str, Any]:
    orientation = infer_side_orientation(cfbd, espn)

    cfbd_week = v2.parse_int(cfbd.get("week"))
    espn_week = v2.espn_week(espn)
    if cfbd_week is None or espn_week is None:
        week_state = "UNAVAILABLE"
    else:
        week_state = "MATCH" if cfbd_week == espn_week else "MISMATCH"

    cfbd_start = v2.parse_datetime(cfbd.get("startDate"))
    espn_start = v2.espn_start(espn)
    kickoff_delta_seconds: float | None = None
    if cfbd_start is None or espn_start is None:
        kickoff_state = "UNAVAILABLE"
    else:
        kickoff_delta_seconds = abs((cfbd_start - espn_start).total_seconds())
        kickoff_state = "MATCH" if kickoff_delta_seconds <= 60 else "MISMATCH"

    cfbd_home_score = v2.parse_float(cfbd.get("homePoints"))
    cfbd_away_score = v2.parse_float(cfbd.get("awayPoints"))
    aligned_home = aligned_espn_side(espn, "home", orientation)
    aligned_away = aligned_espn_side(espn, "away", orientation)

    if orientation not in {"SAME_SIDE", "SWAPPED_SIDES"}:
        score_state = "UNRESOLVED_ORIENTATION"
    elif None in (
        cfbd_home_score,
        cfbd_away_score,
        aligned_home["score"],
        aligned_away["score"],
    ):
        score_state = "UNAVAILABLE"
    else:
        score_state = (
            "MATCH"
            if cfbd_home_score == aligned_home["score"]
            and cfbd_away_score == aligned_away["score"]
            else "MISMATCH"
        )

    cfbd_completed = v2.parse_bool(cfbd.get("completed"))
    espn_completed = v2.espn_completed(espn)
    if cfbd_completed is None or espn_completed is None:
        lifecycle_state = "UNAVAILABLE"
    else:
        lifecycle_state = "MATCH" if cfbd_completed == espn_completed else "MISMATCH"

    return {
        "game_id": normalize_id(cfbd.get("id")),
        "side_orientation": orientation,
        "week_state": week_state,
        "kickoff_state": kickoff_state,
        "kickoff_delta_seconds": kickoff_delta_seconds,
        "score_state": score_state,
        "lifecycle_state": lifecycle_state,
        "cfbd_home_display_state_aligned": v2.compare_display_names(
            cfbd.get("homeTeam"), aligned_home.get("name")
        ),
        "cfbd_away_display_state_aligned": v2.compare_display_names(
            cfbd.get("awayTeam"), aligned_away.get("name")
        ),
        "cfbd": {
            "week": cfbd_week,
            "start_date": cfbd.get("startDate"),
            "home_team": cfbd.get("homeTeam"),
            "away_team": cfbd.get("awayTeam"),
            "home_points": cfbd.get("homePoints"),
            "away_points": cfbd.get("awayPoints"),
            "completed": cfbd.get("completed"),
            "neutral_site": cfbd.get("neutralSite"),
            "season_type": cfbd.get("seasonType"),
            "home_classification": cfbd.get("homeClassification"),
            "away_classification": cfbd.get("awayClassification"),
        },
        "espn": {
            "week": espn_week,
            "start_date": v2.first_value(
                espn, ("game_date", "start_date", "startDate", "date")
            ),
            "home_id": v2.espn_home_id(espn),
            "away_id": v2.espn_away_id(espn),
            "home_team": v2.espn_home_name(espn),
            "away_team": v2.espn_away_name(espn),
            "home_score": v2.espn_home_score(espn),
            "away_score": v2.espn_away_score(espn),
            "status": v2.espn_status(espn),
            "completed_interpretation": espn_completed,
            "neutral_site": v2.parse_bool(espn.get("neutral_site")),
            "season_type": espn.get("season_type"),
        },
        "aligned_participants": {
            "cfbd_home_to_espn": aligned_home,
            "cfbd_away_to_espn": aligned_away,
        },
    }


def derive_team_crosswalk(
    cfbd_index: dict[str, dict[str, Any]],
    espn_index: dict[str, dict[str, Any]],
    matched_ids: list[str],
) -> dict[str, Any]:
    cfbd_to_espn: dict[str, dict[str, Any]] = {}
    espn_to_cfbd: dict[str, set[str]] = defaultdict(set)
    observations = 0
    skipped_unresolved = 0

    for game_id in matched_ids:
        cfbd = cfbd_index[game_id]
        espn = espn_index[game_id]
        orientation = infer_side_orientation(cfbd, espn)
        if orientation not in {"SAME_SIDE", "SWAPPED_SIDES"}:
            skipped_unresolved += 1
            continue

        for side in ("home", "away"):
            cfbd_name = cfbd.get("homeTeam" if side == "home" else "awayTeam")
            aligned = aligned_espn_side(espn, side, orientation)
            espn_id = aligned.get("id")
            espn_name = aligned.get("name")
            if cfbd_name in (None, "") or espn_id is None:
                continue
            observations += 1
            key = str(cfbd_name)
            entry = cfbd_to_espn.setdefault(
                key,
                {"espn_ids": set(), "espn_display_names": set(), "observations": 0},
            )
            entry["espn_ids"].add(espn_id)
            if espn_name not in (None, ""):
                entry["espn_display_names"].add(str(espn_name))
            entry["observations"] += 1
            espn_to_cfbd[espn_id].add(key)

    rendered: dict[str, Any] = {}
    cfbd_conflicts: list[dict[str, Any]] = []
    for name, entry in sorted(cfbd_to_espn.items()):
        ids = sorted(entry["espn_ids"])
        displays = sorted(entry["espn_display_names"])
        rendered[name] = {
            "espn_ids": ids,
            "espn_display_names": displays,
            "observations": entry["observations"],
        }
        if len(ids) > 1:
            cfbd_conflicts.append(
                {"cfbd_team": name, "espn_ids": ids, "espn_display_names": displays}
            )

    espn_conflicts = [
        {"espn_id": identifier, "cfbd_names": sorted(names)}
        for identifier, names in sorted(espn_to_cfbd.items())
        if len(names) > 1
    ]

    return {
        "derivation": "participant-aligned pairing inside exact matched game IDs",
        "identity_strength": "strong provider crosswalk evidence; not canonical identity",
        "participant_observations": observations,
        "matched_games_skipped_for_unresolved_orientation": skipped_unresolved,
        "unique_cfbd_team_names": len(rendered),
        "unique_espn_team_ids": len(espn_to_cfbd),
        "cfbd_name_to_multiple_espn_id_conflict_count": len(cfbd_conflicts),
        "espn_id_to_multiple_cfbd_name_conflict_count": len(espn_conflicts),
        "cfbd_conflict_examples": cfbd_conflicts[:MAX_EXAMPLES],
        "espn_conflict_examples": espn_conflicts[:MAX_EXAMPLES],
        "crosswalk": rendered,
    }


def derive_espn_fbs_ids(
    cfbd_index: dict[str, dict[str, Any]],
    espn_index: dict[str, dict[str, Any]],
    matched_ids: list[str],
) -> set[str]:
    result: set[str] = set()
    for game_id in matched_ids:
        cfbd = cfbd_index[game_id]
        espn = espn_index[game_id]
        orientation = infer_side_orientation(cfbd, espn)
        if orientation not in {"SAME_SIDE", "SWAPPED_SIDES"}:
            continue
        if str(cfbd.get("homeClassification", "")).lower() == "fbs":
            identifier = aligned_espn_side(espn, "home", orientation).get("id")
            if identifier:
                result.add(identifier)
        if str(cfbd.get("awayClassification", "")).lower() == "fbs":
            identifier = aligned_espn_side(espn, "away", orientation).get("id")
            if identifier:
                result.add(identifier)
    return result


def state_counts(items: list[dict[str, Any]], field: str) -> dict[str, int]:
    return v2.state_counts(items, field)


def mismatch_examples(items: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    return [item for item in items if item.get(field) == "MISMATCH"][:MAX_EXAMPLES]


def orientation_examples(items: list[dict[str, Any]], state: str) -> list[dict[str, Any]]:
    return [item for item in items if item.get("side_orientation") == state][:MAX_EXAMPLES]


def kickoff_bucket(seconds: float | None) -> str:
    if seconds is None:
        return "UNAVAILABLE"
    if seconds <= 60:
        return "LE_60S"
    if seconds <= 300:
        return "GT_60S_LE_5M"
    if seconds <= 1800:
        return "GT_5M_LE_30M"
    if seconds <= 7200:
        return "GT_30M_LE_2H"
    return "GT_2H"


def kickoff_bucket_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        key = kickoff_bucket(item.get("kickoff_delta_seconds"))
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def special_status_examples(
    cfbd_index: dict[str, dict[str, Any]],
    espn_index: dict[str, dict[str, Any]],
    matched_ids: list[str],
) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for game_id in matched_ids:
        espn = espn_index[game_id]
        status = v2.espn_status(espn)
        if status is None:
            continue
        token = re.sub(r"[^a-z0-9]+", "", status.lower())
        if not any(word in token for word in ("cancel", "postpon", "delay", "progress")):
            continue
        cfbd = cfbd_index[game_id]
        examples.append(
            {
                "game_id": game_id,
                "cfbd_completed": cfbd.get("completed"),
                "cfbd_home_team": cfbd.get("homeTeam"),
                "cfbd_away_team": cfbd.get("awayTeam"),
                "espn_status": status,
                "espn_home_team": v2.espn_home_name(espn),
                "espn_away_team": v2.espn_away_name(espn),
            }
        )
        if len(examples) >= MAX_EXAMPLES:
            break
    return examples


def compare_season(cfbd_rows: list[dict[str, Any]], espn_rows: list[dict[str, Any]]) -> dict[str, Any]:
    cfbd_index, cfbd_non_null, cfbd_duplicates = v2.build_id_index(
        cfbd_rows, lambda row: normalize_id(row.get("id"))
    )
    espn_index, espn_non_null, espn_duplicates = v2.build_id_index(
        espn_rows, v2.schedule_game_id
    )

    cfbd_ids = set(cfbd_index)
    espn_ids = set(espn_index)
    matched_ids = sorted(cfbd_ids & espn_ids)
    cfbd_only_ids = sorted(cfbd_ids - espn_ids)
    espn_only_ids = sorted(espn_ids - cfbd_ids)

    matched = [compare_matched_game(cfbd_index[i], espn_index[i]) for i in matched_ids]
    crosswalk = derive_team_crosswalk(cfbd_index, espn_index, matched_ids)
    derived_fbs_espn_ids = derive_espn_fbs_ids(cfbd_index, espn_index, matched_ids)

    espn_fbs_involved_ids = {
        identifier
        for identifier, row in espn_index.items()
        if v2.espn_home_id(row) in derived_fbs_espn_ids
        or v2.espn_away_id(row) in derived_fbs_espn_ids
    }

    if espn_ids and espn_ids < cfbd_ids:
        snapshot_relation = "ESPN_EVENT_SET_STRICT_SUBSET_OF_CFBD_AT_ACQUISITION"
    elif cfbd_ids and cfbd_ids < espn_ids:
        snapshot_relation = "CFBD_EVENT_SET_STRICT_SUBSET_OF_ESPN_AT_ACQUISITION"
    elif espn_ids == cfbd_ids:
        snapshot_relation = "RAW_EVENT_SETS_EQUAL"
    else:
        snapshot_relation = "PARTIAL_OVERLAP_OR_DIFFERENT_UNIVERSES"

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
        "snapshot_relation": {
            "state": snapshot_relation,
            "warning": (
                "strict subset relationships are acquisition-state observations; they are not "
                "historical coverage-failure classifications"
            ),
        },
        "id_reconciliation": {
            "exact_id_matches": len(matched_ids),
            "cfbd_exact_id_overlap_rate_at_acquisition": (
                round(len(matched_ids) / len(cfbd_ids), 6) if cfbd_ids else None
            ),
            "cfbd_only_count_at_acquisition": len(cfbd_only_ids),
            "espn_only_count_at_acquisition": len(espn_only_ids),
            "cfbd_only_examples": [
                v2.compact_cfbd_example(cfbd_index[i])
                for i in cfbd_only_ids[:MAX_EXAMPLES]
            ],
            "espn_only_examples": [
                v2.compact_espn_example(espn_index[i])
                for i in espn_only_ids[:MAX_EXAMPLES]
            ],
        },
        "provider_team_crosswalk": crosswalk,
        "normalized_event_universe": {
            "status": "DERIVED_FROM_PARTICIPANT_ALIGNED_EXACT_MATCH_CROSSWALK",
            "method": (
                "infer participant orientation inside exact-ID matched games; derive ESPN FBS "
                "team IDs from aligned CFBD FBS participants; classify ESPN events by those IDs"
            ),
            "derived_espn_fbs_team_ids": len(derived_fbs_espn_ids),
            "espn_fbs_involved_event_ids_at_acquisition": len(espn_fbs_involved_ids),
            "exact_overlap_with_cfbd": len(cfbd_ids & espn_fbs_involved_ids),
            "cfbd_only_after_normalization_at_acquisition": len(
                cfbd_ids - espn_fbs_involved_ids
            ),
            "espn_only_after_normalization_at_acquisition": len(
                espn_fbs_involved_ids - cfbd_ids
            ),
            "espn_only_after_normalization_examples": [
                v2.compact_espn_example(espn_index[i])
                for i in sorted(espn_fbs_involved_ids - cfbd_ids)[:MAX_EXAMPLES]
            ],
            "warning": (
                "for current/partial assets, normalized counts remain snapshot-state evidence and "
                "must not be interpreted as final provider coverage"
            ),
        },
        "matched_field_agreement": {
            "matched_games": len(matched),
            "side_orientation_counts": state_counts(matched, "side_orientation"),
            "swapped_side_examples": orientation_examples(matched, "SWAPPED_SIDES"),
            "unresolved_orientation_examples": orientation_examples(matched, "UNRESOLVED"),
            "week_state_counts": state_counts(matched, "week_state"),
            "kickoff_state_counts": state_counts(matched, "kickoff_state"),
            "kickoff_delta_bucket_counts": kickoff_bucket_counts(matched),
            "score_state_counts": state_counts(matched, "score_state"),
            "lifecycle_state_counts": state_counts(matched, "lifecycle_state"),
            "week_mismatch_examples": mismatch_examples(matched, "week_state"),
            "kickoff_mismatch_examples": mismatch_examples(matched, "kickoff_state"),
            "score_mismatch_examples": mismatch_examples(matched, "score_state"),
            "lifecycle_mismatch_examples": mismatch_examples(matched, "lifecycle_state"),
            "special_status_examples": special_status_examples(
                cfbd_index, espn_index, matched_ids
            ),
            "kickoff_semantic_note": (
                "kickoff disagreement is retained as source-time evidence; scheduled/revised/actual "
                "start semantics are not silently collapsed"
            ),
        },
    }


def advertised_digest_matches(asset: dict[str, Any], actual_sha256: str | None) -> bool | None:
    return v2.advertised_digest_matches(asset, actual_sha256)


def build_report(
    seasons: list[int],
    key: str | None,
    *,
    request_delay_seconds: float,
    max_429_retries: int,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "generated_at": utc_now(),
        "research_only": True,
        "secret_policy": "CFBD_API_KEY is read from the environment only and never emitted",
        "seasons": seasons,
        "request_delay_seconds": request_delay_seconds,
        "max_429_retries": max_429_retries,
        "comparison_policy": (
            "exact game IDs establish event candidates; participants are then aligned independent "
            "of provider home/away side; freshest supported manifest asset is selected"
        ),
    }
    if not key:
        report["status"] = "SKIPPED_NO_CFBD_API_KEY"
        return report

    manifest_acquired_at = utc_now()
    manifest_result = v2.fetch_json(
        v2.SPORTSDATAVERSE_RELEASE_API,
        max_429_retries=max_429_retries,
    )
    manifest = manifest_result.get("data")
    report["sportsdataverse_release_manifest"] = {
        "http_status": manifest_result.get("http_status"),
        "attempts": manifest_result.get("attempts"),
        "acquired_at": manifest_acquired_at,
        "source_url": v2.SPORTSDATAVERSE_RELEASE_API,
        "release_updated_at": manifest.get("updated_at") if isinstance(manifest, dict) else None,
        "asset_count": len(manifest.get("assets", [])) if isinstance(manifest, dict) else None,
    }

    if manifest_result.get("http_status") != 200 or not isinstance(manifest, dict):
        report["status"] = "SPORTSDATAVERSE_MANIFEST_ERROR"
        report["sportsdataverse_release_manifest"]["error"] = manifest
        return report

    report["status"] = "RAN"
    report["results"] = {}

    for index, season in enumerate(seasons):
        season_entry: dict[str, Any] = {}

        cfbd_acquired_at = utc_now()
        cfbd = v2.cfbd_games(season, key, max_429_retries)
        season_entry["cfbd"] = {
            "http_status": cfbd.get("http_status"),
            "attempts": cfbd.get("attempts"),
            "acquired_at": cfbd_acquired_at,
            "query_scope": {"year": season, "seasonType": "both", "classification": "fbs"},
        }

        if request_delay_seconds > 0:
            time.sleep(request_delay_seconds)

        asset = select_schedule_asset(manifest, season)
        if asset is None:
            season_entry["status"] = "SPORTSDATAVERSE_ASSET_NOT_FOUND"
            report["results"][str(season)] = season_entry
            continue

        source_url = str(asset.get("browser_download_url"))
        sd_acquired_at = utc_now()
        sd = v2.fetch_bytes(source_url, max_429_retries=max_429_retries)
        raw_asset = sd.get("data", b"")
        actual_sha256 = hashlib.sha256(raw_asset).hexdigest() if raw_asset else None
        season_entry["sportsdataverse"] = {
            "http_status": sd.get("http_status"),
            "attempts": sd.get("attempts"),
            "acquired_at": sd_acquired_at,
            "asset_name": asset.get("name"),
            "asset_created_at": asset.get("created_at"),
            "asset_updated_at": asset.get("updated_at"),
            "asset_selection_policy": "newest supported asset; format rank only breaks timestamp ties",
            "source_url": source_url,
            "byte_count": len(raw_asset),
            "sha256": actual_sha256,
            "advertised_digest": asset.get("digest"),
            "advertised_digest_matches": advertised_digest_matches(asset, actual_sha256),
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
            espn_rows = v2.decode_schedule_asset(raw_asset, str(asset.get("name")))
        except (OSError, UnicodeDecodeError, ValueError) as exc:
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
