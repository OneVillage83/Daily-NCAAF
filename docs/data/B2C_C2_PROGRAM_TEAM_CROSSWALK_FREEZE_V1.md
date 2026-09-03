# B.2-C C2 — Program / Team Provider Crosswalk Freeze V1

Status: **FROZEN**

Frozen on: 2026-09-02

Evidence:

- `B2C_C1_GAME_EVENT_IDENTITY_FREEZE_V1.md`
- `PROVIDER_PROBE_RESULTS_V15.md`
- `scripts/probes/cross_provider_team_crosswalk_probe.py`
- `tests/probes/test_cross_provider_team_crosswalk_probe.py`

## Frozen empirical boundary

For completed seasons 2023-2025, every FBS program returned by CFBD `/teams/fbs?year=` was independently recovered from the participant-aligned ESPN/SportsDataverse schedule crosswalk.

```text
2023: 133 / 133 mapped; 133 direct provider-ID matches
2024: 134 / 134 mapped; 134 direct provider-ID matches
2025: 136 / 136 mapped; 136 direct provider-ID matches
```

No direct provider-ID mismatch or reverse collision was observed.

Across the full window:

```text
136 unique FBS school names
136 unique CFBD team IDs
136 unique ESPN team IDs
0 same-name multi-ID cases
0 same-ESPN-ID multi-name cases
0 same-CFBD-ID multi-name cases
```

## Frozen interpretation

The audited CFBD and ESPN-derived sources expose the same numeric external team-ID namespace across the measured 2023-2025 FBS universe.

This is **provider crosswalk evidence**, not canonical Daily-NCAAF identity.

```text
external team ID != canonical PROGRAM_ID
```

Daily-NCAAF remains authoritative for canonical program identity.

## Name semantics

Provider display names are mutable attributes.

Example:

```text
external ID 2026
Appalachian State Mountaineers -> App State Mountaineers
```

Locked:

```text
display-name evolution != identity break
name equality != canonical identity proof
name inequality != identity break
```

## Classification semantics

Measured FBS entry transitions:

```text
Kennesaw State: entered 2024
Delaware: entered 2025
Missouri State: entered 2025
```

Locked:

```text
classification membership is a stint/state
FBS entry/exit != new PROGRAM
```

## Production architecture authority

Phase C should represent canonical programs independently from external identifiers.

Minimum contract:

```text
PROGRAM
PROGRAM_SEASON
CLASSIFICATION_STINT
CONFERENCE_AFFILIATION_STINT
PROGRAM_PROVIDER_IDENTIFIER / PROVIDER_IDENTIFIER_OBSERVATION
```

Provider identifier records must retain:

```text
namespace
value
source/provider observation
acquired_at
valid interval when defensible
raw evidence lineage
reconciliation status
```

Even when CFBD and ESPN expose the same numeric value, source provenance is retained.

## Non-authority

This freeze does **not** establish:

- historical PIT availability of provider team metadata;
- conference/venue agreement;
- player identity agreement;
- permanent future identity stability outside the measured window;
- canonical authority for provider names or provider IDs.

Those remain separate evidence gates.

## Next gate

**B.2-C C3 — player cross-provider identity** is active next.
