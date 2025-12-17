"""
Backend FastAPI Application - Main Entry Point

This backend service provides a REST API for the LLM Council system.
It wraps the llm_council SDK (src/) and provides endpoints for:
- Research execution
- History management
- Statistics

HOW TO RUN:
    uvicorn backend.main:app --reload --port 8000

The app will be available at: http://localhost:8000
API docs (Swagger UI): http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.routes import research, history, stats
from backend.database.connection import init_db
import os
from pathlib import Path

# ============================================================================
# LIFESPAN EVENT HANDLER
# ============================================================================

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Lifespan event handler - runs on startup and shutdown

    This replaces the deprecated @app.on_event("startup") and @app.on_event("shutdown")
    """
    # STARTUP
    print("\n" + "="*60)
    print("🚀 LLM Council Backend API Starting Up...")
    print("="*60)

    # Initialize database
    init_db()

    # Create outputs directory if it doesn't exist
    outputs_dir = Path("outputs/council_comparisons")
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # Display API information
    print("\n📚 API Documentation:")
    print("   Swagger UI: http://localhost:8000/docs")
    print("   ReDoc:      http://localhost:8000/redoc")

    print("\n🔗 Endpoints:")
    print("   POST   /api/research       - Execute new research")
    print("   GET    /api/research/{id}  - Get research by ID")
    print("   GET    /api/history        - List research history")
    print("   DELETE /api/research/{id}  - Delete research")
    print("   GET    /api/stats          - Get statistics")

    print("\n🔑 API Keys Status:")
    print(f"   OpenAI:  {'✅ Configured' if os.getenv('OPENAI_API_KEY') else '❌ Not configured'}")
    print(f"   Gemini:  {'✅ Configured' if os.getenv('GEMINI_API_KEY') else '❌ Not configured'}")

    print("\n" + "="*60)
    print("✅ Backend ready to accept requests!")
    print("="*60 + "\n")

    yield

    # SHUTDOWN
    print("\n👋 LLM Council API shutting down...")


# ============================================================================
# CREATE FASTAPI APP
# ============================================================================

app = FastAPI(
    lifespan=lifespan,
    title="LLM Council API",
    description=(
        "Backend API for LLM Council - A multi-agent research system that uses "
        "GPT-4o, Gemini 2.5 Flash, and DeepSeek R1 to provide comprehensive "
        "research analysis with consensus detection and disagreement analysis."
    ),
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc UI
)

# ============================================================================
# CORS CONFIGURATION
# ============================================================================
# This allows your Next.js frontend (running on port 3000) to call this API

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
        "http://localhost:3003",  # Alternative port
        "http://127.0.0.1:3003",
        # Add production URLs here later:
        # "https://your-app.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# ============================================================================
# INCLUDE ROUTES
# ============================================================================
# Routes are organized in separate files for clarity

app.include_router(research.router, prefix="/api", tags=["Research"])
app.include_router(history.router, prefix="/api", tags=["History"])
app.include_router(stats.router, prefix="/api", tags=["Stats"])

# ============================================================================
# ROOT ENDPOINT (health check)
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint with API information

    Test with: curl http://localhost:8000/
    """
    return {
        "message": "LLM Council API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "research": "/api/research",
            "history": "/api/history",
            "stats": "/api/stats"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check for production monitoring

    Test with: curl http://localhost:8000/health
    """
    # Check database connection
    try:
        from backend.database.connection import get_db_session
        db = get_db_session()
        db.execute("SELECT 1")
        db.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Check API keys
    api_keys = {
        "openai": "configured" if os.getenv("OPENAI_API_KEY") else "not configured",
        "gemini": "configured" if os.getenv("GEMINI_API_KEY") else "not configured"
    }

    return {
        "status": "healthy",
        "database": db_status,
        "api_keys": api_keys
    }
