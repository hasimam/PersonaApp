# Mother's Miraat implementation status

Updated: 2026-09-17. Branch: `codex/mothers-miraat-preview`.

Current scope and deferred release: [refined V1 plan](V1_REFINED_PLAN.md). Deployment IDs and live checks below are historical records; they were not reverified for this documentation update.

## Phase 1 — local slice

Implemented: home entry and route, Arabic/English draft content for mothers of one child aged 6–12, 12 situations, four areas, deterministic answer-grounded results, focus selection, three practice cards, check-ins, owned save/resume and deletion. Additive migration `d21e0a6f9310`; existing local database `personaapp_v2`.

Local URL: http://127.0.0.1:3000/mothers-mirror

Verified: Arabic browser journey through results/focus/check-in and refresh; English display; Five new backend tests cover password/session signatures and PostgreSQL fixtures for sparse/all-high/all-low/mixed profiles, ties, ownership, retries, missed days, all three practices and immutable release pinning. Existing backend tests (17) and Journey frontend tests (3) pass. React production build passes.

Startup (two terminals):

```sh
cd /Users/hasanalimam/repos/PersonaApp/backend
ENVIRONMENT=local venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```sh
cd /Users/hasanalimam/repos/PersonaApp/frontend
HOST=127.0.0.1 BROWSER=none REACT_APP_API_URL=http://127.0.0.1:8000 npm start
```

Setup after checkout, using only the local database configured in backend/.env:

```sh
cd /Users/hasanalimam/repos/PersonaApp/backend
venv/bin/alembic upgrade head
venv/bin/python -m app.db.mother_seed_importer --activate-preview
ENVIRONMENT=test venv/bin/python -m unittest tests.test_mother
```

The importer validates bilingual content, coverage, anchors and scoring bands. Activated preview versions are immutable while explicitly editorially draft. Full-release publication is intentionally unavailable before later approval. To edit content, create a new version/file and import it. Existing journeys retain their release.

## Phase 2 — private online preview (complete)

Authenticated configuration verified: existing Vercel project `personaapp-frontend` has no custom domain; its current URL is `personaapp-frontend.vercel.app`. Existing backend is `personaapp-backend.fly.dev`. Neither deployment was changed. User approved a generated preview URL and requires free resources only.

Verified plans: Vercel Hobby, Neon Free. New empty Neon project: `falling-frost-09050112` (`miraati-private-preview`), database `miraati_preview`, Frankfurt. No production users or results copied.

Minimal hosting adjustment: isolated Vercel project serves React and the existing FastAPI backend together through an authenticated Python function. Both application sections use the same preview PostgreSQL database. No Fly preview Machine or paid resource. Bundle script: `python3 scripts/build_private_preview.py`.

The preview build explicitly clears `REACT_APP_API_URL`, uses same-origin APIs, and does not copy the existing Vercel production rewrites. The local API fallback to production was removed. Server-side password/session protection covers UI, assets, docs and API; additional noindex/no-store headers. Live URL: https://miraati-private-preview-hasan-alimams-projects.vercel.app

Vercel project: `miraati-private-preview` / `prj_Ntdhk8Jt76Pz4ZtwVZMCO4AcdYJH`. Verified successful deployment: `dpl_icVFE4ejxZusT2KccVBkyR6BRtxR`, target **staging**, Python 3.12. Both frontend and backend are in this one isolated deployment. Vercel account-only protection is replaced only for this new project by the application's tested password/session gate, so the partner does not need a Vercel account.

Access instructions: the password is in the gitignored, mode-0600 `temp/PREVIEW_ACCESS.txt`. Share the live URL and password directly with the partner. No message was sent. Each browser stores its own journey locator; password access does not transfer journey ownership. The session lasts seven days; Sign out removes it. To revoke all preview sessions, rotate `PREVIEW_SESSION_SECRET` and redeploy. To change the password, regenerate `PREVIEW_PASSWORD_HASH` and rotate the session secret. Never commit `temp/preview-secrets.json` or the access file.

Live HTTP checks passed: unauthenticated UI/API blocked; bad password rejected; cross-origin writes rejected; successful login sets HttpOnly/Secure session; React and assets load; no production backend address in the JS bundle; owned assessment save/submit/resume, focus, difficult/repeat check-in and deletion; wrong owner rejected; original quick and deep starts; logout blocks subsequent API calls. Fixtures were synthetic. The Mother's Miraat smoke-test journey was deleted by its owner token.

Rebuild/update this private preview only:

```sh
cd /Users/hasanalimam/repos/PersonaApp
python3 scripts/build_private_preview.py
# Only needed when server environment values change:
python3 scripts/configure_private_preview.py
python3 scripts/deploy_private_preview.py
python3 scripts/check_private_preview.py https://miraati-private-preview-hasan-alimams-projects.vercel.app temp/PREVIEW_ACCESS.txt
```

The deployment script explicitly targets staging through the Vercel API. Do not replace it with a first-project CLI deployment: Vercel initially labeled `--target preview` as production for this new project. That first build failed before serving content (unsupported Python 3.11), and no public app or routing changed. The corrected staging build uses Python 3.12. No Fly resources or paid upgrades were created. Both verified plans are free and subject to their free-tier quotas.

## Review checkpoint / deferred work

Phases 1–2 remain the release boundary. On 17 September the owner requested a plan update, commit and push; publish the current `codex/mothers-miraat-preview` branch. Production deployment, production migration and the full 30-day release remain outside this update.

Review checkpoint reached: phases 1–2 are complete. Phase 3 remains deferred: remaining 25 practices, day-29 review, day-30 closing and full lifecycle/regression validation after feedback. Three preview cards sample different areas, rather than claiming to deliver the first three days of the future four-week curriculum. No expert review or scientific validation is claimed.

Pilot limits: one browser owns each journey; clearing its storage loses automatic access; one new practice per local calendar day. Test clock changes exist only inside test fixtures, never as a public API bypass. No actual improvement is inferred from participation.

## Login correction — 2026-09-16

Changed the preview Referrer-Policy from `no-referrer` to `same-origin`. Browsers can send `Origin: null` on HTML form POSTs under `no-referrer`, causing the login/logout CSRF check to reject a legitimate form submission. Same-origin referrers preserve browser form behavior without sending referrers to external origins. The CSRF check remains enabled. The HTTP regression check now sends a real Origin and asserts both the response policy and rejection of null/foreign origins. Password and saved data are unchanged.

## Post-implementation UI and persistence changes — 2026-09-17

- Baseline answers save immediately in browser storage with no per-answer request. Reload restores the local draft. Final submission sends the complete answer set; success clears the draft and failure preserves it for retry. Backend draft-save support remains available, but the UI no longer uses it.
- Submitted answers/results, focus and check-ins remain database-backed. Clearing browser storage loses unsubmitted answers as well as automatic access to the owned journey.
- Background, cards, selected answers, buttons and progress now match the main journey. Situation counts come from content, and status messages reserve space to reduce layout shifts.
- Journey deletion uses the shared confirmation modal with explicit cancel/confirm actions.
- Added three frontend regression tests covering immediate local selection and remount, final submission/cleanup, and failed submission/retry. These changes do not implement review, closing or additional practices.

Validation rerun on 17 September: all six frontend tests passed (three Mother's Miraat and three Journey), all five Mother's Miraat backend tests passed against local PostgreSQL, and the frontend production build compiled successfully. React test deprecation/future-flag warnings and an outdated Browserslist data warning remain non-blocking. Live deployment checks were not rerun.
