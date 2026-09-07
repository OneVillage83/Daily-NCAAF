# Daily NCAAF — CFBD Identity Case Probe Specification V1

**Phase:** B.2-B — Targeted Identity & Scope  
**Status:** ACTIVE

---

## 1. Purpose

The broad CFBD family/era audit and Team Talent Composite membership audit are complete enough to stop broad endpoint discovery.

This probe tests the player/coach identity rules directly using bounded real-world cases. The goal is not to build production identity resolution in a research script. The goal is to establish which links CFBD makes explicit, which identifiers remain stable across seasons/programs, and where Daily-NCAAF must reconcile evidence conservatively.

The governing canonical rule remains:

```text
provider IDs are crosswalk evidence
canonical Daily-NCAAF identity is provider-independent
```

A transfer changes `PLAYER_PROGRAM_STINT`, not player identity.

---

## 2. Player cases

### Case A — same-program continuity

```text
Jalen Milroe
Alabama
2021-2024
```

Questions:

- does the roster athlete/player ID remain stable across seasons;
- do jersey/position/metadata changes occur without changing identity;
- does the recruiting record expose a direct `athleteId` link to that roster identity;
- what does `/player/search` return for the same person across years.

### Case B — multiple FBS transfers

```text
Dillon Gabriel
UCF       2019-2021
Oklahoma  2022-2023
Oregon    2024
```

Questions:

- does one provider athlete ID survive both program changes;
- do portal records expose a direct athlete identifier or only contextual/name evidence;
- can chronological program stints be represented without creating multiple canonical players.

### Case C — FCS -> FBS transfer

```text
Travis Hunter
Jackson State  2022
Colorado       2023-2024
```

Questions:

- does identity survive a classification boundary;
- can FCS and FBS roster observations be connected by explicit provider ID;
- what direct recruiting and portal identity evidence exists.

### Case D — single modern FBS transfer

```text
Caleb Downs
Alabama      2023
Ohio State   2024-2025
```

Questions:

- modern roster/provider ID stability;
- recruiting direct-link behavior;
- portal identity fields in a well-covered modern transfer season.

---

## 3. Coach cases

### Same-program long tenure

```text
Nick Saban
```

### Multi-school modern head coach

```text
Kalen DeBoer
```

### FCS/FBS multi-school progression

```text
Curt Cignetti
```

For each coach measure:

- returned provider coach IDs;
- duplicate/multiple person records for the same search;
- nested season entries;
- program changes represented inside one provider identity where applicable;
- year/team/role fields exposed by the response.

This does not solve OC/DC/play-caller history.

---

## 4. Endpoints

The research harness uses bounded requests to:

```text
/player/search
/roster
/recruiting/players
/player/portal
/coaches
```

The CFBD API key is read only from `CFBD_API_KEY` in the local environment and is never emitted.

The harness includes request pacing, bounded HTTP 429 retry/backoff, and an in-memory request cache so repeated portal/recruiting slices are not downloaded multiple times in one run.

---

## 5. Matching discipline

Name comparison in this research harness is only candidate discovery.

```text
NAME MATCH != CANONICAL IDENTITY MATCH
```

Direct provider identifiers are measured where exposed. Candidate rows without an explicit identity link remain contextual evidence.

Required evidence labels:

```text
DIRECT_PROVIDER_LINK
STABLE_PROVIDER_ID
NAME_CONTEXT_CANDIDATE
AMBIGUOUS
UNRESOLVED
```

The harness must never silently convert a normalized-name candidate into a canonical identity decision.

---

## 6. Measurements

For each player case record:

- `/player/search` candidate rows and exposed identifier fields;
- roster candidate count per specified program-season;
- roster provider IDs per season;
- number of distinct roster IDs across the case;
- recruiting candidate rows and any `athleteId` values;
- whether a recruit `athleteId` exactly equals an observed roster ID;
- portal candidate rows for specified transfer seasons;
- any portal identifier fields actually exposed;
- origin/destination/transfer date context;
- discovered schema keys for candidate rows where useful.

For coaches record:

- candidate row count;
- provider IDs;
- nested season count;
- observed teams and season range;
- whether multiple provider IDs are returned for the same exact-name search.

---

## 7. Interpretation rules

### Strong direct evidence

```text
same provider athlete ID across roster seasons/programs
recruiting athleteId == roster athlete ID
same provider coach ID containing multiple team/season stints
```

### Contextual evidence only

```text
same normalized name
same position
origin/destination names
transfer date
recruit school commitment
```

Contextual evidence may support later reconciliation but is not sufficient alone for automatic canonical merging.

---

## 8. Exit criteria

The player/coach portion of B.2-B is complete enough to advance when:

1. at least one same-program player demonstrates provider-ID continuity behavior;
2. at least one transfer demonstrates whether identity survives a school change explicitly;
3. one multi-transfer and one FCS/FBS case are measured;
4. recruiting direct-link presence/absence is demonstrated;
5. portal identity limitations are explicit;
6. multiple coach continuity cases establish provider coach-ID behavior;
7. unresolved cases remain explicit rather than being name-auto-merged.

After this probe, create focused missing-`athleteId` and name-collision cases only if the measured evidence requires them. Then advance to B.2-C CFBD <-> ESPN/cfbfastR reconciliation.
