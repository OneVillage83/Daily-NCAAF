# Daily NCAAF — B.2-C Game Reconciliation Follow-up V1

**Status:** ACTIVE  
**Predecessor:** `PROVIDER_PROBE_RESULTS_V11.md`

## Immediate objective

Repeat C1 with the corrected V2 harness for 2024 and 2026.

The rerun must answer five bounded questions:

1. Does 2024 retain 100% CFBD exact game-ID coverage?
2. After deriving ESPN FBS team IDs from exact matched sides, are any ESPN-only events still FBS-involved?
3. Does the side-derived CFBD-name ↔ ESPN-team-ID crosswalk contain conflicts?
4. Which exact games account for the 15 kickoff mismatches and two score mismatches observed in V1?
5. What is the current 2026 exact-ID overlap using the actual manifest-selected schedule asset?

## Required reliability

The V2 harness must retain:

```text
CFBD acquired_at
SportsDataverse manifest acquired_at
release updated_at
selected asset name
selected asset URL
asset created_at / updated_at
advertised digest
downloaded SHA-256
digest equality result
```

Current-season comparisons are acquisition snapshots, not final-season truth.

## Identity policy

Exact shared event IDs and same-side provider team IDs are strong crosswalk evidence.

They do not replace Daily-NCAAF canonical IDs.

```text
EXTERNAL PROVIDER ID != CANONICAL ID
```

Team display names are never identity keys.

## Exit condition for C1

C1 can close when:

- completed-season exact event-ID coverage is measured after event-universe normalization;
- unmatched normalized FBS-involved events are enumerated;
- team crosswalk conflicts are measured;
- kickoff/score/lifecycle disagreements are explicitly inspected rather than hidden by display text;
- current-season asset/source behavior is understood as an immutable acquisition snapshot.

Then advance to C2 program/team crosswalk hardening and C3 player reconciliation.
