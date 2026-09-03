# B.2-C C5-C — Conference Semantic Alias Validation Plan V1

Status: **ACTIVE**  
Date: 2026-09-03

## Why C5-C exists

C5-B established perfect aligned participant external-team-ID agreement and perfect division agreement across completed 2023-2025, but produced 614 raw conference-label mismatches.

Every emitted mismatch example was the same provider naming-semantic case:

```text
CFBD:        American Athletic
ESPN-native: American Conference / American
ESPN conference_id: 151
```

C5 must not freeze with a known false-positive mismatch class, but it also must not silently add broad fuzzy matching.

C5-C therefore performs one bounded semantic-alias validation pass.

## Allowed semantic equivalence

Exactly one measured equivalence group is permitted:

```text
American Athletic
American Conference
American
```

Canonical comparison token:

```text
american_athletic
```

No other conference labels are remapped.

## Comparison precedence

```text
1. EXACT_ALIAS_MATCH
2. NORMALIZED_ALIAS_MATCH
3. SEMANTIC_ALIAS_MATCH
4. MISMATCH
```

Unavailable states from C5-B remain unchanged.

## Prohibited behavior

```text
no fuzzy string similarity
no edit-distance auto-match
no name-only inference across unknown conferences
no use of backported CFBD fields as ESPN evidence
no replacement of provider labels in raw evidence
no conversion of provider conference IDs into canonical CONFERENCE_ID
```

## Tooling

```text
scripts/probes/cross_provider_context_reconciliation_probe_v3.py
tests/probes/test_cross_provider_context_reconciliation_probe_v3.py
```

Contract:

```text
DAILY_NCAAF_PHASE_B2C_CONTEXT_RECONCILIATION_V3
```

## Rerun window

```text
2023
2024
2025
```

## Freeze-candidate checks

C5 may freeze if V3 confirms:

1. every aligned external team-ID comparison remains `MATCH`;
2. every aligned division comparison remains `MATCH`;
3. no referenced schedule participant lacks team metadata;
4. the 614 known V2 conference mismatches collapse to `SEMANTIC_ALIAS_MATCH` or any residual mismatch is explicitly reviewed;
5. no unrelated conference pair is silently normalized by the semantic-equivalence layer;
6. C5-A neutral-site and conference-game semantic disagreements remain preserved as provider observations;
7. team-season home venue remains separate from event venue identity;
8. direct event venue-ID corroboration remains explicitly unavailable from the current ESPN-native schedule artifact;
9. canonical `PROGRAM_ID`, `CONFERENCE_ID`, `VENUE_ID`, `CLASSIFICATION_STINT`, and `CONFERENCE_AFFILIATION_STINT` remain provider-independent.

## Expected production rule if validated

```text
conference provider label
    -> provider-specific alias normalization
    -> reconciled conference observation
    -> canonical CONFERENCE_AFFILIATION_STINT only after identity/time reconciliation
```

The raw source labels are retained unchanged for replay and provenance.
