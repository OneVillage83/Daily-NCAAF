# Daily NCAAF — B.2-C C1 Game Reconciliation Follow-up V3

## Immediate objective

Close the final C1 instrumentation gap exposed by the successful V3 run without weakening identity rules or adding a provider-name alias table.

V3 proved:

```text
2024 exact CFBD IDs                    920
2024 normalized FBS overlap            920 / 920
team crosswalk conflicts                 0
swapped-side events correctly handled    2
unresolved orientations                  2
```

The two unresolved events are both CFBD `Saint Francis` versus ESPN `St. Francis (PA) Red Flash`, with an independently aligned FBS opponent on the other side.

---

# V4 rule

Inside an already exact-ID matched two-participant event:

```text
one strong participant alignment
+ no strong anchor supporting the opposite orientation
=> orient the remaining participant by elimination
```

The rule may not:

- create an event match without exact event-ID equality;
- override competing opposite-orientation evidence;
- use score equality as identity proof;
- silently create a global name alias;
- turn ambiguous same-name cases into forced identities.

V4 must emit the alignment basis explicitly.

---

# Required local validation

## 1. Pull

```powershell
cd "E:\Daily-NCAAF"
git pull origin docs/full-architecture-v1
```

## 2. Run V4 unit tests

```powershell
python -m unittest discover `
  -s tests/probes `
  -p "test_cross_provider_game_reconciliation_probe_v4.py" `
  -v
```

Expected test count at creation:

```text
10 tests
```

## 3. Run V4 evidence probe

```powershell
python scripts/probes/cross_provider_game_reconciliation_probe_v4.py `
  --seasons 2024,2026 `
  --output local-data/probes/cross_provider_games_v4.json
```

## 4. Inspect output

```powershell
Get-Content "local-data\probes\cross_provider_games_v4.json"
```

---

# C1 freeze requirements

2024 must retain:

```text
exact shared event IDs                  920
normalized ESPN FBS-involved events    920
normalized exact overlap                920
normalized CFBD-only                      0
normalized ESPN-only                      0
week mismatch                             0
team crosswalk conflicts                  0
```

Participant orientation must have:

```text
UNRESOLVED = 0
AMBIGUOUS  = 0
```

Expected orientation shape:

```text
SAME_SIDE       918
SWAPPED_SIDES     2
```

Expected alignment-basis evidence:

```text
ONE_PARTICIPANT_EXACT_EVENT_COUNTERPART_ANCHOR = 2
```

Those two anchored examples should be exactly the Saint Francis events unless the source artifact changes.

Expected score shape:

```text
MATCH       919
UNAVAILABLE   1
MISMATCH      0
```

Expected crosswalk shape:

```text
participant observations              1840
matched games skipped                    0
unique CFBD names                      230
unique ESPN IDs                        230
CFBD -> multiple ESPN ID conflicts       0
ESPN ID -> multiple CFBD names conflicts 0
```

Do not hard-code these expected counts into production logic; they are audit exit expectations against the measured 2024 artifact.

---

# After C1 closes

Advance immediately to:

```text
C2 — program/team provider crosswalk freeze
C3 — player cross-provider reconciliation
```

C2 should formalize provider crosswalk observations such as:

```text
CFBD program observation -> ESPN team ID
```

without promoting any provider identifier to canonical Daily-NCAAF identity.

C3 should test cross-provider player identity against representative continuity paths already proven inside CFBD, including same-program continuity, transfers, and classification changes.

B.2-D prospective revision capture and B.2-E availability-source trials remain separate Phase B gates.
