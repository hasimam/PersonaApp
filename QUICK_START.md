# PersonaApp Quick Start

## TL;DR - Get Running in 5 Minutes

```bash
# 1. Create database
createdb personaapp

# 2. Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: Set DATABASE_URL and SECRET_KEY
alembic upgrade head
python -m app.db.seed

# 3. Start backend (Terminal 1)
uvicorn app.main:app --reload

# 4. Setup frontend (Terminal 2)
cd ../frontend
npm install
cp .env.example .env

# 5. Start frontend
npm start
```

Visit [http://localhost:3000](http://localhost:3000)

---

## What You Just Built

A full-stack personality matching webapp with:

- ✅ **50-question personality test** (Likert scale)
- ✅ **10 personality traits** (Strategic Thinking, Creativity, etc.)
- ✅ **20 celebrity idol profiles** (Taylor Swift, Beyoncé, Elon Musk, etc.)
- ✅ **Cosine similarity matching algorithm**
- ✅ **Interactive results visualization** (charts, comparisons)
- ✅ **Complete REST API** with auto-generated docs

---

## Project Files Overview

### Essential Documentation
- [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) - Milestone-based roadmap
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup instructions
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical deep dive

### Backend Core Files
```
backend/app/
├── main.py              # FastAPI entry point
├── core/
│   ├── scoring.py       # Test scoring logic ⭐
│   └── matching.py      # Cosine similarity ⭐
├── models/              # Database tables
├── api/                 # REST endpoints
└── db/seed.py          # Sample data
```

### Frontend Core Files
```
frontend/src/
├── App.tsx             # Router setup
├── pages/
│   ├── Landing.tsx     # Home page
│   ├── Test.tsx        # Personality test ⭐
│   └── Results.tsx     # Results display ⭐
└── services/api.ts     # Backend API client
```

---

## Key API Endpoints

```
GET  /api/v1/test/start
     → Start test, get questions

POST /api/v1/test/submit
     → Submit answers, get result_id

GET  /api/v1/results/:id
     → Retrieve full results

GET  /docs
     → Interactive API documentation
```

---

## Customization Quick Reference

### Add New Trait

1. **Database**: Add trait via admin or seed script
2. **Questions**: Create 5 questions for the trait
3. **Idols**: Update idol profiles with new trait score

### Add New Idol

```python
# In backend/app/db/seed.py or via admin API
new_idol = Idol(
    name="New Celebrity",
    description="Brief bio",
    image_url="https://...",
    trait_scores={
        "1": 80,  # Strategic Thinking
        "2": 75,  # Execution
        # ... scores for all 10 traits
    }
)
```

### Change Likert Scale

1. **Backend**: Update `settings.LIKERT_SCALE_MAX` in [config.py](backend/app/core/config.py)
2. **Frontend**: Update `LIKERT_OPTIONS` in [QuestionCard.tsx](frontend/src/components/test/QuestionCard.tsx)

### Modify Matching Algorithm

Edit [backend/app/core/matching.py](backend/app/core/matching.py):
- Change from cosine similarity to Euclidean distance
- Add weighted traits
- Filter by categories

---

## Testing Your Changes

### Test Backend API
```bash
# Interactive API testing
open http://localhost:8000/docs

# CLI testing
curl http://localhost:8000/api/v1/test/start
```

### Test Frontend
```bash
cd frontend
npm start
# Browser auto-opens with hot reload
```

### End-to-End Test
1. Take full test
2. Check database:
   ```sql
   psql personaapp
   SELECT * FROM results ORDER BY created_at DESC LIMIT 1;
   ```
3. Verify results page shows correct data

---

## Common Workflows

### Reset Database
```bash
cd backend
source venv/bin/activate
alembic downgrade base
alembic upgrade head
python -m app.db.seed
```

### Add Database Field
```bash
# 1. Edit model in backend/app/models/
# 2. Create migration
alembic revision --autogenerate -m "Add new field"
# 3. Review migration in alembic/versions/
# 4. Apply migration
alembic upgrade head
```

### Deploy to Production
```bash
# Backend (Railway/Render)
git push origin main  # Automatic deploy if configured

# Frontend (Vercel)
npm run build
# Follow Vercel deployment guide
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Database connection fails | Check PostgreSQL running: `brew services list` |
| CORS errors in browser | Verify `CORS_ORIGINS` in backend `.env` |
| Frontend won't start | Delete `node_modules`, run `npm install` again |
| Backend import errors | Activate venv: `source venv/bin/activate` |
| Wrong results showing | Clear cached results: `DELETE FROM results;` |

---

## What's Already Implemented

✅ **MVP Features**
- Complete personality test flow
- Trait score calculation
- Cosine similarity matching
- Top 3 idol results
- Visualization (radar chart, bars)
- Session tracking
- Result caching

✅ **Code Quality**
- Type safety (TypeScript + Pydantic)
- Input validation
- Error handling
- RESTful API design
- Database migrations
- Environment configuration

---

## What's NOT Implemented (Yet)

The following are planned for future milestones:

❌ User authentication (accounts)
❌ Admin interface (currently via API only)
❌ Share results on social media
❌ Friend comparison mode
❌ Analytics dashboard
❌ Multi-language support
❌ Email results
❌ Retake history tracking

See [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) Milestones 8-11 for details.

---

## Next Steps

1. **Familiarize yourself**: Take the test, explore the codebase
2. **Customize data**: Add your own idols and questions
3. **Review milestones**: Read [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)
4. **Start developing**: Follow Milestone 2 (Admin Interface) or Milestone 5 (Polish & UX)

---

## Resources

- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **FastAPI Tutorial**: [https://fastapi.tiangolo.com/tutorial/](https://fastapi.tiangolo.com/tutorial/)
- **React Docs**: [https://react.dev/](https://react.dev/)
- **PostgreSQL Docs**: [https://www.postgresql.org/docs/](https://www.postgresql.org/docs/)

---

## Getting Help

**Before asking for help:**
1. Check [SETUP_GUIDE.md](SETUP_GUIDE.md) troubleshooting section
2. Check browser console for errors (F12)
3. Check backend terminal for error logs
4. Verify environment variables in `.env` files

**Common issues are documented in [SETUP_GUIDE.md](SETUP_GUIDE.md)**

---

Happy building! 🎉
