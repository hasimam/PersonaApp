# PersonaApp - Quick Start Guide

## 🚀 Start Testing in 1 Command

Everything is already set up! Just run:

```bash
./start.sh
```

Your browser will automatically open to [http://localhost:3000](http://localhost:3000)

## 🛑 Stop the App

```bash
./stop.sh
```

## ✅ What's Already Done

- ✅ Node.js 25.2.1 installed
- ✅ Python 3.9.6 virtual environment created
- ✅ PostgreSQL 14 installed and running
- ✅ Database `personaapp` created
- ✅ Backend dependencies installed
- ✅ Frontend dependencies installed
- ✅ Database schema migrated
- ✅ Sample data seeded:
  - 10 personality traits
  - 50 test questions
  - 20 celebrity idol profiles

## 📍 Access Points

- **App**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🎯 How to Use the App

1. Run `./start.sh`
2. Browser opens to http://localhost:3000
3. Click "Start Personality Test"
4. Answer 50 questions
5. Get your top 3 idol matches!

## 🔧 Troubleshooting

### Ports Already in Use

```bash
# Kill backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Kill frontend (port 3000)
lsof -ti:3000 | xargs kill -9
```

### View Logs

```bash
# Backend logs
tail -f /tmp/personaapp-backend.log

# Frontend logs
tail -f /tmp/personaapp-frontend.log
```

### Restart PostgreSQL

```bash
brew services restart postgresql@14
```

## 📝 Manual Start (Alternative)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

---

**That's it!** Run `./start.sh` and you're ready to test! 🎉
