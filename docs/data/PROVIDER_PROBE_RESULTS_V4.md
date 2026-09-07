# Daily NCAAF — Provider Probe Results V4

**Phase:** B.2 — Empirical Coverage & PIT Probe  
**Status:** B.2-A CORE GAMES/PBP AUDIT COMPLETE; superseded for current status by V5  
**Probe generated:** 2026-08-31T06:01:29Z  
**Harness contract used:** `DAILY_NCAAF_PHASE_B2_PROVIDER_COVERAGE_PROBE_V2`

> This document preserves the B.2-A games/PBP audit record. Current B.2-B native-family results are in `PROVIDER_PROBE_RESULTS_V5.md`.

---

## B.2-A final findings preserved

The focused authenticated CFBD follow-up completed successfully after the V2 harness and its eight unit tests were pulled locally.

The local test run reported:

```text
Ran 8 tests in 0.001s
OK
```

The authenticated probe queried:

```text
GET /games
GET /plays
```

with:

```text
seasonType=both
classification=fbs
seasons=2015,2016,2017,2018,2019,2024,2026
weeks=1,8,15
```

Every request returned HTTP 200.

### `wallclock` coverage-era boundary

Observed sampled null behavior:

```text
2015 -> 100% null in weeks 1/8/15
2016 -> 100% null in weeks 1/8/15
2017 -> 100% null in weeks 1/8/15
2018 -> broadly populated with small gaps
2019 -> broadly populated with small gaps
```

Together with the earlier 2014 sample, the empirical boundary candidate is:

```text
PRE_2018  -> unavailable in tested strata
2018_PLUS -> generally available but nullable
```

This is a coverage boundary, not a claim that `wallclock` is an original publication timestamp.

```text
wallclock does not replace acquired_at
wallclock does not prove historical publication availability
```

### 2024 incomplete game resolved

The only incomplete 2024 `classification=fbs` row was:

```text
Liberty at App State
CFBD game id 401640992
2024-09-28
```

The game was canceled because of Hurricane Helene and was not rescheduled.

Locked consequence:

```text
scheduled game object != completed game
incomplete historical row != automatically missing result
```

### FBS query universe

Observed `classification=fbs` composition:

| Season | Total | FBS vs FBS | FBS vs FCS | FCS vs FBS |
|---:|---:|---:|---:|---:|
| 2015 | 870 | 765 | 105 | 0 |
| 2016 | 873 | 760 | 113 | 0 |
| 2017 | 874 | 776 | 98 | 0 |
| 2018 | 884 | 772 | 111 | 1 |
| 2019 | 888 | 774 | 114 | 0 |
| 2024 | 920 | 799 | 121 | 0 |
| 2026 | 888 | 761 | 127 | 0 |

Therefore:

```text
classification=fbs -> observed FBS-involved universe
```

rather than strict FBS-vs-FBS only.

### 2026 live-state evolution

The later snapshot observed:

```text
888 returned game objects
8 completed games
1,412 week-1 PBP rows
8 games with week-1 PBP
```

where the prior snapshot had zero completed games/PBP.

This is direct evidence that current provider state changes through the season and must be captured prospectively with immutable `acquired_at` observations.

### PPA semantics

The V2 probe showed ordinary rush/pass PPA is generally highly populated while kickoff/punt/penalty/timeout/end-period play families are often structurally null.

Locked consequence:

```text
PPA IS NULL != invalid play
```

PPA eligibility must be defined by normalized play family.

---

## B.2-A verdict

The representative core games/PBP audit is complete enough to advance.

Remaining event-side questions belong to later subphases:

- full-season completeness;
- cross-provider game/play reconciliation;
- player-play association coverage;
- prospective live revision/publication timing.

Current provider-family work continues in:

```text
docs/data/PROVIDER_PROBE_RESULTS_V5.md
docs/data/CFBD_NATIVE_FAMILY_FOLLOWUP_PLAN_V1.md
```
