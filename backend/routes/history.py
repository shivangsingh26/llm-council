"""
History API Routes

Endpoints:
- GET /api/history - List research history with pagination and filters
- DELETE /api/research/{id} - Delete a research session
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from pathlib import Path
import os

from backend.schemas import HistoryListResponse, HistoryItem, DeleteResponse
from backend.database.connection import get_db
from backend.database.crud import (
    get_research_sessions,
    get_total_count,
    delete_research_session,
    get_research_session_by_id
)
from src.models.schemas import ResearchDomain

# Create router
router = APIRouter()


@router.get("/history", response_model=HistoryListResponse)
async def get_history(
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    db: Session = Depends(get_db)
):
    """
    Get research history with pagination and filtering

    Returns a list of research sessions ordered by timestamp (newest first).
    Each item contains lightweight metadata - full results can be fetched
    via GET /api/research/{id}.

    Args:
        limit: Maximum number of items to return (1-100)
        offset: Number of items to skip for pagination
        domain: Optional domain filter (sports, finance, shopping, health)
        db: Database session (injected)

    Returns:
        HistoryListResponse with list of research items and total count

    Example:
        GET /api/history?limit=10&offset=0&domain=health
    """
    try:
        # Get research sessions from database
        sessions = get_research_sessions(
            db=db,
            limit=limit,
            offset=offset,
            domain=domain
        )

        # Get total count for pagination
        total = get_total_count(db=db, domain=domain)

        # Convert to HistoryItem schema
        history_items = []
        for session in sessions:
            history_items.append(HistoryItem(
                id=session.id,
                query=session.query,
                domain=ResearchDomain(session.domain),
                timestamp=session.timestamp.isoformat(),
                successful_agents=session.successful_agents,
                total_agents=session.total_agents
            ))

        return HistoryListResponse(
            success=True,
            data=history_items,
            total=total
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve history: {str(e)}"
        )


@router.delete("/research/{research_id}", response_model=DeleteResponse)
async def delete_research(
    research_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a research session

    This will:
    1. Delete the database record
    2. Delete the associated JSON file from outputs/

    Args:
        research_id: UUID of the research session to delete
        db: Database session (injected)

    Returns:
        DeleteResponse with success status

    Example:
        DELETE /api/research/123e4567-e89b-12d3-a456-426614174000
    """
    try:
        # Get research session to find file path
        session = get_research_session_by_id(db, research_id)

        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Research session not found: {research_id}"
            )

        # Delete file if it exists
        if session.file_path:
            file_path = Path(session.file_path)
            if file_path.exists():
                try:
                    os.remove(file_path)
                    print(f"🗑️  Deleted file: {file_path}")
                except Exception as e:
                    print(f"⚠️  Failed to delete file {file_path}: {e}")
                    # Continue anyway - delete from database

        # Delete from database
        deleted = delete_research_session(db, research_id)

        if deleted:
            print(f"✅ Deleted research session: {research_id}")
            return DeleteResponse(
                success=True,
                message="Research session deleted successfully"
            )
        else:
            # Should not reach here since we checked above
            raise HTTPException(
                status_code=404,
                detail=f"Failed to delete research session: {research_id}"
            )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete research: {str(e)}"
        )
