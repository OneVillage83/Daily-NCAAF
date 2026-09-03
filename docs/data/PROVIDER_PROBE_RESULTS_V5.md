# Daily NCAAF — Provider Probe Results V5

**Phase:** B.2 — Empirical Coverage & PIT Probe  
**Status:** B.2-B INITIAL CFBD COLLEGE-NATIVE FAMILY PASS COMPLETE; focused era/scope follow-up active  
**Probe generated:** 2026-08-31T06:58:31Z  
**Harness contract used:** `DAILY_NCAAF_PHASE_B2_CFBD_NATIVE_FAMILY_PROBE_V1`  
**Supersedes for current B.2 status:** `PROVIDER_PROBE_RESULTS_V4.md`; V1-V4 remain prior audit records.

---

## 1. What changed since V4

V4 closed the representative CFBD games/PBP audit strongly enough to begin B.2-B.

The B.2-B harness and its local unit tests were then executed successfully:

```text
Ran 8 tests in 0.001s
OK
```

The authenticated family probe queried representative seasons:

```text
2014
2018
2024
2026
```

and roster samples:

```text
Alabama
Michigan
Notre Dame
Boise State
```

across:

```text
teams
historical conference affiliations
rosters
recruiting
transfer portal
returning production
coaches
talent composite
rankings
Elo / SRS / SP+ / FPI / CORE
historical lines
```

Every family call in this pass returned HTTP 200. A 200 response containing zero rows is treated as an observed empty family for that query, not automatically as a source defect.

---

# P-033 — FBS team identity is clean in all four representative seasons

Observed `/teams/fbs` results:

| Season | Rows | Unique IDs | Duplicate IDs | School nulls | Conference nulls |
|---:|---:|---:|---:|---:|---:|
| 2014 | 128 | 128 | 0 | 0 | 0 |
| 2018 | 130 | 130 | 0 | 0 | 0 |
| 2024 | 134 | 134 | 0 | 0 | 0 |
| 2026 | 138 | 138 | 0 | 0 | 0 |

All returned classifications were `fbs`.

### Interpretation

This is strong empirical support for CFBD as a primary provider crosswalk source for FBS program-season identity.

It does **not** make CFBD team IDs canonical Daily-NCAAF IDs. The canonical hierarchy remains:

```text
SCHOOL
  -> PROGRAM
      -> PROGRAM_SEASON
          -> provider crosswalk(s)
```

Provider IDs remain externally sourced identities that can be versioned/reconciled rather than becoming the internal primary key by definition.

---

# P-034 — Historical conference affiliation is structurally strong but retrospective

Observed `/conferences/affiliations?year=<year>&classification=fbs`:

| Season | Rows | Unique team IDs | Conference nulls | Open-ended rows |
|---:|---:|---:|---:|---:|
| 2014 | 128 | 128 | 0 | 8 |
| 2018 | 130 | 130 | 0 | 8 |
| 2024 | 134 | 134 | 0 | 124 |
| 2026 | 138 | 138 | 0 | 138 |

### Interpretation

The family aligns cleanly with the tested FBS team universe and is highly valuable for historical program-state reconstruction.

The changing `endYear`/open-ended behavior also reinforces that the API is returning the provider's **current historical affiliation truth**, including later-known realignment boundaries. It does not prove that a future affiliation end was historically knowable at an earlier prediction date.

Current classification:

```text
historical conference affiliation -> strong PIT-B reconstruction candidate
publication-time semantics         -> not established
```

Phase C should preserve affiliation stints explicitly rather than storing one mutable `conference` field on a program.

---

# P-035 — Roster provider IDs are clean, but recruit linkage is incomplete and era/team dependent

Across the four sampled programs, every roster query returned unique non-null player IDs with no duplicate IDs.

### Roster -> recruit linkage

Share of roster rows with non-empty `recruitIds`:

| Season | Alabama | Michigan | Notre Dame | Boise State |
|---:|---:|---:|---:|---:|
| 2014 | 61.6% | 59.2% | 59.5% | 52.3% |
| 2018 | 45.8% | 53.1% | 53.6% | 33.0% |
| 2024 | 59.4% | 65.5% | 69.4% | 78.3% |
| 2026 | 72.5% | 75.4% | 85.8% | 79.8% |

`recruitIds` itself was not null in these responses; many rows instead contained an empty list.

### Other roster fields

Modern 2024/2026 height/weight/jersey/position completeness was very high in the sampled programs. Older 2014 weight coverage was materially weaker, including 44 missing Alabama weights, 47 Boise State, 47 Michigan and 37 Notre Dame.

### Locked consequence

```text
roster player ID -> strong provider identity evidence
recruitIds       -> useful linkage evidence
empty recruitIds -> unresolved linkage, NOT proof of no recruiting record
```

Daily-NCAAF must support unresolved recruit/player relationships rather than forcing name-based merges.

---

# P-036 — Recruiting `athleteId` linkage is materially incomplete

Observed `/recruiting/players` linkage:

| Season | Recruit rows | `athleteId` linked | Link rate | `committedTo` present | rating/stars present |
|---:|---:|---:|---:|---:|---:|
| 2014 | 3,772 | 1,786 | 47.4% | 65.1% | 100.0% |
| 2018 | 4,348 | 2,062 | 47.4% | 81.8% | 89.5% |
| 2024 | 4,236 | 2,656 | 62.7% | 82.8% | 87.2% |
| 2026 | 3,987 | 2,221 | 55.7% | 92.7% | 85.6% |

Recruit record IDs themselves were unique and non-null in all tested seasons.

### Identity consequence

This empirically validates the earlier F-3 rule:

```text
recruiting record != college player identity
```

`athleteId` is strong direct provider evidence when present, but its absence is common enough that the canonical system requires an explicit reconciliation state such as:

```text
DIRECT_PROVIDER_LINK
HIGH_CONFIDENCE_RECONCILED
AMBIGUOUS
UNRESOLVED
REJECTED_MATCH
```

Name + school alone must never silently create a canonical merge.

---

# P-037 — Transfer portal has a real era boundary that still needs locating

Observed `/player/portal` rows:

```text
2014 -> 0
2018 -> 0
2024 -> 3,378
2026 -> 4,470
```

For populated seasons:

| Season | Destination known | Transfer date known | Rating known | Stars known |
|---:|---:|---:|---:|---:|
| 2024 | 78.6% | 100.0% | 54.8% | 88.7% |
| 2026 | 78.0% | 100.0% | 64.7% | 86.8% |

2024 eligibility counts were dominated by `Immediate`, with `Withdrawn` and a small `TBD` tail. 2026 additionally included a very small `PendingAppeal` state.

### Locked consequences

1. missing destination is a meaningful transfer-state value, not a broken row;
2. transfer date is extremely complete in these populated samples;
3. ratings are far less complete than stars;
4. portal status/eligibility must be preserved as observed state;
5. 2014/2018 zeros establish that the family cannot be assumed available across the full historical training window.

### Next measurement

Probe 2019-2025 continuously to locate the first non-zero provider season and determine whether the floor reflects real portal-era coverage or a provider backfill boundary.

---

# P-038 — Returning production is broad and internally complete, but remains a derived feature

Observed rows:

```text
2014 -> 125 teams
2018 -> 130 teams
2024 -> 133 teams
2026 -> 136 teams
```

In all tested returned rows:

```text
conference nulls  = 0
totalPPA nulls    = 0
percentPPA nulls  = 0
usage nulls       = 0
```

This is useful coverage evidence, but returning production is still a provider-derived state rather than raw truth.

Locked classification:

```text
useful research/baseline family
PIT eligibility not established
prefer reconstructable Daily-NCAAF rolling/roster-conditioned equivalents where feasible
```

A current retrospective endpoint response must not be inserted directly into a historical prediction snapshot merely because the season parameter is historical.

---

# P-039 — Head-coach IDs are clean in year-filtered responses, but continuity is not yet proven

Observed coach rows/unique IDs:

```text
2014 -> 132 / 132
2018 -> 139 / 139
2024 -> 152 / 152
2026 -> 138 / 138
```

No duplicate provider IDs were observed. Every returned record contained the queried year in its nested `seasons` list.

However, `career_season_entries` equaled returned rows in every year-filtered sample. Therefore this pass does **not** establish multi-season coach-ID continuity or complete career history from a single query.

The architecture remains:

```text
PERSON -> COACH -> COACH_ROLE_STINT
```

and coordinator/play-caller history remains a separate unresolved source family.

---

# P-040 — Talent composite has a scope/era anomaly that cannot be normalized by row count alone

Observed `/talent` rows:

```text
2014 ->   0
2018 -> 236
2024 -> 134
2026 -> 138
```

The 2024/2026 counts line up with the measured FBS team counts, while 2018 is dramatically broader than the 130-team FBS list.

This must not be "fixed" by truncation or by assuming extra rows are duplicates; all 236 returned team names were unique in the probe summary.

Next follow-up must compare the talent-team universe with `/teams/fbs` and determine whether the historical family includes additional classifications or a provider-specific historical scope.

Current classification:

```text
2014 -> unavailable in tested query
2018 -> available, scope unresolved
2024+ -> broad FBS-looking coverage in tested rows
PIT   -> derived/external rating; separate contract required
```

---

# P-041 — Rating families have distinct era and universe semantics

Observed row counts:

| Season | Elo | SRS | SP+ | FPI | CORE |
|---:|---:|---:|---:|---:|---:|
| 2014 | 130 | 128 | 129 | 128 | 0 |
| 2018 | 131 | 130 | 131 | 130 | 130 |
| 2024 | 134 | 265 | 135 | 134 | 134 |
| 2026 | 16 | 0 | 139 | 138 | 0 |

### CORE

The current CFBD methodology documentation states that public retrospective CORE begins with the 2016 season and explicitly describes historical ratings as retrospective methodology results rather than a record of what the model would have reported at that historical time.

Therefore the observed 2014 zero is consistent with the documented coverage floor, while the 2026 zero is a current-season readiness state rather than evidence that the family is permanently unavailable.

Locked classification:

```text
CORE historical -> PIT-C retrospective benchmark/research unless a snapshot boundary is independently captured
```

### Elo

The CFBD API documents that Elo without a `week` parameter defaults to the latest available week. The 2026 response containing only 16 teams while FPI/SP+ cover the broad current FBS universe demonstrates that current-season rating readiness differs by family.

Historical feature contracts must specify the intended week/snapshot explicitly rather than querying `year` alone.

### SRS

The current SRS endpoint exposes `year`, `team` and `conference` filters but no division/classification filter. Therefore the 265-row 2024 response cannot be compared directly with 134 FBS teams.

The follow-up must measure `division` and FBS-team overlap before assigning a coverage grade.

### SP+ / FPI

These families show broad coverage in all four tested eras, but they remain external/provider model outputs. Their historical publication/revision semantics still require conservative PIT classification.

### General rating rule

```text
rating family name != common temporal semantics
```

Every rating family needs its own:

```text
coverage era
entity universe
snapshot boundary
model version/provenance
PIT class
```

---

# P-042 — Rankings are rich historically and season-stage dependent

Observed ranking snapshot rows:

```text
2014 -> 17
2018 -> 16
2024 -> 17
2026 -> 1
```

Historical responses included AP, Coaches, FCS and lower-division polls plus CFP committee snapshots where applicable. The 2026 response currently contains only one snapshot row, consistent with the early season state.

Several historical years reported two snapshot rows labeled week `1`, so canonical ranking identity must not assume `(season, week)` alone is unique.

The next ranking-specific probe should retain additional snapshot dimensions before Phase C defines the key.

---

# P-043 — Historical lines are useful but are not market tape

### Week-1 game coverage

| Season | Game rows | Games with >=1 line | Coverage |
|---:|---:|---:|---:|
| 2014 | 84 | 81 | 96.4% |
| 2018 | 88 | 84 | 95.5% |
| 2024 | 125 | 110 | 88.0% |
| 2026 | 144 | 144 | 100.0% |

### Field behavior

2014:

```text
132 line observations
spread present on all 132
58 over/under null
all opening spread/total fields null
all moneylines null
```

2018:

```text
215 line observations
spread present on all 215
only 8 over/under null
all opening spread/total fields null
all moneylines null
```

2024:

```text
190 line observations
spread and over/under present on all
opening spread present on 46.3%
opening total present on 46.3%
moneyline present on 41.1%
```

2026:

```text
236 line observations
spread and over/under present on all
opening spread present on 75.0%
opening total present on 55.1%
moneyline present on 64.0%
```

### Sportsbook identity normalization

The same 2026 response contained both:

```text
DraftKings
Draft Kings
```

as provider names.

This empirically confirms that sportsbook identity requires a canonical alias/crosswalk layer in `Daily-Data-Core` rather than raw provider-string keys.

### Locked market consequence

```text
CFBD historical lines = useful historical market evidence / benchmark
CFBD historical lines != exact timestamped sportsbook quote tape
```

No observation timestamps were established by this probe, and opening/current/final-like fields do not reconstruct all intermediate price changes.

`Daily-Data-Core` remains authoritative for timestamped sportsbook observations, no-vig calculation, quote chronology and market-source identity.

---

# P-044 — First B.2-B family classifications

These classifications are intentionally provisional pending focused follow-up:

| Family | Current classification |
|---|---|
| FBS teams | PRIMARY PROVIDER CROSSWALK CANDIDATE |
| conference affiliations | STRONG PIT-B HISTORICAL RECONSTRUCTION CANDIDATE |
| rosters | PRIMARY HISTORICAL IDENTITY/ROSTER TRUTH CANDIDATE; pregame availability not implied |
| recruiting | PRIMARY RECRUITING EVIDENCE; identity linkage incomplete |
| transfer portal | PRIMARY MODERN TRANSFER EVIDENCE; historical floor unresolved |
| returning production | DERIVED RESEARCH/BASELINE FAMILY; PIT unresolved |
| coaches | PRIMARY HEAD-COACH EVIDENCE CANDIDATE; role-history depth incomplete |
| talent composite | DERIVED TALENT FAMILY; era/scope unresolved |
| rankings | PRIMARY POLL EVIDENCE CANDIDATE; snapshot-key semantics need refinement |
| Elo/SRS/SP+/FPI | EXTERNAL RATING FAMILIES; separate era/PIT contracts required |
| CORE | RETROSPECTIVE/PIT-C research benchmark unless prospectively captured |
| historical lines | HISTORICAL MARKET EVIDENCE only; timestamped tape remains Daily-Data-Core |

---

# B.2-B immediate follow-up

The first family pass is complete enough to narrow the next API use rather than repeat broad calls.

Next scan:

```text
2015-2026
families = portal,talent,ratings
```

Goals:

1. locate the first non-zero transfer-portal season;
2. locate the talent-composite availability/scope transition;
3. map CORE/Elo/SRS/SP+/FPI row-count readiness by year;
4. identify seasons where rating universe materially exceeds the FBS team universe;
5. avoid treating current-season structural zeros as historical gaps.

After that, use a separate targeted identity/reconciliation pass for:

- recruit -> roster player links;
- multi-season player continuity;
- transfers across program stints;
- head-coach ID continuity;
- ranking snapshot identity;
- CFBD <-> cfbfastR game/player reconciliation.

---

# Current Phase B verdict

**B.2 remains ACTIVE.**

B.2-A representative games/PBP is core-complete. B.2-B's first college-native family pass is complete and has exposed the exact era/scope questions that now deserve targeted measurements.

Phase C remains intentionally blocked until identity/reconciliation and source/PIT contracts are precise enough to design provider-independent canonical tables without guessing.
