"""
Database Connection and Session Management

Provides database engine, session factory, and dependency injection for FastAPI.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.database.models import Base
import os
from pathlib import Path

# Database file location - store in project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATABASE_PATH = PROJECT_ROOT / "llm_council.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create engine
# check_same_thread=False is needed for SQLite to work with FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL debug logging
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    """
    Initialize database - create tables if they don't exist

    Call this when the FastAPI app starts up.
    """
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized at: {DATABASE_PATH}")


def get_db() -> Session:
    """
    FastAPI dependency for database sessions

    Usage in routes:
        @router.get("/endpoint")
        async def endpoint(db: Session = Depends(get_db)):
            # Use db here
            pass

    The session is automatically created and closed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get a database session for non-FastAPI contexts

    Usage:
        db = get_db_session()
        try:
            # Use db here
            db.commit()
        except:
            db.rollback()
        finally:
            db.close()
    """
    return SessionLocal()
