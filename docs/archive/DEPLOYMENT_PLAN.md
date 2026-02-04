# PersonaApp Deployment Plan

## Overview
Deploy PersonaApp online using free hosting services:
- **Database**: Neon (free PostgreSQL)
- **Backend**: Fly.io (free, no cold starts)
- **Frontend**: Vercel (free, optimized for React)

---

## Phase 1: Database Setup (Neon)

### Step 1.1: Create Neon Account
- [x] **YOU**: Go to https://neon.tech and sign up (use GitHub for easy login)
- [x] **YOU**: Create a new project called `personaapp`
- [x] **YOU**: Copy the connection string
- [x] **YOU**: Share the connection string with me

### Step 1.2: Configure Database
- [x] **CLAUDE**: Run migrations on Neon database
- [x] **CLAUDE**: Seed initial data (10 traits, 50 questions, 20 idols)

---

## Phase 2: Backend Deployment (Fly.io)

### Step 2.1: Install Fly CLI
- [x] **YOU**: Install Fly CLI:
  ```bash
  # macOS
  brew install flyctl
  ```
- [ ] **YOU**: Sign up/login:
  ```bash
  fly auth signup
  # or if you have an account:
  fly auth login
  ```
- [ ] **YOU**: Confirm by running `fly auth whoami`

### Step 2.2: Prepare Backend for Deployment
- [x] **CLAUDE**: Create `Dockerfile` for backend
- [x] **CLAUDE**: Create `fly.toml` configuration
- [x] **CLAUDE**: Set environment secrets

### Step 2.3: Deploy Backend
- [x] **CLAUDE**: Deployed to Fly.io
- [x] **CLAUDE**: Verified health check

**Backend URL**: https://personaapp-backend.fly.dev

---

## Phase 3: Frontend Deployment (Vercel)

### Step 3.1: Prepare Frontend
- [ ] **CLAUDE**: Create production environment config
- [ ] **CLAUDE**: Update API base URL for production

### Step 3.2: Deploy to Vercel
- [ ] **YOU**: Go to https://vercel.com and sign up with GitHub
- [ ] **YOU**: Import your repository
- [ ] **YOU**: Set environment variable: `REACT_APP_API_URL` = your Fly.io backend URL
- [ ] **YOU**: Deploy

---

## Phase 4: Final Configuration

### Step 4.1: Update CORS
- [ ] **CLAUDE**: Add Vercel frontend URL to backend CORS settings
- [ ] **YOU**: Redeploy backend with `fly deploy`

### Step 4.2: Test Everything
- [ ] **YOU**: Test the live app end-to-end
- [ ] **CLAUDE**: Fix any issues

---

## Current Progress

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Database | ✅ Complete | Neon (Frankfurt) - 10 traits, 50 questions, 20 idols |
| Phase 2: Backend | ✅ Complete | https://personaapp-backend.fly.dev |
| Phase 3: Frontend | ✅ Complete | https://personaapp-frontend.vercel.app |
| Phase 4: Final | ✅ Complete | CORS configured |

---

## Let's Start!

**First action**: Please go to https://neon.tech, create an account, and set up a new project. Let me know when you have the connection string!
