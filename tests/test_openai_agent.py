"""
OpenAI Agent Tests (GPT-4o)
===========================
Comprehensive test suite for OpenAIAgent.

Test Coverage:
- Agent initialization with AsyncOpenAI
- Async research functionality
- Response parsing
- Token usage tracking
- Error handling
- All 4 domains

Run: python tests/test_openai_agent.py
"""

import os
import asyncio
from dotenv import load_dotenv

from src.agents.openai_agent import OpenAIAgent
from src.models.schemas import ResearchDomain, ResearchResponse, ConfidenceLevel

load_dotenv()


def test_agent_initialization():
    """Test 1: OpenAI Agent Initialization"""
    print("\n" + "="*60)
    print("TEST 1: OpenAI Agent Initialization")
    print("="*60)

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("⚠️  SKIPPED: OPENAI_API_KEY not found in .env")
        return False

    try:
        agent = OpenAIAgent(api_key=api_key)

        assert agent.api_key == api_key
        assert agent.model_name == "gpt-4o"
        assert agent.client is not None

        print("✅ Agent initialized successfully")
        print(f"   Model: {agent.model_name}")
        return True

    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


async def test_async_research_sports():
    """Test 2: Async Research - Sports Domain"""
    print("\n" + "="*60)
    print("TEST 2: Async Research - Sports Domain")
    print("="*60)

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("⚠️  SKIPPED")
        return False

    try:
        agent = OpenAIAgent(api_key=api_key)

        result = await agent.research_async(
            query="Who won the Super Bowl in 2024?",
            domain=ResearchDomain.SPORTS,
            max_tokens=300
        )

        # Verify response
        assert isinstance(result, ResearchResponse)
        assert result.domain == ResearchDomain.SPORTS
        assert result.model_name == "gpt-4o"
        assert len(result.answer) > 0
        assert len(result.key_points) > 0
        assert result.tokens_used is not None  # OpenAI always provides token count

        print("✅ Async research successful")
        print(f"   Answer length: {len(result.answer)} chars")
        print(f"   Key points: {len(result.key_points)}")
        print(f"   Tokens used: {result.tokens_used}")
        print(f"   Confidence: {result.confidence.value}")

        return True

    except Exception as e:
        print(f"❌ Research failed: {e}")
        return False


async def test_async_research_finance():
    """Test 3: Async Research - Finance Domain"""
    print("\n" + "="*60)
    print("TEST 3: Async Research - Finance Domain")
    print("="*60)

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("⚠️  SKIPPED")
        return False

    try:
        agent = OpenAIAgent(api_key=api_key)

        result = await agent.research_async(
            query="What are the current trends in stock market investing?",
            domain=ResearchDomain.FINANCE
        )

        assert isinstance(result, ResearchResponse)
        assert result.domain == ResearchDomain.FINANCE
        assert result.tokens_used > 0

        print("✅ Finance domain research successful")
        print(f"   Tokens: {result.tokens_used}")

        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_async_research_shopping():
    """Test 4: Async Research - Shopping Domain"""
    print("\n" + "="*60)
    print("TEST 4: Async Research - Shopping Domain")
    print("="*60)

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("⚠️  SKIPPED")
        return False

    try:
        agent = OpenAIAgent(api_key=api_key)

        result = await agent.research_async(
            query="What are the best wireless headphones under $200?",
            domain=ResearchDomain.SHOPPING
        )

        assert isinstance(result, ResearchResponse)
        assert result.domain == ResearchDomain.SHOPPING

        print("✅ Shopping domain research successful")
        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_async_research_healthcare():
    """Test 5: Async Research - Healthcare Domain"""
    print("\n" + "="*60)
    print("TEST 5: Async Research - Healthcare Domain")
    print("="*60)

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("⚠️  SKIPPED")
        return False

    try:
        agent = OpenAIAgent(api_key=api_key)

        result = await agent.research_async(
            query="What are the health benefits of meditation?",
            domain=ResearchDomain.HEALTHCARE
        )

        assert isinstance(result, ResearchResponse)
        assert result.domain == ResearchDomain.HEALTHCARE

        print("✅ Healthcare domain research successful")
        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_token_tracking():
    """Test 6: Token Usage Tracking"""
    print("\n" + "="*60)
    print("TEST 6: Token Usage Tracking")
    print("="*60)

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("⚠️  SKIPPED")
        return False

    try:
        agent = OpenAIAgent(api_key=api_key)

        result = await agent.research_async(
            query="Explain AI in one sentence",
            domain=ResearchDomain.HEALTHCARE,
            max_tokens=50  # Small limit
        )

        # OpenAI always provides token usage
        assert result.tokens_used is not None
        assert result.tokens_used > 0

        print("✅ Token tracking works")
        print(f"   Tokens used: {result.tokens_used}")

        # Estimate cost (GPT-4o pricing)
        input_cost = result.tokens_used * 0.0000025  # $2.50 per 1M tokens
        print(f"   Estimated cost: ${input_cost:.6f}")

        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_error_handling():
    """Test 7: Error Handling"""
    print("\n" + "="*60)
    print("TEST 7: Error Handling")
    print("="*60)

    try:
        agent = OpenAIAgent(api_key="sk-invalid-key-12345")

        result = await agent.research_async(
            query="Test",
            domain=ResearchDomain.SPORTS
        )

        print("❌ Should have raised an error!")
        return False

    except Exception as e:
        print(f"✅ Correctly raised error: {type(e).__name__}")
        return True


async def run_all_tests():
    """Run all OpenAI agent tests."""

    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*12 + "OPENAI AGENT (GPT-4o) TEST SUITE" + " "*14 + "║")
    print("╚" + "="*58 + "╝")

    results = {
        "initialization": test_agent_initialization(),
        "async_sports": await test_async_research_sports(),
        "async_finance": await test_async_research_finance(),
        "async_shopping": await test_async_research_shopping(),
        "async_healthcare": await test_async_research_healthcare(),
        "token_tracking": await test_token_tracking(),
        "error_handling": await test_error_handling()
    }

    # Summary
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*20 + "TEST SUMMARY" + " "*26 + "║")
    print("╚" + "="*58 + "╝")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:20} {status}")

    print(f"\n  Passed: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 All OpenAI agent tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
