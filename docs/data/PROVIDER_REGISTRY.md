# Daily NCAAF — Provider Registry V1

**Phase:** B — Source & Coverage Audit  
**Status:** DOCUMENTED CANDIDATE REGISTRY; empirical endpoint probes still required before Phase B closes  
**Audit date:** 2026-08-26

## Purpose

This registry records candidate and supporting data providers for Daily NCAAF. A provider may be useful without being authoritative, complete, PIT-safe, or approved for production. Provider schemas never define Daily NCAAF's canonical schema.

The governing acquisition path remains:

```text
provider
  -> immutable raw evidence
  -> provider adapter
  -> canonical identity/reconciliation
  -> canonical NCAAF state
  -> PIT eligibility
  -> feature snapshot
```

## Provider-role vocabulary

- **PRIMARY HISTORICAL** — preferred source for a broad historical data family.
- **SECONDARY / RECONCILIATION** — independent source useful for gap filling and disagreement detection.
- **LIVE CANDIDATE** — potential pregame/live source requiring latency and timestamp validation.
- **OFFICIAL REFERENCE** — authoritative rules/results/reference material but not necessarily machine-friendly or PIT-complete.
- **COMMERCIAL CANDIDATE** — paid source to evaluate when open/public sources do not satisfy production requirements.
- **CORE** — capability belongs in `Daily-Data-Core`, not this repository.

## PIT-fidelity vocabulary

- **PIT-A** — contemporaneous observations can be stored with defensible availability timestamps.
- **PIT-B** — useful historical snapshots exist, but availability timestamps and/or revision history require reconstruction.
- **PIT-C** — retrospective/final data useful as truth, labels, priors, or benchmarks, but not safe as historical pregame state without reconstruction.
- **PIT-U** — not yet verified.

---

# P-01 — CollegeFootballData (CFBD)

**Role:** PRIMARY HISTORICAL + LIVE CANDIDATE  
**Priority:** P0  
**Adapter family:** `cfbd`

## Verified public capabilities

Current API documentation exposes:

- games, schedules, scores, box scores, media and game weather;
- historical and live play-by-play;
- drives and player/play-stat associations;
- teams, FBS team lists, venues and historical rosters;
- historical conference affiliations and conference changes;
- player search with team stints;
- player usage and season overview;
- returning production;
- transfer portal entries including origin, destination, transfer date, rating/stars and eligibility state;
- recruiting player rankings, team rankings and position-group aggregates;
- 247Sports Team Talent Composite values;
- head-coach identities, seasons and time-bounded tenures, including interim status;
- rankings;
- historical betting lines/results;
- SP+, SRS, Elo, FPI and CFBD CORE ratings;
- advanced/PPA/WP/statistical endpoints;
- NFL draft results useful for offseason departure truth.

The current API explicitly models FBS, FCS, Division II and Division III classifications in several endpoints. Historical conference affiliation endpoints contain `startYear`/`endYear`, and conference-change records contain an `effectiveYear`.

## Particularly valuable Daily NCAAF families

1. canonical program/provider crosswalk seed;
2. schedule/game identity;
3. historical PBP bootstrap;
4. historical roster seed;
5. recruiting and talent priors;
6. transfer-portal and returning-production priors;
7. head-coach history;
8. historical conference realignment;
9. historical market benchmark data;
10. opponent-adjusted and advanced statistical research.

## Current access/commercial status

CFBD's Terms of Use effective 2026-08-12 expressly state that commercial use is permitted and that subscription tier controls quota rather than commercial rights. Current published tiers range from free/academic access through paid higher-call-volume tiers; live PBP is listed from Tier 2 and GraphQL from Tier 3+.

**Important:** production must still comply with the current Terms, including API-key security and restrictions on third-party access/redistribution of raw API responses.

## PIT assessment

**Overall:** mixed `PIT-A/B/C` depending on dataset.

- Live acquisition can become `PIT-A` when Daily NCAAF captures raw responses and `acquired_at` contemporaneously.
- PBP `wallclock` is an event timestamp, not automatically a publication/availability timestamp.
- Transfer `transferDate`, coach effective dates and similar fields describe event/effective state; they do not automatically prove when Daily NCAAF could have known the value.
- Current historical roster/recruiting endpoints require revision-history testing before being treated as historical knowledge-state snapshots.
- Historical lines contain open/current values but the REST response does not by itself establish a complete quote-by-quote timestamped market history.
- CFBD explicitly documents historical CORE as **retrospective** methodology output beginning in 2016; historical CORE must therefore be treated as `PIT-C` unless Daily NCAAF independently reconstructs the rating from PIT-eligible inputs.

## Known limitations/gaps

- No uniform national injury-report endpoint is exposed in the current public API reference.
- Published depth chart / expected starter probability is not a first-class national feed in the current API reference.
- Coordinator/play-caller history is not equivalent to the head-coach coverage exposed by the coach endpoints.
- Exact earliest-season completeness varies by endpoint and must be empirically probed; documentation presence is not evidence of uniform completeness.

## Decision

**ADOPT as P0 historical foundation and one live input provider, but never as sole provider or canonical schema.**

## Reviewed sources

- https://api.collegefootballdata.com/getting-started
- https://api.collegefootballdata.com/api/games
- https://api.collegefootballdata.com/api/plays
- https://api.collegefootballdata.com/api/teams
- https://api.collegefootballdata.com/api/conferences
- https://api.collegefootballdata.com/api/coaches
- https://api.collegefootballdata.com/api/players
- https://api.collegefootballdata.com/api/recruiting
- https://api.collegefootballdata.com/api/betting
- https://api.collegefootballdata.com/api/ratings
- https://api.collegefootballdata.com/core-ratings
- https://collegefootballdata.com/api-tiers
- https://collegefootballdata.com/terms

---

# P-02 — SportsDataverse / cfbfastR CFB data pipeline

**Role:** SECONDARY / RECONCILIATION + HISTORICAL RESEARCH  
**Priority:** P0/P1  
**Adapter family:** `sportsdataverse_espn`

## Verified current capabilities

The active `cfbfastR-cfb-raw` and `cfbfastR-cfb-data` pipeline is ESPN-derived and currently publishes/rebuilds analysis-ready CFB data including:

- play-by-play;
- team and player box scores;
- advanced team/passing/rushing/receiving/defensive/turnover/drive/situational tables;
- play participants;
- drives;
- per-game rosters and season rosters;
- schedules;
- normalized betting;
- injuries;
- recent-season FPI/power-index data;
- linescores for recent seasons.

The June 2026 pipeline documentation states the full PBP corpus was reprocessed for **2004-2025**, approximately 18.6k games. The raw repository supports rebuilding enriched output offline from retained raw ESPN summaries, which is valuable for reproducibility and independent normalization tests.

The current pipeline also notes:

- recent-season-only gating for some FPI/full event-odds extras;
- no CFB officials feed discovered in the ESPN probe;
- no CFB prop-bet feed in that ESPN source path.

## Value to Daily NCAAF

- second independent implementation of game/PBP normalization;
- participant and roster reconciliation;
- cross-checking CFBD play/game IDs and event truth;
- historical PBP gap analysis;
- injury-source discovery and pregame-source research;
- validation of our own EPA/WP and advanced-feature calculations;
- raw-vs-enriched comparison to ensure Daily NCAAF does not accidentally train on enrichment leakage.

## Licensing caution

SportsDataverse software/repositories are open source (several current surfaces report MIT licensing), but an open-source code license does **not automatically grant unrestricted commercial rights to every upstream factual feed or endpoint from which data was retrieved**. Because the current CFB pipeline is ESPN-derived, production use must separately review upstream terms and redistribution/storage constraints before treating it as a commercial production source.

## PIT assessment

**Overall:** `PIT-B/C` historically, potentially `PIT-A` prospectively if used only through a compliant contemporaneous acquisition path.

The current release datasets are analysis-ready historical products and can include values rebuilt by newer enrichment code. That is excellent for football truth and research but dangerous as a record of historical knowledge state.

A release created in 2026 from a 2012 game is not proof that every field in that release was available before the 2012 kickoff.

## Decision

**ADOPT as P0/P1 reconciliation/research source; do not make it the sole production feed and do not assume release-time enriched columns are historical PIT observations.**

## Reviewed sources

- https://github.com/sportsdataverse/cfbfastR-cfb-raw
- https://github.com/sportsdataverse/cfbfastR-cfb-data
- https://github.com/sportsdataverse/cfbfastR-cfb-data/blob/main/DATASETS.md
- https://github.com/sportsdataverse/cfbfastR-cfb-data/blob/main/docs/models/era_model_refresh.md
- https://github.com/sportsdataverse/cfbfastR

---

# P-03 — NCAA official statistics / records / rules

**Role:** OFFICIAL REFERENCE + TRUTH RECONCILIATION  
**Priority:** P1  
**Adapter family:** `ncaa_reference`

## Verified capabilities

NCAA maintains official football statistics/records resources, archived statistical rankings and official playing-rules resources. The public football statistics page includes archived rankings by division and links to team/individual records. The official playing-rules page is the governing source for rules-era research.

## Value

- official result/stat reconciliation;
- historical program/conference/championship research;
- ruleset effective dates;
- validation of timing/overtime/statistical-scoring changes;
- source of truth for rule interpretations when provider schemas disagree.

## PIT assessment

Mostly `PIT-C` for historical stat archives and **authoritative reference** for rules. NCAA archives are not a substitute for timestamped pregame observations.

## Decision

**ADOPT as authoritative reference/reconciliation source, not primary high-frequency acquisition provider.**

## Reviewed sources

- https://www.ncaa.org/championships/statistics-and-records/football/
- https://www.ncaa.org/championships/playing-rules/football-playing-rules/

---

# P-04 — College Football Playoff official site

**Role:** OFFICIAL REFERENCE  
**Priority:** P1  
**Adapter family:** `cfp_reference`

## Value

Use for postseason format, bracket/seed structure, historical CFP era boundaries, site designations and official competition-state verification.

Current official history identifies:

- four-team CFP era: 2014-15 through 2023-24;
- 12-team era beginning 2024-25;
- the 12-team structure continuing for the 2026-27 season.

## PIT assessment

Reference/truth source. Selection rankings and bracket releases can become PIT observations prospectively if captured contemporaneously.

## Decision

**ADOPT for official competition metadata and rules, not as a general stats provider.**

## Reviewed sources

- https://collegefootballplayoff.com/sports/2026/8/10/cfp-history.aspx
- https://collegefootballplayoff.com/sports/2019/5/22/history
- https://collegefootballplayoff.com/news/2026/1/23/2627-format.aspx

---

# P-05 — SportsDataIO NCAA Football

**Role:** COMMERCIAL CANDIDATE — especially availability/injury  
**Priority:** P1 trial/evaluation  
**Adapter family:** `sportsdataio_ncaaf`

## Verified current capabilities relevant to gaps

SportsDataIO's current NCAA Football workflow documentation states that it monitors official injury wires for FBS teams and trusted media sources. It currently lists official conference reports from the Big Ten, SEC, Big 12, ACC, MAC, Conference USA, Sun Belt and American as monitored inputs.

The provider explicitly states that it **does not provide college depth charts or lineup information**. Its current data dictionary exposes injury status fields and reports `InjuryStatus` from 2018.

## Why evaluate

The national injury/availability layer is one of the largest gaps in the open historical foundation. A timestamped commercial injury feed may materially improve F-10 even if another provider remains primary for football event data.

## PIT assessment

Potential `PIT-A` prospectively if API update timestamps/acquisition timestamps are preserved. Historical revision fidelity must be tested; a current injury row is not automatically a historical injury timeline.

## Decision

**TRIAL / CONTRACT REVIEW REQUIRED.** Do not commit until latency, historical access, revision semantics, player identity quality, price and commercial terms are tested.

## Reviewed sources

- https://sportsdata.io/developers/workflow-guide/ncaa-football
- https://sportsdata.io/developers/api-documentation/ncaa-football
- https://sportsdata.io/developers/data-dictionary/ncaa-football

---

# P-06 — Sportradar NCAA Football v7

**Role:** COMMERCIAL CANDIDATE — event/roster/live redundancy  
**Priority:** P1/P2 trial/evaluation  
**Adapter family:** `sportradar_ncaafb`

## Verified current capabilities

Current official NCAAFB v7 documentation describes a B2B REST API with in-house data collection, schedules, team/player data, current/live game data, play-by-play, rosters, seasonal stats, rankings and a Daily Change Log containing IDs and timestamps for modified entities. The current integration guide exposes both team rosters and **game rosters**, which is potentially valuable for participation/availability state.

The current official overview states 100% of Division I games are covered and real-time PBP is available for all FBS games. Because other cached/public surfaces may state older coverage percentages, production qualification must verify the contracted feed rather than rely on marketing text alone.

## PIT assessment

Potentially strong `PIT-A` prospectively because of change-log timestamps and real-time workflows. Historical depth, corrections and availability must be tested under an actual trial/contract.

## Decision

**TRIAL / CONTRACT REVIEW REQUIRED.** Strong candidate for commercial redundancy and live-state reliability if cost is justified.

## Reviewed sources

- https://developer.sportradar.com/football/docs/ncaafb-ig-api-basics
- https://developer.sportradar.com/football/reference/ncaafb-overview
- https://developer.sportradar.com/football/docs/ncaafb-ig-rosters

---

# P-07 — Conference/program official availability sources

**Role:** LIVE CANDIDATE / PRIMARY EVIDENCE for availability observations  
**Priority:** P0 research requirement  
**Adapter family:** `official_availability`

## Scope

College injury reporting is not nationally uniform. Where conferences or programs publish formal availability reports, Daily NCAAF should prefer those primary documents over summaries.

The production design should support provider instances such as:

```text
OFFICIAL_CONFERENCE_REPORT
OFFICIAL_PROGRAM_REPORT
TEAM_TRANSACTION_OR_ROSTER_NOTICE
COACH_PRESS_CONFERENCE
CREDIBLE_BEAT_REPORT
COMMERCIAL_AGGREGATOR
```

with reliability tiers and publication timestamps.

## Decision

**REQUIRED MULTI-SOURCE FAMILY.** This is not one provider; it is a canonical observation family with program/conference-specific adapters.

---

# P-08 — Daily-Data-Core

**Role:** CORE  
**Priority:** P0

Daily NCAAF must consume, not duplicate, the shared platform for:

- sportsbook/provider registry;
- odds and quote snapshots;
- opening/current/closing market history where available;
- implied probability/no-vig utilities;
- weather forecasts and forecast snapshots;
- venue/geospatial/time-zone primitives;
- travel/rest primitives;
- generic raw evidence/provenance;
- run/job lifecycle;
- generic prediction/recommendation records;
- settlement/performance ledger.

CFBD or another NCAAF provider may still supply historical benchmark lines/weather, but the production cross-sport acquisition contract belongs in `Daily-Data-Core`.

---

# Provider adoption summary

| Provider/family | Role | Initial status | Primary reason |
|---|---|---|---|
| CFBD | historical + live | ADOPT P0 | broad college-native coverage |
| SportsDataverse/cfbfastR | reconciliation/research | ADOPT P0/P1 | second PBP/roster/participant implementation |
| NCAA | official reference | ADOPT P1 | rules/results/stat truth |
| CFP official | official postseason reference | ADOPT P1 | competition-era truth |
| SportsDataIO | commercial candidate | TRIAL P1 | injuries/availability |
| Sportradar | commercial candidate | TRIAL P1/P2 | live redundancy, rosters, change logs |
| official conference/program reports | availability evidence | REQUIRED P0 | primary personnel evidence |
| Daily-Data-Core | shared core | REQUIRED P0 | odds/weather/travel/provenance/settlement |

# Provider qualification gate

No provider is production-qualified until we record:

1. exact endpoint/dataset;
2. earliest/latest usable season;
3. entity and field completeness;
4. FBS/FCS behavior;
5. update cadence/latency;
6. revision/correction behavior;
7. timestamp semantics;
8. PIT classification;
9. ID stability;
10. rate limits/cost;
11. license/commercial/storage/attribution requirements;
12. failure behavior;
13. reproducible sample checksums;
14. reconciliation behavior against at least one independent source where practical.

# Phase B implication

The public documentation is sufficient to choose an initial provider strategy, but **not sufficient to close Phase B**. The next substep is an empirical coverage probe across representative seasons/teams/games before the canonical database schema is locked.
