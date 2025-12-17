"""
Backend API Server for LLM Council

This backend service wraps the llm_council SDK (src/) and provides
a REST API + SSE interface for the Next.js frontend.

Architecture:
- src/ = Pure llm_council SDK/package
- backend/ = FastAPI service wrapping the SDK
"""

__version__ = "1.0.0"