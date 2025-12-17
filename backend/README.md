# Backend API Server

This is the backend FastAPI service for LLM Council. It wraps the `llm_council` SDK (located in `src/`) and provides a REST API for the Next.js frontend.

## Architecture

```
┌─────────────────────────────────────┐
│     Frontend (Next.js)              │
│     Port 3000                       │
└──────────────┬──────────────────────┘
               │ HTTP/REST
┌──────────────▼──────────────────────┐
│     Backend (FastAPI)               │
│     Port 8000                       │
│  ┌──────────────────────────────┐  │
│  │  Routes (API Endpoints)      │  │
│  ├──────────────────────────────┤  │
│  │  Services (Business Logic)   │  │
│  ├──────────────────────────────┤  │
│  │  Database (SQLite)           │  │
│  └──────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   LLM Council SDK (src/)            │
│  - Agents (GPT-4o, Gemini, DeepSeek)│
│  - Orchestrator                     │
│  - Aggregator                       │
└─────────────────────────────────────┘
```

## Directory Structure

```
backend/
├── main.py              # FastAPI app entry point
├── schemas.py           # API request/response schemas
├── routes/              # API route handlers
│   ├── research.py      # Research endpoints
│   ├── history.py       # History endpoints
│   └── stats.py         # Statistics endpoint
├── services/            # Business logic layer
│   └── research.py      # Research service (wraps SDK)
└── database/            # Database layer
    ├── models.py        # SQLAlchemy models
    ├── connection.py    # Database connection
    └── crud.py          # Database operations
```

## How to Run

### 1. Install Dependencies

Make sure you're in the project root and have the virtual environment activated:

```bash
# Install dependencies (if not already done)
uv pip install -e .
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root with your API keys:

```bash
# Required for OpenAI Agent (GPT-4o)
OPENAI_API_KEY=sk-...

# Required for Gemini Agent
GEMINI_API_KEY=...

# Optional: DeepSeek uses Ollama (no API key needed)
```

### 3. Start the Backend Server

From the project root:

```bash
uvicorn backend.main:app --reload --port 8000
```

The backend will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Research

- **POST /api/research** - Execute new research
  ```json
  {
    "query": "What are the benefits of exercise?",
    "domain": "health",
    "max_tokens": 500
  }
  ```

- **GET /api/research/{id}** - Get research by ID

### History

- **GET /api/history** - List research history
  - Query params: `limit`, `offset`, `domain`

- **DELETE /api/research/{id}** - Delete research

### Statistics

- **GET /api/stats** - Get dashboard statistics

## Testing

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Get stats
curl http://localhost:8000/api/stats

# Execute research
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the benefits of exercise?",
    "domain": "health",
    "max_tokens": 500
  }'

# Get history
curl http://localhost:8000/api/history?limit=10
```

### Using Swagger UI

Navigate to http://localhost:8000/docs and test endpoints interactively.

## Database

The backend uses SQLite for data persistence:
- **Location**: `llm_council.db` (in project root)
- **Tables**: `research_sessions`

The database is automatically created on first run.

## Development

### Adding New Endpoints

1. Create route handler in `backend/routes/`
2. Add schemas to `backend/schemas.py` if needed
3. Register router in `backend/main.py`

### Adding New Services

1. Create service in `backend/services/`
2. Import and use SDK components from `src/`

## Notes

- The backend is a **wrapper** around the SDK - all core logic lives in `src/`
- `src/` should remain pure Python package code (no FastAPI dependencies)
- All API-specific code lives in `backend/`
