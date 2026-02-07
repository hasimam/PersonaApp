# PersonaApp Plan (Consolidated)

Last updated: 2026-02-07

## Status (Done)
- Online deployment live: Vercel frontend + Fly backend (FRA) + Neon DB (EU Central).
- Quick (v1) and Deep (v2) journeys live.
- Same-origin API via Vercel rewrites.
- Production docs protected by `ADMIN_API_KEY`.
- Seed import includes v1/v2, Quran values, Prophet traits.

## Canonical Architecture
- Frontend: Vercel project `personaapp-frontend` (root `frontend/`).
- Backend: Fly app `personaapp-backend`.
- Database: Neon `neondb` (connection stored in `backend/.env.production.local`, not committed).
- API: `/api/v1/journey/*`.

## Operating Rules
- Update `CORS_ORIGINS` when the public domain changes.
- Keep `backend/seed` in sync with `/seed` (container seed source).
- Do not store secrets in git; use `backend/.env.production.local` and Fly secrets.

## Next Tasks (Short List)
- Add a small online smoke test script (quick + deep).
- Add basic monitoring/alerting for Fly + Neon.
- Expand journey API test coverage.
