# PersonaApp Blueprint

Last updated: 2026-02-04

## 1) What this app is
PersonaApp is a full-stack web app that runs a personality test and returns the top 3 closest idol matches.

- Test format: 1-5 Likert answers
- Model: 10 traits, each scored 0-100
- Matching: cosine similarity between user trait vector and idol vectors
- Languages: English and Arabic (public test/results + bilingual content model)
- Admin: authenticated CRUD for traits, questions, idols

## 2) Current architecture

### Frontend
- Stack: React 18 + TypeScript + Tailwind + Recharts + Axios + React Router
- Entry: `frontend/src/App.tsx`
- Public routes:
  - `/` landing page
  - `/test` test flow
  - `/results/:resultId` results page
- Admin routes:
  - `/admin` login
  - `/admin/dashboard`
  - `/admin/questions`
  - `/admin/idols`
  - `/admin/traits`
- i18n and RTL:
  - language context in `frontend/src/i18n/LanguageContext.tsx`
  - EN/AR strings in `frontend/src/i18n/translations.ts`

### Backend
- Stack: FastAPI + SQLAlchemy + Alembic + PostgreSQL + NumPy/SciPy
- Entry: `backend/app/main.py`
- Routers:
  - `backend/app/api/test.py`
  - `backend/app/api/results.py`
  - `backend/app/api/admin.py`
- Core logic:
  - scoring: `backend/app/core/scoring.py`
  - matching: `backend/app/core/matching.py`

### Database model (current)
- `traits`: bilingual trait fields (`*_en`, `*_ar`)
- `questions`: bilingual text (`text_en`, `text_ar`) + `reverse_scored`
- `idols`: bilingual name/description + `trait_scores` (JSONB)
- `users`: session-based visitor record
- `test_responses`: raw answers
- `results`: cached trait scores + top matches

## 3) API surface

### Public
- `GET /api/v1/test/start?lang=en|ar`
  - creates session
  - returns questions in selected language
- `POST /api/v1/test/submit`
  - validates responses
  - saves responses
  - computes trait scores
  - computes top matches
  - stores result and returns `result_id`
- `GET /api/v1/results/{result_id}?lang=en|ar`
  - returns user trait scores + top matches
- `GET /api/v1/results/{result_id}/compare/{idol_id}?lang=en|ar`
  - detailed trait-by-trait comparison

### Admin (requires `X-Admin-Key`)
- `GET /api/v1/admin/stats`
- Full CRUD for:
  - `/api/v1/admin/questions`
  - `/api/v1/admin/idols`
  - `/api/v1/admin/traits`

## 4) End-to-end flow
1. User starts test (`/test`) -> frontend calls `GET /test/start`.
2. Backend creates `users.session_id` and returns ordered questions.
3. User submits answers -> frontend calls `POST /test/submit`.
4. Backend validates answers, reverse-scores where needed, normalizes each trait to 0-100.
5. Backend computes cosine similarity against every idol profile and stores top N.
6. Frontend loads `/results/:id` via `GET /results/{id}` and renders cards + radar + bars.

## 5) Codebase map

### Backend core files
- `backend/app/main.py`
- `backend/app/api/test.py`
- `backend/app/api/results.py`
- `backend/app/api/admin.py`
- `backend/app/core/scoring.py`
- `backend/app/core/matching.py`
- `backend/app/models/*`
- `backend/app/schemas/*`
- `backend/alembic/versions/*`

### Frontend core files
- `frontend/src/App.tsx`
- `frontend/src/pages/Landing.tsx`
- `frontend/src/pages/Test.tsx`
- `frontend/src/pages/Results.tsx`
- `frontend/src/pages/admin/*`
- `frontend/src/services/api.ts`
- `frontend/src/services/adminApi.ts`
- `frontend/src/i18n/*`

## 6) Current technical state

### Working shape
- MVP test + results flow implemented
- Bilingual DB schema and language-aware public endpoints implemented
- Admin backend + admin UI implemented
- Local run scripts exist (`start.sh`, `stop.sh`)
- Deploy artifacts exist for backend (`backend/Dockerfile`, `backend/fly.toml`)

### Notable gaps / inconsistencies to fix next
- `backend/app/db/seed.py` still uses pre-bilingual field names (`name`, `text`, `description`) and will fail on a fresh migrated DB.
- `frontend/src/components/test/QuestionCard.tsx` Likert labels are hardcoded English (not using i18n strings).
- `frontend/src/components/common/ProgressBar.tsx` uses hardcoded English text.
- Results fallback image points to `/placeholder.png`, but no placeholder file exists in `frontend/public/`.
- `TestSubmission` schema currently enforces `min_length=40` directly; it is not tied to settings.

## 7) Product framing
- Entertainment/self-reflection app, not diagnosis.
- Idol profiles are estimated and should remain explicitly framed as non-clinical.
