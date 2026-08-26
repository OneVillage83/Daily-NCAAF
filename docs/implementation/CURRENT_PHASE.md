# Daily NCAAF — Current Phase

**Current status:** Architecture V1 documentation complete; implementation not yet started.

## Active phase

### Phase B — Source & Coverage Audit

The next implementation-planning task is to identify and validate the actual data foundation before schema/model work begins.

## Immediate objectives

1. Inventory candidate college-football providers and datasets.
2. Map coverage by entity, field, season, and update cadence.
3. Determine historical vs live/pre-kickoff availability.
4. Assign PIT-fidelity classifications.
5. Record license/attribution/cost constraints.
6. Identify provider overlap and reconciliation opportunities.
7. Determine which cross-sport capabilities should be consumed from `Daily-Data-Core`.
8. Produce the initial canonical schema requirements from evidence rather than from provider schemas.

## Required next documents

- `docs/data/PROVIDER_REGISTRY.md`
- `docs/data/SOURCE_COVERAGE_MATRIX.md`
- `docs/data/PIT_AVAILABILITY_MATRIX.md`
- `docs/data/IDENTITY_RULES.md`
- `docs/data/RULESET_ERAS.md`

## Explicitly not started yet

- production database schema
- provider ingestion code
- historical backfill
- feature engineering
- model training
- simulation
- recommendation logic

Experimental investigation is allowed, but none of the above should be treated as production implementation until the source/coverage audit establishes the contracts they depend on.

## Phase transition rule

Phase B is complete only when the major data families required for F-0 through F-14 have documented coverage/availability characteristics and known gaps significant enough to influence schema/PIT design.
