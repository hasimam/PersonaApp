# Hybrid Self-Discovery MVP Integration Plan

Last updated: 2026-02-04

## 1) Product decision
- We will replace the unreleased legacy public flow.
- We will keep the current technical stack unchanged:
  - Frontend: React + TypeScript
  - Backend: FastAPI + SQLAlchemy + Alembic
  - Database: PostgreSQL
  - Current run/deploy model and tooling stay as-is.

## 2) MVP outcomes (what this build must deliver)
- 12-scenario journey with 4 options per scenario.
- Result engine: Top 2 genes + 1 support gene.
- Optional Sahaba-inspired archetype matches (top 1-3).
- Activation screen with exactly 3 items: behavior, reflection, social.
- Psychological safety capture (1-5 judged score).
- Versioned content so results are stable by `version_id`.

## 3) Phase plan

### Phase 1 - Schema foundation (Alembic + models)
Create versioned, data-driven tables:
- Content: `app_versions`, `genes`, `scenarios`, `scenario_options`, `option_weights`, `sahaba_models`, `advice_items`, `advice_triggers`
- Runtime: `test_runs`, `answers`, `computed_gene_scores`, `computed_model_matches`, `feedback`

Implementation notes:
- Add SQLAlchemy models and relationships.
- Keep existing backend/server setup; only schema and app code evolve.
- Add indexes/unique constraints for `(version_id, *_code)` patterns.

### Phase 2 - Seed pack import pipeline (from `seed/`)
Build an importer that loads CSVs into content tables in strict order:
1. `seed/app_versions.csv`
2. `seed/genes.csv`
3. `seed/scenarios.csv`
4. `seed/scenario_options.csv`
5. `seed/option_weights.csv`
6. `seed/sahaba_models.csv`
7. `seed/advice_items.csv`
8. `seed/advice_triggers.csv`

Importer requirements:
- Validate required columns and data types.
- Validate references (`scenario_code`, `option_code`, `gene_code`, `advice_id`, `model_code`).
- Fail fast with clear row-level errors.
- Upsert by `version_id + code` keys to allow iteration.

### Phase 3 - Scoring and matching services
Implement services with no hard-coded scenario logic:
- Gene scoring from `option_weights`.
- Normalize gene scores for UI display.
- Rank: dominant, secondary, support.
- Sahaba matching via vector similarity against `sahaba_models`.
- Activation selection from triggers:
  - exactly 1 `behavior`
  - exactly 1 `reflection`
  - exactly 1 `social`
  - deterministic fallback if a channel has no trigger hit.

### Phase 4 - API contract (replace public flow)
Add/replace endpoints:
- `POST /api/v1/journey/start`
  - input: optional `version_id` (else active version)
  - output: `test_run_id`, `version_id`, scenarios + options
- `POST /api/v1/journey/submit-answers`
  - input: `version_id`, `test_run_id`, `answers[]`
  - output: top genes, narratives, archetype matches, 3 activation items
- `POST /api/v1/journey/feedback`
  - input: `test_run_id`, `judged_score (1-5)`

### Phase 5 - Frontend journey implementation
Replace current public UX with:
1. Intro
2. Prep
3. Scenario loop (auto-next)
4. Safety question
5. Loading
6. Results (Top 2 + support, optional archetypes)
7. Activation choice (3 options only)
8. Closing

Frontend notes:
- Keep current app structure and services style.
- Reuse existing i18n setup and extend translations.
- Store activation choice in `test_runs`.

### Phase 6 - QA + pilot readiness
Checks before pilot:
- Seed import idempotency test.
- Scoring/matching unit tests.
- API integration test for full journey.
- Frontend happy-path smoke test.
- Pilot metrics available from runtime tables:
  - judged-score distribution
  - completion rate
  - activation pick rate

## 4) Data model snapshot (minimal fields)
- `app_versions(version_id PK, name, is_active, published_at, notes)`
- `genes(version_id, gene_code, name_en, name_ar, desc_en, desc_ar, PK(version_id, gene_code))`
- `scenarios(version_id, scenario_code, order_index, scenario_text_en, scenario_text_ar, PK(version_id, scenario_code))`
- `scenario_options(version_id, scenario_code, option_code, option_text_en, option_text_ar, PK(version_id, scenario_code, option_code))`
- `option_weights(version_id, scenario_code, option_code, gene_code, weight, PK(...))`
- `sahaba_models(version_id, model_code, name_en, name_ar, summary_ar, gene_vector_jsonb, PK(version_id, model_code))`
- `advice_items(version_id, advice_id, channel, advice_type, title_en, title_ar, body_en, body_ar, priority, PK(version_id, advice_id))`
- `advice_triggers(version_id, trigger_id, trigger_type, gene_code, model_code, channel, advice_id, min_score, max_score, PK(version_id, trigger_id))`

Runtime:
- `test_runs(id PK, version_id, session_id, selected_activation_id, created_at, submitted_at)`
- `answers(id PK, test_run_id, scenario_code, option_code, created_at)`
- `computed_gene_scores(id PK, test_run_id, gene_code, raw_score, normalized_score)`
- `computed_model_matches(id PK, test_run_id, model_code, similarity, rank)`
- `feedback(id PK, test_run_id, judged_score, created_at)`

## 5) Execution order (short)
1. Migrations + models.
2. CSV importer using all files in `seed/`.
3. Scoring/matching/activation engine.
4. Journey APIs.
5. Frontend journey screens + wiring.
6. QA + pilot launch.

