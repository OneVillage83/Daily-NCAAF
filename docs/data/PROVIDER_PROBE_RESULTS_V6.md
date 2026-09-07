# Daily NCAAF — Provider Probe Results V6

**Phase:** B.2-B — CFBD College-Native Family Expansion  
**Status:** ERA SCAN SUBSTANTIALLY COMPLETE; 2025 retry and targeted scope/identity probes next  
**Probe generated:** 2026-08-31T07:23:43Z  
**Harness contract used:** `DAILY_NCAAF_PHASE_B2_CFBD_NATIVE_FAMILY_PROBE_V1`

---

## 1. Scope

This document records the local authenticated CFBD era scan across:

```text
2015-2026
```

for:

```text
transfer portal
talent composite
Elo / SRS / SP+ / FPI / CORE ratings
```

The run was research-only and emitted no API key.

The scan completed successfully through most of 2024, then encountered temporary HTTP 429 burst-rate responses. Those 429 responses are explicitly **not** interpreted as missing provider data or exhausted monthly quota.

---

## P-040 — Transfer portal observed coverage begins in 2021

Observed row counts:

| Season | Portal rows |
|---:|---:|
| 2015 | 0 |
| 2016 | 0 |
| 2017 | 0 |
| 2018 | 0 |
| 2019 | 0 |
| 2020 | 0 |
| 2021 | 1,770 |
| 2022 | 2,273 |
| 2023 | 2,502 |
| 2024 | 3,378 |
| 2025 | RATE-LIMITED |
| 2026 | RATE-LIMITED IN THIS RUN; prior B.2-B sample returned 4,470 |

The current empirical provider boundary is:

```text
PRE_2021 -> no portal rows in tested annual queries
2021_PLUS -> substantial portal coverage
```

This is an API coverage boundary, not proof that the NCAA transfer portal itself did not exist earlier and not proof of historical publication timing.

Locked consequence:

```text
CFBD portal records cannot be assumed available before 2021
```

A transfer remains a `PLAYER_PROGRAM_STINT` transition, not a new player identity.

### Modern portal missingness is meaningful

Even in covered years, destination and rating are not complete. For example:

```text
2021: 717 / 1,770 destination null; 1,447 / 1,770 rating null
2022: 906 / 2,273 destination null; 1,230 / 2,273 rating null
2023: 895 / 2,502 destination null; 1,611 / 2,502 rating null
2024: 724 / 3,378 destination null; 1,526 / 3,378 rating null
```

`transferDate` was fully populated in these measured covered seasons, but a transfer date is still an effective-event field rather than automatic proof of publication time.

---

## P-041 — Talent composite has a major historical entity-universe change

Observed talent row / unique-team counts:

| Season | Unique teams |
|---:|---:|
| 2015 | 232 |
| 2016 | 237 |
| 2017 | 157 |
| 2018 | 236 |
| 2019 | 231 |
| 2020 | 219 |
| 2021 | 224 |
| 2022 | 233 |
| 2023 | 238 |
| 2024 | 134 |
| 2025 | RATE-LIMITED |
| 2026 | prior B.2-B sample: 138 |

The measured FBS program universe was much smaller than these pre-2024 talent counts. Therefore:

```text
/talent historical response != automatically FBS-only
```

The 2024 response exactly matches the measured 134-team FBS count and the prior 2026 sample matches the 138-team FBS count. The exact scope-transition boundary is not yet locked because 2025 was rate-limited.

Next scope probe must compare talent team names/IDs directly against the season-specific FBS team universe rather than inferring classification from row count alone.

---

## P-042 — CORE public retrospective coverage begins in 2016

Observed CORE rows:

```text
2015:   0
2016: 128
2017: 130
2018: 130
2019: 130
2020: 127
2021: 130
2022: 131
2023: 133
2024: rate-limited in this run; prior sample returned 134
```

This independently matches current CFBD documentation stating that public retrospective CORE ratings begin with the 2016 season.

Locked consequence remains:

```text
CORE = retrospective/provider-derived research feature unless a contemporaneous snapshot was actually captured
```

Historical CORE does not become PIT-A merely because the endpoint exposes `throughWeek` and `modelVersion`.

---

## P-043 — Rating families have distinct entity and temporal semantics

Annual year-only results show materially different behavior by rating family.

### FPI

FPI closely tracks the measured FBS program universe in the sampled completed seasons:

```text
2015 128
2016 128
2017 130
2018 130
2019 130
2020 127
2021 130
2022 131
2023 133
2024 prior sample 134
2026 prior sample 138
```

This makes FPI a strong external benchmark/source candidate, while PIT availability still requires separate treatment.

### SP+

SP+ usually returns approximately the FBS universe plus one additional/null-conference row in these annual queries. Entity-universe reconciliation is required before canonical use.

### Elo

Year-only Elo generally returns near-FBS counts in historical completed seasons, but the API's year-only operation defaults to the latest available week. Therefore a year-only response is not a stable canonical weekly snapshot contract.

### SRS

SRS shows an important scope transition:

```text
2015 128
2016 128
2017 130
2018 130
2019 130
2020  77
2021 130
2022 261
2023 261
2024 265
```

The 2020 reduction is consistent with the disrupted COVID season but is not automatically complete coverage proof. The jump beginning in 2022 demonstrates that `/ratings/srs?year=...` cannot be assumed FBS-only. Current CFBD SRS records expose a `division` field, so later normalization must use explicit row-level entity/division semantics.

Locked consequence:

```text
DO NOT normalize rating families by row count alone
DO NOT assume all CFBD rating endpoints share one team universe
```

---

## P-044 — Temporary HTTP 429 exposed a probe-reliability requirement

The long sequential scan began receiving HTTP 429 responses during the 2024 rating block and across 2025/2026. The returned provider body explicitly stated that this was a short-period rate limit and not exhaustion of monthly API usage.

Therefore:

```text
HTTP 429 != missing dataset
HTTP 429 != empty coverage
HTTP 429 != monthly quota exhausted
```

Research and eventual production acquisition need request pacing, retry/backoff, and explicit transport-state recording.

For this audit, do not rerun the entire 2015-2026 scan. Only the unresolved 2025 slice needs a clean retry; prior successful 2024/2026 B.2-B measurements remain valid observations at their own `acquired_at` times.

---

## B.2-B current verdict

The broad annual source-family audit is now sufficient to stop indiscriminate endpoint scanning.

Verified constraints include:

1. portal coverage is empirically absent in annual queries through 2020 and begins substantially in 2021;
2. portal destination/rating fields remain incomplete even in modern covered seasons;
3. talent-composite historical responses have a changing/non-FBS-only entity universe before the modern period;
4. CORE public retrospective history begins in 2016;
5. Elo, SRS, SP+, FPI and CORE do not share one universal entity or temporal contract;
6. SRS year-only scope expands dramatically beginning in the observed 2022 response;
7. 429 transport failures must remain distinct from data coverage;
8. one clean 2025 retry is still required to complete the continuous era table.

After the 2025 retry, B.2-B should move to targeted identity/scope case studies rather than more broad annual harvesting.
