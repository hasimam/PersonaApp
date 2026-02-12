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
- `CORS_ORIGINS` (update this when the public domain changes)
- `ENVIRONMENT`
- `ADMIN_API_KEY` (protects admin endpoints + `/docs` in production)

### Frontend (`frontend/.env`)
- `REACT_APP_API_URL` (optional; default expected: `http://localhost:8000`)
  - For production on Vercel with same‑origin rewrites, leave this unset.

## 3) Database and migrations

### Apply migrations
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### Migration desync recovery
See `docs/TROUBLESHOOTING.md`.

### New migration workflow
```bash
cd backend
source venv/bin/activate
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

### Hybrid seed pack import
```bash
# Optional but recommended for new scenario content:
# normalize Arabic text (remove accidental diacritics + basic spelling normalization)
python3 scripts/normalize_ar_seed.py --in seed/scenarios_v2.csv --out seed/scenarios_v2.csv --fields scenario_text_ar --polish-phrases
python3 scripts/normalize_ar_seed.py --in seed/scenario_options_v2.csv --out seed/scenario_options_v2.csv --fields option_text_ar --polish-phrases
python3 scripts/normalize_ar_seed.py --in seed/scenarios.csv --out seed/scenarios.csv --fields scenario_text_ar --polish-phrases
python3 scripts/normalize_ar_seed.py --in seed/scenario_options.csv --out seed/scenario_options.csv --fields option_text_ar --polish-phrases

cd backend
source venv/bin/activate
python -m app.db.hybrid_seed_importer --dry-run
python -m app.db.hybrid_seed_importer
```

### Cleanup stale interrupted journey runs
```bash
cd backend
source venv/bin/activate
python scripts/cleanup_test_runs.py --dry-run --days 30
python scripts/cleanup_test_runs.py --days 30
```

## 4) Admin operations
- Login URL: `/admin`
- Authentication: API key entered in UI and sent as `X-Admin-Key`
- Admin entities: traits, questions, idols
- Dashboard stats include Arabic translation coverage
 - Production API docs are protected: use `/docs?admin_key=<ADMIN_API_KEY>` or send `X-Admin-Key` header.

## 4.1 Draft preview flow (expert review, no DB writes)

Use this flow for non-programmer expert validation before publishing a scenario set.

Rules:
- Draft sets must use `scenario_set_code` starting with `draft_` (example: `draft_deep_11`).
- Public `/journey/start` excludes `draft_` sets.
- Preview endpoints never write to runtime tables (`test_runs`, `answers`, computed scores, feedback).

Preview endpoints:
- `POST /api/v1/journey/preview/start`
- `POST /api/v1/journey/preview/submit`

Both endpoints require a signed `preview_token`.

Generate token (local example):
```bash
cd backend
source venv/bin/activate
python3 - <<'PY'
import base64, hashlib, hmac, json, os, time
secret = os.environ["SECRET_KEY"].encode("utf-8")
payload = {
  "version_id": "v2",
  "scenario_set_code": "draft_deep_11",
  "exp": int(time.time()) + 7 * 24 * 3600,
  "test_run_id": 120011
}
payload_b64 = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()).decode().rstrip("=")
sig = hmac.new(secret, payload_b64.encode("utf-8"), hashlib.sha256).digest()
sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
print(f"{payload_b64}.{sig_b64}")
PY
```

Expert link format:
- `https://<frontend-domain>/test?preview=<TOKEN>`

## 4.2 Promote approved draft set to public

After expert approval:
1. In seed CSVs, rename `scenario_set_code` from `draft_*` to public code (example `deep_11`).
2. Re-import seeds:
```bash
cd backend
source venv/bin/activate
python -m app.db.hybrid_seed_importer --dry-run
python -m app.db.hybrid_seed_importer
```
3. Smoke test:
   - public `/journey/start` returns non-draft set
   - preview link still works only for remaining draft sets

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
4. Optional follow-up loop for activation choices (consented email or magic-link return flow; keep anonymous mode available).

## 7) Decisions and defaults
- Keep monolith architecture.
- Keep session-based public test flow.
- Keep relational DB with JSONB only where flexible payloads are needed (`trait_scores`, cached result payloads).
- Prefer explicit, simple APIs over abstraction-heavy redesign.

## 8) Pilot metrics SQL (hybrid journey)

Use these queries against runtime tables after pilot traffic starts.

Note: The psychological safety step is temporarily hidden in the UI. The API still records
`judged_score` with a default value of `3` for compatibility. Until the step returns,
the judged-score distribution will be skewed and not meaningful.

### Judged-score distribution
```sql
SELECT judged_score, COUNT(*) AS count
FROM feedback
GROUP BY judged_score
ORDER BY judged_score;
```

### Completion rate
```sql
SELECT
  COUNT(*) AS total_started,
  COUNT(*) FILTER (WHERE status = 'completed') AS total_completed,
  ROUND(
    (COUNT(*) FILTER (WHERE status = 'completed')::numeric / NULLIF(COUNT(*), 0)) * 100,
    2
  ) AS completion_rate_pct
FROM test_runs;
```

### Activation pick rate
```sql
SELECT
  COUNT(*) FILTER (WHERE status = 'completed') AS completed_runs,
  COUNT(*) FILTER (WHERE selected_activation_id IS NOT NULL) AS runs_with_activation_pick,
  ROUND(
    (COUNT(*) FILTER (WHERE selected_activation_id IS NOT NULL)::numeric
      / NULLIF(COUNT(*) FILTER (WHERE status = 'completed'), 0)) * 100,
    2
  ) AS activation_pick_rate_pct
FROM test_runs;
```
