"""
Research Response Schemas
=========================
Pydantic models for structured AI research outputs.

Why Pydantic?
- Automatic validation: Ensures data has correct types
- IDE autocomplete: Type hints make coding easier
- Serialization: Easy conversion to/from JSON
- Documentation: Self-documenting code

Learning: Instead of parsing raw text, we get structured objects!
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class ResearchDomain(str, Enum):
    """
    The four research domains for your AI Council.

    Enum provides:
    - Type safety: Can't use invalid domain names
    - Autocomplete: IDE suggests valid options
    - Validation: Pydantic rejects invalid values
    """
    SPORTS = "sports"
    FINANCE = "finance"
    SHOPPING = "shopping"
    HEALTHCARE = "healthcare"


class ConfidenceLevel(str, Enum):
    """
    How confident the AI is in its research.

    This will be important later when models disagree!
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ResearchResponse(BaseModel):
    """
    Main research response from a single AI agent.

    This is what each AI model returns when researching a query.

    Field Parameters:
    - description: Explains what the field contains
    - examples: Shows valid values
    - min_length/max_length: Validation rules

    Learning Point: Structured data makes it easy to compare
    responses from different models later!
    """

    # Core response data
    query: str = Field(
        description="The original research question asked",
        examples=["What were the scores in yesterday's NBA games?"]
    )

    answer: str = Field(
        description="The AI's research findings",
        min_length=10,
        examples=["The Lakers beat the Celtics 112-109 in overtime..."]
    )

    # Metadata about the research
    domain: ResearchDomain = Field(
        description="Which domain this research belongs to"
    )

    confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.MEDIUM,
        description="How confident the AI is in this answer"
    )

    # Supporting information
    key_points: List[str] = Field(
        default_factory=list,
        description="Main takeaways as bullet points",
        examples=[["Lakers won 112-109", "LeBron scored 35 points", "Game went to OT"]]
    )

    sources: Optional[List[str]] = Field(
        default=None,
        description="URLs or references (if available)",
        examples=[["https://nba.com/game/lal-vs-bos"]]
    )

    # Tracking info
    model_name: str = Field(
        description="Which AI model produced this response",
        examples=["gemini-2.5-flash", "gpt-4o", "claude-3-5-sonnet"]
    )

    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When this research was conducted"
    )

    # Token usage (for cost tracking)
    tokens_used: Optional[int] = Field(
        default=None,
        description="Total tokens consumed by this request"
    )

    class Config:
        """
        Pydantic configuration.

        json_schema_extra provides example data for documentation.
        This appears in API docs and helps other developers understand usage.
        """
        json_schema_extra = {
            "example": {
                "query": "What are the latest electric vehicle sales trends?",
                "answer": "Electric vehicle sales increased 35% year-over-year in Q4 2024...",
                "domain": "finance",
                "confidence": "high",
                "key_points": [
                    "EV sales up 35% YoY",
                    "Tesla leads with 42% market share",
                    "China remains largest EV market"
                ],
                "sources": ["https://example.com/ev-report"],
                "model_name": "gemini-2.5-flash",
                "tokens_used": 245
            }
        }


class ComparisonResult(BaseModel):
    """
    Aggregated result from multiple AI agents.

    Used by the Council Orchestrator to compare and synthesize
    responses from multiple models.

    This enables:
    - Seeing all model responses side-by-side
    - Identifying consensus (where models agree)
    - Highlighting disagreements (where models differ)
    - Creating a synthesized final answer
    """

    # Core data
    query: str = Field(
        description="The research question asked"
    )

    domain: ResearchDomain = Field(
        description="Research domain"
    )

    # Individual responses from each model
    responses: Dict[str, ResearchResponse] = Field(
        description="Map of model name to response",
        examples=[{"gpt-4o": {}, "gemini-2.5-flash": {}}]
    )

    # Comparison metrics
    total_agents: int = Field(
        description="Total number of agents queried"
    )

    successful_agents: int = Field(
        description="Number of agents that responded successfully"
    )

    failed_agents: List[str] = Field(
        default_factory=list,
        description="List of models that failed to respond"
    )

    # Analysis
    consensus_points: List[str] = Field(
        default_factory=list,
        description="Key points where all models agree"
    )

    disagreement_points: List[str] = Field(
        default_factory=list,
        description="Points where models disagree"
    )

    confidence_range: Optional[str] = Field(
        default=None,
        description="Range of confidence levels across models",
        examples=["medium to very_high"]
    )

    # Synthesized output
    synthesized_answer: Optional[str] = Field(
        default=None,
        description="Combined/synthesized answer from all models"
    )

    # Metadata
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When this council research was conducted"
    )

    total_tokens: Optional[int] = Field(
        default=None,
        description="Total tokens used across all models"
    )

    total_cost: Optional[float] = Field(
        default=None,
        description="Estimated total cost in USD"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Is it safe to invest in crypto now?",
                "domain": "finance",
                "responses": {
                    "gpt-4o": {},
                    "gemini-2.5-flash": {}
                },
                "total_agents": 3,
                "successful_agents": 2,
                "failed_agents": ["deepseek-r1:14b"],
                "consensus_points": [
                    "Cryptocurrency is highly volatile",
                    "Diversification is important"
                ],
                "disagreement_points": [
                    "GPT suggests waiting, Gemini says buy small amounts"
                ],
                "confidence_range": "medium to high",
                "synthesized_answer": "Crypto remains high-risk; only invest what you can afford to lose",
                "total_tokens": 1234,
                "total_cost": 0.0012
            }
        }


# Example usage (for learning):
if __name__ == "__main__":
    """
    This demonstrates how to use these schemas.
    Run: python -m src.models.schemas
    """

    # Create a research response
    response = ResearchResponse(
        query="Who won the Super Bowl in 2024?",
        answer="The Kansas City Chiefs won Super Bowl LVIII, defeating the San Francisco 49ers 25-22 in overtime.",
        domain=ResearchDomain.SPORTS,
        confidence=ConfidenceLevel.VERY_HIGH,
        key_points=[
            "Chiefs won 25-22 in OT",
            "First Super Bowl to go to overtime under new rules",
            "Patrick Mahomes named MVP"
        ],
        model_name="gemini-2.5-flash",
        tokens_used=156
    )

    # Pydantic automatically validates the data
    print("✅ Response created successfully!")
    print(f"\nQuery: {response.query}")
    print(f"Domain: {response.domain.value}")
    print(f"Confidence: {response.confidence.value}")
    print(f"\nAnswer:\n{response.answer}")
    print(f"\nKey Points:")
    for point in response.key_points:
        print(f"  • {point}")

    # Convert to JSON (useful for saving/APIs)
    print("\n" + "="*60)
    print("JSON Representation:")
    print(response.model_dump_json(indent=2))
