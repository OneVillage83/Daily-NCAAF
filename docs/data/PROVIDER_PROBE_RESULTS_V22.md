# Provider Probe Results V22 — B.2-C C5-D Final Context Classification

Status: **COMPLETE / FREEZE EVIDENCE**  
Date: 2026-09-07

## User-executed validation

The corrected C5-D V4 offline suite completed successfully:

```text
Ran 10 tests in 0.002s
OK
```

The live probe then completed with contract:

```text
DAILY_NCAAF_PHASE_B2C_CONTEXT_RECONCILIATION_V4
```

and status `RAN`.

## Completed-season exact-event coverage

```text
2023  910 / 910  coverage 1.0
2024  920 / 920  coverage 1.0
2025  934 / 934  coverage 1.0
```

Every referenced participant had ESPN-native team metadata.

```text
missing referenced team metadata = 0
```

## External team-ID and division agreement

Across every aligned participant in all three seasons:

```text
home external team ID   MATCH only
away external team ID   MATCH only
home division           MATCH only
away division           MATCH only
```

No team-ID or division conflict was emitted.

## Conference states after explicit semantic aliases

V4 retained explicit provider-label aliases only. No fuzzy matching was introduced.

The American family remains:

```text
American Athletic
American Conference
American
```

The measured Coastal Athletic family is now also an explicit naming equivalence:

```text
Coastal Athletic
Coastal Athletic Association
CAA
```

All other differences remain `MISMATCH` and are classified separately rather than coerced into equality.

## Exhaustive residual mismatch classification

Aggregate residual conference differences:

```text
CONFERENCE_ASSOCIATION_MODEL_DIFFERENCE       37
TEMPORAL_AFFILIATION_CONFLICT_CANDIDATE        1
UNCLASSIFIED                                    0
TOTAL                                          38
```

Exact signatures:

```text
CFBD=Big South :: ESPN_ID=179 :: ESPN=Ohio Valley Conference | OVC        1
CFBD=Big South-OVC :: ESPN_ID=179 :: ESPN=Ohio Valley Conference | OVC   22
CFBD=OVC-Big South :: ESPN_ID=179 :: ESPN=Ohio Valley Conference | OVC   14
CFBD=UAC :: ESPN_ID=30 :: ESPN=Southland Conference | Southland | land    1
```

By season:

```text
2023
  CONFERENCE_ASSOCIATION_MODEL_DIFFERENCE       10
  TEMPORAL_AFFILIATION_CONFLICT_CANDIDATE        1
  UNCLASSIFIED                                    0

2024
  CONFERENCE_ASSOCIATION_MODEL_DIFFERENCE       13
  UNCLASSIFIED                                    0

2025
  CONFERENCE_ASSOCIATION_MODEL_DIFFERENCE       14
  UNCLASSIFIED                                    0
```

## Interpretation

The 37 Big South/OVC observations are retained as a football-association modeling difference. They are not provider-name aliases for canonical conference membership.

The one 2023 `UAC` versus ESPN-native `Southland` observation is retained as a temporal affiliation conflict candidate. It is evidence that team-season metadata can be temporally backfilled or otherwise differ from season-specific game context and therefore cannot establish historical `CONFERENCE_AFFILIATION_STINT` truth by itself.

## Frozen rules supported by C5

```text
FIELD ABSENT != MISMATCH
UNAVAILABLE != CONTRADICTORY DATA
provider display label != canonical identity
venue display text != venue identity
TEAM_SEASON_HOME_VENUE_OBSERVATION != GAME_VENUE_OBSERVATION
provider neutral-site flag != canonical truth by default
conferenceGame != conference_competition semantics by definition
CONFERENCE ASSOCIATION != MEMBER CONFERENCE
TEAM-SEASON CONFERENCE METADATA != guaranteed historical affiliation truth
provider conference ID != canonical CONFERENCE_ID
provider venue ID != canonical VENUE_ID
```

Canonical conference affiliation and venue identity remain provider-independent, time-aware structures backed by raw observations and provenance.

## Freeze gate

C5 freeze gate passed:

```text
external team-ID conflicts             0
division conflicts                     0
missing referenced team metadata       0
unclassified conference residuals      0
```

B.2-C C5 is therefore eligible to freeze.
