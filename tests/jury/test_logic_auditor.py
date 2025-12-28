"""
Unit tests for Logic Auditor jury specialist.

Tests:
- Contradiction detection
- Consistency checking
- Reasoning gap identification
- Error handling
"""

import pytest
import os
from unittest.mock import AsyncMock, patch
from src.jury.logic_auditor import LogicAuditor
from src.models.schemas import ResearchResponse


@pytest.fixture
def google_api_key():
    """Get Google API key from environment."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")
    return api_key


@pytest.fixture
def logic_auditor(google_api_key):
    """Create LogicAuditor instance."""
    return LogicAuditor(api_key=google_api_key)


@pytest.fixture
def consistent_responses():
    """Sample consistent council responses."""
    return {
        "gpt-4o": ResearchResponse(
            answer="Python is a high-level programming language. It uses dynamic typing.",
            key_points=["High-level language", "Dynamic typing"],
            sources=["Python Documentation"],
            confidence=0.95,
            reasoning_trace="Well-documented language features"
        ),
        "gemini-2.5-flash": ResearchResponse(
            answer="Python is dynamically typed and high-level, making it easy to learn.",
            key_points=["Dynamic typing", "Easy to learn"],
            sources=["Python.org"],
            confidence=0.92,
            reasoning_trace="Official documentation"
        )
    }


@pytest.fixture
def contradictory_responses():
    """Sample contradictory council responses."""
    return {
        "model_1": ResearchResponse(
            answer="The experiment showed positive results with 95% confidence.",
            key_points=["Positive results", "95% confidence"],
            sources=["Study A"],
            confidence=0.9,
            reasoning_trace="Clear statistical significance"
        ),
        "model_2": ResearchResponse(
            answer="The same experiment failed to show any significant effect (p > 0.05).",
            key_points=["No significant effect", "p > 0.05"],
            sources=["Study B"],
            confidence=0.85,
            reasoning_trace="No statistical significance"
        )
    }


@pytest.mark.asyncio
async def test_logic_auditor_initialization(google_api_key):
    """Test Logic Auditor can be initialized."""
    auditor = LogicAuditor(api_key=google_api_key)

    assert auditor is not None
    assert auditor.model_name == "gemini-2.5-flash"
    assert auditor.role.value == "logic_auditor"
    assert auditor.model is not None


@pytest.mark.asyncio
async def test_analyze_consistent_logic(logic_auditor, consistent_responses):
    """Test analysis of logically consistent responses."""
    query = "What are the key features of Python?"
    synthesized_answer = "Python is a high-level, dynamically-typed programming language."

    result = await logic_auditor.analyze(
        query=query,
        council_responses=consistent_responses,
        synthesized_answer=synthesized_answer
    )

    # Check result structure
    assert "contradictions" in result
    assert "reasoning_gaps" in result
    assert "consistency_score" in result
    assert "role" in result
    assert result["role"] == "logic_auditor"

    # Consistent responses should have high consistency score
    assert isinstance(result["consistency_score"], float)
    assert 0.0 <= result["consistency_score"] <= 1.0
    assert result["consistency_score"] >= 0.5


@pytest.mark.asyncio
async def test_analyze_contradictions(logic_auditor, contradictory_responses):
    """Test detection of contradictions."""
    query = "What were the results of the experiment?"
    synthesized_answer = "The experiment showed mixed results."

    result = await logic_auditor.analyze(
        query=query,
        council_responses=contradictory_responses,
        synthesized_answer=synthesized_answer
    )

    # Should detect contradictions
    assert "contradictions" in result
    assert isinstance(result["contradictions"], list)

    # Consistency score should be lower for contradictory responses
    assert result["consistency_score"] < 1.0


@pytest.mark.asyncio
async def test_compile_statements(logic_auditor, consistent_responses):
    """Test statement compilation from responses."""
    synthesized_answer = "Python is a high-level language."

    statements = logic_auditor._compile_statements(
        consistent_responses,
        synthesized_answer
    )

    assert isinstance(statements, list)
    assert len(statements) > 0
    assert len(statements) <= 15  # Should limit to 15 statements


@pytest.mark.asyncio
async def test_build_audit_prompt(logic_auditor):
    """Test audit prompt construction."""
    query = "Test query"
    statements = ["Statement 1", "Statement 2", "Statement 3"]

    prompt = logic_auditor._build_audit_prompt(query, statements)

    assert isinstance(prompt, str)
    assert "Research Question" in prompt
    assert "Test query" in prompt
    assert "Statement 1" in prompt
    assert "Statements to Audit" in prompt


@pytest.mark.asyncio
async def test_format_metadata(logic_auditor):
    """Test metadata formatting."""
    metadata = logic_auditor._format_metadata()

    assert "role" in metadata
    assert "model" in metadata
    assert metadata["role"] == "logic_auditor"
    assert metadata["model"] == "gemini-2.5-flash"


@pytest.mark.asyncio
async def test_parse_audit_json_format(logic_auditor):
    """Test parsing of audit results in JSON format."""
    json_text = """```json
    {
        "contradictions": [
            {
                "claim_ids": ["c1", "c3"],
                "conflict": "Claims are mutually exclusive",
                "severity": "major"
            }
        ],
        "reasoning_gaps": ["Missing link between premise and conclusion"],
        "circular_reasoning_detected": false,
        "consistency_score": 0.65,
        "critical_issues": []
    }
    ```"""

    result = logic_auditor._parse_audit(json_text)

    assert "contradictions" in result
    assert "consistency_score" in result
    assert result["consistency_score"] == 0.65
    assert len(result["contradictions"]) == 1
    assert result["contradictions"][0]["severity"] == "major"


@pytest.mark.asyncio
async def test_parse_audit_fallback(logic_auditor):
    """Test fallback parsing for non-JSON text."""
    non_json_text = "This is not valid JSON"

    result = logic_auditor._parse_audit(non_json_text)

    # Should return fallback structure
    assert "contradictions" in result
    assert "reasoning_gaps" in result
    assert "consistency_score" in result
    assert result["consistency_score"] == 0.7
    assert "critical_issues" in result
    assert "Failed to parse audit results" in result["critical_issues"]


@pytest.mark.asyncio
async def test_error_handling(logic_auditor):
    """Test error handling with API errors."""
    # Create auditor with invalid key
    invalid_auditor = LogicAuditor(api_key="invalid_key_12345")

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

    result = await invalid_auditor.analyze(
        query=query,
        council_responses=responses,
        synthesized_answer=synthesized_answer
    )

    # Should return error state
    assert "error" in result
    assert result["consistency_score"] == 0.5
    assert "contradictions" in result
    assert "reasoning_gaps" in result


@pytest.mark.asyncio
async def test_circular_reasoning_detection(logic_auditor):
    """Test detection of circular reasoning."""
    circular_responses = {
        "model": ResearchResponse(
            answer="A is true because B is true. B is true because A is true.",
            key_points=["A implies B", "B implies A"],
            sources=["Circular Source"],
            confidence=0.4,
            reasoning_trace="Circular dependency"
        )
    }

    query = "What is the relationship between A and B?"
    synthesized_answer = "A and B are mutually dependent."

    result = await logic_auditor.analyze(
        query=query,
        council_responses=circular_responses,
        synthesized_answer=synthesized_answer
    )

    # Should analyze circular reasoning
    assert "circular_reasoning_detected" in result or "contradictions" in result
    assert isinstance(result["consistency_score"], float)


@pytest.mark.asyncio
async def test_severity_classification(logic_auditor, contradictory_responses):
    """Test that contradictions are classified by severity."""
    query = "Test query with contradictions"
    synthesized_answer = "Synthesized answer"

    result = await logic_auditor.analyze(
        query=query,
        council_responses=contradictory_responses,
        synthesized_answer=synthesized_answer
    )

    # Check for contradiction severity if contradictions found
    if result.get("contradictions"):
        for contradiction in result["contradictions"]:
            if isinstance(contradiction, dict) and "severity" in contradiction:
                assert contradiction["severity"] in ["critical", "major", "minor"]


@pytest.mark.asyncio
async def test_empty_responses(logic_auditor):
    """Test handling of empty responses."""
    empty_responses = {}
    query = "Test query"
    synthesized_answer = "Test answer"

    result = await logic_auditor.analyze(
        query=query,
        council_responses=empty_responses,
        synthesized_answer=synthesized_answer
    )

    # Should handle gracefully
    assert "consistency_score" in result
    assert isinstance(result["consistency_score"], float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
