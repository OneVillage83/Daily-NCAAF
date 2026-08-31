# Daily NCAAF — CFBD College-Native Family Probe Specification V1

**Phase:** B.2-B — CFBD College-Native Family Expansion  
**Status:** INITIAL PASS COMPLETE; focused follow-up active  
**Contract:** `DAILY_NCAAF_PHASE_B2_CFBD_NATIVE_FAMILY_PROBE_V1`

---

## 1. Purpose

B.2-A established representative CFBD game/PBP behavior. B.2-B measures the college-football-native identity and state families that matter most to Daily-NCAAF:

```text
teams / conference affiliation
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

The goal is not to download the entire provider. The goal is to measure enough representative eras and identity/state behavior to constrain provider-independent Phase C contracts.

The initial representative run described by this specification is now complete. Its measured results are recorded in:

```text
docs/data/PROVIDER_PROBE_RESULTS_V5.md
```

The evidence-driven next pass is defined in:

```text
docs/data/CFBD_NATIVE_FAMILY_FOLLOWUP_PLAN_V1.md
```

---

## 2. Governing rules

1. All calls are read-only.
2. `CFBD_API_KEY` is read only from the environment.
3. The key value is never written to output.
4. Raw authenticated payloads remain local.
5. Checked-in evidence should be aggregate counts, null/duplicate measurements, field-era observations and documented conclusions.
6. Endpoint existence does not establish PIT eligibility.
7. Current retrospective API state does not prove historical publication state.
8. A zero-row family is classified by season/provider semantics before being labeled missing.
9. Provider IDs are crosswalk candidates, not canonical Daily-NCAAF identities.
10. Historical lines are not assumed to be a quote-by-quote sportsbook tape.

---

## 3. Initial representative eras

Initial seasons:

```text
2014
2018
2024
2026
```

Why:

- **2014** — CFP transition and pre-2018 `wallclock` era;
- **2018** — first empirically observed broadly populated CFBD `wallclock` season in B.2-A;
- **2024** — modern realignment/12-team CFP era with rich completed-season data;
- **2026** — current/live season-state behavior.

The first pass demonstrated that continuous-year follow-up is now required for portal/talent/rating era floors.

---

## 4. Representative roster programs

Initial roster sample:

```text
Alabama
Michigan
Notre Dame
Boise State
```

This deliberately spans major-conference, independent and non-power-program contexts. These are probe examples, not privileged production identities.

The next identity-specific pass must include known transfer players, multiple-transfer players, similar-name collisions, position/jersey changes and FBS/FCS movers.

---

## 5. Families and measurements

### 5.1 Teams

Endpoint:

```text
GET /teams/fbs?year=<year>
```

Measure rows, provider team-ID uniqueness, school/conference nullness and classification distribution.

Initial result: unique/non-null FBS team IDs in all representative seasons. See V5.

### 5.2 Historical conference affiliation

Endpoint:

```text
GET /conferences/affiliations?year=<year>&classification=fbs
```

Measure rows, unique team IDs, conference nullness, open-ended affiliation rows and classification distribution.

Historical affiliation truth remains separate from historical publication timing.

### 5.3 Rosters

Endpoint:

```text
GET /roster?year=<year>&team=<team>&classification=fbs
```

Measure player ID uniqueness, position/jersey/height/weight nullness and `recruitIds` linkage.

Initial result: provider player IDs were clean in sampled teams, while direct recruit linkage varied materially by team/era. Historical roster truth is not automatically pregame expected participation.

### 5.4 Recruiting

Endpoint:

```text
GET /recruiting/players?year=<year>&classification=HighSchool
```

Measure recruiting record ID uniqueness and nullable `athleteId`, commitment, ranking/rating/stars and position fields.

Initial result: direct `athleteId` linkage is useful but materially incomplete. No absent provider link may be silently replaced by a name-only merge.

### 5.5 Transfer portal

Endpoint:

```text
GET /player/portal?year=<year>
```

Measure rows, destination/date/rating/stars missingness, eligibility and origin/destination breadth.

Initial result: 2014/2018 returned zero rows while 2024/2026 were heavily populated. The exact provider availability floor is now a focused follow-up target.

### 5.6 Returning production

Endpoint:

```text
GET /player/returning?year=<year>
```

Measure rows/teams and PPA/usage missingness.

This remains a derived provider feature family and requires separate PIT/reconstruction treatment.

### 5.7 Coaches

Endpoint:

```text
GET /coaches?year=<year>
```

Measure coach provider-ID uniqueness and queried-year nested-season behavior.

The first pass did not establish cross-season coach-ID continuity and does not solve coordinator/play-caller history.

### 5.8 Talent composite

Endpoint:

```text
GET /talent?year=<year>
```

Measure rows, unique teams and missing values.

Initial result: 2014 returned zero, 2018 returned a universe much larger than FBS, and 2024/2026 matched FBS-sized counts. Historical scope must be resolved before feature use.

### 5.9 Rankings

Endpoint:

```text
GET /rankings?year=<year>&seasonType=both
```

Measure snapshot rows, week labels, poll names and nested rank counts.

Initial result: some historical seasons contain multiple snapshot rows sharing week `1`; `(season, week)` alone is therefore not accepted as canonical ranking identity.

### 5.10 Ratings

Endpoints:

```text
GET /ratings/elo
GET /ratings/srs
GET /ratings/sp
GET /ratings/fpi
GET /ratings/core
```

Measure rows, unique teams and conference nullness by family/era.

Initial result: rating families have materially different coverage, entity-universe and current-season readiness semantics. Each family requires its own PIT/provenance contract.

### 5.11 Historical lines

Endpoint:

```text
GET /lines?year=<year>&week=<week>&seasonType=regular
```

Measure game rows, games with lines, nested line observations, provider names, spread/total/opening/moneyline coverage.

Initial result: field richness changes sharply by era and raw provider-name aliases exist. Historical line responses remain market evidence rather than timestamped quote tape.

---

## 6. Secret and output policy

`CFBD_API_KEY` remains environment-only. The generated aggregate JSON contains no key value.

Recommended local output:

```text
local-data/probes/
```

which remains ignored by Git.

---

## 7. Initial run — completed

```powershell
python scripts/probes/cfbd_native_family_probe.py `
  --seasons 2014,2018,2024,2026 `
  --teams "Alabama,Michigan,Notre Dame,Boise State" `
  --output local-data/probes/cfbd_native_families_v1.json
```

The helper tests passed locally before the authenticated run.

---

## 8. Next run

Do not repeat the full initial matrix. Use the focused plan:

```text
docs/data/CFBD_NATIVE_FAMILY_FOLLOWUP_PLAN_V1.md
```

Immediate next call set:

```powershell
python scripts/probes/cfbd_native_family_probe.py `
  --seasons 2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025,2026 `
  --families "portal,talent,ratings" `
  --output local-data/probes/cfbd_native_era_scan_v1.json
```

This bounded scan locates the remaining availability/scope transitions before actual player/coach identity reconciliation begins.

---

## 9. B.2-B completion gate

B.2-B is sufficiently measured when:

1. major native families have explicit availability eras;
2. team/program/recruit/player/coach identity strengths and gaps are quantified;
3. derived ratings/returning-production/talent families have explicit PIT classifications;
4. historical market evidence remains separated from timestamped market tape;
5. remaining questions are identity/reconciliation problems rather than vague provider-coverage assumptions.

At that point move into B.2-C instead of expanding provider calls indefinitely.
