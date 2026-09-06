# B.2-C C5-D Harness Fix — 2026-09-06

Status: **FIXED / RE-RUN REQUIRED**

## Trigger

The user-executed C5-D V4 unit suite produced 5 errors with:

```text
AttributeError: module 'cross_provider_context_reconciliation_probe_v2' has no attribute 'normalize_id'
```

The failing path was `residual_mismatch_class()` in:

```text
scripts/probes/cross_provider_context_reconciliation_probe_v4.py
```

## Root cause

C5-D imported the C5-B context module as `v2` and attempted to call:

```python
v2.normalize_id(...)
```

However, `normalize_id` belongs to the lower-level game reconciliation utility module:

```text
cross_provider_game_reconciliation_probe_v2.py
```

The C5-B module imports that helper module internally but does not re-export `normalize_id` as a top-level function.

## Fix

C5-D now imports the owning utility explicitly:

```python
import cross_provider_game_reconciliation_probe_v2 as game_v2
```

and uses:

```python
conference_id = game_v2.normalize_id(espn_conference_id)
```

No source-data semantics, classification rules, alias rules, or freeze criteria changed.

## Regression coverage

The existing C5-D tests that failed exercise the corrected path directly:

```text
test_big_south_ovc_is_association_model_difference
test_ovc_big_south_is_association_model_difference
test_summary_counts_all_residual_signatures
test_uac_southland_is_temporal_conflict_candidate
test_unknown_signature_is_unclassified
```

A successful rerun of the full 10-test C5-D suite is required before executing the live V4 probe.

## Audit rule

```text
HARNESS IMPLEMENTATION ERROR != PROVIDER DATA FAILURE
```

The failed unit run produced no valid C5-D source-evidence conclusion and does not alter the previously measured C5-A/B/C evidence.
