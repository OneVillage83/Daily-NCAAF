# Provider Probe Results V20 — B.2-C C5-B Team-Season Context Reconciliation

Status: **MEASURED / FOLLOW-UP REQUIRED BEFORE C5 FREEZE**  
Date: 2026-09-03

## User-executed validation

```text
12 tests
OK
```

Probe:

```text
scripts/probes/cross_provider_context_reconciliation_probe_v2.py
```

Output:

```text
local-data/probes/cross_provider_context_v2.json
```

Contract:

```text
DAILY_NCAAF_PHASE_B2C_CONTEXT_RECONCILIATION_V2
```

## Scope

Completed seasons:

```text
2023
2024
2025
```

C5-B joins exact-ID matched CFBD games and ESPN-native schedule participants to the ESPN-native portion of the mixed `espn_cfb_teams` season artifact.

Backported CFBD fields in the team release are explicitly excluded from second-path evidence.

## Source integrity

All measured schedule and team-season assets returned advertised SHA-256 digests matching the downloaded bytes.

Team metadata had:

```text
2023 duplicate team IDs                    0
2024 duplicate team IDs                    0
2025 duplicate team IDs                    0

2023 missing referenced team metadata      0
2024 missing referenced team metadata      0
2025 missing referenced team metadata      0
```

The ESPN-native team table is broader than the target FBS event universe. `is_fbs_true_rows` is therefore descriptive source metadata and is not used as the canonical FBS program count.

## Exact event identity remains stable

```text
season  CFBD games  exact shared game IDs  CFBD exact-ID coverage  CFBD-only
2023          910                    910                 100%              0
2024          920                    920                 100%              0
2025          934                    934                 100%              0
```

## Participant external team-ID reconciliation

Every aligned participant matched the same external numeric team ID:

```text
2023 home MATCH 910   away MATCH 910
2024 home MATCH 920   away MATCH 920
2025 home MATCH 934   away MATCH 934

TOTAL MATCH = 5,528 / 5,528 participant observations
```

No external-team-ID problem example was emitted.

Frozen candidate rule remains:

```text
shared provider team ID = strong crosswalk evidence
provider team ID != canonical PROGRAM_ID
```

## Classification / division reconciliation

Every participant division comparison matched:

```text
2023 home MATCH 910   away MATCH 910
2024 home MATCH 920   away MATCH 920
2025 home MATCH 934   away MATCH 934

TOTAL MATCH = 5,528 / 5,528 participant observations
```

No division mismatch example was emitted.

This is strong evidence that the measured CFBD classification labels and ESPN-native division labels agree on the aligned event participants in the completed-season window.

Classification remains program-season/context state, not program identity.

## Conference-label reconciliation

Raw V2 states:

```text
2023 home EXACT_ALIAS_MATCH 820   MISMATCH 90
     away EXACT_ALIAS_MATCH 799   MISMATCH 111

2024 home EXACT_ALIAS_MATCH 830   MISMATCH 90
     away EXACT_ALIAS_MATCH 806   MISMATCH 114

2025 home EXACT_ALIAS_MATCH 842   MISMATCH 92
     away EXACT_ALIAS_MATCH 817   MISMATCH 117
```

Across the three seasons:

```text
EXACT_ALIAS_MATCH  4,914
MISMATCH              614
TOTAL                5,528
```

Critically, every emitted mismatch example in all three seasons was the same provider naming-semantic pair:

```text
CFBD:        American Athletic
ESPN-native: American Conference / American
ESPN conference_id: 151
```

No emitted example showed a different underlying affiliation pair.

This is not yet sufficient to silently relabel all 614 raw mismatches. A bounded V3 rerun is required with one explicit enumerated semantic-equivalence rule. Unknown labels must continue to remain mismatches.

## Home-venue anchor evidence

The team-season `venue_id` is a home-venue observation, not direct game-venue truth.

Measured states:

```text
2023 MATCH 783   DIFFERENT 62   NOT_APPLICABLE 65
2024 MATCH 781   DIFFERENT 58   NOT_APPLICABLE 81
2025 MATCH 799   DIFFERENT 71   NOT_APPLICABLE 64
```

Combined:

```text
MATCH                         2,363
DIFFERENT_FROM_TEAM_HOME_VENUE 191
NOT_APPLICABLE_CONTEXT          210
```

The difference examples demonstrate that the ESPN team-season home-venue field must not be substituted for event venue identity. Examples include team metadata pointing to older or otherwise different venue identities while the game record points to the actual event site, including patterns such as:

```text
Illinois       Memorial Stadium event vs Foster Stadium team metadata
Rutgers        SHI Stadium event vs HighPoint.com Stadium team metadata
Houston        TDECU Stadium event vs Robertson Stadium team metadata
Baylor         McLane Stadium event vs Floyd Casey Stadium team metadata
Hawai'i        Clarence T.C. Ching event vs Aloha Stadium team metadata
San Diego St.  Snapdragon Stadium event vs SDCCU Stadium team metadata
```

Therefore:

```text
TEAM_SEASON_HOME_VENUE_OBSERVATION
    !=
GAME_VENUE_OBSERVATION

provider venue ID
    !=
canonical VENUE_ID
```

The current SportsDataverse schedule asset does not expose a direct event `venue_id`, so C5 cannot claim independent event-venue-ID corroboration from that artifact.

## Side orientation

```text
2023 SAME_SIDE 906   SWAPPED_SIDES 4
2024 SAME_SIDE 918   SWAPPED_SIDES 2
2025 SAME_SIDE 934   SWAPPED_SIDES 0
```

C1 orientation semantics continue to be required before participant context comparison.

## C5-B conclusions

Safe to lock as evidence:

```text
5,528 / 5,528 aligned participant external team IDs match
5,528 / 5,528 aligned participant division labels match
0 missing referenced team metadata IDs
0 duplicate team IDs in measured team-season assets
all measured schedule/team asset digests verify
team-season home venue must never substitute for event venue
```

Not yet frozen:

```text
conference-label reconciliation
```

because 614 V2 observations are still labeled `MISMATCH`, despite every emitted example being the same `American Athletic` vs `American Conference` semantic naming case.

## Immediate follow-up gate

Run C5-C V3 with explicit enumerated semantic equivalence:

```text
American Athletic
American Conference
American
```

Only this measured equivalence group is allowed.

C5 may become a freeze candidate if V3 retains:

```text
external team-ID problems = 0
division mismatches = 0
missing referenced team metadata = 0
unknown conference mismatches = 0 or individually explainable
```

Venue limitations remain explicitly frozen as a source-contract limitation rather than being repaired or guessed.
