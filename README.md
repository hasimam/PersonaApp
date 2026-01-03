# PersonaApp - Personality Matching Webapp

A personality-matching webapp that allows users to take a custom personality test and discover their top 3 most similar idols based on trait vector analysis.

## Quick Start

### ✨ Everything is Already Set Up!

All dependencies are installed, database is configured and seeded with sample data.

### Running the App

Simply run:

```bash
./start.sh
```

This will:
1. Start PostgreSQL (if not running)
2. Start the backend API server (port 8000)
3. Start the frontend React app (port 3000)
4. Automatically open your browser to http://localhost:3000

### Stopping the App

```bash
./stop.sh
```

This gracefully stops both the backend and frontend servers.

## Access Points

- **Web App**: [http://localhost:3000](http://localhost:3000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

## What's Already Configured

✅ Node.js 25.2.1 and npm 11.6.2
✅ Python 3.9.6 with virtual environment
✅ PostgreSQL 14 database (`personaapp`)
✅ All backend dependencies installed
✅ All frontend dependencies installed
✅ Database schema migrated
✅ Sample data seeded (10 traits, 50 questions, 20 idols)
✅ Environment files configured

## Manual Start (Alternative)

If you prefer to run servers manually:

**Terminal 1 - Backend**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend**
```bash
cd frontend
npm start
```

## Project Structure

See [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) for detailed architecture and milestones.

## Documentation

- [Development Plan](DEVELOPMENT_PLAN.md) - Milestones, tech stack, and roadmap
- [Product Design](docs/Product%20Design%20from%20The%20App.md) - UX and features
- [Technical Design](docs/The%20App%20Technical%20Design.md) - Architecture
- [API Documentation](http://localhost:8000/docs) - Auto-generated Swagger docs (when backend is running)

## Tech Stack

- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python
- **Database**: PostgreSQL
- **Matching**: Cosine similarity algorithm

## License

MIT
