# Daily NCAAF — CFBD Native Family Follow-up Plan V1

**Phase:** B.2-B — CFBD College-Native Family Expansion  
**Status:** ACTIVE  
**Purpose:** Convert the broad first-pass family probe into a narrow set of era/scope measurements before identity reconciliation and Phase C.

---

## 1. Why a focused follow-up is needed

The first B.2-B run established that most candidate families are accessible and useful, but it also exposed several non-uniform behaviors:

- transfer portal rows are zero in 2014/2018 but large in 2024/2026;
- talent composite is zero in 2014, unexpectedly broad in 2018, and FBS-sized in 2024/2026;
- CORE, Elo, SRS, SP+ and FPI have materially different historical/current-season readiness;
- current rating endpoints do not all expose the same entity-universe filters;
- historical line fields change materially by era;
- recruit/player linkage is useful but incomplete.

The next pass should answer those specific questions rather than repeating all families.

---

## 2. Follow-up A — portal/talent/rating era scan

Use the existing research harness:

```text
scripts/probes/cfbd_native_family_probe.py
```

with:

```text
seasons = 2015 through 2026
families = portal,talent,ratings
```

PowerShell:

```powershell
python scripts/probes/cfbd_native_family_probe.py `
  --seasons 2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025,2026 `
  --families "portal,talent,ratings" `
  --output local-data/probes/cfbd_native_era_scan_v1.json
```

### Questions

#### Transfer portal

Measure the first season with non-zero rows and the growth pattern thereafter.

Do not assume the first non-zero provider season equals the historical beginning of the NCAA transfer portal. The result may reflect provider backfill scope.

#### Talent composite

Locate the transition from zero historical availability to populated data and identify years where the returned team count materially exceeds the FBS-team count measured for the same year.

Do not truncate or discard extra teams until their classification/scope is understood.

#### Ratings

Track annual row counts for:

```text
Elo
SRS
SP+
FPI
CORE
```

and distinguish:

```text
NOT_YET_APPLICABLE
HISTORICALLY_UNAVAILABLE
AVAILABLE_WITH_NARROW_CURRENT_SAMPLE
AVAILABLE_BROAD
ENTITY_UNIVERSE_UNRESOLVED
```

CORE must remain retrospective/PIT-C unless a contemporaneous snapshot is captured. Elo year-only queries must not be treated as an explicit historical week because the endpoint defaults to the latest available week when `week` is omitted.

---

## 3. Follow-up B — rating-universe refinement

After Follow-up A identifies anomalous years, extend the research harness or use a targeted diagnostic to compare rating team names against the corresponding `/teams/fbs?year=` universe.

Required metrics:

```text
rating rows
unique rating teams
FBS team count
rating teams matching FBS names
rating teams not matching FBS names
FBS teams absent from rating response
duplicate rating-team rows
```

For SRS additionally measure:

```text
division distribution
conference nullness
```

Reason: the current SRS operation does not expose a classification query parameter, so an SRS year response may represent a broader universe than FBS.

---

## 4. Follow-up C — recruit/player identity cases

The aggregate linkage rates prove that direct provider linkage is incomplete. The next identity pass must use representative actual entities rather than only counts.

Required cases:

```text
same-program multi-season player
one-transfer player
multiple-transfer player
recruit with direct athleteId
recruit without athleteId but later college roster presence
similar-name collision
position change
jersey-number change
FBS <-> FCS mover where available
```

For each case preserve:

```text
CFBD recruit record ID
CFBD athlete/player ID
roster-season appearances
recruitIds
portal origin/destination
program-season stints
match method
match confidence
conflicting evidence
```

No name-only automatic merge is permitted.

---

## 5. Follow-up D — coach continuity

The year-filtered coach response returned clean IDs but only one matching nested season entry per returned row in the initial probe.

Measure selected multi-year head coaches across adjacent seasons to determine:

```text
same person -> same CFBD coach ID?
team change -> same CFBD coach ID?
interim season behavior?
name change/format behavior?
```

This validates the provider crosswalk for:

```text
PERSON -> COACH -> COACH_ROLE_STINT
```

It does not replace the separate coordinator/play-caller source audit.

---

## 6. Follow-up E — ranking snapshot identity

Historical ranking responses showed multiple snapshot rows sharing week `1` in some seasons.

Before Phase C, inspect the underlying ranking snapshot fields and determine which dimensions distinguish those rows.

Do not define ranking identity as only:

```text
(year, week)
```

until uniqueness is demonstrated.

Likely required canonical dimensions will include provider snapshot identity plus poll name and temporal observation metadata, but the exact key remains evidence-gated.

---

## 7. Follow-up F — historical line semantics

The first pass already establishes that historical line field coverage is era-dependent and that provider-name aliases exist.

Next market audit should sample multiple weeks for representative seasons rather than treating week 1 as universal:

```text
2014
2018
2024
2025
2026
```

Suggested weeks:

```text
1
8
15
```

Measure:

```text
games with line observations
provider-name aliases
spread coverage
total coverage
opening spread coverage
opening total coverage
moneyline coverage
```

This remains evidence only. Without observation timestamps, CFBD historical lines are not a quote-by-quote market tape.

Daily-Data-Core owns:

```text
canonical sportsbook identity
provider aliases
quote acquired_at
price chronology
no-vig
closing-snapshot policy
```

---

## 8. Stop condition for B.2-B

B.2-B can be considered sufficiently measured when:

1. major native families have explicit availability eras;
2. team/program/recruit/player/coach identity strengths and gaps are quantified;
3. derived ratings/returning-production/talent families have PIT classifications rather than implicit trust;
4. historical market evidence is separated from timestamped market tape;
5. remaining source gaps are precise enough to enter B.2-C reconciliation without redesigning the source model.

At that point the work should move to cross-provider identity/reconciliation rather than endlessly expanding provider calls.
