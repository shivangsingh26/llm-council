"""
Unit tests for Assumption Critic jury specialist.

Tests:
- Hidden assumption detection
- Edge case generation
- Bias identification
- Robustness scoring
"""

import pytest
import os
from unittest.mock import AsyncMock, patch
from src.jury.assumption_critic import AssumptionCritic
from src.models.schemas import ResearchResponse


@pytest.fixture
def openai_api_key():
    """Get OpenAI API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")
    return api_key


@pytest.fixture
def assumption_critic(openai_api_key):
    """Create AssumptionCritic instance."""
    return AssumptionCritic(api_key=openai_api_key)


@pytest.fixture
def sample_responses_with_assumptions():
    """Sample responses that make implicit assumptions."""
    return {
        "model_1": ResearchResponse(
            answer="Economic growth always leads to improved quality of life.",
            key_points=["Economic growth", "Quality of life improvement"],
            sources=["Economics textbook"],
            confidence=0.7,
            reasoning_trace="Traditional economic theory"
        ),
        "model_2": ResearchResponse(
            answer="Higher GDP correlates with better living standards.",
            key_points=["GDP correlation", "Living standards"],
            sources=["World Bank data"],
            confidence=0.75,
            reasoning_trace="Statistical correlation"
        )
    }


@pytest.fixture
def robust_responses():
    """Sample responses with minimal assumptions."""
    return {
        "model": ResearchResponse(
            answer="In controlled laboratory conditions at standard temperature and pressure, water boils at 100°C.",
            key_points=["Controlled conditions", "100°C boiling point", "STP"],
            sources=["Physics textbook"],
            confidence=0.98,
            reasoning_trace="Well-defined physical constant"
        )
    }


@pytest.mark.asyncio
async def test_assumption_critic_initialization(openai_api_key):
    """Test Assumption Critic can be initialized."""
    critic = AssumptionCritic(api_key=openai_api_key)

    assert critic is not None
    assert critic.model_name == "gpt-4o"
    assert critic.role.value == "assumption_critic"
    assert critic.client is not None


@pytest.mark.asyncio
async def test_analyze_assumptions(assumption_critic, sample_responses_with_assumptions):
    """Test detection of hidden assumptions."""
    query = "Does economic growth improve quality of life?"
    synthesized_answer = "Economic growth generally improves quality of life."

    result = await assumption_critic.analyze(
        query=query,
        council_responses=sample_responses_with_assumptions,
        synthesized_answer=synthesized_answer
    )

    # Check result structure
    assert "hidden_assumptions" in result
    assert "edge_cases" in result
    assert "robustness_score" in result
    assert "role" in result
    assert result["role"] == "assumption_critic"

    # Check types
    assert isinstance(result["hidden_assumptions"], list)
    assert isinstance(result["edge_cases"], list)
    assert isinstance(result["robustness_score"], float)
    assert 0.0 <= result["robustness_score"] <= 1.0


@pytest.mark.asyncio
async def test_analyze_robust_claims(assumption_critic, robust_responses):
    """Test analysis of robust claims with few assumptions."""
    query = "At what temperature does water boil?"
    synthesized_answer = "Water boils at 100°C at standard temperature and pressure."

    result = await assumption_critic.analyze(
        query=query,
        council_responses=robust_responses,
        synthesized_answer=synthesized_answer
    )

    # Robust claims should have high robustness score
    assert result["robustness_score"] >= 0.5
    assert "hidden_assumptions" in result
    assert "edge_cases" in result


@pytest.mark.asyncio
async def test_build_critique_prompt(assumption_critic, sample_responses_with_assumptions):
    """Test critique prompt construction."""
    query = "Test query"
    synthesized_answer = "Test answer"

    prompt = assumption_critic._build_critique_prompt(
        query,
        synthesized_answer,
        sample_responses_with_assumptions
    )

    assert isinstance(prompt, str)
    assert "Research Question" in prompt
    assert "Test query" in prompt
    assert "Synthesized Answer" in prompt
    assert "Test answer" in prompt
    assert "Council Responses" in prompt


@pytest.mark.asyncio
async def test_format_metadata(assumption_critic):
    """Test metadata formatting."""
    metadata = assumption_critic._format_metadata()

    assert "role" in metadata
    assert "model" in metadata
    assert metadata["role"] == "assumption_critic"
    assert metadata["model"] == "gpt-4o"


@pytest.mark.asyncio
async def test_parse_critique_json_format(assumption_critic):
    """Test parsing of critique results in JSON format."""
    json_text = """```json
    {
        "hidden_assumptions": [
            "Assumes Western legal framework",
            "Presumes current geopolitical status"
        ],
        "edge_cases": [
            {
                "scenario": "What if interest rates go negative?",
                "impact": "Claim would not hold"
            }
        ],
        "bias_detected": {
            "type": "confirmation_bias",
            "description": "Only considers supporting evidence"
        },
        "fragile_claims": ["Claim X breaks under scenario Y"],
        "robustness_score": 0.65,
        "recommendations": ["Consider alternative frameworks"]
    }
    ```"""

    result = assumption_critic._parse_critique(json_text)

    assert "hidden_assumptions" in result
    assert "edge_cases" in result
    assert "robustness_score" in result
    assert result["robustness_score"] == 0.65
    assert len(result["hidden_assumptions"]) == 2
    assert "bias_detected" in result


@pytest.mark.asyncio
async def test_parse_critique_fallback(assumption_critic):
    """Test fallback parsing for non-JSON text."""
    non_json_text = "This is not valid JSON"

    result = assumption_critic._parse_critique(non_json_text)

    # Should return fallback structure
    assert "hidden_assumptions" in result
    assert "edge_cases" in result
    assert "robustness_score" in result
    assert result["robustness_score"] == 0.6
    assert "recommendations" in result
    assert "Failed to parse critique results" in result["recommendations"]


@pytest.mark.asyncio
async def test_error_handling(assumption_critic):
    """Test error handling with API errors."""
    # Create critic with invalid key
    invalid_critic = AssumptionCritic(api_key="invalid_key_12345")

    query = "Test query"
    responses = {
        "model": ResearchResponse(
            answer="Test answer",
            key_points=["Test"],
            sources=[],
            confidence=0.5,
            reasoning_trace=""
        )
    }
    synthesized_answer = "Test synthesis"

    result = await invalid_critic.analyze(
        query=query,
        council_responses=responses,
        synthesized_answer=synthesized_answer
    )

    # Should return error state
    assert "error" in result
    assert result["robustness_score"] == 0.5
    assert "hidden_assumptions" in result
    assert "edge_cases" in result


@pytest.mark.asyncio
async def test_bias_detection(assumption_critic):
    """Test detection of bias in responses."""
    biased_responses = {
        "model": ResearchResponse(
            answer="All studies show that product X is superior to all alternatives.",
            key_points=["Product X superior", "All studies agree"],
            sources=["ProductX Marketing"],
            confidence=0.9,
            reasoning_trace="Company-sponsored research"
        )
    }

    query = "Is product X the best?"
    synthesized_answer = "Product X is superior according to available studies."

    result = await assumption_critic.analyze(
        query=query,
        council_responses=biased_responses,
        synthesized_answer=synthesized_answer
    )

    # Should analyze potential bias
    assert "bias_detected" in result or "hidden_assumptions" in result
    assert isinstance(result["robustness_score"], float)


@pytest.mark.asyncio
async def test_edge_case_generation(assumption_critic, sample_responses_with_assumptions):
    """Test generation of edge cases."""
    query = "Does economic growth improve quality of life?"
    synthesized_answer = "Economic growth generally improves quality of life."

    result = await assumption_critic.analyze(
        query=query,
        council_responses=sample_responses_with_assumptions,
        synthesized_answer=synthesized_answer
    )

    # Should generate edge cases
    assert "edge_cases" in result
    assert isinstance(result["edge_cases"], list)


@pytest.mark.asyncio
async def test_recommendations(assumption_critic, sample_responses_with_assumptions):
    """Test that recommendations are provided."""
    query = "Does economic growth improve quality of life?"
    synthesized_answer = "Economic growth improves quality of life."

    result = await assumption_critic.analyze(
        query=query,
        council_responses=sample_responses_with_assumptions,
        synthesized_answer=synthesized_answer
    )

    # Should provide recommendations
    assert "recommendations" in result
    assert isinstance(result["recommendations"], list)


@pytest.mark.asyncio
async def test_fragile_claims_detection(assumption_critic):
    """Test detection of fragile claims."""
    fragile_responses = {
        "model": ResearchResponse(
            answer="Stock market will always go up in the long run.",
            key_points=["Market always rises", "Long-term guarantee"],
            sources=["Investment Blog"],
            confidence=0.6,
            reasoning_trace="Historical trend"
        )
    }

    query = "Will the stock market always go up?"
    synthesized_answer = "Historically, markets trend upward."

    result = await assumption_critic.analyze(
        query=query,
        council_responses=fragile_responses,
        synthesized_answer=synthesized_answer
    )

    # Should identify fragile claims
    assert "fragile_claims" in result or "edge_cases" in result
    # Fragile claims should result in lower robustness
    assert result["robustness_score"] <= 0.8


@pytest.mark.asyncio
async def test_system_prompt_temperature(assumption_critic):
    """Test that system prompt encourages creative thinking."""
    system_prompt = assumption_critic._get_system_prompt()

    assert "devil's advocate" in system_prompt.lower()
    assert "challenge" in system_prompt.lower()
    assert "edge cases" in system_prompt.lower()


@pytest.mark.asyncio
async def test_empty_responses(assumption_critic):
    """Test handling of empty responses."""
    empty_responses = {}
    query = "Test query"
    synthesized_answer = "Test answer"

    result = await assumption_critic.analyze(
        query=query,
        council_responses=empty_responses,
        synthesized_answer=synthesized_answer
    )

    # Should handle gracefully
    assert "robustness_score" in result
    assert isinstance(result["robustness_score"], float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
