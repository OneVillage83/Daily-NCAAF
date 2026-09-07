# B.2-C C5-D Residual Conference Classification Plan V1

Status: **COMPLETE / C5 FROZEN**  
Date opened: 2026-09-05 America/Los_Angeles  
Date completed: 2026-09-07 America/Los_Angeles

## Purpose

C5-C/V3 reduced the raw conference mismatch bucket from 614 to 81 by proving the explicit American Athletic / American Conference naming equivalence. The remaining observations were not allowed to be solved with broader fuzzy matching.

C5-D made the residual evidence exhaustive and classifiable before C5 freeze.

## V4 contract

```text
DAILY_NCAAF_PHASE_B2C_CONTEXT_RECONCILIATION_V4
```

Probe:

```text
scripts/probes/cross_provider_context_reconciliation_probe_v4.py
```

Tests:

```text
tests/probes/test_cross_provider_context_reconciliation_probe_v4.py
```

Final user-executed validation:

```text
Ran 10 tests in 0.002s
OK
```

## Explicit semantic alias policy

V4 retained the V3 American Athletic equivalence and added one evidence-backed naming equivalence:

```text
American Athletic
American Conference
American
    -> american_athletic

Coastal Athletic
Coastal Athletic Association
CAA
    -> coastal_athletic_association
```

This remains an enumerated table. No fuzzy matching is permitted.

## Final residual mismatch classes

### CONFERENCE_ASSOCIATION_MODEL_DIFFERENCE

Measured signatures:

```text
CFBD=Big South :: ESPN_ID=179 :: ESPN=Ohio Valley Conference | OVC        1
CFBD=Big South-OVC :: ESPN_ID=179 :: ESPN=Ohio Valley Conference | OVC   22
CFBD=OVC-Big South :: ESPN_ID=179 :: ESPN=Ohio Valley Conference | OVC   14
```

Total:

```text
37
```

Interpretation:

The Big South and OVC operated a joint football association. A provider may label football competition through that association while another path exposes OVC-oriented team metadata.

This is **not** a team identity conflict and is not coerced into canonical conference equality.

### TEMPORAL_AFFILIATION_CONFLICT_CANDIDATE

Measured signature:

```text
CFBD=UAC :: ESPN_ID=30 :: ESPN=Southland Conference | Southland | land   1
```

Known example:

```text
Stephen F. Austin, 2023
```

The conflict is retained as evidence that team-season metadata cannot automatically establish historical season affiliation truth.

Production implication:

```text
CONFERENCE_AFFILIATION_STINT
```

must be time-bounded and evidence-versioned. Later/current team metadata may never overwrite earlier season affiliation evidence.

### UNCLASSIFIED

Final result:

```text
UNCLASSIFIED = 0
```

## Exhaustive signature result

V4 aggregated every residual mismatch across the complete compared row set rather than relying on bounded examples.

Aggregate:

```text
CONFERENCE_ASSOCIATION_MODEL_DIFFERENCE       37
TEMPORAL_AFFILIATION_CONFLICT_CANDIDATE        1
UNCLASSIFIED                                    0
TOTAL                                          38
```

By season:

```text
2023: association 10, temporal 1, unclassified 0
2024: association 13, temporal 0, unclassified 0
2025: association 14, temporal 0, unclassified 0
```

## Freeze gate result

C5-D proved:

1. all requested seasons completed successfully;
2. CFBD exact game-ID coverage remained 100%;
3. external participant team IDs remained conflict-free;
4. participant division/classification remained conflict-free;
5. referenced team metadata remained complete;
6. every residual conference mismatch was assigned to an explicit measured class;
7. `conference_mismatch_unclassified_count == 0`;
8. temporal affiliation conflict evidence remained source disagreement rather than alias;
9. team-season home venue remained non-authoritative for event venue.

The correct freeze is **not** “all providers agree.” The freeze is:

> all measured context differences are either direct matches, explicitly enumerated naming equivalences, explicitly modeled football-association differences, or explicitly retained temporal affiliation conflicts, with no unresolved identity ambiguity.

## Final status

**C5-D COMPLETE. B.2-C C5 COMPLETE / FROZEN.**

Freeze artifacts:

```text
docs/data/PROVIDER_PROBE_RESULTS_V22.md
docs/data/B2C_C5_VENUE_CONFERENCE_CONTEXT_FREEZE_V1.md
```

Next:

```text
B.2-C C6 — selected play-level reconciliation
```
