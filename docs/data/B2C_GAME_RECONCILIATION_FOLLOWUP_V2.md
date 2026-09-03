# B.2-C C1 — Game Reconciliation Follow-up V2

## Purpose

Correct the final two C1 measurement hazards discovered by the V2 run:

1. provider home/away orientation is not canonical participant identity;
2. release asset freshness can differ across formats.

## V3 invariant

Exact game ID equality is tested first. Only after the event is matched do we orient the two participants.

```text
EXACT EVENT ID
  -> compare participant set
  -> infer SAME_SIDE / SWAPPED_SIDES / UNRESOLVED
  -> align provider team IDs to CFBD participants
  -> compare scores by participant
  -> derive team crosswalk
```

Home/away is never allowed to manufacture a new team identity or a score mismatch.

## Orientation states

```text
SAME_SIDE
SWAPPED_SIDES
AMBIGUOUS
UNRESOLVED
```

Display text may orient participants only inside an exact-ID-matched event. It is not allowed to create a game identity by itself.

## Score states

```text
MATCH
MISMATCH
UNAVAILABLE
UNRESOLVED_ORIENTATION
```

A score is compared only after participant orientation is known.

## Current snapshot rule

If the SportsDataverse event set is a strict subset of CFBD at acquisition time, record:

```text
ESPN_EVENT_SET_STRICT_SUBSET_OF_CFBD_AT_ACQUISITION
```

Do not relabel the unmatched future schedule as provider missingness.

The exact acquired asset, digest and acquisition time remain authoritative evidence of what that provider snapshot contained.

## Asset selection

Supported formats:

```text
.csv.gz
.csv
```

Selection rule:

1. choose the newest supported asset by `updated_at` / `created_at`;
2. use format preference only to break a timestamp tie;
3. hash the downloaded bytes;
4. verify advertised SHA-256 when available.

This prevents an old `.csv.gz` from silently outranking a newly regenerated `.csv`.

## Temporal disagreement

Kickoff deltas are bucketed and retained with examples.

They remain source semantic evidence until scheduled/revised/actual-start meaning is proven.

```text
provider kickoff delta != automatic provider error
```

## Expected C1 freeze evidence

For completed 2024:

- complete normalized FBS event-ID overlap;
- zero unexplained team-ID crosswalk conflicts;
- provider side swaps explicit;
- scores aligned by participant;
- lifecycle agreement measured;
- kickoff differences preserved rather than silently overwritten.

For current 2026:

- exact IDs measured only for rows present in both snapshots;
- strict subset state called a snapshot delta;
- lifecycle/score lag retained as immutable current-state evidence;
- no final-season coverage conclusion drawn from an early-season public asset.

## Tooling

```text
scripts/probes/cross_provider_game_reconciliation_probe_v3.py
tests/probes/test_cross_provider_game_reconciliation_probe_v3.py
```

If the corrected 2024 run has no unresolved identity conflict, C1 may close and C2 can freeze the program/team crosswalk contract while C3 begins player reconciliation.
