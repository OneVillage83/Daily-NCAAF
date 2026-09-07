# B.2-C C3 — Player Cross-Provider Identity Freeze V1

Status: **COMPLETE / FROZEN**

Prerequisites:

- C1 game/event identity — COMPLETE/FROZEN
- C2 program/team provider crosswalk — COMPLETE/FROZEN
- C3-A targeted identity — COMPLETE
- C3-B breadth/coverage — COMPLETE

Evidence:

```text
docs/data/PROVIDER_PROBE_RESULTS_V16.md
docs/data/PROVIDER_PROBE_RESULTS_V17.md
```

## Freeze conclusion

Recent measured FBS CFBD roster athlete IDs and ESPN-derived SportsDataverse `athlete_id` values use a dominant shared external athlete-ID namespace.

This is an identity/crosswalk freeze, **not** a roster-completeness freeze.

## Target continuity evidence

```text
Jalen Milroe 4432734
  Alabama 2023 -> Alabama 2024
  direct shared provider ID throughout

Dillon Gabriel 4427238
  Oklahoma 2022 -> Oklahoma 2023 -> Oregon 2024
  direct shared provider ID throughout

Caleb Downs 4870706
  Alabama 2023 -> Ohio State 2024 -> Ohio State 2025
  direct shared provider ID throughout

Travis Hunter 4685415
  Jackson State 2022: CFBD-only because ESPN-derived team roster was absent
  Colorado 2023 -> Colorado 2024: direct shared provider ID
```

Locked:

```text
transfer != new PLAYER identity
classification change != new PLAYER identity
zero provider team rows != player absence
```

## Population-shaped evidence

### C3-A — nine FBS slices

```text
CFBD athlete-ID observations       1111
ESPN athlete-ID observations       1111
shared                             1099
CFBD-only                            12
ESPN-only                            12
weighted overlap                 98.92% / 98.92%
duplicate-ID slices                  0
```

### C3-B — thirteen deterministic FBS slices

```text
CFBD athlete-ID observations       1634
ESPN athlete-ID observations       1638
shared                             1616
CFBD-only                            18
ESPN-only                            22
weighted CFBD overlap            98.8984%
weighted ESPN overlap            98.6569%
zero-team-row slices                 0
duplicate-ID slices                  0
```

### Combined measured FBS slices

```text
team-season slices                   22
CFBD athlete-ID observations       2745
ESPN athlete-ID observations       2749
shared                             2715
combined weighted CFBD overlap    98.9071%
combined weighted ESPN overlap    98.7632%
```

These are observation counts across team-season slices, not globally unique-person counts.

## Provider coverage remains source-specific

Examples such as Georgia 2024 and Utah 2024 prove the two providers do not expose identical roster membership even while their shared identifiers agree.

Therefore:

```text
provider-only athlete row != identity disagreement
provider roster membership != canonical PLAYER_PROGRAM_STINT truth
missing provider row != player absence
```

A production player crosswalk must retain source and observation context rather than treating one provider roster as complete truth.

## Names are not keys

Exact shared athlete IDs were observed with provider display differences such as suffix changes, preferred-name changes, abbreviations and accent marks.

Locked:

```text
name equality != identity proof
name inequality != identity break
names may discover candidates but may not repair identifier conflicts
```

## Phase C contract implication

Production design should separate canonical identity from provider observations:

```text
PLAYER
  canonical player_id

PLAYER_PROVIDER_CROSSWALK
  player_id
  provider
  provider_athlete_id
  observed_at / acquired_at
  evidence source
  confidence / reconciliation method
  valid interval where defensible

PLAYER_PROGRAM_STINT
  canonical player_id
  canonical program_id
  stint interval / season state
  provenance
```

The external athlete ID remains a provider crosswalk. It never becomes the canonical Daily-NCAAF `PLAYER_ID`.

## PIT boundary

Cross-provider identity agreement does not make roster data historically PIT-safe.

```text
shared provider ID != publication timestamp
shared provider ID != historical availability proof
```

Historical feature eligibility still requires the separate PIT/revision evidence gates.

## Residual limitation

The SportsDataverse 2022 Jackson State roster slice contained zero rows, so Travis Hunter's FCS-origin stint is not cross-provider confirmed by this roster family. CFBD itself preserves the same athlete ID across Jackson State -> Colorado. This remains a source-coverage limitation rather than an identity failure.

## Exit

C3 is frozen. The next B.2-C gate is C4 transfer-event reconciliation: reconcile identifier-less CFBD portal observations against the frozen player/program identities and surrounding source-specific roster stints without allowing name-only portal rows to become identity authority.
