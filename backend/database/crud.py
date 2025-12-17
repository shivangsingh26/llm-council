"""
CRUD Operations for Database

Provides functions to Create, Read, Update, and Delete research sessions.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from backend.database.models import ResearchSession
from typing import List, Optional, Dict, Any
import json


def create_research_session(
    db: Session,
    session_id: str,
    query: str,
    domain: str,
    successful_agents: int,
    total_agents: int,
    failed_agents: List[str],
    total_tokens: int,
    total_cost: float,
    file_path: str
) -> ResearchSession:
    """
    Create a new research session in the database

    Args:
        db: Database session
        session_id: UUID for the research session
        query: Research question
        domain: Research domain (health, finance, etc.)
        successful_agents: Number of agents that succeeded
        total_agents: Total number of agents
        failed_agents: List of agent names that failed
        total_tokens: Total tokens used
        total_cost: Total cost in USD
        file_path: Path to the full JSON result file

    Returns:
        Created ResearchSession object
    """
    research = ResearchSession(
        id=session_id,
        query=query,
        domain=domain,
        successful_agents=successful_agents,
        total_agents=total_agents,
        failed_agents=json.dumps(failed_agents) if failed_agents else "[]",
        total_tokens=total_tokens,
        total_cost=total_cost,
        file_path=file_path
    )

    db.add(research)
    db.commit()
    db.refresh(research)

    return research


def get_research_sessions(
    db: Session,
    limit: int = 20,
    offset: int = 0,
    domain: Optional[str] = None
) -> List[ResearchSession]:
    """
    Get paginated list of research sessions

    Args:
        db: Database session
        limit: Maximum number of items to return
        offset: Number of items to skip
        domain: Optional domain filter

    Returns:
        List of ResearchSession objects
    """
    query = db.query(ResearchSession)

    # Apply domain filter if provided
    if domain:
        query = query.filter(ResearchSession.domain == domain)

    # Order by timestamp descending (newest first)
    query = query.order_by(desc(ResearchSession.timestamp))

    # Apply pagination
    return query.offset(offset).limit(limit).all()


def get_research_session_by_id(db: Session, session_id: str) -> Optional[ResearchSession]:
    """
    Get a single research session by ID

    Args:
        db: Database session
        session_id: UUID of the research session

    Returns:
        ResearchSession object or None if not found
    """
    return db.query(ResearchSession).filter(ResearchSession.id == session_id).first()


def delete_research_session(db: Session, session_id: str) -> bool:
    """
    Delete a research session from the database

    Args:
        db: Database session
        session_id: UUID of the research session to delete

    Returns:
        True if deleted, False if not found
    """
    research = get_research_session_by_id(db, session_id)

    if research:
        db.delete(research)
        db.commit()
        return True

    return False


def get_total_count(db: Session, domain: Optional[str] = None) -> int:
    """
    Get total count of research sessions (for pagination)

    Args:
        db: Database session
        domain: Optional domain filter

    Returns:
        Total count
    """
    query = db.query(ResearchSession)

    if domain:
        query = query.filter(ResearchSession.domain == domain)

    return query.count()


def get_stats(db: Session) -> Dict[str, Any]:
    """
    Get aggregate statistics for the dashboard

    Args:
        db: Database session

    Returns:
        Dictionary with statistics:
        - total_research: Total number of research sessions
        - total_tokens: Sum of all tokens used
        - total_cost: Sum of all costs
    """
    result = db.query(
        func.count(ResearchSession.id).label('total'),
        func.sum(ResearchSession.total_tokens).label('tokens'),
        func.sum(ResearchSession.total_cost).label('cost')
    ).first()

    return {
        "total_research": result.total or 0,
        "total_queries": result.total or 0,  # Same as total_research
        "total_tokens": int(result.tokens or 0),
        "total_cost": float(result.cost or 0.0),
        "active_agents": 3  # Fixed value - GPT-4o, Gemini, DeepSeek
    }


def get_recent_sessions(db: Session, limit: int = 5) -> List[ResearchSession]:
    """
    Get most recent research sessions

    Args:
        db: Database session
        limit: Number of recent sessions to return

    Returns:
        List of ResearchSession objects
    """
    return (
        db.query(ResearchSession)
        .order_by(desc(ResearchSession.timestamp))
        .limit(limit)
        .all()
    )
