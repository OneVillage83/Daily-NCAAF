# Daily NCAAF — Provider Coverage Probe Specification V1

**Phase:** B.2 — Empirical Coverage & PIT Probe  
**Status:** ACTIVE V1  
**Purpose:** Define a reproducible, research-only measurement contract for deciding whether candidate provider data is suitable for later canonical-schema and historical-PIT work.

---

## 1. Governing rule

A provider is not accepted because an endpoint exists, a package exposes a table, or a historical file can be downloaded.

Daily NCAAF must measure, by data family and era:

- whether the artifact exists;
- whether expected entities are present;
- whether identifiers are stable enough to reconcile;
- whether critical fields are populated;
- whether timestamps mean what we need them to mean;
- whether later revisions/reprocessing can change old records;
- whether the data was legitimately knowable at a historical prediction snapshot;
- whether use/licensing/storage terms are compatible with The Daily Line.

The probe is evidence gathering. It does **not** define the production schema and does **not** authorize a provider table as a model feature table.

---

## 2. Probe implementation

Initial harness:

```text
scripts/probes/provider_coverage_probe.py
```

Contract version:

```text
DAILY_NCAAF_PHASE_B2_PROVIDER_COVERAGE_PROBE_V1
```

The harness is intentionally standard-library-only so a clean Python environment can run the first audit without installing the later production stack.

### Modes

```text
--mode public
--mode cfbd
--mode all
```

`public` inspects public SportsDataverse/cfbfastR release metadata.

`cfbd` performs small read-only CollegeFootballData endpoint probes when `CFBD_API_KEY` exists in the process environment.

`all` runs both; absence of `CFBD_API_KEY` is recorded as `SKIPPED_NO_CFBD_API_KEY`, not as a provider failure.

---

## 3. Secret policy

The only initial credentialed probe is CFBD.

Required environment variable:

```text
CFBD_API_KEY
```

Rules:

1. never put the key in source code;
2. never pass the key as a command-line argument;
3. never emit the key into JSON output;
4. never commit `.env` or local credential files;
5. aggregate probe output may be committed only after verifying that it contains no secret/provider-restricted payload;
6. raw authenticated responses remain local unless their provider terms and repository policy explicitly permit retention/publication.

Future SportsDataIO/Sportradar trial credentials follow the same pattern.

---

## 4. Local output policy

Recommended local paths:

```text
local-data/probes/
local-data/raw-probes/
```

These are research artifacts and should remain ignored by Git.

Checked-in Phase B evidence should consist of:

- aggregate counts;
- null/duplicate rates;
- schema observations;
- non-sensitive hashes/checksums where useful;
- documented source URLs/release identifiers;
- conclusions and caveats.

Do not commit large provider payloads merely because they are downloadable.

---

## 5. Representative season strata

Default automated seasons:

```text
2004
2006
2010
2014
2015
2018
2020
2021
2023
2024
2025
2026
```

The broader B.2 matrix may additionally probe:

```text
2016
2019
```

Why these strata:

| Season | Reason |
|---|---|
| 2004 | earliest current cfbfastR rich-PBP candidate era |
| 2006 | beginning of current documented consensus historical betting backfill |
| 2010 | mature pre-structured-participant era |
| 2014 | CFP transition / player-participant era boundary candidate |
| 2015 | cfbfastR recent-extras floor for FPI/full event odds |
| 2018 | modern pre-overtime-rule-change reference |
| 2019 | first modern OT transition |
| 2020 | COVID-disrupted schedule/roster regime |
| 2021 | further modern OT transition |
| 2023 | major clock-rule transition |
| 2024 | 12-team CFP + two-minute timing-era transition; completed rich public build available |
| 2025 | latest completed season in current public PBP release |
| 2026 | current preseason/live-availability behavior |

Historical training eras must be chosen from measured field quality, not merely the oldest available year.

---

## 6. Required game strata

Season-level counts alone are insufficient. B.2 must eventually include explicit cases for:

- FBS vs FBS;
- FBS vs FCS;
- FCS vs FCS where relevant to opponent/state reconstruction;
- independent programs;
- conference realignment transitions;
- neutral-site regular-season games;
- conference championship games;
- bowls;
- CFP games;
- rivalry/officially-neutral-but-regionally-asymmetric games;
- canceled/rescheduled games;
- overtime games across rule eras.

The canonical schema cannot assume every scheduled game has identical competition semantics.

---

## 7. Required player/roster strata

Probe cases must include:

- same-school multi-season player;
- transfer player;
- multiple-transfer player where available;
- jersey-number change;
- position change;
- redshirt/eligibility transition;
- freshman with recruiting prior but little/no college participation;
- player appearing in game roster but not participation;
- player appearing in participation but with incomplete season-roster metadata;
- same/similar-name collision.

These cases validate the F-3 identity architecture before canonical tables are implemented.

---

## 8. Public SportsDataverse/cfbfastR manifest probe

Initial public release families:

```text
schedules
play_by_play
game_rosters
play_participants
betting
injuries
power_index
```

For each season and family, record where available:

```text
present
asset name
artifact size
artifact creation timestamp
artifact update timestamp
digest
release tag
release last-updated timestamp
```

### Interpretation

Artifact presence proves **published artifact existence**, not:

- row completeness;
- PIT correctness;
- original historical publication timing;
- feature eligibility;
- provider-ID stability;
- absence of retrospective enrichment.

A 2004 parquet created/rebuilt in 2026 is a current historical artifact, not a 2004 knowledge snapshot.

---

## 9. CFBD read-only probe

Initial endpoints:

```text
GET /games
GET /plays
```

Initial game query dimensions:

```text
year
seasonType=both
classification=fbs
```

Initial play probe weeks:

```text
1
8
15
```

These are sparse audit samples, not historical acquisition.

### Game measurements

Record:

```text
row count
unique game IDs
duplicate game-ID rows
completed rows
neutral-site rows
home-conference null count
away-conference null count
```

Later extensions should measure venue, classification, postseason, score/status, kickoff and conference semantics by era.

### Play measurements

Record:

```text
row count
unique game IDs
unique play IDs
duplicate play-ID rows
wallclock null count
PPA null count
play-text null count
play-type distribution
```

Later extensions should test player/stat endpoints, teams, rosters, recruiting, transfers, returning production, coaches, lines and ratings separately.

---

## 10. Schema/leakage guardrails

The probe must maintain a provider-field hazard registry.

Verified cfbfastR play-level look-ahead fields currently include:

```text
lead_text
lead_start_team
lead_start_yardsToEndzone
lead_start_down
lead_start_distance
lead_scoringPlay
```

These describe the next play and are prohibited predictor inputs for a play-level next-state model.

This is the first explicit example of the broader rule:

> No provider table may be wholesale-approved as a feature family.

Every production feature must receive a Daily-NCAAF feature contract specifying its source fields, transformation, grain, temporal availability and leakage classification.

Other classes requiring review include:

- full-season aggregates;
- closing/final betting values;
- retrospective ratings;
- modern model outputs recomputed over old games;
- final participation used as if it were pregame expected participation;
- later corrections exposed through a current API response.

---

## 11. PIT timestamp probe contract

For any candidate live/current provider, distinguish at least:

```text
event_at
provider_modified_at
published_at
acquired_at
valid_from
valid_to
```

Do not infer equivalence.

Example:

```text
wallclock != original publication timestamp
modified != original publication timestamp
release_created_at != event availability timestamp
```

### Prospective capture test

For a future/current game, capture repeated observations and compare:

```text
source payload
provider timestamp(s)
our acquired_at
hash of payload/record
next observation
revision delta
```

This is necessary before assigning a high-confidence live PIT contract.

---

## 12. Revision probe contract

For mutable provider objects, B.2 should determine:

- whether an object is overwritten or versioned;
- whether a provider exposes a change log;
- whether historical requests return corrected truth only;
- whether original publication timestamps survive corrections;
- whether identifiers remain stable after correction;
- how long corrections typically arrive after event completion.

Daily NCAAF will preserve its own immutable observations even when upstream providers overwrite theirs.

---

## 13. Coverage metrics

Where row data is accessible, calculate at minimum:

```text
coverage_ratio = observed_expected_entities / expected_entities
null_rate(field) = null_rows / rows
duplicate_rate(key) = duplicate_key_rows / key_rows
identity_match_rate = resolved_cross_provider_entities / attempted_entities
```

For event data, also track:

```text
games_with_any_pbp / scheduled_or_completed_games
plays_with_player_identity / relevant_plays
games_with_game_roster / games
injury_observation_games / games
```

A zero injury count is not converted into a 100% healthy-player rate.

---

## 14. Data-quality classifications

Initial audit classifications:

```text
VERIFIED_HIGH
VERIFIED_WITH_GAPS
PARTIAL
SPARSE
RETROSPECTIVE_ONLY
PIT_RECONSTRUCTABLE
PIT_UNKNOWN
UNAVAILABLE
CREDENTIAL_GATED
TRIAL_GATED
```

Classification is assigned per **dataset/field/era**, not per provider as a whole.

Example:

```text
SportsDataverse 2024 schedules      -> strong artifact coverage
SportsDataverse 2024 PBP            -> strong completed-game artifact coverage
SportsDataverse 2024 injuries       -> observed zero rows in public build
SportsDataverse 2026 schedules      -> preseason available
SportsDataverse 2026 PBP            -> not yet expected before games occur
```

---

## 15. Current empirical anchors

### 2024 cfbfastR public build

The checked public build log reports:

```text
schedules           966 rows / 966 games
betting             966 rows / 966 games
pbp              162,953 rows / 966 games
play_participants 151,607 rows / 966 games
game_rosters      230,344 rows / 966 games
rosters            27,477 athlete-team rows
injuries                0 rows / 966 games
```

Additional rich box/drive/advanced datasets were also built.

This establishes that the public ESPN-derived injury family can be empty even while game/PBP/roster acquisition is extensive.

### 2026 preseason cfbfastR public build

The current public log reports:

```text
schedules      946 rows / 946 games
betting        946 rows / 946 games
team_box     1,892 rows / 946 games
power_index  1,776 rows
pbp               0 rows
play participants 0 rows
game rosters      0 rows
injuries           0 rows
```

The same log explicitly notes the season has not started and weekly ratings/team-summary products are not yet built.

This proves dataset readiness is **season-stage dependent**. A zero-row event dataset before games occur is different from a zero-row injury dataset across a completed season.

---

## 16. Public release-era anchor

Current SportsDataverse `espn_cfb_pbp` release metadata exposes per-season PBP artifacts from **2004 through 2025**.

Representative parquet sizes observed in the current release metadata:

| Season | Parquet bytes |
|---:|---:|
| 2004 | 25,433,813 |
| 2006 | 37,776,491 |
| 2010 | 47,369,845 |
| 2014 | 52,536,515 |
| 2015 | 52,676,389 |
| 2018 | 52,349,196 |
| 2020 | 33,314,893 |
| 2021 | 48,771,364 |
| 2023 | 50,724,205 |
| 2024 | 55,106,146 |
| 2025 | 59,265,929 |

Artifact size is only a coarse coverage signal; it does not establish expected-vs-observed game completeness. The 2020 size drop is a useful reminder that calendar/season structure can change materially.

No 2026 completed-season PBP artifact should be expected before the season has produced plays.

---

## 17. Run examples

Public manifest probe:

```bash
python scripts/probes/provider_coverage_probe.py \
  --mode public \
  --output local-data/probes/sportsdataverse_manifest.json
```

Small representative CFBD probe after setting the key locally:

```bash
export CFBD_API_KEY="..."
python scripts/probes/provider_coverage_probe.py \
  --mode cfbd \
  --seasons 2004,2010,2014,2020,2024,2025,2026 \
  --cfbd-weeks 1,8,15 \
  --output local-data/probes/cfbd_sample.json
```

Windows PowerShell:

```powershell
$env:CFBD_API_KEY = "..."
python scripts/probes/provider_coverage_probe.py `
  --mode cfbd `
  --seasons 2004,2010,2014,2020,2024,2025,2026 `
  --cfbd-weeks 1,8,15 `
  --output local-data/probes/cfbd_sample.json
```

Do not paste API keys into issue bodies, commit messages or checked-in command transcripts.

---

## 18. B.2 completion gate

The probe phase is not complete merely because the harness runs.

Before Phase C, we need enough empirical evidence to lock or conservatively exclude:

1. schedule/game identity coverage;
2. historical PBP coverage and era breaks;
3. roster/game-roster/player identity behavior;
4. participation coverage;
5. recruiting/transfer/returning-production eras;
6. coach/staff history coverage;
7. injury/availability strategy and known missingness;
8. historical market ownership boundary with Daily-Data-Core;
9. ruleset/competition-era joining semantics;
10. timestamp/revision handling;
11. FBS/FCS and postseason representation;
12. remaining credential/commercial gaps.

Only after these are sufficiently measured may Phase C design canonical contracts around reality rather than provider assumptions.
