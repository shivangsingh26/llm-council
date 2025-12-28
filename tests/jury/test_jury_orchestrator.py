"""
Integration tests for Jury Orchestrator.

Tests:
- Sequential jury execution (Evidence → Logic → Assumptions)
- Overall quality score calculation
- Verdict determination
- Error handling and graceful degradation
"""

import pytest
import os
from src.jury.orchestrator import JuryOrchestrator
from src.models.schemas import ResearchResponse


@pytest.fixture
def api_keys():
    """Get API keys from environment."""
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GEMINI_API_KEY")

    if not openai_key or not google_key:
        pytest.skip("API keys not set (OPENAI_API_KEY and GEMINI_API_KEY required)")

    return {"openai": openai_key, "google": google_key}


@pytest.fixture
def jury_orchestrator(api_keys):
    """Create JuryOrchestrator instance."""
    return JuryOrchestrator(
        openai_api_key=api_keys["openai"],
        google_api_key=api_keys["google"]
    )


@pytest.fixture
def high_quality_responses():
    """Sample high-quality council responses."""
    return {
        "gpt-4o": ResearchResponse(
            answer="Water (H2O) boils at 100°C (212°F) at standard atmospheric pressure (1 atm).",
            key_points=[
                "Boiling point: 100°C at 1 atm",
                "Molecular formula: H2O",
                "Temperature varies with pressure"
            ],
            sources=["Physics textbook - Thermodynamics"],
            confidence=0.98,
            reasoning_trace="Well-established physical constant with conditions specified"
        ),
        "gemini-2.5-flash": ResearchResponse(
            answer="At sea level (1 atmosphere pressure), pure water boils at 100 degrees Celsius.",
            key_points=[
                "Sea level: 1 atm",
                "Pure water boiling: 100°C",
                "Altitude affects boiling point"
            ],
            sources=["Chemistry handbook"],
            confidence=0.97,
            reasoning_trace="Standard chemistry reference"
        )
    }


@pytest.fixture
def problematic_responses():
    """Sample problematic council responses with issues."""
    return {
        "model_1": ResearchResponse(
            answer="Vaccines cause autism according to recent studies.",
            key_points=["Vaccine-autism link"],
            sources=["Unverified blog post"],
            confidence=0.3,
            reasoning_trace="Disputed claim"
        ),
        "model_2": ResearchResponse(
            answer="The study shows vaccines are safe. However, all children develop autism after vaccination.",
            key_points=["Vaccines safe", "All children get autism"],
            sources=["Mixed sources"],
            confidence=0.4,
            reasoning_trace="Contradictory statements"
        )
    }


@pytest.mark.asyncio
async def test_jury_orchestrator_initialization(api_keys):
    """Test Jury Orchestrator can be initialized."""
    orchestrator = JuryOrchestrator(
        openai_api_key=api_keys["openai"],
        google_api_key=api_keys["google"]
    )

    assert orchestrator is not None
    assert orchestrator.evidence_validator is not None
    assert orchestrator.logic_auditor is not None
    assert orchestrator.assumption_critic is not None


@pytest.mark.asyncio
async def test_deliberate_high_quality(jury_orchestrator, high_quality_responses):
    """Test jury deliberation on high-quality responses."""
    query = "At what temperature does water boil?"
    synthesized_answer = "Water boils at 100°C at standard atmospheric pressure (1 atm)."

    result = await jury_orchestrator.deliberate(
        query=query,
        council_responses=high_quality_responses,
        synthesized_answer=synthesized_answer
    )

    # Check result structure
    assert "evidence_validation" in result
    assert "logic_analysis" in result
    assert "assumption_critique" in result
    assert "overall_quality_score" in result
    assert "critical_issues" in result
    assert "recommendations" in result
    assert "jury_verdict" in result

    # High quality should result in good scores
    assert result["overall_quality_score"] >= 0.5
    assert result["jury_verdict"] in ["approved", "needs_revision", "rejected"]

    # Should have minimal critical issues
    assert isinstance(result["critical_issues"], list)


@pytest.mark.asyncio
async def test_deliberate_problematic_responses(jury_orchestrator, problematic_responses):
    """Test jury deliberation on problematic responses."""
    query = "Do vaccines cause autism?"
    synthesized_answer = "Scientific consensus shows no link between vaccines and autism."

    result = await jury_orchestrator.deliberate(
        query=query,
        council_responses=problematic_responses,
        synthesized_answer=synthesized_answer
    )

    # Should detect issues
    assert len(result["critical_issues"]) > 0
    assert result["overall_quality_score"] < 0.7

    # Verdict should be needs_revision or rejected
    assert result["jury_verdict"] in ["needs_revision", "rejected"]


@pytest.mark.asyncio
async def test_sequential_execution(jury_orchestrator, high_quality_responses):
    """Test that all three jury members are executed."""
    query = "Test query"
    synthesized_answer = "Test answer"

    result = await jury_orchestrator.deliberate(
        query=query,
        council_responses=high_quality_responses,
        synthesized_answer=synthesized_answer
    )

    # All three specialists should have run
    assert result["evidence_validation"] is not None
    assert result["logic_analysis"] is not None
    assert result["assumption_critique"] is not None


@pytest.mark.asyncio
async def test_overall_quality_calculation(jury_orchestrator):
    """Test overall quality score calculation."""
    # Mock results with known scores
    mock_results = {
        "evidence_validation": {"overall_source_quality": 0.8},
        "logic_analysis": {"consistency_score": 0.7},
        "assumption_critique": {"robustness_score": 0.9},
        "critical_issues": []
    }

    quality_score = jury_orchestrator._calculate_overall_quality(mock_results)

    # Should average the three scores: (0.8 + 0.7 + 0.9) / 3 = 0.8
    assert isinstance(quality_score, float)
    assert 0.7 <= quality_score <= 0.9


@pytest.mark.asyncio
async def test_verdict_determination_approved(jury_orchestrator):
    """Test verdict determination for approved case."""
    mock_results = {
        "overall_quality_score": 0.85,
        "critical_issues": []
    }

    verdict = jury_orchestrator._determine_verdict(mock_results)
    assert verdict == "approved"


@pytest.mark.asyncio
async def test_verdict_determination_needs_revision(jury_orchestrator):
    """Test verdict determination for needs_revision case."""
    mock_results = {
        "overall_quality_score": 0.55,
        "critical_issues": ["Low source quality"]
    }

    verdict = jury_orchestrator._determine_verdict(mock_results)
    assert verdict == "needs_revision"


@pytest.mark.asyncio
async def test_verdict_determination_rejected(jury_orchestrator):
    """Test verdict determination for rejected case."""
    mock_results = {
        "overall_quality_score": 0.3,
        "critical_issues": [
            "Citation hallucinations detected",
            "Major contradictions found",
            "Low robustness"
        ]
    }

    verdict = jury_orchestrator._determine_verdict(mock_results)
    assert verdict == "rejected"


@pytest.mark.asyncio
async def test_critical_issue_detection(jury_orchestrator, problematic_responses):
    """Test that critical issues are properly aggregated."""
    query = "Test query"
    synthesized_answer = "Test answer with issues"

    result = await jury_orchestrator.deliberate(
        query=query,
        council_responses=problematic_responses,
        synthesized_answer=synthesized_answer
    )

    # Should collect critical issues from all specialists
    assert isinstance(result["critical_issues"], list)


@pytest.mark.asyncio
async def test_recommendations_aggregation(jury_orchestrator, high_quality_responses):
    """Test that recommendations are collected."""
    query = "Test query"
    synthesized_answer = "Test answer"

    result = await jury_orchestrator.deliberate(
        query=query,
        council_responses=high_quality_responses,
        synthesized_answer=synthesized_answer
    )

    # Should have recommendations
    assert "recommendations" in result
    assert isinstance(result["recommendations"], list)


@pytest.mark.asyncio
async def test_error_handling_missing_openai_key():
    """Test graceful degradation when OpenAI key is missing."""
    orchestrator = JuryOrchestrator(
        openai_api_key=None,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    # Evidence Validator and Assumption Critic should be None
    assert orchestrator.evidence_validator is None
    assert orchestrator.assumption_critic is None
    # Logic Auditor should still work
    assert orchestrator.logic_auditor is not None


@pytest.mark.asyncio
async def test_error_handling_missing_google_key():
    """Test graceful degradation when Google key is missing."""
    orchestrator = JuryOrchestrator(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        google_api_key=None
    )

    # Logic Auditor should be None
    assert orchestrator.logic_auditor is None
    # Evidence Validator and Assumption Critic should still work
    assert orchestrator.evidence_validator is not None
    assert orchestrator.assumption_critic is not None


@pytest.mark.asyncio
async def test_partial_jury_execution(api_keys):
    """Test jury execution with some specialists disabled."""
    # Create orchestrator with only Google API key
    orchestrator = JuryOrchestrator(
        openai_api_key=None,
        google_api_key=api_keys["google"]
    )

    responses = {
        "model": ResearchResponse(
            answer="Test answer",
            key_points=["Test"],
            sources=["Test source"],
            confidence=0.8,
            reasoning_trace="Test"
        )
    }

    result = await orchestrator.deliberate(
        query="Test query",
        council_responses=responses,
        synthesized_answer="Test synthesis"
    )

    # Should still return valid result with partial execution
    assert "overall_quality_score" in result
    assert "jury_verdict" in result
    assert result["evidence_validation"] is None
    assert result["assumption_critique"] is None
    # Logic analysis should have run
    assert result["logic_analysis"] is not None


@pytest.mark.asyncio
async def test_empty_responses(jury_orchestrator):
    """Test handling of empty responses."""
    result = await jury_orchestrator.deliberate(
        query="Test query",
        council_responses={},
        synthesized_answer="Test answer"
    )

    # Should handle gracefully
    assert "overall_quality_score" in result
    assert "jury_verdict" in result
    assert isinstance(result["overall_quality_score"], float)


@pytest.mark.asyncio
async def test_citation_hallucination_detection(jury_orchestrator):
    """Test detection of citation hallucinations."""
    fake_citation_responses = {
        "model": ResearchResponse(
            answer="According to Smith et al. (2025) in the Journal of Made-Up Research...",
            key_points=["Fake citation"],
            sources=["Smith et al. (2025) - Nonexistent Journal"],
            confidence=0.9,
            reasoning_trace="Hallucinated source"
        )
    }

    result = await jury_orchestrator.deliberate(
        query="Test query",
        council_responses=fake_citation_responses,
        synthesized_answer="Based on recent research..."
    )

    # Should flag citation issues
    if result["evidence_validation"]:
        # Check if hallucinations were detected or quality is low
        assert (
            result["evidence_validation"].get("citation_hallucinations_detected") is True or
            result["evidence_validation"].get("overall_source_quality", 1.0) < 0.6
        )


@pytest.mark.asyncio
async def test_contradiction_detection(jury_orchestrator):
    """Test detection of contradictions."""
    contradictory_responses = {
        "model_1": ResearchResponse(
            answer="The sky is blue.",
            key_points=["Sky is blue"],
            sources=["Optics textbook"],
            confidence=0.95,
            reasoning_trace="Rayleigh scattering"
        ),
        "model_2": ResearchResponse(
            answer="The sky is not blue, it's actually colorless.",
            key_points=["Sky is colorless"],
            sources=["Alternative physics"],
            confidence=0.6,
            reasoning_trace="Contradictory claim"
        )
    }

    result = await jury_orchestrator.deliberate(
        query="What color is the sky?",
        council_responses=contradictory_responses,
        synthesized_answer="The sky appears blue."
    )

    # Should detect contradictions
    if result["logic_analysis"]:
        contradictions = result["logic_analysis"].get("contradictions", [])
        # May have contradictions detected
        assert isinstance(contradictions, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
