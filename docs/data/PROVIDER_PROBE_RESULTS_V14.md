# Provider Probe Results V14 — B.2-C C1 V4 Freeze Evidence

Status: **C1 GAME / EVENT RECONCILIATION COMPLETE / FROZEN**

Evidence source: user-executed `DAILY_NCAAF_PHASE_B2C_CROSS_PROVIDER_GAME_RECONCILIATION_V4` run on 2026-09-01.

## Test result

`tests/probes/test_cross_provider_game_reconciliation_probe_v4.py`:

```text
Ran 10 tests
OK
```

## Completed 2024 event universe

```text
CFBD FBS-involved events                 920
SportsDataverse/ESPN events              966
exact shared event IDs                    920
CFBD-only raw IDs                           0
ESPN-only raw IDs                          46
normalized ESPN FBS-involved events      920
normalized exact overlap                  920
normalized CFBD-only                        0
normalized ESPN-only                        0
```

The 46 raw ESPN-only rows remain broader-universe events rather than CFBD omissions after participant-derived FBS normalization.

## Participant orientation freeze

```text
SAME_SIDE                                  918
SWAPPED_SIDES                                2
UNRESOLVED                                   0
AMBIGUOUS                                    0
```

The two provider-side reversals remain:

```text
401677085  UTSA / Coastal Carolina
401677093  USC / Texas A&M
```

Both are score matches after participant alignment.

Locked:

```text
provider home/away side != canonical participant identity
same exact event + same participant set + swapped provider sides != identity conflict
```

## Counterpart-anchor evidence

Exactly two events used:

```text
ONE_PARTICIPANT_EXACT_EVENT_COUNTERPART_ANCHOR = 2
```

They were:

```text
401644732  Kent State vs Saint Francis
401644737  Eastern Michigan vs Saint Francis
```

CFBD displays `Saint Francis`; ESPN displays `St. Francis (PA) Red Flash`. In both exact-ID two-participant events, the other participant independently anchored the orientation and the remaining participant was aligned by elimination.

Locked rule:

```text
EXACT EVENT ID
+ exactly two participants
+ one strong participant alignment
+ no competing opposite-orientation anchor
=> remaining participant may be aligned by counterpart elimination
```

This is event-local reconciliation evidence, not a global alias rule.

## Field agreement after participant alignment

```text
week MATCH                     920
week MISMATCH                    0
lifecycle MATCH                920
score MATCH                    919
score UNAVAILABLE                1
score MISMATCH                   0
```

The single unavailable score is the real Liberty-at-App-State cancellation (`401640992`), represented by ESPN as `STATUS_CANCELED` and CFBD as incomplete.

## Team-provider crosswalk evidence

```text
participant observations                       1840
matched games skipped for unresolved orientation  0
unique CFBD team names                           230
unique ESPN team IDs                             230
CFBD name -> multiple ESPN IDs conflicts           0
ESPN ID -> multiple CFBD names conflicts           0
```

This is strong provider-crosswalk evidence for the measured 2024 event universe. Provider IDs remain provider IDs; they do not become canonical Daily-NCAAF identities.

## Kickoff-time evidence remains outside C1 identity freeze

```text
<= 60 seconds             905
> 60 sec <= 5 min           1
> 5 min <= 30 min            6
> 30 min <= 2 hours          6
> 2 hours                     2
```

These differences remain provider-time semantic observations. C1 does not collapse them into one canonical kickoff meaning.

## Source integrity / mutable-release evidence

The selected 2024 SportsDataverse asset was:

```text
asset: cfb_schedule_2024.csv
bytes: 156942
sha256: 6249cc0922e3fe3eade3634b733bd193b92b5b07e6ee4ca456b5efd2b670ca86
advertised digest match: true
```

The asset metadata timestamp had regenerated since the prior run while the content digest stayed unchanged. This demonstrates that release metadata can move without underlying season-content change; source hash remains authoritative evidence for content identity.

The 2026 selected asset remained:

```text
asset: cfb_schedule_2026.csv
bytes: 1504
sha256: d458d6a80fb037718001320f3e5dbc9d126c72db4c8bc14c47df9f9d8bb55c8e
advertised digest match: true
```

## 2026 acquisition-state evidence

At acquisition:

```text
CFBD season events                    888
SportsDataverse/ESPN events             8
exact shared IDs                        8
ESPN-only                                0
```

All eight shared events aligned on participants and kickoff. Three remained final in CFBD while the immutable SportsDataverse snapshot still carried `STATUS_IN_PROGRESS` with intermediate scores.

Locked:

```text
current provider snapshot != final season truth
provider update cadence is source-specific
source hash + acquired_at are mandatory
```

This remains supporting evidence for B.2-D, not a substitute for prospective repeated live capture.

## C1 exit decision

Every predeclared completed-2024 C1 identity criterion passed:

```text
exact shared IDs                           920
normalized FBS overlap                     920 / 920
normalized CFBD-only                         0
normalized ESPN-only                         0
unresolved orientation                       0
ambiguous orientation                        0
team crosswalk conflicts                     0
score mismatch                               0
week mismatch                                0
```

Therefore:

```text
B.2-C C1 — GAME / EVENT RECONCILIATION
COMPLETE / FROZEN
```

Next gate: **C2 — program/team provider-crosswalk stability and freeze across completed seasons.**