# B.2-C C6 — Selected Play-Level Reconciliation Plan V1

Status: **ACTIVE — C6-A**  
Date: 2026-09-07

## Objective

Establish how safely a selected set of CollegeFootballData historical `/plays` rows can be reconciled to ESPN-native play-by-play for the same already-frozen game identities.

C6 is not a model-building step and does not make either source point-in-time safe. It is a delivery-path/identifier/semantic reconciliation audit.

## Provenance

The governing B.2-C provenance addendum still applies. CFBD and the selected ESPN path are not treated as independent upstream corroboration.

Second path for C6-A:

```text
ESPN site-v2 game summary play-by-play
https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event=<GAME_ID>
```

The current cfbfastR implementation documents the same ESPN summary endpoint for its legacy ESPN CFB play-by-play path, while current cfbfastR also exposes core-v2 game play endpoints.

## Why C6 starts with exact play IDs

C1 proved exact game IDs and participant orientation. C6 must now test whether play IDs are also directly compatible.

The first rule is therefore:

```text
exact PLAY_ID equality
    before
semantic field comparison
```

If exact play-ID overlap is insufficient, a later bounded pass may evaluate composite alignment. C6-A must not invent such alignment in advance.

## Selected games

Initial deterministic cases:

```text
401520375  2023 reference game used by current ESPN/cfbfastR PBP tests
401628339  2024 FBS-v-FCS reference game used by current ESPN/cfbfastR tests
401628459  2024 regular-season context case
401677085  2024 postseason event with frozen C1 SWAPPED_SIDES orientation
401677093  2024 postseason event with frozen C1 SWAPPED_SIDES orientation
401754516  2025 regular-season Stanford/Hawai'i context case
```

The probe resolves authoritative season/week/seasonType from CFBD `/games?id=...` before requesting historical `/plays`.

## CFBD acquisition constraint

Current CFBD `/plays` requires `year` and `week` rather than `gameId`. C6 therefore:

1. resolves the target game metadata;
2. fetches the corresponding FBS-involved week/seasonType play universe;
3. filters locally to the exact frozen game ID.

No API key value is emitted. `CFBD_API_KEY` is read from the environment only.

## Play-ID reconciliation states

Per game:

```text
cfbd_unique_play_ids
espn_unique_play_ids
exact_shared_play_ids
cfbd_only_play_ids
espn_only_play_ids
cfbd_exact_id_overlap_rate
espn_exact_id_overlap_rate
duplicate_play_ids per path
```

Provider-only plays remain provider-only evidence. They are not silently paired by row number, sequence number, clock or text.

## Semantic comparisons on exact shared IDs only

C6-A compares:

```text
period
clock seconds
down
distance
yards to goal
scoring flag
play type text
play text
```

States are explicit:

```text
MATCH
MISMATCH
UNAVAILABLE_BOTH
UNAVAILABLE_ONE_SIDE
```

Text comparison additionally distinguishes:

```text
EXACT
NORMALIZED
MISMATCH
UNAVAILABLE_BOTH
UNAVAILABLE_ONE_SIDE
```

No semantic field is used to repair identity in this pass.

## Required output

The full local JSON retains:

```text
acquired_at
HTTP status
request metadata
per-path row counts
exact-ID sets/counts
field-state counts
bounded mismatch examples
raw-source endpoint provenance
```

The terminal output is a compact summary so the user does not need to paste the full artifact.

## C6-A decision gate

C6-A may become a freeze candidate if the selected cases show:

1. no duplicate play IDs on either path, or every duplicate is explicitly explained;
2. high exact play-ID overlap on every completed selected game;
3. provider-only play rows are bounded and surfaced;
4. core state fields on shared IDs are overwhelmingly compatible or differences are semantically classified;
5. play text/type differences are not promoted to identity failures;
6. no row-order or name-only heuristic is required to force reconciliation.

If exact play IDs are not sufficiently compatible, C6 proceeds to a bounded C6-B composite-alignment study rather than weakening the identity contract.

## Frozen constraints carried forward

```text
provider PLAY_ID != canonical PLAY_ID by assumption
row sequence != identity
clock alone != identity
play text alone != identity
cross-delivery match != PIT-safe
historical final PBP != historical knowledge state
```

## Tooling

```text
scripts/probes/cross_provider_play_reconciliation_probe.py
tests/probes/test_cross_provider_play_reconciliation_probe.py
```

Contract:

```text
DAILY_NCAAF_PHASE_B2C_SELECTED_PLAY_RECONCILIATION_V1
```
