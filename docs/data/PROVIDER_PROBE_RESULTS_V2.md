# Daily NCAAF — Provider Probe Results V2

**Phase:** B.2 — Empirical Coverage & PIT Probe  
**Status:** HISTORICAL PUBLIC-MEASUREMENT RECORD; superseded for current status by V3-V5  
**Probe date:** 2026-08-26

> V2 records the public SportsDataverse/cfbfastR measurement pass. Authenticated CFBD games/PBP evidence continues in V3/V4, and current CFBD college-native family evidence is in `PROVIDER_PROBE_RESULTS_V5.md`.

---

## Public measurements preserved

### 2024 completed-season cfbfastR build

The public build reported:

```text
966 schedules
966 betting rows
162,953 PBP rows from 966 games
151,607 play-participant rows from 966 games
230,344 game-roster rows from 966 games
27,477 season athlete-team roster rows
0 injury rows from 966 games
```

Locked consequence:

```text
NO INJURY ROW != HEALTHY
NO INJURY ROW -> NO_OBSERVATION / UNKNOWN
```

### 2026 preseason cfbfastR state

The preseason build contained schedules/betting before PBP/roster/injury event products were available.

Locked coverage-state vocabulary:

```text
NOT_YET_APPLICABLE
EXPECTED_BUT_MISSING
NO_OBSERVATION
PARTIAL
AVAILABLE
```

### Public historical artifact era

Current SportsDataverse PBP release metadata exposed season artifacts from 2004 through 2025. Artifact existence did not prove complete game/field coverage or historical publication timing.

### Historical roster artifact

Game-roster artifacts reached the early PBP era, but current historical roster truth remained distinct from historical pregame expected availability.

### Leakage guardrail

Verified cfbfastR next-play look-ahead fields included:

```text
lead_text
lead_start_team
lead_start_yardsToEndzone
lead_start_down
lead_start_distance
lead_scoringPlay
```

No provider table may be wholesale-approved as a model feature family.

### Research harness

V2 also established the repeatable provider coverage harness, helper tests and repository secret/local-output hygiene.

For current Phase B status use:

```text
docs/data/PROVIDER_PROBE_RESULTS_V5.md
docs/implementation/CURRENT_PHASE.md
```
