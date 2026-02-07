# PersonaApp Deployment Workflow

Last updated: 2026-02-04

## 1) Local development workflow

### 1.1 Backend setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit backend/.env
```

Set local backend env (minimum):
```env
DATABASE_URL=postgresql://localhost/personaapp
SECRET_KEY=<your-local-secret>
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ENVIRONMENT=development
```

### 1.2 Frontend setup
```bash
cd frontend
npm install
```

Use local API in development:
```bash
cat > frontend/.env.development.local <<'EOF'
REACT_APP_API_URL=http://127.0.0.1:8000
EOF
```

### 1.3 DB migrate + seed (required)
```bash
cd backend
source venv/bin/activate
alembic upgrade head
python -m app.db.hybrid_seed_importer
```

### 1.4 Run locally
```bash
# terminal 1
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# terminal 2
cd frontend
HOST=127.0.0.1 npm start
```

Open:
- Frontend: http://127.0.0.1:3000
- Backend docs: http://127.0.0.1:8000/docs

## 2) Pre-release checks

```bash
# backend tests
cd backend
source venv/bin/activate
python -m unittest tests/test_hybrid_engine.py tests/test_journey_validation.py tests/test_journey_api_flow.py tests/test_hybrid_seed_importer_idempotency.py

# frontend tests + build
cd frontend
CI=true npm test -- --watchAll=false --runTestsByPath src/pages/Journey.test.tsx
npm run build
```

## 3) Production deployment workflow

### 3.0 Vercel same-origin setup (one-time)
- Vercel project root: `frontend`
- Keep `REACT_APP_API_URL` unset for production.
- Ensure `frontend/vercel.json` includes rewrites for `/api/*`, `/docs`, `/openapi.json`, `/redoc` to the Fly backend.

### 3.0.1 Neon reset (destructive)
- In Neon, reset or recreate the `personaapp` database.
- Update `DATABASE_URL` in Fly to the new/clean database.

### 3.1 Deploy backend
1. Deploy backend service (Fly/other).
2. Set production env vars on host:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `CORS_ORIGINS` (include your frontend production origin; update this when the public domain changes)
   - `ENVIRONMENT=production`
   - `ADMIN_API_KEY` (protects admin endpoints + docs in production)
3. Run migrations on production DB:
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```
4. Import seed/content (or your curated content release):
```bash
cd backend
source venv/bin/activate
python -m app.db.hybrid_seed_importer
```

### 3.2 Deploy frontend
Set production frontend env (optional):
```env
REACT_APP_API_URL=https://<your-backend-domain>
```
If you use Vercel rewrites for same‑origin API calls, leave `REACT_APP_API_URL` unset.

Build and deploy frontend artifact:
```bash
cd frontend
npm run build
```

## 4) Post-deploy smoke checks

1. `GET /docs?admin_key=<ADMIN_API_KEY>` loads.
2. Journey flow works end-to-end:
   - `/journey/start` returns scenarios
   - `/journey/submit-answers` returns genes + activation
   - `/journey/feedback` stores judged score and selected activation
3. Confirm pilot metrics queries run (`docs/DEV_OPERATIONS.md` section 8).

## 4.1 Online testing (public domain)
- Frontend UI: `https://<vercel-domain>/`
- Docs (admin-protected): `https://<vercel-domain>/docs?admin_key=<ADMIN_API_KEY>`
- API (same-origin): `https://<vercel-domain>/api/v1/journey/start`

## 5) Safety rules

- Never use production DB credentials in local `.env`.
- Keep local frontend pointed to local backend for development.
- Treat `alembic upgrade head` + seed import as required in every new environment.
- Use versioned content (`version_id`) for controlled content changes.
