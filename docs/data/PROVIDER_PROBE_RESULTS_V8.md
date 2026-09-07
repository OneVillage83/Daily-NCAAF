# Daily NCAAF — Provider Probe Results V8

**Phase:** B.2-B — CFBD Targeted Identity & Scope  
**Status:** TALENT MEMBERSHIP SCOPE COMPLETE; player/transfer identity cases next  
**Probe generated:** 2026-08-31T07:48:42Z  
**Harness contract:** `DAILY_NCAAF_PHASE_B2_CFBD_TALENT_SCOPE_PROBE_V1`

---

## 1. Purpose

This document records the exact-membership comparison between:

```text
GET /teams/fbs?year=<season>
GET /talent?year=<season>
```

for 2023-2026.

Unlike the earlier row-count audit, this probe compares exact provider team-name sets and deliberately surfaces mismatches instead of fuzzy-normalizing them away.

Local test result before execution:

```text
Ran 6 tests in 0.001s
OK
```

Every API request in the membership run returned HTTP 200 on the first attempt.

---

## P-049 — 2023 Team Talent Composite spans the full FBS universe plus 105 additional programs

Observed 2023 membership:

```text
FBS unique names             133
Talent unique names          238
Exact-name overlap           133
FBS missing from talent        0
Talent outside FBS           105
Exact membership match      false
```

All 133 FBS program names were present in the talent response. The 105 additional names include programs such as:

```text
Abilene Christian
Delaware
Idaho
Jackson State
Montana
Montana State
North Dakota State
Sacramento State
South Dakota State
Villanova
Youngstown State
```

and many other recognizable FCS programs.

Locked consequence:

```text
2023 /talent is not FBS-only
```

The earlier 238-row count was therefore a true broader entity universe, not primarily a provider-name alias artifact.

No production feature query may infer classification from the presence of a Team Talent Composite row alone.

---

## P-050 — 2024 Team Talent Composite exactly matches FBS membership

Observed 2024 membership:

```text
FBS unique names             134
Talent unique names          134
Exact-name overlap           134
FBS missing from talent        0
Talent outside FBS             0
Exact membership match       true
```

This is a clean exact membership match at the provider-name level for the observed snapshot.

However, this does not justify a timeless rule that all 2024+ talent responses are complete FBS snapshots. The 2025 result disproves that simplification.

---

## P-051 — 2025 talent is an FBS subset missing exactly Air Force and Navy

Observed 2025 membership:

```text
FBS unique names             136
Talent unique names          134
Exact-name overlap           134
FBS missing from talent        2
Talent outside FBS             0
Exact membership match      false
```

The two FBS programs missing from the Team Talent Composite response are:

```text
Air Force
Navy
```

There are no talent programs outside the FBS list in 2025.

Therefore this is not explained by a simple exact-name alias mismatch in the observed provider output. It is a provider-family coverage omission for those two FBS programs in the measured 2025 snapshot.

Locked consequences:

```text
NO TALENT ROW != ZERO TALENT
NO TALENT ROW != NON-FBS
```

and:

```text
Team Talent Composite coverage must be represented as an observation with explicit missingness
```

The model must never impute a zero composite merely because a program is absent from the provider response.

---

## P-052 — 2026 Team Talent Composite again exactly matches FBS membership

Observed 2026 membership:

```text
FBS unique names             138
Talent unique names          138
Exact-name overlap           138
FBS missing from talent        0
Talent outside FBS             0
Exact membership match       true
```

This confirms that the 2025 Air Force/Navy omission is not a permanent exclusion rule in the immediately following observed season.

It must remain a season/snapshot-specific missingness fact unless provider provenance later explains the cause.

---

## P-053 — Team Talent Composite requires season-specific entity-universe and coverage state

The four-season exact membership result is:

| Season | FBS | Talent | Overlap | Missing FBS | Outside FBS | Exact match |
|---:|---:|---:|---:|---:|---:|:---:|
| 2023 | 133 | 238 | 133 | 0 | 105 | No |
| 2024 | 134 | 134 | 134 | 0 | 0 | Yes |
| 2025 | 136 | 134 | 134 | 2 | 0 | No |
| 2026 | 138 | 138 | 138 | 0 | 0 | Yes |

The correct canonical contract is therefore not:

```text
/talent == FBS teams
```

and not:

```text
2024+ /talent == complete FBS universe
```

Instead:

```text
TALENT_OBSERVATION
  provider
  season
  provider_program_identity
  talent_value
  acquired_at
  coverage_state
  source_scope / classification evidence
  PIT classification
```

must be reconciled against the canonical program-season universe.

At minimum, coverage state must distinguish:

```text
OBSERVED
EXPECTED_BUT_MISSING
OUTSIDE_TARGET_CLASSIFICATION
UNRESOLVED_IDENTITY
```

---

## B.2-B scope verdict

The Team Talent Composite scope question is complete enough to exit broad/talent-specific discovery.

Verified:

1. historical talent scope can include a much broader-than-FBS universe;
2. exact membership can match FBS in some seasons;
3. an FBS program can be missing from an otherwise FBS-only response;
4. row count alone cannot determine entity scope or completeness;
5. missing provider talent is not a numeric zero;
6. season-specific reconciliation against canonical program membership is mandatory.

The next B.2-B work is targeted player/recruit/transfer identity continuity, followed by coach continuity and then B.2-C cross-provider reconciliation.
