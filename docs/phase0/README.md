# ASTRO Phase 0 — Product, Policy, and Evaluation

This directory contains the Phase 0 deliverables for ASTRO AI.

Phase 0 answers three questions before any code is written:
1. What can ASTRO do, and what guarantees do we give the user?
2. What can go wrong, and how do we prevent it?
3. How will we measure whether the local model is good enough?

## Files

- `CAPABILITIES.md` — permission model, risk levels, approval rules.
- `THREAT_MODEL.md` — threats, mitigations, and acceptance tests.
- `EVAL.md` — evaluation plan, benchmark categories, and baseline model candidates.
- `eval/` — minimal runnable evaluation harness and fixtures.

## Exit criteria

Phase 0 is done when:
- [ ] `CAPABILITIES.md` and `THREAT_MODEL.md` are reviewed and merged.
- [ ] A benchmark suite exists with at least 5 retrieval and 5 safety tests.
- [ ] A baseline model is selected with a reproducible score report.
- [ ] README shows Phase 0 status as complete.

## Current status

See root `README.md` for phase-by-phase status.
