# B.2-C C5-C — Conference Semantic Alias Validation Plan V1

Status: **COMPLETE / MEASURED**  
Date: 2026-09-05

## Why C5-C existed

C5-B established perfect aligned participant external-team-ID agreement and perfect division agreement across completed 2023-2025, but produced 614 raw conference-label mismatches.

Every emitted C5-B mismatch example was the same provider naming-semantic case:

```text
CFBD:        American Athletic
ESPN-native: American Conference / American
ESPN conference_id: 151
```

C5-C therefore performed one bounded semantic-alias validation pass with no fuzzy matching.

## Allowed semantic equivalence tested

```text
American Athletic
American Conference
American
    -> american_athletic
```

No other conference labels were remapped in V3.

## User-executed test result

```text
Ran 8 tests in 0.001s
OK
```

## Measured V3 result

Across 5,528 aligned participant observations:

```text
EXACT_ALIAS_MATCH      4,914
SEMANTIC_ALIAS_MATCH     533
MISMATCH                  81
TOTAL                    5,528
```

The 81 residual conference mismatches were all on the away-participant side in the measured state counts. External participant IDs and division/classification labels remained perfect matches, and referenced team metadata remained complete.

Observed residual example families include:

- `Coastal Athletic` vs `Coastal Athletic Association` / `CAA`;
- `Big South-OVC` vs `Ohio Valley Conference` / `OVC`;
- `OVC-Big South` vs `Ohio Valley Conference` / `OVC`;
- `Big South` vs `Ohio Valley Conference` / `OVC`;
- `UAC` vs `Southland Conference` / `Southland` for Stephen F. Austin in 2023.

## Interpretation

C5-C succeeded as a diagnostic.

It proved that the initial 614-mismatch V2 bucket mixed together multiple semantic classes. The American naming class was safely collapsed, but the remaining classes cannot all be treated as aliases.

Independent historical context confirms:

- `Coastal Athletic` vs `Coastal Athletic Association` is a naming-equivalence candidate;
- Big South/OVC labels describe a joint football association and should remain distinct from a simple member-conference identity;
- Stephen F. Austin competed in UAC football in 2023 and entered the Southland in 2024, so a 2023 Southland team-metadata value is a temporal-affiliation conflict/backfill warning, not an alias.

## Locked rules

```text
NO FUZZY CONFERENCE MATCHING
CONFERENCE ASSOCIATION != MEMBER CONFERENCE
TEAM-SEASON CONFERENCE METADATA != GUARANTEED HISTORICAL PIT AFFILIATION
LATER/CURRENT AFFILIATION MUST NOT BACKFILL EARLIER SEASONS
```

Provider labels and IDs remain evidence only; they do not become canonical `CONFERENCE_ID` or `CONFERENCE_AFFILIATION_STINT` without time-aware reconciliation.

## Handoff

C5-D is now active.

Artifacts:

```text
docs/data/PROVIDER_PROBE_RESULTS_V21.md
docs/data/B2C_C5_RESIDUAL_CONFERENCE_CLASSIFICATION_PLAN_V1.md
scripts/probes/cross_provider_context_reconciliation_probe_v4.py
tests/probes/test_cross_provider_context_reconciliation_probe_v4.py
```

C5-D aggregates every residual mismatch signature across the complete matched set and leaves any unknown signature `UNCLASSIFIED`.

```text
UNCLASSIFIED > 0 => C5 FREEZE BLOCKED
```
