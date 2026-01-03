# PersonaApp Setup Guide

Complete step-by-step instructions to get your development environment running.

## Prerequisites

Before starting, ensure you have these installed:

- **Node.js** 18+ and npm ([Download](https://nodejs.org/))
- **Python** 3.9+ ([Download](https://www.python.org/downloads/))
- **PostgreSQL** 14+ ([Download](https://www.postgresql.org/download/))
- **Git** ([Download](https://git-scm.com/))

## Step 1: Clone or Initialize Repository

If you haven't already:

```bash
cd /Users/hasanalimam/repos/PersonaApp
git init
git add .
git commit -m "Initial commit - PersonaApp setup"
```

## Step 2: Database Setup

### Create PostgreSQL Database

```bash
# Start PostgreSQL (if not already running)
# macOS with Homebrew:
brew services start postgresql

# Create database
createdb personaapp

# Verify database exists
psql -l | grep personaapp
```

## Step 3: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env with your settings (use your preferred editor)
nano .env
```

### Configure `.env` File

Edit `backend/.env`:

```bash
DATABASE_URL=postgresql://localhost/personaapp
SECRET_KEY=your-secret-key-change-this-in-production-use-random-string
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

To generate a secure SECRET_KEY:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Initialize Database

```bash
# Still in backend/ directory with venv activated

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# Seed database with sample data
python -m app.db.seed
```

You should see output like:
```
✓ Created database tables
✓ Created 10 traits
✓ Created 50 questions
✓ Created 20 idol profiles
✅ Database seeding completed successfully!
```

### Test Backend

```bash
# Start the FastAPI server
uvicorn app.main:app --reload
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) to see the interactive API documentation.

Test the health endpoint:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

## Step 4: Frontend Setup

Open a **new terminal** (keep backend running):

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env if needed (defaults should work)
# REACT_APP_API_URL=http://localhost:8000
```

### Start Frontend

```bash
npm start
```

The app should automatically open in your browser at [http://localhost:3000](http://localhost:3000).

## Step 5: Verify Everything Works

### Test the Complete Flow

1. **Landing Page**: Visit [http://localhost:3000](http://localhost:3000)
2. **Start Test**: Click "Start Personality Test"
3. **Answer Questions**: Answer all 50 questions
4. **View Results**: See your top 3 idol matches and personality profile

### Check Backend Logs

In your backend terminal, you should see API requests being logged:

```
INFO:     127.0.0.1 - "GET /api/v1/test/start HTTP/1.1" 200 OK
INFO:     127.0.0.1 - "POST /api/v1/test/submit HTTP/1.1" 200 OK
INFO:     127.0.0.1 - "GET /api/v1/results/1 HTTP/1.1" 200 OK
```

## Common Issues & Solutions

### Issue: PostgreSQL Connection Error

**Error**: `could not connect to server: Connection refused`

**Solution**:
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Start if not running
brew services start postgresql
```

### Issue: Port 8000 Already in Use

**Solution**:
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --reload --port 8001
# Update frontend .env: REACT_APP_API_URL=http://localhost:8001
```

### Issue: Port 3000 Already in Use

**Solution**:
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or run on different port
PORT=3001 npm start
```

### Issue: Module Import Errors in Backend

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: CORS Errors in Browser Console

**Solution**:

Check `backend/.env` has correct CORS settings:
```
CORS_ORIGINS=http://localhost:3000
```

If using different port, update accordingly.

## Project Structure Overview

```
PersonaApp/
├── backend/              # FastAPI Python backend
│   ├── app/
│   │   ├── api/          # API route handlers
│   │   ├── core/         # Business logic (scoring, matching)
│   │   ├── db/           # Database config and seeding
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic validation schemas
│   │   └── main.py       # FastAPI app entry point
│   ├── alembic/          # Database migrations
│   ├── requirements.txt
│   └── .env              # Environment variables
│
├── frontend/             # React TypeScript frontend
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Route pages (Landing, Test, Results)
│   │   ├── services/     # API client
│   │   ├── types/        # TypeScript interfaces
│   │   └── App.tsx       # Main app component
│   ├── public/
│   ├── package.json
│   └── .env              # Environment variables
│
└── docs/                 # Planning documents
```

## Development Workflow

### Running Both Servers

You need **two terminal windows**:

**Terminal 1 - Backend**:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm start
```

### Making Database Changes

1. Update model in `backend/app/models/`
2. Create migration:
   ```bash
   alembic revision --autogenerate -m "Description of change"
   ```
3. Review migration in `alembic/versions/`
4. Apply migration:
   ```bash
   alembic upgrade head
   ```

### Adding New API Endpoints

1. Create/update route in `backend/app/api/`
2. Add schemas in `backend/app/schemas/`
3. Update frontend API client in `frontend/src/services/api.ts`
4. Test in Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Next Steps

Now that your development environment is running, refer to [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) for:

- Milestone-based development roadmap
- Feature implementation order
- Testing strategies
- Deployment guidelines

## Quick Commands Reference

```bash
# Backend
cd backend
source venv/bin/activate              # Activate venv
uvicorn app.main:app --reload         # Start server
alembic upgrade head                  # Run migrations
python -m app.db.seed                 # Seed database
pytest                                # Run tests (when added)

# Frontend
cd frontend
npm start                             # Start dev server
npm run build                         # Production build
npm test                              # Run tests

# Database
psql personaapp                       # Connect to database
createdb personaapp                   # Create database
dropdb personaapp                     # Delete database (careful!)
```

## Getting Help

- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Development Plan**: [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)
- **Technical Design**: [docs/The App Technical Design.md](docs/The%20App%20Technical%20Design.md)

Happy coding! 🚀
