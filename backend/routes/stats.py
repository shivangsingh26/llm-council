"""
Statistics API Routes

Endpoints:
- GET /api/stats - Get dashboard statistics
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.schemas import StatsResponse
from backend.database.connection import get_db
from backend.database.crud import get_stats

# Create router
router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get aggregate statistics for the dashboard

    This endpoint calculates and returns:
    - total_research: Total number of research sessions
    - total_queries: Same as total_research
    - total_tokens: Sum of all tokens used across all research
    - total_cost: Sum of all costs in USD
    - active_agents: Number of available agents (always 3)

    All data is aggregated from the database.

    Args:
        db: Database session (injected)

    Returns:
        StatsResponse with aggregate statistics

    Example:
        GET /api/stats

        Response:
        {
          "total_research": 45,
          "total_queries": 45,
          "total_tokens": 123456,
          "total_cost": 0.185,
          "active_agents": 3
        }
    """
    try:
        # Get stats from database
        stats = get_stats(db)

        return StatsResponse(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )
