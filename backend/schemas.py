"""
API Request/Response Schemas

These Pydantic models define the structure of data coming IN (requests)
and going OUT (responses) from the API.

Separation:
- API schemas = what the frontend sends/receives (simple, flat)
- SDK schemas (src/models/schemas.py) = internal business logic (complex, nested)
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from src.models.schemas import ResearchDomain, ComparisonResult


# ============================================================================
# REQUEST SCHEMAS (what frontend sends TO backend)
# ============================================================================

class ResearchRequest(BaseModel):
    """
    Request body for starting a new research session

    Example from frontend:
    {
        "query": "What are the benefits of exercise?",
        "domain": "health",
        "max_tokens": 500
    }
    """
    query: str = Field(..., min_length=10, description="Research question (min 10 chars)")
    domain: ResearchDomain = Field(..., description="Research domain")
    max_tokens: Optional[int] = Field(500, ge=100, le=2000, description="Max tokens per agent")


# ============================================================================
# RESPONSE SCHEMAS (what backend sends TO frontend)
# ============================================================================

class ResearchResponse(BaseModel):
    """
    Response after research completes

    This wraps the ComparisonResult from SDK schemas
    """
    success: bool
    message: str
    data: Optional[ComparisonResult] = None
    error: Optional[str] = None


class HistoryItem(BaseModel):
    """
    Single item in history list (lightweight version)

    Why lightweight? When showing a list, we don't need ALL details.
    Full details are fetched when user clicks "View"
    """
    id: str
    query: str
    domain: ResearchDomain
    timestamp: str
    successful_agents: int
    total_agents: int


class HistoryListResponse(BaseModel):
    """Response containing list of research history"""
    success: bool
    data: List[HistoryItem]
    total: int


class StatsResponse(BaseModel):
    """
    Dashboard statistics

    These numbers are calculated from the database
    """
    total_research: int = Field(description="Total research sessions")
    total_queries: int = Field(description="Same as total_research for now")
    total_tokens: int = Field(description="Sum of all tokens used")
    total_cost: float = Field(description="Sum of all costs")
    active_agents: int = Field(default=3, description="Number of available agents")


class DeleteResponse(BaseModel):
    """Response after deleting a research session"""
    success: bool
    message: str


# ============================================================================
# SSE EVENT SCHEMAS (Server-Sent Events for streaming)
# ============================================================================

class AgentStatusEvent(BaseModel):
    """
    Real-time update about an agent's status

    Frontend receives these as SSE events and updates UI in real-time
    """
    event_type: str = Field(description="status_update | agent_start | agent_complete | complete")
    model_name: Optional[str] = None
    status: Optional[str] = None  # idle | running | completed | failed
    data: Optional[Dict] = None
