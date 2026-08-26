# Daily NCAAF — Provider Probe Results V2

**Phase:** B.2 — Empirical Coverage & PIT Probe  
**Status:** PUBLIC MANIFEST + PUBLIC BUILD-LOG MEASUREMENT COMPLETE; authenticated CFBD row probe remains credential-gated  
**Probe date:** 2026-08-26  
**Supersedes for current B.2 status:** `PROVIDER_PROBE_RESULTS_V1.md` while preserving V1 as the earlier audit record.

---

## 1. What changed since V1

V1 established that the candidate datasets and schemas exist and identified several PIT/leakage hazards from public source code and documentation.

V2 adds measurable public evidence from:

- SportsDataverse release manifests;
- the current cfbfastR 2024 season build log;
- the current cfbfastR 2026 preseason build log;
- the new repeatable Daily-NCAAF probe harness;
- a small unit-test contract for the harness.

This is still an audit phase. No production ingestion contract is locked by these results.

---

# P-012 — 2024 completed-season public build counts

## Source

`sportsdataverse/cfbfastR-cfb-data/logs/cfbfastR_cfb_data_logfile_2024.log`

## Observed build output

| Dataset | Rows | Games reported by build |
|---|---:|---:|
| schedules | 966 | 966 |
| betting | 966 | 966 |
| play_by_play | 162,953 | 966 |
| play_participants | 151,607 | 966 |
| team_box | 1,932 | 966 |
| player_box | 78,993 | 966 |
| drives | 22,419 | 966 |
| game_rosters | 230,344 | 966 |
| linescores | 7,862 | 966 |
| power_index | 1,838 | 966 |
| injuries | **0** | 966 |
| adv_team | 1,892 | 966 |
| adv_passing | 2,905 | 966 |
| adv_rushing | 10,481 | 966 |
| adv_receiving | 16,032 | 966 |
| adv_defensive | 1,892 | 966 |
| adv_turnover | 1,892 | 966 |
| adv_drives | 1,892 | 966 |
| adv_situational | 1,892 | 966 |

The build also reports:

```text
rosters 2024: 27,477 athlete-team rows
from 230,344 game-roster rows
```

## Interpretation

This is strong evidence that the public ESPN-derived pipeline can produce extensive completed-season schedule/PBP/participation/roster coverage while producing **zero injury records across the same 966-game build**.

The correct architecture remains:

```text
NO INJURY ROW != HEALTHY
```

Instead:

```text
NO INJURY ROW -> NO_OBSERVATION / UNKNOWN
```

unless a stronger source supplies a status observation.

## Coverage classification after P-012

| Family | 2024 public-build classification |
|---|---|
| schedules | VERIFIED_HIGH at artifact/build level |
| PBP | VERIFIED_HIGH at artifact/build level; field-level audit still required |
| game rosters | VERIFIED_HIGH at artifact/build level; pregame timing still unknown |
| participation | VERIFIED_WITH_GAPS pending player-ID/null-rate probe |
| injuries | SPARSE/UNAVAILABLE through this public ESPN-derived block for this build |
| betting | artifact exists for every build game; PIT quote semantics not established |
| advanced/enriched fields | available, but retrospective/model-version review required |

---

# P-013 — 2026 preseason availability is family-dependent

## Source

`sportsdataverse/cfbfastR-cfb-data/logs/cfbfastR_cfb_data_logfile_2026.log`

## Observed current build output

```text
schedules        946 rows from 946 games
betting          946 rows from 946 games
team_box       1,892 rows from 946 games
power_index    1,776 rows

pbp                 0 rows from 946 games
play_participants   0 rows from 946 games
player_box           0 rows from 946 games
drives               0 rows from 946 games
game_rosters         0 rows from 946 games
linescores            0 rows from 946 games
injuries              0 rows from 946 games
advanced PBP-derived  0 rows
```

The log explicitly says the season has not started for the PBP/team-summary steps.

It also reports:

- no 2026 game-roster parquet yet;
- weekly ratings missing through-week 1-15;
- weekly team summaries missing through-week 1-15;
- returning production skipped because that job had no 2026 roster data yet.

## Interpretation

A zero-row dataset has to be interpreted in context.

### Expected structural zero

```text
2026 PBP = 0 before games occur
```

is not evidence of provider failure.

### Problematic coverage zero

```text
2024 injuries = 0 after a 966-game completed-season build
```

is evidence that the source family cannot be treated as uniform national injury coverage.

## Architectural consequence

Coverage state needs at least:

```text
NOT_YET_APPLICABLE
EXPECTED_BUT_MISSING
NO_OBSERVATION
PARTIAL
AVAILABLE
```

rather than one boolean `has_data`.

This should influence Phase C schema design.

---

# P-014 — Public PBP release artifacts verify 2004-2025 season publication

## Source

Current GitHub release metadata for:

```text
sportsdataverse/sportsdataverse-data
release tag: espn_cfb_pbp
```

The release currently exposes season-specific play-by-play artifacts from **2004 through 2025** in multiple formats, including parquet.

Representative parquet artifacts observed:

| Season | Artifact | Bytes |
|---:|---|---:|
| 2004 | `play_by_play_2004.parquet` | 25,433,813 |
| 2006 | `play_by_play_2006.parquet` | 37,776,491 |
| 2010 | `play_by_play_2010.parquet` | 47,369,845 |
| 2014 | `play_by_play_2014.parquet` | 52,536,515 |
| 2015 | `play_by_play_2015.parquet` | 52,676,389 |
| 2018 | `play_by_play_2018.parquet` | 52,349,196 |
| 2020 | `play_by_play_2020.parquet` | 33,314,893 |
| 2021 | `play_by_play_2021.parquet` | 48,771,364 |
| 2023 | `play_by_play_2023.parquet` | 50,724,205 |
| 2024 | `play_by_play_2024.parquet` | 55,106,146 |
| 2025 | `play_by_play_2025.parquet` | 59,265,929 |

The current release was rebuilt/updated in 2026, reinforcing the V1 conclusion that release creation/update time is not the historical event-availability time.

## What this proves

```text
2004-2025 PBP season artifacts exist now
```

## What this does NOT prove

It does not by itself prove:

- every expected game exists;
- all games have complete PBP;
- all fields have stable coverage across eras;
- player IDs are equally reliable across eras;
- current derived fields existed historically;
- release rows are original historical snapshots.

The 2020 artifact is materially smaller than adjacent modern seasons, which is directionally consistent with the disrupted 2020 schedule but must not be interpreted solely from file size.

---

# P-015 — Public game-roster release reaches the early PBP era

## Source

Current GitHub release metadata for:

```text
release tag: espn_cfb_game_rosters
```

The release includes a `game_rosters_2004.parquet` artifact and subsequent season artifacts.

This makes game-roster reconstruction worth probing all the way back to the early PBP era.

However, the current release family was built/published years after those historical seasons.

## PIT consequence

Historical game-roster **truth** may be useful for postgame/player-identity reconstruction, but current availability does not establish that the same roster snapshot was known before kickoff in 2004.

Therefore:

```text
historical game roster truth
```

must remain separate from:

```text
pregame expected roster/availability state
```

---

# P-016 — Public schedule artifacts reach 2004 and current preseason

Current SportsDataverse schedule release metadata contains season assets beginning at least in 2004, while the 2026 build already reports 946 schedule rows before the season's PBP exists.

## Consequence

Schedule truth is a strong candidate foundational family, but later B.2 probes still need to test:

- canceled/rescheduled games;
- kickoff revisions;
- neutral-site designation;
- FBS/FCS classification;
- conference membership at game time;
- postseason game type;
- provider game-ID stability.

Schedule fields can revise before kickoff, so Daily NCAAF will preserve immutable schedule observations rather than only the latest state.

---

# P-017 — Phase B.2 probe harness implemented

Daily-NCAAF now contains:

```text
scripts/probes/provider_coverage_probe.py
```

The initial harness:

1. probes public SportsDataverse release manifests;
2. records representative season artifact presence, names, sizes, timestamps and digests;
3. contains an explicit cfbfastR next-play leakage-field hazard registry;
4. supports small authenticated CFBD read-only probes;
5. reads `CFBD_API_KEY` from the environment only;
6. never includes the key value in generated output;
7. distinguishes a missing CFBD key as a skipped credential-gated probe rather than a source failure;
8. emits the versioned audit contract `DAILY_NCAAF_PHASE_B2_PROVIDER_COVERAGE_PROBE_V1`.

The harness is research-only and must not become production acquisition by inertia.

---

# P-018 — Probe helper tests added

Daily-NCAAF now contains:

```text
tests/probes/test_provider_coverage_probe.py
```

The tests cover:

- season-list parsing;
- release-asset selection preference;
- game-count/duplicate/null summarization;
- play-count/duplicate/null summarization;
- explicit CFBD no-key skip behavior;
- persistence of the known cfbfastR look-ahead guardrail fields.

This keeps B.2 measurement logic reviewable before it informs Phase C decisions.

---

# P-019 — Secret and local-probe hygiene locked

A repository `.gitignore` now excludes:

```text
.env
.env.*
local-data/
probe-output/
Python caches / local virtual environments
```

while permitting a future `.env.example`.

The Phase B.2 probe specification explicitly prohibits committing provider secrets or large raw authenticated payloads.

---

# Updated empirical findings matrix

| Question | Current evidence | Status |
|---|---|---|
| Does public PBP exist in 2004? | release artifact verified | YES |
| Does public PBP span through latest completed 2025 season? | release artifacts verified through 2025 | YES |
| Is 2004 guaranteed complete enough for model training? | artifact exists; expected-vs-observed game/field probe incomplete | NOT YET |
| Does 2024 public PBP build span all 966 schedule rows in that build? | log reports 162,953 PBP rows from 966 games | YES at build-log level |
| Does 2024 game-roster build span same 966-game build? | 230,344 rows from 966 games | YES at build-log level |
| Does ESPN-derived injury block provide useful 2024 national coverage? | 0 rows from 966-game build | NO |
| Are zero 2026 PBP rows currently a failure? | season not started; 946 schedules already exist | NO — NOT_YET_APPLICABLE |
| Are provider release timestamps PIT availability timestamps? | historical files rebuilt in 2026 | NO |
| Can provider PBP tables be wholesale model inputs? | explicit `lead_*` look-ahead fields exist | NO |
| Is CFBD row-level empirical testing possible without a key? | API requires bearer auth | CREDENTIAL_GATED |
| Is a repeatable audit harness now in Daily-NCAAF? | script + tests + spec committed | YES |

---

# Remaining B.2 work

## B.2-A — CFBD authenticated representative row probe

Run the committed harness with a locally supplied `CFBD_API_KEY` and measure representative `/games` and `/plays` strata.

This should validate:

- expected-vs-observed game counts;
- duplicate game/play IDs;
- conference/classification null behavior;
- neutral-site representation;
- PBP row/game coverage by selected weeks;
- `wallclock`, PPA and play-text null behavior;
- schema differences by era.

## B.2-B — CFBD college-native family expansion

After the initial games/PBP probe is stable, add targeted probes for:

- teams/conferences;
- rosters/players;
- recruiting;
- transfer portal;
- returning production;
- coaches;
- lines;
- ratings/rankings.

Do not request the entire API indiscriminately.

## B.2-C — Cross-provider reconciliation cases

Select a small set of representative games and players and measure:

```text
CFBD <-> ESPN/cfbfastR game match
CFBD <-> ESPN/cfbfastR player match
transfer player continuity
conference/venue agreement
play match where practical
```

## B.2-D — Prospective live timestamp/revision capture

Once 2026 games begin, repeatedly capture a small number of current games to measure:

```text
provider timestamp
our acquired_at
payload hash
revision time
correction behavior
```

This is required before high-confidence live PIT semantics are assigned.

## B.2-E — Availability-source trial

The injury finding is now strong enough to justify a focused next-source trial rather than hoping ESPN/CFBD fills the gap.

Trial questions for official conference/program feeds and commercial candidates:

- Does a timestamped observation exist before kickoff?
- Is historical revision history available?
- Are statuses player-ID resolvable?
- How often are reports absent?
- What is publication latency?
- Are depth/expected-start semantics included or only injury labels?

---

# Current Phase B verdict

**B.2 remains ACTIVE.**

The public-source portion has progressed from documentation claims to reproducible and measurable evidence. We now have enough evidence to lock several negative constraints:

1. the ESPN-derived injury family cannot be treated as national availability truth;
2. historical release artifacts cannot be treated as historical publication snapshots;
3. provider feature tables require field-level leakage contracts;
4. dataset readiness must distinguish season-stage structural zeros from true coverage gaps.

We do **not** yet have enough authenticated CFBD row-level and cross-provider identity evidence to unlock Phase C.
