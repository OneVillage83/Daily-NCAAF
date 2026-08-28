# Daily NCAAF — Provider Probe Results V3

**Phase:** B.2 — Empirical Coverage & PIT Probe  
**Status:** B.2-A INITIAL AUTHENTICATED CFBD MEASUREMENT COMPLETE; focused era/scope follow-up active  
**Probe generated:** 2026-08-28T03:11:31Z  
**Harness contract used:** `DAILY_NCAAF_PHASE_B2_PROVIDER_COVERAGE_PROBE_V1`  
**Supersedes for current B.2 status:** `PROVIDER_PROBE_RESULTS_V2.md`; V1/V2 remain prior audit records.

---

## 1. What changed since V2

V2 stopped at public SportsDataverse/cfbfastR measurements because authenticated CFBD row-level testing had not yet been executed.

V3 records the first successful local authenticated CFBD run of the committed research harness against:

```text
GET /games
GET /plays
```

with:

```text
seasonType=both
classification=fbs
seasons=2004,2010,2014,2020,2024,2025,2026
weeks=1,8,15
```

Every request in this run returned HTTP 200. The generated aggregate report intentionally omitted the API key and remains a local research artifact.

This run does **not** establish production ingestion semantics. It establishes measured provider behavior that can constrain later Phase C contracts.

---

# P-020 — Authenticated CFBD games/PBP access verified across representative eras

Observed `/games` summaries:

| Season | Rows | Unique game IDs | Duplicate game-ID rows | Completed | Neutral-site | Conference-null rows |
|---:|---:|---:|---:|---:|---:|---:|
| 2004 | 730 | 730 | 0 | 730 | 53 | 4 |
| 2010 | 808 | 808 | 0 | 808 | 63 | 0 |
| 2014 | 868 | 868 | 0 | 868 | 68 | 0 |
| 2020 | 570 | 570 | 0 | 570 | 37 | 0 |
| 2024 | 920 | 920 | 0 | 919 | 80 | 0 |
| 2025 | 934 | 934 | 0 | 934 | 64 | 0 |
| 2026 | 888 | 888 | 0 | 0 | 11 | 0 |

Interpretation:

1. game IDs were unique within every tested season response;
2. the COVID-disrupted 2020 schedule is visibly smaller, as expected from season structure rather than automatically implying provider failure;
3. 2026 contains scheduled game objects before any sampled PBP exists, which is a useful live-season readiness property;
4. one 2024 row is currently marked incomplete and requires targeted identification before a completed-season completeness claim is made;
5. conference is not universally populated in the oldest sampled era, so the canonical schema must permit source-level null observations and resolve conference affiliation from versioned program-season identity where possible.

---

# P-021 — Sampled play IDs are unique and play text is nearly complete

Aggregating the three sampled weeks per played season:

| Season | Sampled play rows | Duplicate play-ID rows | Play-text null rows |
|---:|---:|---:|---:|
| 2004 | 10,899 | 0 | 0 |
| 2010 | 28,442 | 0 | 0 |
| 2014 | 34,868 | 0 | 0 |
| 2020 | 21,433 | 0 | 0 |
| 2024 | 37,472 | 0 | 1 |
| 2025 | 37,449 | 0 | 0 |
| 2026 | 0 | 0 | 0 |

Across these sparse representative strata, CFBD play identifiers behaved cleanly and `playText` was essentially complete.

This supports CFBD as a strong candidate historical event/PBP source, but does not remove the need for:

- full-season expected-vs-observed coverage;
- cross-provider game/play reconciliation;
- player/stat association coverage checks;
- correction/revision testing;
- field-level leakage contracts.

---

# P-022 — `wallclock` has a major historical-era break and is not a universal timestamp

Observed aggregate null behavior across the three sampled weeks:

| Season | Sampled play rows | `wallclock` null rows | Null rate |
|---:|---:|---:|---:|
| 2004 | 10,899 | 10,899 | 100.00% |
| 2010 | 28,442 | 28,442 | 100.00% |
| 2014 | 34,868 | 34,868 | 100.00% |
| 2020 | 21,433 | 21 | 0.10% |
| 2024 | 37,472 | 871 | 2.32% |
| 2025 | 37,449 | 364 | 0.97% |

This is one of the most important B.2-A findings.

The correct architecture is now empirically constrained to:

```text
CFBD wallclock IS OPTIONAL BY ERA
CFBD wallclock IS NOT a universal historical publication timestamp
```

It cannot be a required canonical field and cannot be used to reconstruct historical pregame/live knowledge state in early eras.

Even in modern seasons it is not perfectly populated, so live PIT capture must use Daily-NCAAF/Daily-Data-Core `acquired_at` plus immutable raw evidence rather than depending on provider `wallclock` alone.

A focused 2015-2019 run is required to locate the transition more precisely.

---

# P-023 — PPA nullness is substantial but cannot be interpreted as generic data failure

Observed aggregate PPA null behavior:

| Season | Sampled play rows | PPA null rows | Null rate |
|---:|---:|---:|---:|
| 2004 | 10,899 | 3,112 | 28.55% |
| 2010 | 28,442 | 7,547 | 26.53% |
| 2014 | 34,868 | 7,767 | 22.28% |
| 2020 | 21,433 | 4,937 | 23.03% |
| 2024 | 37,472 | 9,492 | 25.33% |
| 2025 | 37,449 | 9,274 | 24.76% |

These totals include many play families where PPA may not be applicable or may have different enrichment behavior, including timeouts, kickoffs, punts, end-period events and penalties.

Therefore:

```text
raw PPA null rate != PBP coverage failure
```

The next harness version measures PPA nullness by play type so we can distinguish structural non-applicability from unexpected missingness on eligible scrimmage plays.

PPA also remains a derived provider field and requires its own PIT/model-version contract before historical feature use.

---

# P-024 — CFBD and cfbfastR season totals are not automatically the same universe

The earlier public cfbfastR build reported:

```text
2024 schedules = 966
2026 schedules = 946
```

The authenticated CFBD query used in this V3 run returned:

```text
2024 games with classification=fbs = 920
2026 games with classification=fbs = 888
```

Observed deltas:

```text
2024: 46 games
2026: 58 games
```

This is **not** currently labeled a provider completeness defect.

The two sources may differ in:

- inclusion universe;
- FBS/FCS game handling;
- spring/all-star handling;
- canceled/postponed objects;
- postseason classification;
- source update timing;
- other event-scope rules.

The current CFBD API documents `classification` as a game query dimension and exposes both `homeClassification` and `awayClassification` on game objects. The next probe version therefore records classification-pair counts and explicit query scope.

Locked consequence:

```text
NEVER compare provider season row totals without first normalizing event universe
```

This becomes a direct B.2-C reconciliation requirement.

---

# P-025 — 2026 zero PBP is confirmed as structurally not-yet-applicable

For 2026:

```text
/games rows = 888
completed = 0
week 1 PBP = 0
week 8 PBP = 0
week 15 PBP = 0
```

This agrees directionally with the prior cfbfastR preseason observation that schedules exist before PBP-derived products.

The coverage-state contract remains:

```text
NOT_YET_APPLICABLE
EXPECTED_BUT_MISSING
NO_OBSERVATION
PARTIAL
AVAILABLE
```

and must not collapse these states into one boolean.

---

# P-026 — CFBD API shape supports explicit game-scope reconciliation

Current CFBD `/games` documentation exposes fields including:

```text
id
season
week
seasonType
startDate
startTimeTBD
completed
neutralSite
conferenceGame
homeId / awayId
homeConference / awayConference
homeClassification / awayClassification
homePoints / awayPoints
venueId / venue
playoff
```

This is sufficient to make the next reconciliation probe explicit rather than name/count based.

The probe must measure classification pairs such as:

```text
FBS vs FBS
FBS vs FCS
FCS vs FBS
other returned combinations
```

and preserve incomplete/canceled/rescheduled examples for identity review.

---

# Harness revision after V3 evidence

The research harness has been advanced to:

```text
DAILY_NCAAF_PHASE_B2_PROVIDER_COVERAGE_PROBE_V2
```

New diagnostics include:

- game classification-pair counts;
- classification null counts;
- season-type counts;
- incomplete-game examples;
- score-missing counts;
- start-time-TBD counts;
- explicit CFBD query-scope metadata;
- normalized null rates;
- PPA nullness by top play type;
- wallclock nullness by top play type.

The V2 harness remains research-only.

---

# Updated B.2-A verdict

## What is now verified

- authenticated CFBD access works with the environment-only secret pattern;
- representative `/games` and `/plays` requests succeed across early, disrupted, modern and current-season eras;
- no duplicate game IDs were observed in sampled season responses;
- no duplicate play IDs were observed in sampled PBP weeks;
- play text is nearly complete in the sampled rows;
- early-era `wallclock` is completely absent in sampled 2004/2010/2014 PBP;
- modern `wallclock` is highly populated but still incomplete;
- raw PPA nullness is too semantically mixed to treat as one data-quality metric;
- CFBD and cfbfastR season counts require explicit universe reconciliation.

## What is not yet verified

- exact `wallclock` transition year;
- full-season PBP completeness;
- exact identity of the one 2024 incomplete CFBD game;
- FBS/FCS classification-pair composition behind provider count deltas;
- roster/player/recruiting/transfer/coaching family coverage;
- cross-provider game/player match rates;
- prospective live publication/revision latency.

---

# Immediate next probe

After pulling the V2 harness, run:

```powershell
git pull origin docs/full-architecture-v1

python -m unittest tests.probes.test_provider_coverage_probe -v

python scripts/probes/provider_coverage_probe.py `
  --mode cfbd `
  --seasons 2015,2016,2017,2018,2019,2024,2026 `
  --cfbd-weeks 1,8,15 `
  --output local-data/probes/cfbd_followup_v2.json
```

The follow-up is intentionally narrow. It answers two unresolved questions before B.2-B expands into college-native roster/recruiting/transfer/coaching families:

1. when does usable `wallclock` begin appearing?;
2. what classification/status structure explains the CFBD season universe and the 2024 incomplete row?

---

# Current Phase B verdict

**B.2 remains ACTIVE.**

B.2-A is no longer credential-gated: the initial authenticated representative row probe is complete. A narrow B.2-A follow-up is active to locate timestamp-era and event-universe boundaries, after which B.2-B college-native family expansion can proceed.

Phase C remains intentionally blocked until B.2-B/B.2-C evidence is sufficient for provider-independent canonical contracts.
