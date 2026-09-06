# B.2-C C5-D Residual Conference Classification Plan V1

Date: 2026-09-05 America/Los_Angeles

## Purpose

C5-C/V3 reduced the raw conference mismatch bucket from 614 to 81 by proving the explicit American Athletic / American Conference naming equivalence. The remaining 81 observations are not allowed to be solved with broader fuzzy matching.

C5-D exists to make the residual evidence exhaustive and classifiable before C5 freeze.

## Problem discovered in V3

The residual examples are not one homogeneous class.

They include at least:

- simple provider naming differences;
- football conference-association modeling differences;
- likely season/historical affiliation backfill.

These must remain distinct in the production ontology.

## V4 contract

`DAILY_NCAAF_PHASE_B2C_CONTEXT_RECONCILIATION_V4`

Probe:

`scripts/probes/cross_provider_context_reconciliation_probe_v4.py`

Tests:

`tests/probes/test_cross_provider_context_reconciliation_probe_v4.py`

## Explicit semantic alias policy

V4 retains the V3 American Athletic equivalence and adds one independently verified naming equivalence:

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

This remains an enumerated evidence-backed table. No fuzzy matching is permitted.

## Residual mismatch classes

### CONFERENCE_ASSOCIATION_MODEL_DIFFERENCE

Measured rule:

- CFBD: `Big South-OVC`, `OVC-Big South`, or `Big South`
- ESPN-native conference id: `179`
- ESPN-native aliases include `Ohio Valley Conference` / `OVC`

Interpretation:

The Big South and OVC operated a joint football association. A provider may label the football competition by the association while another provider's team metadata projects the OVC umbrella/member-conference identity.

This is **not** automatically a team identity conflict and must not be coerced into canonical conference equality.

### TEMPORAL_AFFILIATION_CONFLICT_CANDIDATE

Measured rule:

- CFBD: `UAC`
- ESPN-native conference id: `30`
- ESPN-native aliases include `Southland Conference` / `Southland`

Known example:

- Stephen F. Austin, 2023.

Independent historical context shows SFA in UAC football in 2023 and Southland beginning in 2024. Therefore the 2023 ESPN team-season conference value is not safe historical season truth.

Production implication:

`CONFERENCE_AFFILIATION_STINT` must be time-bounded and evidence-versioned. A later/current team metadata value may never overwrite an earlier season affiliation.

### UNCLASSIFIED

Any residual signature that does not match a measured rule remains `UNCLASSIFIED`.

`UNCLASSIFIED > 0` blocks C5 freeze.

## Exhaustive signature requirement

V2/V3 example arrays are bounded for output size and therefore are not sufficient to prove that all residual mismatch signatures have been observed.

V4 aggregates every residual mismatch across the complete compared row set into:

- `conference_mismatch_signature_counts`
- `conference_mismatch_signature_classes`
- `conference_mismatch_class_counts`
- `conference_mismatch_total`
- `conference_mismatch_unclassified_count`

This removes dependence on the example cap.

## Compact output requirement

The full report is still retained as immutable local evidence when `--output` is supplied.

However, stdout prints only `compact_summary` so the operator does not need to dump a hundreds-of-thousands-character JSON artifact into the terminal/chat.

The compact summary includes per season:

- exact game-ID match count and coverage;
- missing referenced team metadata count;
- side-orientation counts;
- external team-ID states;
- division states;
- conference states;
- residual mismatch class counts;
- full residual mismatch signature counts;
- unclassified residual count.

It also includes aggregate residual signature/class counts across all requested seasons.

## Freeze gate

C5 may be frozen if the C5-D run proves all of the following:

1. all requested seasons complete successfully;
2. CFBD exact game-ID coverage remains 100%;
3. external participant team IDs remain conflict-free;
4. participant division/classification remains conflict-free;
5. referenced team metadata remains complete;
6. every residual conference mismatch is assigned to an explicit measured class;
7. `conference_mismatch_unclassified_count == 0`;
8. temporal affiliation conflicts remain retained as source disagreements rather than aliases;
9. team-season home venue remains non-authoritative for event venue.

If those gates pass, the correct freeze is not "all providers agree." The correct freeze is:

> all measured differences are either direct matches, explicitly enumerated naming equivalences, explicitly modeled conference-association differences, or explicitly retained historical affiliation conflicts with no unresolved identity ambiguity.

That is sufficient for a provider-independent production contract.
