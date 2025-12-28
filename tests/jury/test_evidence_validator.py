"""
Unit tests for Evidence Validator jury specialist.

Tests:
- Source verification
- Citation hallucination detection
- Source quality assessment
- Error handling
"""

import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock
from src.jury.evidence_validator import EvidenceValidator
from src.models.schemas import ResearchResponse


@pytest.fixture
def openai_api_key():
    """Get OpenAI API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")
    return api_key


@pytest.fixture
def evidence_validator(openai_api_key):
    """Create EvidenceValidator instance."""
    return EvidenceValidator(api_key=openai_api_key)


@pytest.fixture
def sample_council_responses():
    """Sample council responses for testing."""
    return {
        "gpt-4o": ResearchResponse(
            answer="The Earth orbits the Sun due to gravitational attraction, completing one orbit every 365.25 days.",
            key_points=["Gravitational attraction", "365.25 days orbit"],
            sources=["NASA Planetary Fact Sheet"],
            confidence=0.95,
            reasoning_trace="Well-established astronomical fact"
        ),
        "gemini-2.5-flash": ResearchResponse(
            answer="Earth's orbital period is approximately 365.25 days, which is why we have leap years.",
            key_points=["365.25 day period", "Leap year explanation"],
            sources=["Scientific American"],
            confidence=0.92,
            reasoning_trace="Based on Kepler's laws"
        )
    }


@pytest.mark.asyncio
async def test_evidence_validator_initialization(openai_api_key):
    """Test Evidence Validator can be initialized."""
    validator = EvidenceValidator(api_key=openai_api_key)

    assert validator is not None
    assert validator.model_name == "gpt-4o"
    assert validator.role.value == "evidence_validator"
    assert validator.client is not None


@pytest.mark.asyncio
async def test_analyze_valid_sources(evidence_validator, sample_council_responses):
    """Test analysis of responses with valid sources."""
    query = "How long does Earth take to orbit the Sun?"
    synthesized_answer = "Earth orbits the Sun in approximately 365.25 days."

    result = await evidence_validator.analyze(
        query=query,
        council_responses=sample_council_responses,
        synthesized_answer=synthesized_answer
    )

    # Check result structure
    assert "validations" in result
    assert "overall_source_quality" in result
    assert "citation_hallucinations_detected" in result
    assert "role" in result
    assert result["role"] == "evidence_validator"

    # Check quality metrics
    assert isinstance(result["overall_source_quality"], float)
    assert 0.0 <= result["overall_source_quality"] <= 1.0
    assert isinstance(result["citation_hallucinations_detected"], bool)


@pytest.mark.asyncio
async def test_analyze_controversial_claims(evidence_validator):
    """Test analysis of controversial or unsupported claims."""
    controversial_responses = {
        "model_1": ResearchResponse(
            answer="Ancient aliens built the pyramids according to recent discoveries.",
            key_points=["Alien construction"],
            sources=["UnverifiedBlog.com"],
            confidence=0.3,
            reasoning_trace="Speculative claim"
        )
    }

    query = "Who built the pyramids?"
    synthesized_answer = "The pyramids were built by ancient Egyptians."

    result = await evidence_validator.analyze(
        query=query,
        council_responses=controversial_responses,
        synthesized_answer=synthesized_answer
    )

    # Should flag low-quality sources
    assert result["overall_source_quality"] < 0.8
    assert "validations" in result


@pytest.mark.asyncio
async def test_analyze_missing_sources(evidence_validator):
    """Test analysis when sources are missing."""
    no_source_responses = {
        "model_1": ResearchResponse(
            answer="Water boils at 100 degrees Celsius.",
            key_points=["Boiling point 100°C"],
            sources=[],  # No sources
            confidence=0.9,
            reasoning_trace="Common knowledge"
        )
    }

    query = "At what temperature does water boil?"
    synthesized_answer = "Water boils at 100°C at sea level."

    result = await evidence_validator.analyze(
        query=query,
        council_responses=no_source_responses,
        synthesized_answer=synthesized_answer
    )

    # Should handle missing sources gracefully
    assert "validations" in result
    assert isinstance(result["overall_source_quality"], float)


@pytest.mark.asyncio
async def test_format_metadata(evidence_validator):
    """Test metadata formatting."""
    metadata = evidence_validator._format_metadata()

    assert "role" in metadata
    assert "model" in metadata
    assert metadata["role"] == "evidence_validator"
    assert metadata["model"] == "gpt-4o"


@pytest.mark.asyncio
async def test_extract_claims_and_sources(evidence_validator, sample_council_responses):
    """Test extraction of claims and sources."""
    synthesized_answer = "Earth takes 365.25 days to orbit the Sun."

    claims = evidence_validator._extract_claims_and_sources(
        sample_council_responses,
        synthesized_answer
    )

    assert isinstance(claims, list)
    assert len(claims) > 0

    # Check claim structure
    for claim in claims:
        assert "claim" in claim
        assert "origin" in claim


@pytest.mark.asyncio
async def test_error_handling(evidence_validator):
    """Test error handling with invalid API key."""
    # Create validator with invalid key
    invalid_validator = EvidenceValidator(api_key="invalid_key_12345")

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

    result = await invalid_validator.analyze(
        query=query,
        council_responses=responses,
        synthesized_answer=synthesized_answer
    )

    # Should return error state
    assert "error" in result
    assert result["overall_source_quality"] == 0.0
    assert result["citation_hallucinations_detected"] is True


@pytest.mark.asyncio
async def test_high_quality_academic_sources(evidence_validator):
    """Test recognition of high-quality academic sources."""
    academic_responses = {
        "model": ResearchResponse(
            answer="According to peer-reviewed research in Nature (2023), climate change is accelerating.",
            key_points=["Peer-reviewed", "Nature journal"],
            sources=["Nature Journal - Climate Research 2023"],
            confidence=0.95,
            reasoning_trace="Published in top-tier journal"
        )
    }

    query = "What does recent research say about climate change?"
    synthesized_answer = "Climate change is accelerating according to Nature (2023)."

    result = await evidence_validator.analyze(
        query=query,
        council_responses=academic_responses,
        synthesized_answer=synthesized_answer
    )

    # High-quality sources should score well
    assert result["overall_source_quality"] >= 0.5
    assert result["citation_hallucinations_detected"] is False


@pytest.mark.asyncio
async def test_parse_validation_json_format(evidence_validator):
    """Test parsing of validation results in JSON format."""
    json_text = """```json
    {
        "validations": [
            {
                "claim_id": "c1",
                "claim_text": "Test claim",
                "evidence_status": "verified",
                "issues": [],
                "source_quality_score": 0.85
            }
        ],
        "overall_source_quality": 0.85,
        "citation_hallucinations_detected": false,
        "critical_issues": []
    }
    ```"""

    result = evidence_validator._parse_validation(json_text)

    assert "validations" in result
    assert "overall_source_quality" in result
    assert result["overall_source_quality"] == 0.85
    assert result["citation_hallucinations_detected"] is False


@pytest.mark.asyncio
async def test_parse_validation_fallback(evidence_validator):
    """Test fallback parsing for non-JSON text."""
    non_json_text = "This is not valid JSON text"

    result = evidence_validator._parse_validation(non_json_text)

    # Should return fallback structure
    assert "validations" in result
    assert "overall_source_quality" in result
    assert result["overall_source_quality"] == 0.5
    assert "critical_issues" in result
    assert "Failed to parse validation results" in result["critical_issues"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
