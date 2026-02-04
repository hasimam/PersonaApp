# PersonaApp Development & Operations

Last updated: 2026-02-04

## 1) Local setup

### Prerequisites
- Node.js + npm
- Python 3.9+
- PostgreSQL

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env
alembic upgrade head
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
```

### Run app
- Quick: `./start.sh`
- Stop: `./stop.sh`

Manual run:
```bash
# terminal 1
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# terminal 2
cd frontend
npm start
```

## 2) Environment variables

### Backend (`backend/.env`)
- `DATABASE_URL`
- `SECRET_KEY`
- `CORS_ORIGINS`
- `ENVIRONMENT`
- `ADMIN_API_KEY`

### Frontend (`frontend/.env`)
- `REACT_APP_API_URL` (default expected: `http://localhost:8000`)

## 3) Database and migrations

### Apply migrations
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### New migration workflow
```bash
cd backend
source venv/bin/activate
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

### Hybrid seed pack import
```bash
cd backend
source venv/bin/activate
python -m app.db.hybrid_seed_importer --dry-run
python -m app.db.hybrid_seed_importer
```

## 4) Admin operations
- Login URL: `/admin`
- Authentication: API key entered in UI and sent as `X-Admin-Key`
- Admin entities: traits, questions, idols
- Dashboard stats include Arabic translation coverage

## 5) Deployment notes
- Backend deploy config present:
  - `backend/Dockerfile`
  - `backend/fly.toml`
- Frontend is standard CRA build (`npm run build`) and can be deployed to Vercel or similar.

## 6) Consolidated roadmap (pragmatic)

### Phase A: Stabilization (high priority)
1. Fix seed script for bilingual schema.
2. Add/ship missing placeholder asset or remove dependency.
3. Make QuestionCard/ProgressBar fully i18n.
4. Add basic backend and frontend smoke tests.

### Phase B: Feature work foundation
1. Tighten API validation around trait score completeness.
2. Add lightweight audit trail for admin mutations (optional table or logs).
3. Improve test UX (save progress per session, optional pagination shortcuts).

### Phase C: Product expansion
1. Trait weighting or alternative matching modes.
2. Shareable result card/link.
3. Analytics events for completion and drop-off.

## 7) Decisions and defaults
- Keep monolith architecture.
- Keep session-based public test flow.
- Keep relational DB with JSONB only where flexible payloads are needed (`trait_scores`, cached result payloads).
- Prefer explicit, simple APIs over abstraction-heavy redesign.
