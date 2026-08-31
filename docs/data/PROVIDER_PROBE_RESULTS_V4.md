# Daily NCAAF — Provider Probe Results V4

**Phase:** B.2 — Empirical Coverage & PIT Probe  
**Status:** B.2-A CORE GAMES/PBP AUDIT COMPLETE; B.2-B college-native family expansion active  
**Probe generated:** 2026-08-31T06:01:29Z  
**Harness contract used:** `DAILY_NCAAF_PHASE_B2_PROVIDER_COVERAGE_PROBE_V2`  
**Supersedes for current B.2 status:** `PROVIDER_PROBE_RESULTS_V3.md`; V1-V3 remain prior audit records.

---

## 1. What changed since V3

The focused authenticated CFBD follow-up completed successfully after the V2 harness and its eight unit tests were pulled locally.

The local test run reported:

```text
Ran 8 tests in 0.001s
OK
```

The authenticated probe then queried:

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

This run closes the two narrow B.2-A questions left by V3:

1. locate the observed `wallclock` era transition;
2. explain the 2024 incomplete game and characterize the CFBD FBS query universe.

---

# P-027 — The observed `wallclock` transition occurs between 2017 and 2018

Sampled null rates by season/week:

| Season | Week 1 | Week 8 | Week 15 | Interpretation |
|---:|---:|---:|---:|---|
| 2015 | 100.00% | 100.00% | 100.00% | absent in all sampled rows |
| 2016 | 100.00% | 100.00% | 100.00% | absent in all sampled rows |
| 2017 | 100.00% | 100.00% | 100.00% | absent in all sampled rows |
| 2018 | 0.3406% | 0.0983% | 0.0000% | suddenly highly populated |
| 2019 | 0.0929% | 0.0444% | 0.6562% | highly populated with small gaps |

Together with V3:

```text
2014 sampled wallclock = 100% null
2015 sampled wallclock = 100% null
2016 sampled wallclock = 100% null
2017 sampled wallclock = 100% null
2018 sampled wallclock = mostly populated
```

The empirical architecture boundary is therefore:

```text
CFBD historical PBP wallclock era candidate:
PRE_2018  -> unavailable in tested strata
2018_PLUS -> generally available but nullable
```

This is a **coverage-era boundary**, not a claim that `wallclock` is an original provider-publication timestamp.

Locked consequence:

```text
wallclock may describe event timing where populated
wallclock does not replace acquired_at
wallclock does not prove historical publication availability
```

Prospective B.2-D capture is still required before assigning live PIT publication semantics.

---

# P-028 — The lone incomplete 2024 CFBD FBS game is Liberty at App State

The V2 harness identified the only incomplete 2024 row as:

```text
game id:       401640992
week:          5
away:          Liberty
home:          App State
start_date:    2024-09-28T19:30:00Z
completed:     false
scores:        null / null
```

This is not an unexplained provider defect. Official App State and Liberty records confirm that the September 28, 2024 game was canceled because of Hurricane Helene and was not rescheduled.

Canonical consequence:

```text
scheduled game object != completed game
incomplete historical row != automatically missing result
```

Phase C must preserve event lifecycle/status semantics so canceled/postponed/rescheduled games are represented explicitly rather than forced into played-game assumptions.

---

# P-029 — `classification=fbs` means an FBS-involved game universe, not only FBS-vs-FBS

Observed season composition:

| Season | Total rows | FBS vs FBS | FBS vs FCS | FCS vs FBS |
|---:|---:|---:|---:|---:|
| 2015 | 870 | 765 | 105 | 0 |
| 2016 | 873 | 760 | 113 | 0 |
| 2017 | 874 | 776 | 98 | 0 |
| 2018 | 884 | 772 | 111 | 1 |
| 2019 | 888 | 774 | 114 | 0 |
| 2024 | 920 | 799 | 121 | 0 |
| 2026 | 888 | 761 | 127 | 0 |

Therefore the CFBD query:

```text
classification=fbs
```

must be interpreted as an **FBS-involved event scope** in the observed responses, not as a strict `home=fbs AND away=fbs` filter.

This explains why cross-provider reconciliation must compare explicit game identities and classification semantics rather than raw season totals.

---

# P-030 — 2026 demonstrates live season-state evolution

The earlier 2026 probe had returned zero completed games and zero PBP in the sampled weeks. The August 31 follow-up now observed:

```text
2026 games returned       888
completed                   8
incomplete                880
week 1 PBP rows          1,412
week 1 games with PBP        8
week 8 PBP                   0
week 15 PBP                  0
```

This is valuable prospective evidence that the provider changes as the live season begins.

However, this one later snapshot does not tell us when each provider row first appeared or how corrections propagate. B.2-D must preserve repeated raw observations with `acquired_at` and hashes.

---

# P-031 — Overall PPA nullness is dominated by semantic non-applicability

The V2 probe measured PPA nullness by play type.

Across representative seasons, ordinary scrimmage plays are typically near complete. Examples from 2015 week 1:

```text
Rush                 3 / 8,573 null   = 0.035%
Pass Reception       7 / 4,279 null   = 0.164%
Pass Incompletion    0 / 2,967 null   = 0.000%
Sack                  1 /   482 null   = 0.208%
```

while many non-scrimmage/administrative families are structurally 100% null:

```text
Kickoff
Punt
Penalty
Timeout
End Period
```

Similar behavior appears in later sampled seasons.

Therefore:

```text
PPA IS NULL
```

must never be treated as a generic invalid-play flag.

Future feature contracts need an explicit PPA eligibility rule by normalized play family.

---

# P-032 — Modern wallclock missingness is not confined to one play family

The 2024 week-1 sample showed `wallclock` gaps across ordinary and administrative play types, including rushes, receptions, incompletions, penalties, punts, timeouts, kickoffs, sacks and touchdowns.

This means a modern missing `wallclock` value cannot be safely imputed merely from play type.

Canonical event time must therefore remain decomposed into source observations rather than requiring one provider field.

---

# B.2-A final verdict

The **core games/PBP representative audit is complete enough to advance**.

Verified constraints now include:

1. authenticated CFBD historical/current games and PBP access works across the tested eras;
2. no duplicate game IDs were observed in sampled season responses;
3. no duplicate play IDs were observed in sampled weeks;
4. play text is nearly complete in the measured samples;
5. `wallclock` is absent through the tested 2017 strata and becomes broadly available in 2018;
6. `wallclock` remains nullable and is not historical publication proof;
7. PPA nullness is play-family dependent rather than a generic coverage defect;
8. FBS query scope includes FBS-vs-FCS games;
9. the one incomplete 2024 game is a real canceled event rather than an unexplained missing final;
10. current-season provider state evolves over time, reinforcing immutable acquisition requirements.

This does **not** mean all games/PBP questions are finished. Full-season completeness, live revisions, cross-provider identity rates and player-stat associations remain later B.2 work. It means those questions no longer block moving into the next source families.

---

# B.2-B — college-native family expansion begins

The next bounded probe family covers:

```text
teams / historical conference affiliation
rosters
recruiting
transfer portal
returning production
coaches
talent composite
rankings
ratings
historical lines
```

Primary measurements include:

- stable provider IDs and duplicates;
- player/recruit linkage via `recruitIds` and recruiting `athleteId`;
- roster field missingness;
- transfer destination/date/rating/eligibility missingness;
- historical family-era zeros versus real gaps;
- coach-season identity behavior;
- team/conference realignment representation;
- rating-family coverage by era;
- betting-provider and field availability without misclassifying historical lines as timestamped quote tape.

Historical ratings and line artifacts remain subject to PIT classification even when rows exist.

---

# Current Phase B verdict

**B.2 remains ACTIVE.**

B.2-A core games/PBP representative measurement is now complete. B.2-B authenticated college-native family measurement is the active next workstream. B.2-C cross-provider identity reconciliation, B.2-D prospective live revision capture and B.2-E availability-source trials remain before Phase C.
