# Daily NCAAF — CFBD College-Native Family Probe Specification V1

**Phase:** B.2-B — CFBD College-Native Family Expansion  
**Status:** ACTIVE  
**Contract:** `DAILY_NCAAF_PHASE_B2_CFBD_NATIVE_FAMILY_PROBE_V1`

---

## 1. Purpose

B.2-A established representative CFBD game/PBP behavior. B.2-B now measures the college-football-native identity and state families that matter most to Daily-NCAAF:

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

Default seasons:

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

Later passes may add 2004/2010/2015/2020/2025 where a family’s observed floor or transition requires it.

---

## 4. Representative roster programs

Default roster sample:

```text
Alabama
Michigan
Notre Dame
Boise State
```

This deliberately spans major-conference and independent/non-power-program contexts. These are probe examples, not privileged production identities.

A later identity-specific pass must include known transfer players, multiple-transfer players, similar-name collisions, position/jersey changes and FBS/FCS movers.

---

## 5. Families and measurements

### 5.1 Teams

Endpoint:

```text
GET /teams/fbs?year=<year>
```

Measure:

- rows;
- unique provider team IDs;
- duplicate IDs;
- school nullness;
- conference nullness;
- classification distribution.

### 5.2 Historical conference affiliation

Endpoint:

```text
GET /conferences/affiliations?year=<year>&classification=fbs
```

Measure:

- rows;
- unique team IDs;
- team-ID nullness;
- conference nullness;
- open-ended affiliation rows;
- classification distribution.

This family is especially important for program-season identity and realignment.

### 5.3 Rosters

Endpoint:

```text
GET /roster?year=<year>&team=<team>&classification=fbs
```

Measure:

- rows;
- player ID uniqueness;
- position/jersey/height/weight nullness;
- `recruitIds` presence/non-empty linkage.

Historical roster truth is not automatically pregame expected participation.

### 5.4 Recruiting

Endpoint:

```text
GET /recruiting/players?year=<year>&classification=HighSchool
```

Measure:

- recruiting record ID uniqueness;
- nullable `athleteId` linkage rate;
- commitment/ranking/rating/stars/position missingness.

`athleteId` is a useful provider linkage signal, but Daily-NCAAF may not auto-merge records when the linkage is absent.

### 5.5 Transfer portal

Endpoint:

```text
GET /player/portal?year=<year>
```

Measure:

- rows;
- destination nullness;
- transfer-date nullness;
- rating/stars missingness;
- eligibility distribution;
- unique origins/destinations.

A transfer row does not create a new canonical player identity.

### 5.6 Returning production

Endpoint:

```text
GET /player/returning?year=<year>
```

Measure:

- rows and unique teams;
- conference nullness;
- total/percent PPA missingness;
- usage missingness.

This remains a derived provider feature family and needs separate PIT/reconstruction treatment.

### 5.7 Coaches

Endpoint:

```text
GET /coaches?year=<year>
```

Measure:

- coach provider ID uniqueness;
- whether the queried year appears in returned nested seasons;
- career-season entry counts;
- deprecated `hireDate` missingness only as an observed source field.

The architecture remains `PERSON -> COACH -> COACH_ROLE_STINT`; a current provider head-coach record does not solve coordinator/play-caller history.

### 5.8 Talent composite

Endpoint:

```text
GET /talent?year=<year>
```

Measure rows, unique teams and missing values.

Talent composite is a derived external rating and must receive its own feature/PIT contract.

### 5.9 Rankings

Endpoint:

```text
GET /rankings?year=<year>&seasonType=both
```

Measure snapshot rows, weeks, poll families and nested rank rows.

Published poll snapshots may be useful historical state, but exact release timing still needs a defensible availability rule.

### 5.10 Ratings

Initial endpoints:

```text
GET /ratings/elo
GET /ratings/srs
GET /ratings/sp
GET /ratings/fpi
GET /ratings/core
```

Measure rows, unique teams and conference missingness by era.

Special caution:

- rating families differ in historical coverage and semantics;
- CFBD documents CORE historical ratings as retrospective methodology output, not a record of what CORE would have said at that historical time;
- no rating is automatically PIT-safe merely because `year` or `week` exists.

### 5.11 Historical lines

Initial bounded query:

```text
GET /lines?year=<year>&week=1&seasonType=regular
```

Measure:

- game rows;
- games with one or more line observations;
- line observation count;
- provider distribution;
- spread/total/opening-field/moneyline missingness.

Locked interpretation:

```text
historical line response != timestamped historical quote tape
```

Daily-Data-Core remains the owner of sportsbook quote snapshots and market chronology.

---

## 6. Failure and quota behavior

The probe must not abort the entire audit because one endpoint returns an access-tier, rate-limit or family-specific error.

Each family records its HTTP status/error independently so we can distinguish:

```text
AVAILABLE
EMPTY
CREDENTIAL_OR_TIER_GATED
RATE_LIMITED
PROVIDER_ERROR
```

without silently converting those states into missing data.

---

## 7. Local run

After pulling the branch and confirming `CFBD_API_KEY` remains set in the PowerShell session:

```powershell
python -m unittest discover -s tests/probes -p "test_cfbd_native_family_probe.py" -v

python scripts/probes/cfbd_native_family_probe.py `
  --seasons 2014,2018,2024,2026 `
  --teams "Alabama,Michigan,Notre Dame,Boise State" `
  --output local-data/probes/cfbd_native_families_v1.json
```

The JSON remains under ignored `local-data/`.

If quota/tier limits make the all-family pass too expensive, use `--families` to run smaller groups, for example:

```powershell
python scripts/probes/cfbd_native_family_probe.py `
  --seasons 2014,2018,2024,2026 `
  --families teams,conferences,rosters,recruiting,portal,returning `
  --output local-data/probes/cfbd_native_identity_v1.json
```

---

## 8. B.2-B completion criteria

B.2-B does not close when the endpoints merely return 200.

It closes only when we can describe, by family and era:

- coverage floors and structural zeros;
- identifier quality;
- major missingness;
- revision/PIT classification or conservative exclusion;
- identity implications;
- whether the provider is primary, secondary, benchmark-only or unsuitable for that family.

The resulting evidence feeds B.2-C cross-provider reconciliation and then Phase C canonical schema design.
