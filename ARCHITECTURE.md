# PersonaApp Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                            │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              React Frontend (Port 3000)                   │ │
│  │                                                           │ │
│  │  • Landing Page                                          │ │
│  │  • Test Interface (50 questions)                        │ │
│  │  • Results Display (Top 3 matches + charts)            │ │
│  │                                                         │ │
│  │  Components:                                           │ │
│  │    - QuestionCard (Likert scale input)               │ │
│  │    - ProgressBar                                     │ │
│  │    - Results visualization (Recharts)               │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓ HTTP/REST                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              API Routes (/api/v1/)                  │   │
│  │                                                     │   │
│  │  • POST /test/start    → Generate session & questions │
│  │  • POST /test/submit   → Process responses        │   │
│  │  • GET  /results/:id   → Retrieve results         │   │
│  └─────────────────────────────────────────────────────┘   │
│                           ↓                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Business Logic (Core)                    │   │
│  │                                                     │   │
│  │  scoring.py:                                       │   │
│  │    - Aggregate Likert responses                   │   │
│  │    - Apply reverse scoring                        │   │
│  │    - Normalize to 0-100 scale                    │   │
│  │                                                   │   │
│  │  matching.py:                                    │   │
│  │    - Convert trait dicts to vectors             │   │
│  │    - Calculate cosine similarity                │   │
│  │    - Rank idols by similarity                  │   │
│  └─────────────────────────────────────────────────┘   │
│                           ↓                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │        SQLAlchemy ORM Models                    │   │
│  │                                                 │   │
│  │  • Trait        • Question                     │   │
│  │  • Idol         • User                        │   │
│  │  • TestResponse • Result                     │   │
│  └─────────────────────────────────────────────────┘   │
│                           ↓                             │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              PostgreSQL Database                        │
│                                                         │
│  Tables:                                               │
│    - traits          (10 personality dimensions)       │
│    - questions       (50 test questions)              │
│    - idols           (20+ celebrity profiles)         │
│    - users           (session tracking)               │
│    - test_responses  (individual answers)            │
│    - results         (cached calculations)           │
└─────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

### Flow 1: User Takes Test

```
┌──────────┐
│  User    │
│  clicks  │
│ "Start"  │
└────┬─────┘
     │
     ▼
┌─────────────────────────┐
│ Frontend: Landing.tsx   │
│ Navigates to /test      │
└────┬────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────┐
│ Frontend: Test.tsx                          │
│ useEffect() on mount                        │
│   → calls testApi.startTest()               │
└────┬────────────────────────────────────────┘
     │ HTTP GET
     ▼
┌─────────────────────────────────────────────┐
│ Backend: GET /api/v1/test/start             │
│                                             │
│ 1. Generate UUID session_id                 │
│ 2. Create User record in DB                 │
│ 3. Query all Questions from DB              │
│ 4. Return {session_id, questions[]}         │
└────┬────────────────────────────────────────┘
     │ JSON Response
     ▼
┌─────────────────────────────────────────────┐
│ Frontend: Test.tsx                          │
│ Stores session_id & questions in state     │
│ Renders QuestionCard component             │
│                                            │
│ User answers 50 questions (1-5 scale)     │
│ Stored in Map<question_id, answer>       │
└────┬───────────────────────────────────────┘
     │
     ▼ User clicks "Submit"
┌─────────────────────────────────────────────┐
│ Frontend: Test.tsx                          │
│ handleSubmit()                             │
│   → calls testApi.submitTest()             │
│   → sends {session_id, responses[]}        │
└────┬────────────────────────────────────────┘
     │ HTTP POST
     ▼
┌─────────────────────────────────────────────┐
│ Backend: POST /api/v1/test/submit           │
│                                             │
│ 1. Validate session_id exists               │
│ 2. Validate all responses (scoring.py)      │
│ 3. Save responses to test_responses table   │
│ 4. Calculate trait scores (scoring.py)      │
│    • Group by trait_id                      │
│    • Apply reverse scoring                  │
│    • Normalize to 0-100                     │
│ 5. Find top matches (matching.py)           │
│    • Load all idol profiles                 │
│    • Calculate cosine similarity            │
│    • Sort and take top 3                    │
│ 6. Save Result record to DB                 │
│ 7. Return {result_id}                       │
└────┬────────────────────────────────────────┘
     │ JSON Response
     ▼
┌─────────────────────────────────────────────┐
│ Frontend: Test.tsx                          │
│ Navigates to /results/:result_id           │
└─────────────────────────────────────────────┘
```

### Flow 2: Viewing Results

```
┌──────────────────────────────────────────────┐
│ Frontend: Results.tsx                        │
│ useEffect() on mount                         │
│   → calls resultsApi.getResult(resultId)     │
└────┬─────────────────────────────────────────┘
     │ HTTP GET
     ▼
┌─────────────────────────────────────────────┐
│ Backend: GET /api/v1/results/:result_id     │
│                                             │
│ 1. Query Result record from DB              │
│ 2. Get trait names from traits table        │
│ 3. Get full idol info from idols table      │
│ 4. Format and return response               │
└────┬────────────────────────────────────────┘
     │ JSON Response
     ▼
┌─────────────────────────────────────────────┐
│ Frontend: Results.tsx                       │
│                                            │
│ Displays:                                  │
│ • Top 3 idol cards with similarity %       │
│ • Radar chart (user's trait profile)      │
│ • Bar charts (trait-by-trait scores)      │
└─────────────────────────────────────────────┘
```

---

## Scoring Algorithm Detail

```python
# For each trait (e.g., "Strategic Thinking")

Input: 5 questions × Likert responses (1-5)
Example: [4, 5, 2, 4, 3]
         ↑           ↑
    normal    reverse-scored

Step 1: Apply reverse scoring
  - Normal questions: keep as-is
  - Reverse questions: score = (5 + 1) - original
    Example: 2 becomes (6 - 2) = 4

Adjusted: [4, 5, 4, 4, 3]

Step 2: Calculate average
  Average = (4 + 5 + 4 + 4 + 3) / 5 = 4.0

Step 3: Normalize to 0-100 scale
  Formula: ((avg - min) / (max - min)) × 100
  = ((4.0 - 1) / (5 - 1)) × 100
  = (3.0 / 4.0) × 100
  = 75.0

Output: Strategic Thinking = 75.0
```

---

## Matching Algorithm Detail

```python
# Cosine Similarity Calculation

User Trait Vector:
  [Strategic=75, Execution=85, Creativity=60, ...]
  → Vector U = [75, 85, 60, 80, 70, 75, 90, 65, 85, 80]

Idol Trait Vector (e.g., Taylor Swift):
  [Strategic=85, Execution=90, Creativity=95, ...]
  → Vector I = [85, 90, 95, 80, 85, 70, 90, 65, 85, 75]

Cosine Similarity Formula:
  similarity = (U · I) / (||U|| × ||I||)

Where:
  U · I = dot product = 75×85 + 85×90 + ... = 62,950
  ||U|| = magnitude of U = sqrt(75² + 85² + ...) = 249.4
  ||I|| = magnitude of I = sqrt(85² + 90² + ...) = 269.1

  similarity = 62,950 / (249.4 × 269.1) = 0.938

Result: 93.8% match with Taylor Swift
```

**Why Cosine Similarity?**
- Measures angle between vectors (not distance)
- Focuses on pattern similarity, not absolute values
- Scale-invariant (works with normalized scores)
- Standard in personality psychology and recommendation systems

---

## Database Schema Details

### Core Tables

**traits**
```sql
id          SERIAL PRIMARY KEY
name        VARCHAR(100)        -- "Strategic Thinking"
description TEXT                -- Full explanation
high_behavior TEXT              -- What high scores mean
low_behavior  TEXT              -- What low scores mean
created_at  TIMESTAMP
```

**questions**
```sql
id              SERIAL PRIMARY KEY
text            TEXT               -- Question text
trait_id        INTEGER FK         -- Links to trait
reverse_scored  BOOLEAN            -- Needs score reversal?
order_index     INTEGER            -- Display order
created_at      TIMESTAMP
```

**idols**
```sql
id          SERIAL PRIMARY KEY
name        VARCHAR(100)           -- "Taylor Swift"
description TEXT                   -- Brief bio
image_url   VARCHAR(255)          -- Profile image
trait_scores JSONB                 -- {"1": 75, "2": 90, ...}
created_at  TIMESTAMP
```

**users**
```sql
id          SERIAL PRIMARY KEY
session_id  VARCHAR(255) UNIQUE   -- UUID for session
email       VARCHAR(255)          -- Optional (MVP uses session)
created_at  TIMESTAMP
```

**test_responses**
```sql
id          SERIAL PRIMARY KEY
user_id     INTEGER FK            -- Links to user
session_id  VARCHAR(255)          -- For session tracking
question_id INTEGER FK            -- Links to question
response    INTEGER               -- 1-5 Likert value
created_at  TIMESTAMP
```

**results**
```sql
id          SERIAL PRIMARY KEY
user_id     INTEGER FK
session_id  VARCHAR(255)
trait_scores JSONB                -- {"1": 75.5, "2": 82.3, ...}
top_matches  JSONB                -- [{"idol_id": 5, "similarity": 0.92}, ...]
created_at   TIMESTAMP
```

---

## Technology Justification

### Backend: FastAPI (Python)

**Chosen because:**
- ✅ Fast development with automatic API docs
- ✅ Python ecosystem for math (NumPy, SciPy)
- ✅ Pydantic for strong typing and validation
- ✅ Async support for scalability
- ✅ Easy to test and maintain

**Alternatives considered:**
- Node.js/Express: Less ideal for mathematical operations
- Django: More heavyweight, slower iteration

### Frontend: React + TypeScript

**Chosen because:**
- ✅ Component reusability (QuestionCard, IdolCard)
- ✅ Large ecosystem (Recharts for visualization)
- ✅ TypeScript for type safety
- ✅ Easy to migrate to React Native later

**Alternatives considered:**
- Vue: Smaller ecosystem
- Next.js: Overkill for MVP (no SSR needed)

### Database: PostgreSQL

**Chosen because:**
- ✅ JSONB support (flexible trait storage)
- ✅ ACID compliance (data integrity)
- ✅ Excellent performance for reads
- ✅ Free and open-source

**Alternatives considered:**
- Firebase: Less control, potential cost scaling
- MongoDB: Less structure, harder to query

---

## Security Considerations

### MVP (Current)
- Session-based identification (no passwords)
- Input validation via Pydantic
- CORS restrictions
- SQL injection prevention (ORM)

### Future Enhancements
- JWT authentication
- Rate limiting
- HTTPS only
- User data encryption
- GDPR compliance (data deletion)

---

## Performance Optimizations

### Current
- Result caching in database
- Database query optimization (indexed fields)
- Single calculation per test submission

### Future
- Redis caching for idol profiles
- CDN for static assets
- Database query pagination
- Frontend code splitting
- Image optimization

---

## Scalability Plan

### MVP Scale
- Supports: 100-1,000 concurrent users
- Infrastructure: Single server

### Growth Path
1. **1,000-10,000 users**: Add database replicas
2. **10,000-100,000 users**: Horizontal scaling, load balancer
3. **100,000+ users**: Microservices, separate matching service

---

## Testing Strategy

### Unit Tests
- Scoring algorithm accuracy
- Cosine similarity correctness
- Input validation

### Integration Tests
- API endpoint responses
- Database operations
- End-to-end test flow

### User Testing
- Consistency checks (retake same answers)
- Face validity (matches make sense)
- Completion rate tracking

---

## Deployment Architecture (Future)

```
┌──────────────┐
│   Vercel     │  ← React Frontend
│  (Frontend)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Railway    │  ← FastAPI Backend
│  (Backend)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL  │  ← Managed Database
│   (Render)   │
└──────────────┘
```

**Why this stack?**
- Free tier available for MVP
- Easy deployment (Git push)
- Automatic HTTPS
- Built-in monitoring
- Easy to scale

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Session-based auth (no login) | Reduces friction, faster MVP |
| 50 questions (5 per trait) | Balance between accuracy and completion |
| 1-5 Likert scale | Familiar, easy to understand |
| Cosine similarity | Industry standard for personality matching |
| JSONB for trait storage | Flexible schema for future trait changes |
| Cached results | Avoid re-calculation, faster loading |
| Top 3 matches only | Focused, shareable, not overwhelming |

---

## Future Architecture Enhancements

1. **Microservices**: Separate matching service for heavy computation
2. **Message Queue**: Async result processing for large user base
3. **Analytics Pipeline**: Track patterns, improve matching
4. **A/B Testing**: Question variations, UI experiments
5. **Real-time**: WebSocket for live result updates
