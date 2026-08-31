# Daily NCAAF — CFBD Recruit Linkage Gap Probe Spec V1

**Phase:** B.2-B — Targeted Identity Cases  
**Status:** COMPLETE  
**Purpose:** measure how CFBD identity behaves when recruiting `athleteId` is absent, and surface unsafe name-collision cases.  
**Result:** `docs/data/PROVIDER_PROBE_RESULTS_V10.md`

---

## 1. Research question

The positive identity cases proved that recruiting `athleteId` can directly link recruiting records to stable roster athlete IDs when present.

However broad recruiting measurement showed that `athleteId` is absent for a material share of recruits.

This probe asked:

```text
When recruit.athleteId is null,
can the later roster row's recruitIds recover a direct provider link?
```

and, if not:

```text
what contextual evidence remains and where is name matching ambiguous?
```

---

## 2. Governing safety rule

```text
NAME MATCH != IDENTITY MATCH
```

Exact normalized names may locate candidate rows for audit purposes only.

The probe must never assign a canonical player identity.

Allowed interpretations:

```text
DIRECT_ROSTER_RECRUIT_ID_LINK
NAME_CONTEXT_ONLY_STABLE_ROSTER_CANDIDATE
AMBIGUOUS_NAME_COLLISION
UNRESOLVED
```

Only the first state is an explicit provider-link recovery.

---

## 3. Target years

Measured bounded scan:

```text
2021
2022
2023
2024
```

These seasons are modern enough to have useful roster/recruiting coverage while spanning the observed direct-link incompleteness.

---

## 4. Candidate selection

For each year the probe:

1. fetched the season-specific FBS program set;
2. fetched high-school recruiting rows;
3. filtered to rows where:
   - `athleteId` was null;
   - `committedTo` was a measured FBS program;
   - recruiting record ID and name were present;
4. selected a small deterministic sample, prioritizing higher-ranked records where ranking existed;
5. queried the committed program's roster for the same season;
6. if no exact-name candidate was observed, queried the following season as a bounded fallback.

This was a research sample, not an estimate of national reconciliation success rate.

---

## 5. Direct provider-link recovery rule

For each roster candidate the probe inspected:

```text
roster.recruitIds
```

If the recruiting record's provider recruit ID appeared in that list, the intended classification was:

```text
DIRECT_ROSTER_RECRUIT_ID_LINK
```

If an exact-name candidate exposed one stable roster athlete ID but did not carry the recruit ID, it remained:

```text
NAME_CONTEXT_ONLY_STABLE_ROSTER_CANDIDATE
```

If multiple candidate roster IDs shared the normalized name:

```text
AMBIGUOUS_NAME_COLLISION
```

If no candidate was found:

```text
UNRESOLVED
```

---

## 6. Name-collision audit

Within each recruiting-year response, rows were grouped by normalized name.

The probe surfaced bounded examples with:

```text
recruit record ID
name
committedTo
position
athleteId
```

Duplicate-name records were treated as ambiguity evidence, never automatic duplicate people.

---

## 7. Measured outcome

The local test suite reported:

```text
Ran 9 tests in 0.003s
OK
```

Across 12 selected missing-`athleteId` cases:

```text
DIRECT_ROSTER_RECRUIT_ID_LINK                 0
NAME_CONTEXT_ONLY_STABLE_ROSTER_CANDIDATE     8
UNRESOLVED                                    4
```

No sampled roster `recruitIds` list contained the tested recruiting-record ID.

This does **not** prove roster `recruitIds` are never useful. It proves they cannot be assumed to provide a direct join to the selected `/recruiting/players` row without additional semantic evidence.

Normalized-name collisions were observed in every tested year, including cases where same name, school and position still did not provide a safe unique record identity.

Full evidence and canonical consequences are recorded in:

```text
docs/data/PROVIDER_PROBE_RESULTS_V10.md
```

---

## 8. Reliability / secret policy

- `CFBD_API_KEY` came from the local environment only.
- The key was never emitted.
- Requests were paced.
- HTTP 429 behavior used bounded backoff.
- HTTP failure remained a transport state, not a data-coverage result.
- Research tooling remains separate from production acquisition.

---

## 9. Exit decision

The exit criterion is satisfied because the probe demonstrated both contextual-only missing-link behavior and empirical name ambiguity without exposing a new failure mode requiring additional broad CFBD discovery.

Therefore:

```text
B.2-B — COMPLETE
B.2-C — ACTIVE NEXT
```

Continue with:

```text
docs/data/B2C_CROSS_PROVIDER_RECONCILIATION_PLAN_V1.md
scripts/probes/cross_provider_game_reconciliation_probe.py
```
