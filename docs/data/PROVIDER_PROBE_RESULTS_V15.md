# Provider Probe Results V15 — B.2-C C2 Program / Team Provider Crosswalk

Status: **COMPLETE / FREEZE EVIDENCE**

Source run: `cross_provider_team_crosswalk_probe.py`, completed 2026-09-02 against completed seasons 2023-2025.

## Test status

```text
11 tests
OK
```

## Per-season result

| Season | CFBD FBS programs | Schedule-derived ESPN mappings | Coverage | CFBD ID = ESPN ID | ID mismatches | within-season reverse conflicts |
|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 133 | 133 | 100% | 133 | 0 | 0 |
| 2024 | 134 | 134 | 100% | 134 | 0 | 0 |
| 2025 | 136 | 136 | 100% | 136 | 0 | 0 |

Event reconciliation context remained clean in every season:

```text
2023 exact normalized overlap 910; CFBD-only 0; ESPN-only 0
2024 exact normalized overlap 920; CFBD-only 0; ESPN-only 0
2025 exact normalized overlap 934; CFBD-only 0; ESPN-only 0
```

No C1 team-crosswalk conflict was observed in any season.

## Cross-season identity result

Across the full completed-season window:

```text
unique FBS school names        136
unique CFBD team IDs           136
unique ESPN team IDs           136

same CFBD school -> multiple provider IDs     0
same ESPN ID -> multiple CFBD school names    0
same CFBD ID -> multiple CFBD school names    0
```

Therefore, for every measured FBS program in 2023-2025:

```text
CFBD /teams/fbs id == independently derived ESPN team_id
```

This is strong empirical evidence that the two measured sources expose the same numeric team-ID namespace over the audited window.

It does **not** make that external ID canonical Daily-NCAAF identity.

## Display-name evolution

Display strings are not identity. One measured example:

```text
CFBD school: App State
external team id: 2026
2023 ESPN display: Appalachian State Mountaineers
2024-2025 ESPN display: App State Mountaineers
```

The stable ID survives display-name evolution.

Locked:

```text
provider display-name change != identity change
name inequality != provider-ID break
```

## FBS membership transitions

Measured transitions:

```text
2023 -> 2024
entered FBS: Kennesaw State
exited FBS: none

2024 -> 2025
entered FBS: Delaware, Missouri State
exited FBS: none
```

Each entrant retained one stable external team ID in the season in which it joined the FBS universe.

Locked:

```text
FBS membership transition != new PROGRAM identity
classification stint != provider team identity
```

## Phase C consequence

Daily-NCAAF must keep its own canonical `PROGRAM_ID`.

External identity should be modeled as a provider-identifier observation with explicit namespace/source provenance, for example conceptually:

```text
PROGRAM
  -> PROGRAM_PROVIDER_IDENTIFIER
       identifier_namespace
       identifier_value
       observed_via_source
       valid_from / valid_to where known
       acquired_at
       evidence lineage
```

The audited evidence supports treating the CFBD and ESPN numeric team identifiers as the same measured external namespace for 2023-2025, while still preserving source-specific observations and never promoting that value to canonical `PROGRAM_ID`.

## C2 disposition

All predeclared C2 freeze criteria passed:

1. complete schedule-derived FBS crosswalk coverage in every audited season;
2. zero unresolved within-season provider-ID collisions;
3. zero CFBD-vs-derived-ESPN team-ID mismatches;
4. zero hidden cross-season ID drift;
5. membership transitions surfaced separately from identity;
6. display-name evolution surfaced without rewriting identity.

**B.2-C C2 may be frozen.**
