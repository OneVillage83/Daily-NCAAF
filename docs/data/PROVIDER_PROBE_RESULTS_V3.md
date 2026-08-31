# Daily NCAAF — Provider Probe Results V3

**Phase:** B.2 — Empirical Coverage & PIT Probe  
**Status:** HISTORICAL AUDIT RECORD; superseded for current status by V4/V5  
**Probe generated:** 2026-08-28T03:11:31Z  
**Harness contract used:** `DAILY_NCAAF_PHASE_B2_PROVIDER_COVERAGE_PROBE_V1`

> V3 records the first successful authenticated CFBD games/PBP representative run. The focused B.2-A follow-up is preserved in `PROVIDER_PROBE_RESULTS_V4.md`; current B.2-B family evidence is in `PROVIDER_PROBE_RESULTS_V5.md`.

---

## V3 findings preserved

The first authenticated CFBD pass queried `/games` and `/plays` for:

```text
2004, 2010, 2014, 2020, 2024, 2025, 2026
```

with representative weeks 1/8/15. Every request returned HTTP 200.

Observed constraints included:

- zero duplicate sampled game IDs;
- zero duplicate sampled play IDs;
- near-complete play text;
- `wallclock` completely absent in sampled 2004/2010/2014 plays;
- modern `wallclock` broadly populated but nullable;
- overall PPA null rates too semantically mixed to treat as one coverage metric;
- CFBD and cfbfastR season totals not directly comparable without normalizing event universe;
- current-season schedules can exist before PBP.

The V3 run led directly to the V2 harness that measured classification pairs, incomplete game examples and PPA/wallclock missingness by play type.

For the finalized B.2-A conclusions, use `PROVIDER_PROBE_RESULTS_V4.md`.
