# PersonaApp - Personality Matching Webapp

A personality-matching webapp that allows users to take a custom personality test and discover their top 3 most similar idols based on trait vector analysis.

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- PostgreSQL 14+

### Setup

1. **Clone and install dependencies**
```bash
# Frontend setup
cd frontend
npm install

# Backend setup
cd ../backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Database setup**
```bash
# Create PostgreSQL database
createdb personaapp

# Run migrations
cd backend
alembic upgrade head

# Seed initial data
python -m app.db.seed
```

3. **Environment variables**
```bash
# Backend (.env in backend/)
DATABASE_URL=postgresql://localhost/personaapp
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000

# Frontend (.env in frontend/)
REACT_APP_API_URL=http://localhost:8000
```

4. **Run development servers**
```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm start
```

Visit http://localhost:3000 to see the app!

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
