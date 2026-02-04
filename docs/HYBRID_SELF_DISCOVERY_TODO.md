# Hybrid Self-Discovery Implementation TODO

Source: `docs/HYBRID_SELF_DISCOVERY_PLAN.md`

## Phase checklist
- [x] Phase 1 - Schema foundation (Alembic + SQLAlchemy models)
  - [x] Add new content/runtime tables
  - [x] Add constraints and indexes for versioned codes
  - [x] Wire model exports
  - [x] Validate migration + model imports
  - [x] Commit phase separately
- [x] Phase 2 - Seed pack import pipeline (`seed/` CSVs)
- [ ] Phase 3 - Scoring and matching services
- [ ] Phase 4 - API contract (`/journey/*`)
- [ ] Phase 5 - Frontend journey implementation
- [ ] Phase 6 - QA + pilot readiness

## Workflow rule
- Implement one phase at a time.
- Validate each phase before commit.
- Pause for explicit approval before starting next phase.
