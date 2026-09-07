# Provider Probe Results V21 — C5-C V3 Conference Semantic Validation

Date recorded: 2026-09-05 America/Los_Angeles

## Scope

This note records the user-executed C5-C/V3 run for completed seasons 2023-2025.

Contract:

`DAILY_NCAAF_PHASE_B2C_CONTEXT_RECONCILIATION_V3`

The V3 probe preserved the C5-B source/provenance rules and added only one explicit semantic naming equivalence:

- CFBD: `American Athletic`
- ESPN-native: `American Conference` / `American`

No fuzzy matching was permitted.

## Test result

The user executed:

```powershell
python -m unittest discover `
  -s tests/probes `
  -p "test_cross_provider_context_reconciliation_probe_v3.py" `
  -v
```

Result:

```text
Ran 8 tests in 0.001s
OK
```

## Full probe result

The probe completed successfully for 2023, 2024 and 2025.

All three seasons retained:

- CFBD HTTP 200;
- zero duplicate CFBD game IDs;
- 100% CFBD exact game-ID coverage against the ESPN-native schedule artifact;
- zero referenced ESPN schedule team IDs without team-season metadata;
- zero external participant team-ID mismatches;
- zero participant division/classification mismatches.

### Season state counts

#### 2023

```text
exact game-ID matches: 910
CFBD exact-ID coverage: 1.0

home external team ID: MATCH 910
away external team ID: MATCH 910
home division: MATCH 910
away division: MATCH 910

home conference:
  EXACT_ALIAS_MATCH     820
  SEMANTIC_ALIAS_MATCH   90

away conference:
  EXACT_ALIAS_MATCH     799
  SEMANTIC_ALIAS_MATCH   86
  MISMATCH                25

orientation:
  SAME_SIDE             906
  SWAPPED_SIDES           4
```

#### 2024

```text
exact game-ID matches: 920
CFBD exact-ID coverage: 1.0

home external team ID: MATCH 920
away external team ID: MATCH 920
home division: MATCH 920
away division: MATCH 920

home conference:
  EXACT_ALIAS_MATCH     830
  SEMANTIC_ALIAS_MATCH   90

away conference:
  EXACT_ALIAS_MATCH     806
  SEMANTIC_ALIAS_MATCH   88
  MISMATCH                26

orientation:
  SAME_SIDE             918
  SWAPPED_SIDES           2
```

#### 2025

```text
exact game-ID matches: 934
CFBD exact-ID coverage: 1.0

home external team ID: MATCH 934
away external team ID: MATCH 934
home division: MATCH 934
away division: MATCH 934

home conference:
  EXACT_ALIAS_MATCH     842
  SEMANTIC_ALIAS_MATCH   92

away conference:
  EXACT_ALIAS_MATCH     817
  SEMANTIC_ALIAS_MATCH   87
  MISMATCH                30

orientation:
  SAME_SIDE             934
```

### Aggregate conference result

Across 5,528 aligned participant observations:

```text
EXACT_ALIAS_MATCH      4,914
SEMANTIC_ALIAS_MATCH     533
MISMATCH                  81
TOTAL                    5,528
```

The prior V2 result had 614 raw conference mismatches. V3 therefore correctly reclassified 533 American Athletic / American Conference observations while leaving 81 residual differences exposed.

Important: all residual conference mismatches in the measured state counts are on the away-participant side, which in the emitted cases is the FCS opponent side. No team-ID or division conflict accompanies them.

## Residual mismatch families observed in emitted examples

V3 deliberately retained several additional patterns rather than forcing them into the American alias rule.

Observed examples include:

1. `Coastal Athletic` vs `Coastal Athletic Association` / `CAA`, ESPN conference id 48.
2. `Big South-OVC` vs `Ohio Valley Conference` / `OVC`, ESPN conference id 179.
3. `OVC-Big South` vs `Ohio Valley Conference` / `OVC`, ESPN conference id 179.
4. `Big South` vs `Ohio Valley Conference` / `OVC`, ESPN conference id 179.
5. `UAC` vs `Southland Conference` / `Southland`, ESPN conference id 30, including Stephen F. Austin in 2023.

The V2/V3 report emits only a bounded number of examples, so these example families are not yet asserted to be the exhaustive set of all 81 residual observations. A full-signature aggregation pass is required before C5 freeze.

## Independent historical-context checks

These checks are used to classify the residual semantics; they are not treated as independent game-data corroboration.

### Coastal Athletic Association naming

The CAA's own historical page states that the Colonial Athletic Association changed its name to the **Coastal Athletic Association** on July 20, 2023.

Source:

`https://caasports.com/sports/2014/5/16/caabio.aspx`

The measured CFBD label `Coastal Athletic` versus ESPN-native `Coastal Athletic Association` / `CAA` is therefore a naming-equivalence candidate, not by itself evidence of a different affiliation.

### Big South-OVC association semantics

The Big South's official 2023 announcement states that the Big South Conference and Ohio Valley Conference began a **joint association of their football member institutions** for the 2023 season.

Source:

`https://bigsouthsports.com/news/2022/12/13/big-south-and-ohio-valley-announce-2023-football-conference-schedule.aspx`

Therefore labels such as `Big South-OVC` / `OVC-Big South` versus ESPN's `Ohio Valley Conference` metadata should not be blindly collapsed into a single canonical conference identity. They represent a conference-association/modeling distinction that the production ontology must preserve explicitly.

### Stephen F. Austin temporal affiliation warning

The United Athletic Conference's official 2023 football statistics include Stephen F. Austin as a 2023 UAC participant.

Source:

`https://uacfootball.com/stats.aspx?path=football&year=2023`

The Southland Conference later announced that Stephen F. Austin would compete immediately in the Southland beginning in **2024**.

Source:

`https://www.southland.org/news/2023/12/7/southland-conference-announces-2024-conference-football-schedule.aspx`

Therefore a 2023 ESPN team-season row labeling Stephen F. Austin as Southland is not a safe semantic alias for UAC. It is evidence that the ESPN team-season metadata can contain a temporally backfilled or otherwise non-season-faithful conference affiliation observation.

## Locked implications

```text
TEAM ID AGREEMENT != CONFERENCE AFFILIATION AGREEMENT
DIVISION AGREEMENT != CONFERENCE AFFILIATION AGREEMENT
CONFERENCE DISPLAY LABEL != CANONICAL CONFERENCE IDENTITY
CONFERENCE ASSOCIATION != MEMBER CONFERENCE
TEAM-SEASON METADATA != GUARANTEED HISTORICAL PIT AFFILIATION STATE
CURRENT/LATER AFFILIATION MUST NOT BACKFILL AN EARLIER SEASON
```

Also retain the existing venue rule:

```text
TEAM_SEASON_HOME_VENUE_OBSERVATION != GAME_VENUE_OBSERVATION
```

## C5 status after V3

C5 is **not yet frozen**.

V3 is considered a successful diagnostic because it:

- validated the American Athletic naming equivalence;
- preserved perfect participant ID and division agreement;
- exposed 81 residual conference differences instead of hiding them;
- identified the need to distinguish naming aliases, football-association semantics and temporal affiliation conflicts.

## Immediate next gate

Run C5-D/V4 to aggregate every residual mismatch signature over the complete matched set and classify each signature conservatively.

C5 may freeze once:

1. external participant IDs remain conflict-free;
2. division labels remain conflict-free;
3. referenced team metadata remains complete;
4. every residual conference signature is explicitly classified;
5. no unknown/unclassified signature remains;
6. temporal affiliation conflicts are retained as provider evidence rather than coerced into equality.
