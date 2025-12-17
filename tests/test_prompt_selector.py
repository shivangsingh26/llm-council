"""
Tests for dynamic prompt selector.
"""

from src.prompts.prompt_selector import PromptSelector, get_research_prompt
from src.models.schemas import ResearchDomain


def test_complexity_detection():
    """Test query complexity analysis."""
    selector = PromptSelector()

    # Simple queries
    assert selector.analyze_query_complexity("What is Apple stock price?") == "simple"
    assert selector.analyze_query_complexity("Current NBA score") == "simple"

    # Moderate queries
    assert selector.analyze_query_complexity(
        "Tell me about iPhone 15 features and specifications"
    ) == "moderate"

    # Complex queries
    assert selector.analyze_query_complexity(
        "Compare Apple and Microsoft stock performance and explain why"
    ) == "complex"
    assert selector.analyze_query_complexity(
        "Analyze the pros and cons of investing in Tesla"
    ) == "complex"


def test_domain_prompts():
    """Test domain-specific prompts are generated."""
    selector = PromptSelector()

    # Finance domain
    prompts = selector.get_prompt(
        query="What's the current price of Apple stock?",
        domain=ResearchDomain.FINANCE
    )

    assert "financial" in prompts["system"].lower()
    assert "disclaimer" in prompts["system"].lower()
    assert prompts["metadata"]["domain"] == "finance"
    assert prompts["metadata"]["complexity"] == "simple"

    # Healthcare domain
    prompts = selector.get_prompt(
        query="What are the side effects of aspirin?",
        domain=ResearchDomain.HEALTHCARE
    )

    assert "medical" in prompts["system"].lower()
    assert "disclaimer" in prompts["system"].lower()
    assert prompts["metadata"]["domain"] == "healthcare"


def test_tools_instruction():
    """Test tool usage instructions."""
    selector = PromptSelector()

    # Without tools
    prompts = selector.get_prompt(
        query="Test query",
        domain=ResearchDomain.FINANCE
    )
    assert "Tools Available" not in prompts["system"]

    # With tools
    prompts = selector.get_prompt(
        query="Test query",
        domain=ResearchDomain.FINANCE,
        available_tools=["web_search", "finance_api"]
    )
    assert "Tools Available" in prompts["system"]
    assert "Web search" in prompts["system"]
    assert "Stock prices" in prompts["system"]


def test_convenience_function():
    """Test the convenience function."""
    prompts = get_research_prompt(
        query="Compare Tesla and Ford stock",
        domain=ResearchDomain.FINANCE,
        available_tools=["finance_api"],
        max_tokens=500
    )

    assert "system" in prompts
    assert "user" in prompts
    assert "metadata" in prompts
    assert prompts["metadata"]["complexity"] == "complex"


def test_synthesis_prompt():
    """Test master synthesizer prompt generation."""
    selector = PromptSelector()

    agent_responses = {
        "gpt-4o": "Apple stock is currently at $180",
        "gemini": "AAPL trading at $180.50",
        "deepseek": "Apple shares are around $180"
    }

    synthesis_prompt = selector.get_synthesis_prompt(
        query="What's Apple stock price?",
        agent_responses=agent_responses,
        domain=ResearchDomain.FINANCE
    )

    assert "gpt-4o" in synthesis_prompt
    assert "gemini" in synthesis_prompt
    assert "deepseek" in synthesis_prompt
    assert "Consensus Analysis" in synthesis_prompt
    assert "Synthesized Answer" in synthesis_prompt


if __name__ == "__main__":
    # Run tests
    test_complexity_detection()
    print("✅ Complexity detection tests passed")

    test_domain_prompts()
    print("✅ Domain prompts tests passed")

    test_tools_instruction()
    print("✅ Tools instruction tests passed")

    test_convenience_function()
    print("✅ Convenience function tests passed")

    test_synthesis_prompt()
    print("✅ Synthesis prompt tests passed")

    print("\n🎉 All tests passed!")
