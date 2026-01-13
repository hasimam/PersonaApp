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
| Step 1: DB Migration | ⏳ Not Started | |
| Step 2: API Updates | ⏳ Not Started | |
| Step 3: Admin Backend | ⏳ Not Started | |
| Step 4: Admin Frontend | ⏳ Not Started | |
| Step 5: Frontend i18n | ⏳ Not Started | |

---

## Let's Start!

Ready to begin with Step 1 (Database Migration)?
