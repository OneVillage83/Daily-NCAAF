# B.2-C C3-B — Player Cross-Provider Breadth / Coverage Plan V1

Status: **ACTIVE**

Prerequisites:

- C1 game/event identity — COMPLETE/FROZEN
- C2 program/team provider crosswalk — COMPLETE/FROZEN
- C3-A targeted player identity — COMPLETE

## Objective

Determine whether the high exact athlete-ID overlap measured in C3-A generalizes beyond the four targeted continuity programs, without turning provider roster coverage into an identity assumption.

C3-B is a deterministic breadth pass, not a full historical backfill.

## Why this pass exists

C3-A measured nine FBS team-season slices and found:

```text
1099 / 1111 exact shared athlete IDs
98.92% weighted overlap on each provider side
0 duplicate athlete IDs in measured FBS slices
```

However, those slices were concentrated around Alabama, Oklahoma, Colorado, Oregon and Ohio State. A broader conference/membership sample is required before freezing the player cross-provider contract.

## Deterministic sample

### 2024 conference / structural strata

```text
ACC          Clemson          team_id 228
Big Ten      Michigan         team_id 130
Big 12       Utah             team_id 254
SEC          Georgia          team_id 61
AAC          Army             team_id 349
C-USA        Kennesaw State   team_id 338   # recent FBS entrant
MAC          Toledo           team_id 2649
Mountain West Boise State     team_id 68
Sun Belt     App State        team_id 2026
Pac-12       Oregon State     team_id 204
Independent  Notre Dame       team_id 87
```

### 2025 membership-transition strata

```text
Delaware       team_id 48    # enters FBS in 2025
Missouri State team_id 2623  # enters FBS in 2025
```

The sample intentionally includes major-conference, Group-of-Five, independent, service-academy, recent-FBS-entry and conference-realignment contexts.

## Inputs

CFBD:

```text
GET /roster?year=<season>&team=<team>&classification=fbs
```

SportsDataverse / ESPN-derived:

```text
espn_cfb_rosters season asset
```

The external team IDs are frozen C2 evidence.

## Required per-slice evidence

```text
CFBD roster rows
ESPN roster rows
CFBD unique athlete IDs
ESPN unique athlete IDs
exact shared athlete IDs
CFBD-only athlete IDs
ESPN-only athlete IDs
CFBD exact-ID overlap rate
ESPN exact-ID overlap rate
duplicate athlete IDs
same-ID display-name differences
```

Coverage states:

```text
COMPLETE_EXACT_ID_SET_MATCH
HIGH_EXACT_ID_OVERLAP
PARTIAL_EXACT_ID_OVERLAP
NO_ESPN_TEAM_ROWS
NO_CFBD_TEAM_ROWS
UNRESOLVED
```

`HIGH_EXACT_ID_OVERLAP` is descriptive audit output, not an identity merge rule.

## Aggregate evidence

Across compared non-empty slices report:

```text
slice count
complete-set-equality slice count
zero-ESPN-row slice count
CFBD unique athlete IDs total
ESPN unique athlete IDs total
exact shared athlete IDs total
CFBD-only total
ESPN-only total
weighted exact-ID overlap rates
minimum per-slice overlap rates
slices containing duplicate IDs
```

## Safety rules

```text
provider athlete ID != canonical PLAYER_ID
provider-only roster row != identity disagreement
missing provider roster row != player absence
name equality != identity proof
name inequality != identity break
classification/program membership != player identity
shared provider ID != PIT safety
```

## C3 freeze candidate criteria

C3 can freeze after C3-B if:

1. the broader FBS sample continues to show a dominant exact shared athlete-ID namespace;
2. no unexplained provider-ID collision appears;
3. provider-only roster rows are explicitly modeled as coverage differences;
4. any zero-team-coverage slice is retained as a source coverage gap, not a player absence claim;
5. the C3-A transfer cases remain valid direct identity evidence;
6. the Phase C contract keeps canonical `PLAYER_ID` independent from provider IDs.

C3 freeze will be an identity/crosswalk freeze, not a claim that either provider roster is population-complete.
