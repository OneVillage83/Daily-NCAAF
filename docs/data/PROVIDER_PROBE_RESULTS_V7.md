# Daily NCAAF — Provider Probe Results V7

**Phase:** B.2-B — CFBD College-Native Family Expansion  
**Status:** BROAD 2015-2026 ERA SCAN COMPLETE; targeted membership/identity cases next  
**Probe generated:** 2026-08-31T07:29:20Z  
**Harness contract used:** `DAILY_NCAAF_PHASE_B2_CFBD_NATIVE_FAMILY_PROBE_V1`

---

## 1. Purpose

This document records the clean 2025 retry that closes the unresolved annual tail from `PROVIDER_PROBE_RESULTS_V6.md`.

The retry queried only:

```text
transfer portal
talent composite
Elo / SRS / SP+ / FPI / CORE
```

All requests returned HTTP 200.

The local output remained research-only and did not emit the CFBD API key.

---

## P-045 — 2025 transfer portal coverage is substantial and consistent with the modern era

Observed 2025 portal summary:

```text
rows                    4,499
destination null          729
rating null             1,988
stars null                686
transferDate null           0
unique origins            346
unique destinations       341
```

Approximate missingness:

```text
destination missing  ~= 16.2%
rating missing       ~= 44.2%
stars missing        ~= 15.2%
transferDate missing  =  0.0%
```

Eligibility values were dominated by:

```text
Immediate       4,316
Withdrawn         181
TBD                 1
PendingAppeal       1
```

Combined with the continuous annual scan, the current empirical CFBD portal coverage contract is:

```text
2015-2020 -> 0 annual rows in tested queries
2021      -> 1,770
2022      -> 2,273
2023      -> 2,502
2024      -> 3,378
2025      -> 4,499
2026      -> 4,470 in the prior representative snapshot
```

Locked consequence:

```text
CFBD portal coverage floor observed = 2021
```

This is a provider/API coverage boundary. It is not proof of when transfers occurred historically and does not make `transferDate` a publication timestamp.

---

## P-046 — 2025 talent count disproves a simple "2024+ equals FBS universe" rule

Observed 2025 talent response:

```text
rows = 134
unique teams = 134
```

By comparison, 2025 Elo/CORE/FPI each returned 136 teams while SP+ returned 137 rows/teams. Those rating counts strongly suggest that the relevant modern FBS-era universe is larger than the 134-team talent response, but row counts alone are not sufficient to prove exact membership.

Therefore the prior tentative interpretation:

```text
2024+ talent == FBS-only
```

is **not locked**.

Instead the evidence now requires direct membership comparison:

```text
/talent?year=<season> team set
vs
/teams/fbs?year=<season> team set
```

for at least:

```text
2023
2024
2025
2026
```

The comparison must measure exact overlap, FBS teams absent from talent, talent teams outside the FBS list, and provider-name/identity mismatches.

---

## P-047 — 2025 ratings continue the family-specific scope pattern

Observed 2025 ratings:

```text
CORE  136 rows / 136 unique teams
Elo   136 / 136
FPI   136 / 136
SP+   137 / 137, 1 null conference
SRS   266 rows / 265 unique teams, 1 null conference
```

This reinforces the already-locked rule:

```text
rating families do not share one entity universe
```

### FPI / CORE / Elo

The 136-team counts are tightly aligned with one another in 2025, but each family still needs its own temporal/PIT semantics.

### SP+

SP+ continues the repeated pattern of approximately the FBS-sized universe plus one extra/null-conference row. Entity reconciliation remains required.

### SRS

The 2025 SRS response remains much broader than the FBS-sized rating families and even contains one duplicated team identity at the row-count level:

```text
266 rows
265 unique teams
```

Therefore year-only SRS must be normalized using row-level division/entity semantics rather than row count or conference alone.

---

## P-048 — Continuous 2015-2026 era scan is complete enough to stop broad harvesting

With the clean 2025 retry, the broad annual portal/talent/rating audit no longer has a transport-gated year.

Resolved broad boundaries:

1. transfer-portal annual coverage is absent through 2020 and begins substantially in 2021;
2. CORE public retrospective history begins in 2016;
3. SRS expands to a much broader entity universe beginning in the observed 2022 response;
4. talent-composite entity scope changes materially across eras and cannot be inferred from row count alone;
5. FPI is consistently close to the FBS-sized universe in completed seasons;
6. Elo year-only behavior remains latest-available-week rather than an explicit canonical snapshot;
7. SP+ has a persistent near-FBS-plus-extra entity pattern;
8. provider transport/rate failures remain separate from coverage states.

The correct next work is no longer another annual scan.

---

## B.2-B next gate

Proceed in this order:

```text
1. Talent membership scope comparison: 2023-2026
2. Player/recruit/transfer identity cases
3. Coach continuity cases
4. B.2-C CFBD <-> cfbfastR reconciliation
```

B.2-B can close after these targeted cases establish that the planned provider-independent identity/state contracts are defensible.
