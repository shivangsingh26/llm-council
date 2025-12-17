"""
Unit Tests for Master Synthesizer
==================================
Tests the MasterSynthesizer class using o1-mini for deep reasoning.

Run:
    pytest tests/test_master_synthesizer.py -v
    pytest tests/test_master_synthesizer.py -v -s  # With output
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import os

from src.council.master_synthesizer import MasterSynthesizer
from src.models.schemas import (
    ResearchResponse,
    ResearchDomain,
    ConfidenceLevel,
    ComparisonResult
)


# Sample mock responses for testing
@pytest.fixture
def mock_responses():
    """Create mock research responses from different agents."""
    return {
        "gpt-4o": ResearchResponse(
            query="What are the benefits of exercise?",
            answer="Regular exercise improves cardiovascular health, boosts mood, and enhances overall fitness.",
            domain=ResearchDomain.HEALTHCARE,
            confidence=ConfidenceLevel.HIGH,
            key_points=[
                "Improves cardiovascular health",
                "Boosts mood and mental health",
                "Enhances physical fitness"
            ],
            model_name="gpt-4o",
            timestamp=datetime.now(),
            tokens_used=500
        ),
        "gemini-2.5-flash": ResearchResponse(
            query="What are the benefits of exercise?",
            answer="Exercise has numerous benefits including better heart health, improved mood, weight management, and increased energy levels.",
            domain=ResearchDomain.HEALTHCARE,
            confidence=ConfidenceLevel.VERY_HIGH,
            key_points=[
                "Better heart health",
                "Improved mood",
                "Weight management",
                "Increased energy"
            ],
            model_name="gemini-2.5-flash",
            timestamp=datetime.now(),
            tokens_used=450
        )
    }


class TestMasterSynthesizerInitialization:
    """Test synthesizer initialization."""

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        synthesizer = MasterSynthesizer(api_key="test-key")
        assert synthesizer.api_key == "test-key"
        assert synthesizer.model == "o1-mini"

    def test_init_with_env_var(self, monkeypatch):
        """Test initialization with environment variable."""
        monkeypatch.setenv("OPENAI_API_KEY", "env-key")
        synthesizer = MasterSynthesizer()
        assert synthesizer.api_key == "env-key"

    def test_init_without_api_key(self, monkeypatch):
        """Test initialization fails without API key."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(ValueError, match="OpenAI API key required"):
            MasterSynthesizer()

    def test_init_with_different_model(self):
        """Test initialization with different reasoning model."""
        synthesizer = MasterSynthesizer(api_key="test-key", model="o1")
        assert synthesizer.model == "o1"


class TestPromptBuilding:
    """Test prompt construction for reasoning model."""

    def test_build_synthesis_prompt_basic(self, mock_responses):
        """Test basic prompt building."""
        synthesizer = MasterSynthesizer(api_key="test-key")
        prompt = synthesizer._build_synthesis_prompt(
            query="What are the benefits of exercise?",
            responses=mock_responses,
            context=None
        )

        # Check prompt contains key elements
        assert "What are the benefits of exercise?" in prompt
        assert "gpt-4o" in prompt
        assert "gemini-2.5-flash" in prompt
        assert "Improves cardiovascular health" in prompt
        assert "JSON" in prompt
        assert "consensus_points" in prompt

    def test_build_synthesis_prompt_with_context(self, mock_responses):
        """Test prompt building with context."""
        synthesizer = MasterSynthesizer(api_key="test-key")
        context = {
            "tools_used": {"web_search": "Found 5 articles"},
            "research_plan": "Focus on health benefits"
        }
        prompt = synthesizer._build_synthesis_prompt(
            query="Test query",
            responses=mock_responses,
            context=context
        )

        assert "Tools Used" in prompt
        assert "web_search" in prompt
        assert "Research Plan" in prompt


class TestResponseParsing:
    """Test parsing of reasoning model outputs."""

    def test_parse_valid_json(self):
        """Test parsing valid JSON output."""
        synthesizer = MasterSynthesizer(api_key="test-key")

        json_output = """```json
{
  "consensus_points": ["Point 1", "Point 2"],
  "disagreement_points": ["Disagreement 1"],
  "knowledge_gaps": ["Gap 1"],
  "synthesized_answer": "Test answer",
  "confidence_range": "high",
  "confidence_reasoning": "Because reasons",
  "verification_needed": ["Claim 1"],
  "reasoning_trace": "My reasoning"
}
```"""

        parsed = synthesizer._parse_synthesis(json_output)

        assert len(parsed["consensus_points"]) == 2
        assert parsed["consensus_points"][0] == "Point 1"
        assert parsed["synthesized_answer"] == "Test answer"
        assert parsed["confidence_range"] == "high"

    def test_parse_direct_json(self):
        """Test parsing JSON without code blocks."""
        synthesizer = MasterSynthesizer(api_key="test-key")

        json_output = """{
  "consensus_points": ["Point 1"],
  "disagreement_points": [],
  "knowledge_gaps": [],
  "synthesized_answer": "Answer",
  "confidence_range": "medium",
  "confidence_reasoning": "",
  "verification_needed": [],
  "reasoning_trace": ""
}"""

        parsed = synthesizer._parse_synthesis(json_output)
        assert parsed["consensus_points"] == ["Point 1"]

    def test_parse_natural_language_fallback(self):
        """Test fallback to natural language parsing."""
        synthesizer = MasterSynthesizer(api_key="test-key")

        natural_output = "This is just natural language text without JSON."

        parsed = synthesizer._parse_synthesis(natural_output)

        # Should use natural language fallback
        assert "synthesized_answer" in parsed
        assert parsed["confidence_range"] == "medium"
        assert len(parsed["synthesized_answer"]) > 0


class TestValidation:
    """Test output validation."""

    def test_validate_complete_output(self):
        """Test validation with complete output."""
        synthesizer = MasterSynthesizer(api_key="test-key")

        complete_output = {
            "consensus_points": ["Point"],
            "disagreement_points": [],
            "knowledge_gaps": [],
            "synthesized_answer": "Answer",
            "confidence_range": "high",
            "confidence_reasoning": "Reasoning",
            "verification_needed": [],
            "reasoning_trace": "Trace"
        }

        validated = synthesizer._validate_parsed_output(complete_output)
        assert validated == complete_output

    def test_validate_incomplete_output(self):
        """Test validation fills in missing fields."""
        synthesizer = MasterSynthesizer(api_key="test-key")

        incomplete_output = {
            "synthesized_answer": "Answer"
        }

        validated = synthesizer._validate_parsed_output(incomplete_output)

        # Should have all required fields
        assert "consensus_points" in validated
        assert "disagreement_points" in validated
        assert "knowledge_gaps" in validated
        assert validated["consensus_points"] == []


class TestTokenAndCostCalculation:
    """Test token and cost calculations."""

    def test_calculate_total_tokens(self, mock_responses):
        """Test total token calculation."""
        synthesizer = MasterSynthesizer(api_key="test-key")

        # Mock synthesis response
        mock_synthesis = Mock()
        mock_synthesis.usage = Mock()
        mock_synthesis.usage.total_tokens = 1000

        total = synthesizer._calculate_total_tokens(mock_responses, mock_synthesis)

        # Should include worker tokens (500 + 450) + synthesis tokens (1000)
        assert total == 1950

    def test_calculate_total_cost(self, mock_responses):
        """Test total cost calculation."""
        synthesizer = MasterSynthesizer(api_key="test-key", model="o1-mini")

        # Mock synthesis response
        mock_synthesis = Mock()
        mock_synthesis.usage = Mock()
        mock_synthesis.usage.prompt_tokens = 1000
        mock_synthesis.usage.completion_tokens = 500

        cost = synthesizer._calculate_total_cost(mock_responses, mock_synthesis)

        # Should calculate based on pricing
        # o1-mini: $3/$12 per 1M tokens
        # Input: 1000 tokens = $0.003
        # Output: 500 tokens = $0.006
        # Total synthesis: $0.009
        # Plus worker costs
        assert cost > 0


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY environment variable"
)
class TestRealSynthesis:
    """Integration tests with real OpenAI API (requires API key)."""

    async def test_real_synthesis(self, mock_responses):
        """Test real synthesis with o1-mini (skipped without API key)."""
        synthesizer = MasterSynthesizer(model="o1-mini")

        result = await synthesizer.synthesize(
            query="What are the benefits of exercise?",
            responses=mock_responses,
            domain=ResearchDomain.HEALTHCARE
        )

        # Check result structure
        assert isinstance(result, ComparisonResult)
        assert result.query == "What are the benefits of exercise?"
        assert result.successful_agents == 2
        assert len(result.synthesized_answer) > 0
        assert result.total_tokens > 0
        assert result.total_cost > 0

        # Check new fields
        assert isinstance(result.consensus_points, list)
        assert isinstance(result.disagreement_points, list)
        assert result.confidence_range in ["low", "medium", "high", "very_high", "medium to high", "high to very_high"]

        print(f"\n✅ Real synthesis test passed!")
        print(f"   Consensus points: {len(result.consensus_points)}")
        print(f"   Synthesized answer: {result.synthesized_answer[:100]}...")
        print(f"   Tokens: {result.total_tokens}")
        print(f"   Cost: ${result.total_cost:.6f}")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
