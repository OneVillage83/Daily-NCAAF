# B.2-C C5-D Harness Fix — 2026-09-06

Status: **FIXED / RE-RUN REQUIRED**

## Incident 1 — wrong normalize_id owner

### Trigger

The first user-executed C5-D V4 unit suite produced 5 errors with:

```text
AttributeError: module 'cross_provider_context_reconciliation_probe_v2' has no attribute 'normalize_id'
```

The failing path was `residual_mismatch_class()` in:

```text
scripts/probes/cross_provider_context_reconciliation_probe_v4.py
```

### Root cause

C5-D imported the C5-B context module as `v2` and attempted to call:

```python
v2.normalize_id(...)
```

However, `normalize_id` belongs to the lower-level game reconciliation utility module:

```text
cross_provider_game_reconciliation_probe_v2.py
```

The C5-B module imports that helper module internally but does not re-export `normalize_id` as a top-level function.

### Fix

C5-D now imports the owning utility explicitly:

```python
import cross_provider_game_reconciliation_probe_v2 as game_v2
```

and uses:

```python
conference_id = game_v2.normalize_id(espn_conference_id)
```

No source-data semantics, classification rules, alias rules, or freeze criteria changed.

## Incident 2 — recursive summarize monkey-patch

### Trigger

After the first fix, the user executed the live V4 probe and received:

```text
RecursionError: maximum recursion depth exceeded
```

The traceback repeatedly entered:

```text
summarize_with_signatures()
  -> v2.summarize(rows)
  -> summarize_with_signatures()
  -> ...
```

### Root cause

`build_report()` intentionally monkey-patches:

```python
v2.summarize = summarize_with_signatures
```

so the inherited V2 report builder can emit the new residual-signature fields.

However, `summarize_with_signatures()` itself called:

```python
v2.summarize(rows)
```

After the monkey-patch, that attribute no longer referred to the original V2 summarizer; it referred back to `summarize_with_signatures()`, causing infinite recursion.

### Fix

C5-D now captures the underlying V2 summarizer exactly once at module import time, before any monkey-patching:

```python
BASE_V2_SUMMARIZE = v2.summarize
```

and the extended summarizer calls the preserved base implementation:

```python
base = BASE_V2_SUMMARIZE(rows)
```

`build_report()` still restores both monkey-patched V2 functions in `finally`, so module-global state remains unchanged after every run.

### Regression coverage

The existing `test_summary_counts_all_residual_signatures` now explicitly recreates the live monkey-patch shape:

```python
with patch.object(probe.v2, "summarize", probe.summarize_with_signatures):
    summary = probe.summarize_with_signatures(rows)
```

This directly verifies that the extended summarizer uses the preserved base function instead of recursively following the live `v2.summarize` attribute.

## Required rerun

The full C5-D suite remains **10 tests**. All 10 must pass before the live V4 evidence run is accepted.

Then rerun:

```text
python scripts/probes/cross_provider_context_reconciliation_probe_v4.py --seasons 2023,2024,2025 --output local-data/probes/cross_provider_context_v4.json
```

The live run must complete and print the compact summary before any C5 freeze decision.

## Audit rules

```text
HARNESS IMPLEMENTATION ERROR != PROVIDER DATA FAILURE
FAILED LIVE HARNESS EXECUTION != SOURCE EVIDENCE
MONKEY-PATCHED WRAPPER MUST CALL A PRESERVED BASE IMPLEMENTATION
```

Neither harness incident changes the previously measured C5-A/B/C evidence. No C5-D provider-data conclusion is valid until the corrected suite and live probe complete successfully.
