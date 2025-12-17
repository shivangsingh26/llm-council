"""
SQLAlchemy Database Models

Defines the database schema for research sessions and history.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()


class ResearchSession(Base):
    """
    Research session model - stores metadata about each research query

    The full ComparisonResult is saved as JSON file in outputs/,
    while this table stores lightweight metadata for quick querying.
    """
    __tablename__ = "research_sessions"

    # Primary key - UUID
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Query details
    query = Column(Text, nullable=False, index=True)
    domain = Column(String(50), nullable=False, index=True)

    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Agent results summary
    successful_agents = Column(Integer, default=0)
    total_agents = Column(Integer, default=0)
    failed_agents = Column(Text, nullable=True)  # JSON array of failed agent names

    # Usage metrics
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)

    # File reference
    file_path = Column(String(500), nullable=True)  # Path to full JSON result

    def __repr__(self):
        return f"<ResearchSession(id={self.id}, query={self.query[:50]}...)>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "query": self.query,
            "domain": self.domain,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "successful_agents": self.successful_agents,
            "total_agents": self.total_agents,
            "failed_agents": self.failed_agents,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "file_path": self.file_path,
        }
