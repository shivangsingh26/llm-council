# Phase 4 Implementation Plan
**LLM Council Backend API + Frontend Integration**

## 📋 Overview

This document outlines the complete implementation plan for Phase 4, which connects the frontend (Next.js) with the backend (FastAPI) to create a fully functional full-stack LLM Council application.

### Phase 4 Goals
1. ✅ Build FastAPI REST API endpoints around existing council functionality
2. ✅ Implement Server-Sent Events (SSE) for real-time agent status updates
3. ✅ Add SQLite database for research history persistence
4. ✅ Connect frontend to backend APIs (replace all mock data)
5. ✅ Test complete end-to-end flow with all 3 agents

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Dashboard │  │ Research │  │ History  │  │ Settings │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │             │              │             │         │
│       └─────────────┴──────────────┴─────────────┘         │
│                     │                                       │
│              ┌──────▼───────┐                              │
│              │ SDK Client   │                              │
│              │ (fetch API)  │                              │
│              └──────┬───────┘                              │
└─────────────────────┼─────────────────────────────────────┘
                      │ HTTP/SSE
┌─────────────────────▼─────────────────────────────────────┐
│                BACKEND (FastAPI + Python)                  │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                  API Routes                           │ │
│  │  /api/research    /api/history    /api/stats         │ │
│  └──────────┬────────────┬────────────┬──────────────────┘ │
│             │            │            │                    │
│  ┌──────────▼────────────▼────────────▼──────────────────┐ │
│  │           Council Orchestrator                        │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │ │
│  │  │  GPT-4o  │  │  Gemini  │  │ DeepSeek │           │ │
│  │  │  Agent   │  │  Agent   │  │  Agent   │           │ │
│  │  └──────────┘  └──────────┘  └──────────┘           │ │
│  │                  (asyncio.gather)                     │ │
│  └──────────┬────────────────────────────────────────────┘ │
│             │                                              │
│  ┌──────────▼──────────────────────────────────────────┐  │
│  │      Response Aggregator                            │  │
│  │  - Consensus detection                              │  │
│  │  - Disagreement analysis                            │  │
│  │  - Cost calculation                                 │  │
│  └──────────┬──────────────────────────────────────────┘  │
│             │                                              │
│  ┌──────────▼──────────────────────────────────────────┐  │
│  │      SQLite Database + File Storage                 │  │
│  │  - Research history (metadata)                      │  │
│  │  - Full results (JSON files in outputs/)           │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure Changes

### Backend (New Files to Create)
```
src/api/
├── __init__.py           # ✅ Exists
├── main.py               # ✅ Exists (needs route imports)
├── schemas.py            # ✅ Exists
├── routes/               # 🆕 TO CREATE
│   ├── __init__.py       # 🆕
│   ├── research.py       # 🆕 POST /api/research, GET /api/research/{id}
│   ├── history.py        # 🆕 GET /api/history, DELETE /api/research/{id}
│   └── stats.py          # 🆕 GET /api/stats
├── database/             # 🆕 TO CREATE
│   ├── __init__.py       # 🆕
│   ├── models.py         # 🆕 SQLAlchemy models
│   ├── connection.py     # 🆕 Database connection
│   └── crud.py           # 🆕 CRUD operations
└── services/             # 🆕 TO CREATE
    ├── __init__.py       # 🆕
    └── research.py       # 🆕 Research service (orchestration logic)
```

### Frontend (Files to Modify)
```
frontend/
├── lib/
│   └── sdk-client.ts     # 🔧 MODIFY: Ensure correct backend URL
├── app/
│   ├── page.tsx          # 🔧 MODIFY: Replace mock stats/history
│   ├── research/
│   │   └── page.tsx      # 🔧 MODIFY: Replace mock research, add SSE
│   ├── history/
│   │   └── page.tsx      # 🔧 MODIFY: Replace mock history
│   └── settings/
│       └── page.tsx      # 🔧 MODIFY: (Optional - Phase 5)
└── .env.local            # 🆕 CREATE: Add NEXT_PUBLIC_API_URL
```

---

## 🔧 Backend Implementation Details

### 1. API Routes

#### `/api/research` (POST) - Start New Research
**File**: `src/api/routes/research.py`

**Request**:
```json
{
  "query": "What are the benefits of exercise?",
  "domain": "health",
  "max_tokens": 500
}
```

**Flow**:
1. Validate request (Pydantic)
2. Initialize agents based on available API keys
3. Create `CouncilOrchestrator` with agents
4. Run `council.research_all()` (parallel execution)
5. Aggregate responses with `ResponseAggregator`
6. Save to database + JSON files
7. Return `ComparisonResult`

**Response**:
```json
{
  "success": true,
  "message": "Research completed successfully",
  "data": {
    "query": "...",
    "synthesized_answer": "...",
    "responses": {...},
    "consensus_points": [...],
    "total_tokens": 1234,
    "total_cost": 0.000185
  }
}
```

---

#### `/api/research/stream` (GET with SSE) - Real-time Updates
**File**: `src/api/routes/research.py`

**Purpose**: Stream agent status updates in real-time using Server-Sent Events

**Event Types**:
```typescript
// Event 1: Agent starting
{event: "agent_start", data: {model_name: "gpt-4o", status: "running"}}

// Event 2: Agent completed
{event: "agent_complete", data: {model_name: "gpt-4o", status: "completed", tokens: 245}}

// Event 3: Agent failed
{event: "agent_error", data: {model_name: "gemini-2.5-flash", status: "failed", error: "API rate limit"}}

// Event 4: All completed
{event: "complete", data: {successful_agents: 3, total_agents: 3, result: {...}}}
```

**Implementation Pattern**:
```python
from sse_starlette.sse import EventSourceResponse

@router.get("/api/research/stream")
async def stream_research(query: str, domain: str):
    async def event_generator():
        # Start agents
        yield {"event": "agent_start", "data": {...}}

        # Run research (with callbacks)
        result = await council.research_all_with_callbacks(...)

        # Yield progress events
        yield {"event": "agent_complete", "data": {...}}

        # Final result
        yield {"event": "complete", "data": result}

    return EventSourceResponse(event_generator())
```

---

#### `/api/history` (GET) - List Research History
**File**: `src/api/routes/history.py`

**Query Parameters**:
- `limit` (int, default=20): Number of items
- `offset` (int, default=0): Pagination offset
- `domain` (str, optional): Filter by domain

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "query": "What are...",
      "domain": "health",
      "timestamp": "2024-12-14T10:30:00Z",
      "successful_agents": 3,
      "total_agents": 3
    }
  ],
  "total": 45
}
```

---

#### `/api/research/{id}` (GET) - Get Specific Research
**File**: `src/api/routes/research.py`

**Response**: Full `ComparisonResult` object

---

#### `/api/research/{id}` (DELETE) - Delete Research
**File**: `src/api/routes/history.py`

**Response**:
```json
{
  "success": true,
  "message": "Research deleted successfully"
}
```

---

#### `/api/stats` (GET) - Dashboard Statistics
**File**: `src/api/routes/stats.py`

**Response**:
```json
{
  "total_research": 45,
  "total_queries": 45,
  "total_tokens": 123456,
  "total_cost": 0.185,
  "active_agents": 3
}
```

**Calculation**: Query database + sum from saved JSON files

---

### 2. Database Layer

#### Schema Design (SQLite + SQLAlchemy)

**Table: `research_sessions`**
```sql
CREATE TABLE research_sessions (
    id TEXT PRIMARY KEY,              -- UUID
    query TEXT NOT NULL,
    domain TEXT NOT NULL,
    timestamp TEXT NOT NULL,          -- ISO 8601
    successful_agents INTEGER,
    total_agents INTEGER,
    failed_agents TEXT,               -- JSON array
    total_tokens INTEGER,
    total_cost REAL,
    file_path TEXT,                   -- Path to full JSON result
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Index**:
```sql
CREATE INDEX idx_timestamp ON research_sessions(timestamp DESC);
CREATE INDEX idx_domain ON research_sessions(domain);
```

---

#### SQLAlchemy Model
**File**: `src/api/database/models.py`

```python
from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    successful_agents = Column(Integer)
    total_agents = Column(Integer)
    failed_agents = Column(String)  # JSON
    total_tokens = Column(Integer)
    total_cost = Column(Float)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

#### Database Connection
**File**: `src/api/database/connection.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

DATABASE_URL = "sqlite:///./llm_council.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # For SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create tables if they don't exist"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

#### CRUD Operations
**File**: `src/api/database/crud.py`

```python
from sqlalchemy.orm import Session
from .models import ResearchSession
from typing import List, Optional

def create_research_session(db: Session, data: dict) -> ResearchSession:
    """Insert new research session"""
    session = ResearchSession(**data)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_research_sessions(
    db: Session,
    limit: int = 20,
    offset: int = 0,
    domain: Optional[str] = None
) -> List[ResearchSession]:
    """Get paginated research sessions"""
    query = db.query(ResearchSession)
    if domain:
        query = query.filter(ResearchSession.domain == domain)
    return query.order_by(ResearchSession.timestamp.desc()).offset(offset).limit(limit).all()

def get_research_session_by_id(db: Session, id: str) -> Optional[ResearchSession]:
    """Get single research session by ID"""
    return db.query(ResearchSession).filter(ResearchSession.id == id).first()

def delete_research_session(db: Session, id: str) -> bool:
    """Delete research session"""
    session = get_research_session_by_id(db, id)
    if session:
        db.delete(session)
        db.commit()
        return True
    return False

def get_total_count(db: Session, domain: Optional[str] = None) -> int:
    """Get total count for pagination"""
    query = db.query(ResearchSession)
    if domain:
        query = query.filter(ResearchSession.domain == domain)
    return query.count()

def get_stats(db: Session) -> dict:
    """Get aggregate statistics"""
    from sqlalchemy import func
    result = db.query(
        func.count(ResearchSession.id).label('total'),
        func.sum(ResearchSession.total_tokens).label('tokens'),
        func.sum(ResearchSession.total_cost).label('cost')
    ).first()

    return {
        "total_research": result.total or 0,
        "total_tokens": result.tokens or 0,
        "total_cost": result.cost or 0.0
    }
```

---

### 3. Research Service Layer
**File**: `src/api/services/research.py`

**Purpose**: Orchestrate the research flow (separate business logic from routes)

```python
from src.council.orchestrator import CouncilOrchestrator
from src.council.aggregator import ResponseAggregator
from src.agents.openai_agent import OpenAIAgent
from src.agents.gemini_agent import GeminiResearchAgent
from src.agents.deepseek_agent import DeepSeekAgent
from src.utils.output_manager import OutputManager
from src.models.schemas import ResearchDomain, ComparisonResult
import os

class ResearchService:
    def __init__(self):
        self.output_manager = OutputManager()

    def _create_agents(self):
        """Create agents based on available API keys"""
        agents = []

        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            agents.append(OpenAIAgent(api_key=os.getenv("OPENAI_API_KEY")))

        # Gemini
        if os.getenv("GEMINI_API_KEY"):
            agents.append(GeminiResearchAgent(api_key=os.getenv("GEMINI_API_KEY")))

        # DeepSeek (local)
        try:
            deepseek = DeepSeekAgent()
            if deepseek.check_ollama_status():
                agents.append(deepseek)
        except:
            pass  # Ollama not available

        return agents

    async def execute_research(
        self,
        query: str,
        domain: ResearchDomain,
        max_tokens: int = 500
    ) -> ComparisonResult:
        """Execute research with all available agents"""
        # Create agents
        agents = self._create_agents()

        if not agents:
            raise ValueError("No agents available. Please configure API keys.")

        # Create council and run research
        council = CouncilOrchestrator(agents)
        responses = await council.research_all(
            query=query,
            domain=domain,
            max_tokens=max_tokens
        )

        # Aggregate responses
        aggregator = ResponseAggregator()
        comparison = aggregator.aggregate(
            responses=responses,
            query=query,
            domain=domain
        )

        # Save to file
        self.output_manager.save_comparison(comparison)

        return comparison
```

---

## 🎨 Frontend Integration Details

### 1. Environment Variables
**File**: `frontend/.env.local` (create this file)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

### 2. SDK Client Updates
**File**: `frontend/lib/sdk-client.ts`

**Current implementation is already correct!** Just ensure `.env.local` is set.

Verify `executeResearch()` uses:
```typescript
const response = await fetch(`${this.baseUrl}/api/research`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(request)
})
```

---

### 3. Dashboard Integration
**File**: `frontend/app/page.tsx`

**Replace mock data (lines 7-16)**:
```typescript
// ❌ OLD (mock)
const mockStats = { total_research: 0, ... }
const mockRecentResearch = []

// ✅ NEW (real API)
import { sdkClient } from '@/lib/sdk-client'

export default async function DashboardPage() {
  // Fetch from backend
  const stats = await sdkClient.getStats()
  const recentResearch = await sdkClient.getHistory(5)

  return (
    <div>
      <StatsCards data={stats} />
      <RecentActivity items={recentResearch} />
    </div>
  )
}
```

---

### 4. Research Page Integration
**File**: `frontend/app/research/page.tsx`

**Replace mock research (lines 28-82)**:

```typescript
// ❌ OLD (setTimeout mock)
setTimeout(() => { ... }, 3000)

// ✅ NEW (real API with SSE)
import { sdkClient } from '@/lib/sdk-client'

const handleSubmit = async (data) => {
  setIsLoading(true)

  try {
    // Option 1: Simple POST (no streaming)
    const result = await sdkClient.executeResearch(data)
    setResults(result)

    // Option 2: SSE Streaming (real-time updates)
    const eventSource = sdkClient.streamResearch(data)

    eventSource.addEventListener('agent_start', (e) => {
      const data = JSON.parse(e.data)
      updateAgentStatus(data.model_name, 'running')
    })

    eventSource.addEventListener('agent_complete', (e) => {
      const data = JSON.parse(e.data)
      updateAgentStatus(data.model_name, 'completed')
    })

    eventSource.addEventListener('complete', (e) => {
      const result = JSON.parse(e.data)
      setResults(result)
      setIsLoading(false)
      eventSource.close()
    })
  } catch (error) {
    toast.error('Research failed: ' + error.message)
  }
}
```

---

### 5. History Page Integration
**File**: `frontend/app/history/page.tsx`

**Replace mock history (lines 10-42)**:

```typescript
// ❌ OLD (generateMockHistory)
const mockHistory = generateMockHistory()

// ✅ NEW (real API)
import { sdkClient } from '@/lib/sdk-client'
import { useState, useEffect } from 'react'

export default function HistoryPage() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      const data = await sdkClient.getHistory()
      setHistory(data)
    } catch (error) {
      toast.error('Failed to load history')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await sdkClient.deleteResearch(id)
      toast.success('Research deleted')
      loadHistory()  // Refresh list
    } catch (error) {
      toast.error('Delete failed')
    }
  }

  return (
    <div>
      {loading ? (
        <LoadingSkeleton />
      ) : (
        <HistoryList items={history} onDelete={handleDelete} />
      )}
    </div>
  )
}
```

---

## 🧪 Testing Strategy

### Backend Testing

#### 1. Test API Endpoints with curl

```bash
# Start backend
uvicorn src.api.main:app --reload --port 8000

# Health check
curl http://localhost:8000/health

# Test research (with all 3 agents)
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the benefits of exercise?",
    "domain": "health",
    "max_tokens": 500
  }'

# Get history
curl http://localhost:8000/api/history?limit=10

# Get stats
curl http://localhost:8000/api/stats

# Test SSE streaming
curl -N http://localhost:8000/api/research/stream?query=test&domain=general
```

#### 2. Test with Swagger UI
Navigate to: `http://localhost:8000/docs`

---

### Frontend Testing

#### 1. Test in Browser
```bash
# Start frontend
cd frontend
npm run dev

# Visit: http://localhost:3000
```

#### 2. Manual Testing Checklist
- [ ] Dashboard shows real stats
- [ ] Dashboard shows recent activity
- [ ] Research form submits successfully
- [ ] Agent status updates in real-time (if using SSE)
- [ ] Results display correctly with all sections
- [ ] History page loads research list
- [ ] History filters work
- [ ] Delete research works
- [ ] Error states show appropriate messages

---

### Integration Testing

#### Test Complete Flow
1. Start backend: `uvicorn src.api.main:app --reload --port 8000`
2. Start frontend: `npm run dev` (in frontend/)
3. Ensure `.env` has API keys: `OPENAI_API_KEY`, `GEMINI_API_KEY`
4. Optionally start Ollama: `ollama serve` + `ollama pull deepseek-r1:14b`
5. Submit research query
6. Verify all 3 agents respond
7. Check database: `sqlite3 llm_council.db "SELECT * FROM research_sessions;"`
8. Check file saved: `ls outputs/council_comparisons/health/`

---

## 📝 Implementation Order (Step-by-Step)

### Stage 1: Backend Foundation
1. ✅ Create routes directory and files
2. ✅ Create database models and connection
3. ✅ Initialize database (run migration script)
4. ✅ Test database CRUD operations

### Stage 2: API Endpoints (No SSE yet)
5. ✅ Implement `/api/research` POST endpoint
6. ✅ Implement `/api/history` GET endpoint
7. ✅ Implement `/api/research/{id}` GET endpoint
8. ✅ Implement `/api/research/{id}` DELETE endpoint
9. ✅ Implement `/api/stats` GET endpoint
10. ✅ Test all endpoints with curl/Swagger

### Stage 3: Frontend Integration (Basic)
11. ✅ Create `.env.local` with API URL
12. ✅ Update Dashboard to fetch real stats
13. ✅ Update Dashboard to fetch real history
14. ✅ Update Research form to call backend
15. ✅ Update History page to fetch real data
16. ✅ Update History delete to call backend
17. ✅ Test full flow (frontend → backend → database)

### Stage 4: Real-time SSE (Advanced)
18. ✅ Implement `/api/research/stream` SSE endpoint
19. ✅ Update Research page to use SSE
20. ✅ Test real-time agent status updates

### Stage 5: Polish & Testing
21. ✅ Add comprehensive error handling
22. ✅ Add loading states everywhere
23. ✅ Test edge cases (failed agents, network errors)
24. ✅ Update documentation
25. ✅ Create demo video/screenshots

---

## 🚀 Running the Full Stack

### Terminal 1: Backend
```bash
cd /Users/shivangsingh/Desktop/llm-council
source .venv/bin/activate
uvicorn src.api.main:app --reload --port 8000
```

### Terminal 2: Frontend
```bash
cd /Users/shivangsingh/Desktop/llm-council/frontend
npm run dev
```

### Terminal 3 (Optional): Ollama for DeepSeek
```bash
ollama serve
```

### Access URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: `llm_council.db` (in project root)

---

## 📊 Success Criteria

### Backend
- [ ] All 5 API endpoints working
- [ ] Database persists research history
- [ ] All 3 agents can run successfully
- [ ] SSE streaming works
- [ ] Error handling for failed agents
- [ ] API documentation at /docs

### Frontend
- [ ] No mock data (all real API calls)
- [ ] Dashboard shows actual stats
- [ ] Research form works end-to-end
- [ ] Real-time agent status updates (SSE)
- [ ] History page loads and deletes work
- [ ] Loading states during API calls
- [ ] Error messages for failures

### Integration
- [ ] Frontend ↔ Backend communication works
- [ ] CORS configured correctly
- [ ] Database updates after each research
- [ ] File system outputs match database
- [ ] All 3 agents respond correctly
- [ ] Cost calculations accurate

---

## 🔮 Future Enhancements (Phase 5+)

### Backend
- [ ] User authentication (JWT)
- [ ] Rate limiting (per user/IP)
- [ ] Web search integration (Tavily API)
- [ ] LangGraph for advanced workflows
- [ ] Redis caching for repeated queries
- [ ] Async task queue (Celery)
- [ ] Model comparison metrics

### Frontend
- [ ] Settings persistence to backend
- [ ] User accounts and login
- [ ] Compare page (side-by-side comparison)
- [ ] Analytics page (charts and trends)
- [ ] Export research as PDF
- [ ] Share research links

### Deployment
- [ ] Deploy backend to Railway/Render
- [ ] Deploy frontend to Vercel
- [ ] Set up production database (PostgreSQL)
- [ ] Configure environment variables
- [ ] Set up monitoring (Sentry)
- [ ] Add logging (structured logs)

---

## 📚 Key Files Reference

### Backend
| File | Purpose |
|------|---------|
| `src/api/main.py` | FastAPI app entry point |
| `src/api/routes/research.py` | Research endpoints |
| `src/api/routes/history.py` | History endpoints |
| `src/api/routes/stats.py` | Stats endpoint |
| `src/api/database/models.py` | SQLAlchemy models |
| `src/api/database/crud.py` | Database operations |
| `src/api/services/research.py` | Research orchestration |

### Frontend
| File | Purpose |
|------|---------|
| `lib/sdk-client.ts` | API client wrapper |
| `app/page.tsx` | Dashboard |
| `app/research/page.tsx` | Research form |
| `app/history/page.tsx` | History list |
| `.env.local` | Environment config |

---

**Last Updated**: 2024-12-15
**Status**: Ready for Implementation
**Estimated Time**: 8-12 hours (split across multiple sessions)

Let's build this! 🚀
