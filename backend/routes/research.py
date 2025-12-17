"""
Research API Routes

Endpoints:
- POST /api/research - Execute new research with all agents
- GET /api/research/{id} - Get specific research result by ID
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import uuid
import json
from pathlib import Path

from backend.schemas import ResearchRequest, ResearchResponse
from backend.services.research import ResearchService
from backend.database.connection import get_db
from backend.database.crud import create_research_session, get_research_session_by_id
from src.models.schemas import ComparisonResult

# Create router
router = APIRouter()

# Initialize research service
research_service = ResearchService()


@router.post("/research", response_model=ResearchResponse)
async def execute_research(
    request: ResearchRequest,
    db: Session = Depends(get_db)
):
    """
    Execute new research with all available agents

    This endpoint:
    1. Validates the request
    2. Runs research with all available agents (GPT-4o, Gemini, DeepSeek)
    3. Aggregates the results
    4. Saves to database and file system
    5. Returns the comparison result

    Args:
        request: ResearchRequest with query, domain, and max_tokens
        db: Database session (injected)

    Returns:
        ResearchResponse with success status and ComparisonResult data

    Example:
        POST /api/research
        {
            "query": "What are the benefits of exercise?",
            "domain": "health",
            "max_tokens": 500
        }
    """
    try:
        print(f"\n{'='*60}")
        print(f"📝 New research request received")
        print(f"{'='*60}")

        # Execute research using the service
        # This also saves the file via OutputManager
        comparison = await research_service.execute_research(
            query=request.query,
            domain=request.domain,
            max_tokens=request.max_tokens or 500
        )

        # Generate session ID
        session_id = str(uuid.uuid4())

        # Failed agents are already tracked in comparison.failed_agents by the SDK
        failed_agents = comparison.failed_agents if comparison.failed_agents else []

        # Get file path from the _metadata field (added by OutputManager)
        # If not available, construct expected path
        file_path = None
        if hasattr(comparison, 'model_dump'):
            data = comparison.model_dump()
            if '_metadata' in data and 'file_path' in data['_metadata']:
                file_path = data['_metadata']['file_path']

        # Fallback: construct expected path pattern (without timestamp since we don't know it)
        # We'll need to search for the file in the directory
        if not file_path:
            # The file was just saved, so find the most recent file in the domain directory
            domain_dir = Path(f"outputs/council_comparisons/{request.domain.value}")
            if domain_dir.exists():
                files = sorted(domain_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
                if files:
                    file_path = str(files[0])

        # Save metadata to database
        db_session = create_research_session(
            db=db,
            session_id=session_id,
            query=request.query,
            domain=request.domain.value,
            successful_agents=len(comparison.responses) - len(failed_agents),
            total_agents=len(comparison.responses),
            failed_agents=failed_agents,
            total_tokens=comparison.total_tokens,
            total_cost=comparison.total_cost,
            file_path=file_path
        )

        print(f"✅ Research session saved to database: {session_id}")
        print(f"{'='*60}\n")

        return ResearchResponse(
            success=True,
            message="Research completed successfully",
            data=comparison
        )

    except ValueError as e:
        # Configuration errors (no agents available)
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Unexpected errors
        print(f"❌ Research failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Research execution failed: {str(e)}"
        )


@router.get("/research/{research_id}", response_model=ResearchResponse)
async def get_research_by_id(
    research_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific research result by ID

    This endpoint:
    1. Looks up the research session in the database
    2. Loads the full ComparisonResult from the JSON file
    3. Returns the complete result

    Args:
        research_id: UUID of the research session
        db: Database session (injected)

    Returns:
        ResearchResponse with the full ComparisonResult

    Example:
        GET /api/research/123e4567-e89b-12d3-a456-426614174000
    """
    try:
        # Get research session from database
        session = get_research_session_by_id(db, research_id)

        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Research session not found: {research_id}"
            )

        # Load full result from JSON file
        if session.file_path:
            file_path = Path(session.file_path)

            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    comparison = ComparisonResult(**data)

                return ResearchResponse(
                    success=True,
                    message="Research result retrieved successfully",
                    data=comparison
                )
            else:
                # File not found - return metadata only
                raise HTTPException(
                    status_code=404,
                    detail=f"Result file not found: {session.file_path}"
                )
        else:
            # No file path stored
            raise HTTPException(
                status_code=404,
                detail="No result file associated with this research session"
            )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve research: {str(e)}"
        )
