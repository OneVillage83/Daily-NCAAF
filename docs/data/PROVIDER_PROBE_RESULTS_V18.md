# Daily-NCAAF Provider Probe Results V18

Date recorded: 2026-09-03
Status: **B.2-C C4 COMPLETE / FREEZE EVIDENCE**

## Scope

This evidence records the user-executed C4 transfer-event reconciliation probe:

```text
contract: DAILY_NCAAF_PHASE_B2C_TRANSFER_EVENT_RECONCILIATION_V1
unit tests: 10
result: OK
probe status: RAN
```

The probe reconciles identifier-less CFBD portal observations against already-frozen C2 program identities, C3 external athlete-ID evidence, and surrounding CFBD plus ESPN-derived roster observations.

## Aggregate result

```text
TWO_SIDED_DIRECT_SHARED_ID_BRACKET  3
PARTIAL_DIRECT_SHARED_ID_BRACKET    1
PORTAL_CONTEXT_AMBIGUOUS            0
PORTAL_CONTEXT_NOT_FOUND            0
IDENTIFIER_CONFLICT                 0
UNRESOLVED                          0
```

Every targeted transfer had exactly one contextual CFBD portal candidate and every measured `transferDate` matched the expected provider observation.

## Dillon Gabriel — UCF -> Oklahoma

```text
portal season: 2022
expected athlete id: 4427238
portal candidates: 1
portal transferDate: 2021-11-27T07:07:00.000Z
transferDate state: MATCH

origin UCF 2021:
  CFBD expected id present: true
  ESPN expected id present: true
  state: DIRECT_SHARED_PROVIDER_ID

destination Oklahoma 2022:
  CFBD expected id present: true
  ESPN expected id present: true
  state: DIRECT_SHARED_PROVIDER_ID

reconciliation:
  TWO_SIDED_DIRECT_SHARED_ID_BRACKET
```

## Dillon Gabriel — Oklahoma -> Oregon

```text
portal season: 2024
expected athlete id: 4427238
portal candidates: 1
portal transferDate: 2023-12-04T14:01:00.000Z
transferDate state: MATCH

origin Oklahoma 2023:
  DIRECT_SHARED_PROVIDER_ID

destination Oregon 2024:
  DIRECT_SHARED_PROVIDER_ID

reconciliation:
  TWO_SIDED_DIRECT_SHARED_ID_BRACKET
```

## Caleb Downs — Alabama -> Ohio State

```text
portal season: 2024
expected athlete id: 4870706
portal candidates: 1
portal transferDate: 2024-01-17T15:39:00.000Z
transferDate state: MATCH

origin Alabama 2023:
  DIRECT_SHARED_PROVIDER_ID

destination Ohio State 2024:
  DIRECT_SHARED_PROVIDER_ID

reconciliation:
  TWO_SIDED_DIRECT_SHARED_ID_BRACKET
```

## Travis Hunter — Jackson State -> Colorado

```text
portal season: 2023
expected athlete id: 4685415
portal candidates: 1
portal transferDate: 2022-12-19T04:36:00.000Z
transferDate state: MATCH

origin Jackson State 2022:
  CFBD expected id present: true
  ESPN team rows: 0
  state: NO_ESPN_TEAM_ROWS

destination Colorado 2023:
  DIRECT_SHARED_PROVIDER_ID

reconciliation:
  PARTIAL_DIRECT_SHARED_ID_BRACKET
```

This is the correct conservative result. The known SportsDataverse Jackson State 2022 coverage gap remains explicit and is not repaired by a name match.

## Raw observation reproducibility

Every selected SportsDataverse roster asset verified its advertised SHA-256 digest:

```text
2021 cfb_rosters_2021.csv.gz  digest match true
2022 cfb_rosters_2022.csv.gz  digest match true
2023 cfb_rosters_2023.csv.gz  digest match true
2024 cfb_rosters_2024.csv.gz  digest match true
```

Each portal candidate also received a deterministic provider-record SHA-256 so the exact contextual row can be retained as immutable audit evidence.

## Frozen interpretation

```text
portal row != PLAYER identity authority
portal name + origin + destination = contextual candidate evidence only
same frozen athlete id before/after transfer = strong continuity evidence
portal origin/destination != canonical PLAYER_PROGRAM_STINT by itself
missing ESPN origin roster != transfer failure
transferDate = provider transfer/effective-time observation
transferDate != publication time
transferDate != acquired_at
```

The canonical model therefore requires separate concepts for:

```text
PLAYER
PLAYER_PROGRAM_STINT
TRANSFER_OBSERVATION
```

A `TRANSFER_OBSERVATION` may reconcile to a canonical player only through an explicit reconciliation record/method/confidence/evidence chain.

## C4 verdict

**C4 is COMPLETE / FROZEN.**

The four targeted events satisfy the predeclared freeze criteria without an identifier conflict, forced portal identity merge, or hidden source-coverage gap.
