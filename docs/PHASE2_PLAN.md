# Phase 2: Bilingual Support & Admin Panel

## Overview
Add English/Arabic support and an admin panel to manage content.

---

## Step 1: Database Migration (Bilingual Support)

### Changes:
- Rename existing text columns to `*_en` (English)
- Add new `*_ar` columns (Arabic - empty for now)

### Tables to Update:

**questions:**
- `text` → `text_en`
- Add `text_ar` (nullable)

**idols:**
- `name` → `name_en`
- `description` → `description_en`
- Add `name_ar` (nullable)
- Add `description_ar` (nullable)

**traits:**
- `name` → `name_en`
- `description` → `description_en`
- `high_behavior` → `high_behavior_en`
- `low_behavior` → `low_behavior_en`
- Add `name_ar`, `description_ar`, `high_behavior_ar`, `low_behavior_ar` (nullable)

---

## Step 2: Backend API Updates

- Add `?lang=en` or `?lang=ar` query parameter to endpoints
- Return content in requested language
- Filter out content that doesn't exist in requested language

---

## Step 3: Admin Panel (Backend)

### New Endpoints:
- `POST /admin/questions` - Create question (en/ar)
- `PUT /admin/questions/{id}` - Update question
- `DELETE /admin/questions/{id}` - Delete question
- Same for `/admin/idols` and `/admin/traits`
- `GET /admin/stats` - Dashboard stats

### Authentication:
- Simple admin password (environment variable)
- Or basic JWT auth

---

## Step 4: Admin Panel (Frontend)

### Pages:
- `/admin` - Dashboard with stats
- `/admin/questions` - Manage questions
- `/admin/idols` - Manage idols
- `/admin/traits` - Manage traits

### Features:
- Add/Edit/Delete content
- Side-by-side English/Arabic input fields
- Preview content in both languages

---

## Step 5: Frontend i18n

### Changes:
- Add language switcher (EN/AR toggle)
- RTL layout support for Arabic
- Pass `?lang=` to API calls
- Store language preference in localStorage

---

## Current Progress

| Step | Status | Notes |
|------|--------|-------|
| Step 1: DB Migration | ✅ Complete | Columns renamed to *_en, *_ar columns added |
| Step 2: API Updates | ✅ Complete | ?lang=en/ar parameter added to endpoints |
| Step 3: Admin Backend | ✅ Complete | CRUD endpoints + stats + API key auth |
| Step 4: Admin Frontend | ✅ Complete | Dashboard + CRUD pages for all entities |
| Step 5: Frontend i18n | ✅ Complete | Language switcher + RTL support |

---

## Step 3 Implementation Details

### Files Created/Modified:
- `backend/app/core/config.py` - Added `ADMIN_API_KEY` setting
- `backend/app/schemas/admin.py` - Pydantic models for CRUD operations
- `backend/app/api/admin.py` - All admin endpoints
- `backend/app/main.py` - Registered admin router

### Admin Endpoints (all require `X-Admin-Key` header):
- `GET /api/v1/admin/stats` - Dashboard statistics
- `GET/POST /api/v1/admin/questions` - List/Create questions
- `GET/PUT/DELETE /api/v1/admin/questions/{id}` - Read/Update/Delete question
- `GET/POST /api/v1/admin/idols` - List/Create idols
- `GET/PUT/DELETE /api/v1/admin/idols/{id}` - Read/Update/Delete idol
- `GET/POST /api/v1/admin/traits` - List/Create traits
- `GET/PUT/DELETE /api/v1/admin/traits/{id}` - Read/Update/Delete trait

---

## Step 4 Implementation Details

### Files Created:
- `frontend/src/types/admin.ts` - TypeScript types for admin entities
- `frontend/src/services/adminApi.ts` - Admin API service with auth
- `frontend/src/pages/admin/AdminLogin.tsx` - Login page with API key auth
- `frontend/src/pages/admin/AdminLayout.tsx` - Layout with sidebar navigation
- `frontend/src/pages/admin/AdminDashboard.tsx` - Stats dashboard
- `frontend/src/pages/admin/AdminQuestions.tsx` - Questions CRUD with modal
- `frontend/src/pages/admin/AdminIdols.tsx` - Idols CRUD with modal
- `frontend/src/pages/admin/AdminTraits.tsx` - Traits CRUD with modal

### Files Modified:
- `frontend/src/App.tsx` - Added admin routes

### Admin Routes:
- `/admin` - Login page
- `/admin/dashboard` - Stats dashboard with translation progress
- `/admin/questions` - Manage questions (table view + modal)
- `/admin/idols` - Manage idols (card view + modal)
- `/admin/traits` - Manage traits (list view + modal)

### Features:
- API key authentication stored in localStorage
- Side-by-side English/Arabic input fields in all forms
- Dashboard shows translation coverage progress
- Full CRUD for questions, idols, and traits
- Responsive design with Tailwind CSS

---

## Step 5 Implementation Details

### Files Created:
- `frontend/src/i18n/translations.ts` - English/Arabic translation strings
- `frontend/src/i18n/LanguageContext.tsx` - Language context and useLanguage hook
- `frontend/src/components/LanguageSwitcher.tsx` - EN/AR toggle component

### Files Modified:
- `frontend/src/App.tsx` - Wrapped with LanguageProvider
- `frontend/src/services/api.ts` - Added lang parameter to API calls
- `frontend/src/index.css` - Added RTL support styles
- `frontend/src/pages/Landing.tsx` - i18n + language switcher
- `frontend/src/pages/Test.tsx` - i18n + language switcher
- `frontend/src/pages/Results.tsx` - i18n + language switcher

### Features:
- Language switcher (EN/AR toggle) on all public pages
- RTL layout support for Arabic
- Language preference stored in localStorage
- API calls pass `?lang=` parameter
- All UI text translated to Arabic

---

## Phase 2 Complete!

All 5 steps have been implemented:
1. Database bilingual columns (*_en, *_ar)
2. Backend API with language parameter
3. Admin panel backend (CRUD + stats)
4. Admin panel frontend (Dashboard + management pages)
5. Frontend i18n (translations + RTL)

### To Test (Production):
- **Frontend**: https://personaapp-frontend.vercel.app
- **Admin Panel**: https://personaapp-frontend.vercel.app/admin
- **Backend API**: https://personaapp-backend.fly.dev

### To Test (Local):
1. Start backend: `cd backend && source venv/bin/activate && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm start`
3. Visit http://localhost:3000

### Next Steps:
1. Set `ADMIN_API_KEY` environment variable on Fly.io for secure admin access
2. Redeploy frontend to Vercel to include the new i18n and admin features
3. Add Arabic translations to questions/idols/traits via admin panel
