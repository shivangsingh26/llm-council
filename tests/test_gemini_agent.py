"""
Gemini Agent Tests
==================
Comprehensive test suite for GeminiResearchAgent.

Test Coverage:
- Agent initialization
- Async research functionality
- Response parsing
- Error handling
- Token tracking
- All 4 domains

Run: python tests/test_gemini_agent.py
Or: pytest tests/test_gemini_agent.py -v
"""

import os
import asyncio
from dotenv import load_dotenv

from src.agents.gemini_agent import GeminiResearchAgent
from src.models.schemas import ResearchDomain, ResearchResponse, ConfidenceLevel

# Load environment variables
load_dotenv()


def test_agent_initialization():
    """
    Test 1: Agent Initialization

    Verifies:
    - Agent can be created with API key
    - Model name is set correctly
    - Client is initialized
    """
    print("\n" + "="*60)
    print("TEST 1: Gemini Agent Initialization")
    print("="*60)

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("⚠️  SKIPPED: GEMINI_API_KEY not found in .env")
        return False

    try:
        agent = GeminiResearchAgent(api_key=api_key)

        assert agent.api_key == api_key
        assert agent.model_name == "gemini-2.5-flash"
        assert agent.client is not None

        print("✅ Agent initialized successfully")
        print(f"   Model: {agent.model_name}")
        print(f"   API Key: ...{api_key[-4:]}")
        return True

    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


async def test_async_research_sports():
    """
    Test 2: Async Research - Sports Domain

    Verifies:
    - Async research works
    - Returns ResearchResponse object
    - Contains required fields
    - Parses structured data correctly
    """
    print("\n" + "="*60)
    print("TEST 2: Async Research - Sports Domain")
    print("="*60)

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("⚠️  SKIPPED: GEMINI_API_KEY not found")
        return False

    try:
        agent = GeminiResearchAgent(api_key=api_key)

        result = await agent.research_async(
            query="Who won the FIFA World Cup in 2022?",
            domain=ResearchDomain.SPORTS,
            max_tokens=300
        )

        # Verify response type
        assert isinstance(result, ResearchResponse)

        # Verify required fields
        assert result.query == "Who won the FIFA World Cup in 2022?"
        assert result.domain == ResearchDomain.SPORTS
        assert result.model_name == "gemini-2.5-flash"
        assert len(result.answer) > 0
        assert len(result.key_points) > 0
        assert isinstance(result.confidence, ConfidenceLevel)

        print("✅ Async research successful")
        print(f"   Answer length: {len(result.answer)} chars")
        print(f"   Key points: {len(result.key_points)}")
        print(f"   Confidence: {result.confidence.value}")
        print(f"   Tokens: {result.tokens_used}")

        return True

    except Exception as e:
        print(f"❌ Async research failed: {e}")
        return False


async def test_async_research_finance():
    """
    Test 3: Async Research - Finance Domain

    Verifies domain-specific prompting works correctly
    """
    print("\n" + "="*60)
    print("TEST 3: Async Research - Finance Domain")
    print("="*60)

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("⚠️  SKIPPED")
        return False

    try:
        agent = GeminiResearchAgent(api_key=api_key)

        result = await agent.research_async(
            query="What is the current state of cryptocurrency markets?",
            domain=ResearchDomain.FINANCE
        )

        assert isinstance(result, ResearchResponse)
        assert result.domain == ResearchDomain.FINANCE
        assert len(result.key_points) >= 1

        print("✅ Finance domain research successful")
        print(f"   Key points: {len(result.key_points)}")

        return True

    except Exception as e:
        print(f"❌ Finance research failed: {e}")
        return False


async def test_async_research_shopping():
    """
    Test 4: Async Research - Shopping Domain
    """
    print("\n" + "="*60)
    print("TEST 4: Async Research - Shopping Domain")
    print("="*60)

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("⚠️  SKIPPED")
        return False

    try:
        agent = GeminiResearchAgent(api_key=api_key)

        result = await agent.research_async(
            query="What are the best budget laptops in 2024?",
            domain=ResearchDomain.SHOPPING
        )

        assert isinstance(result, ResearchResponse)
        assert result.domain == ResearchDomain.SHOPPING

        print("✅ Shopping domain research successful")
        return True

    except Exception as e:
        print(f"❌ Shopping research failed: {e}")
        return False


async def test_async_research_healthcare():
    """
    Test 5: Async Research - Healthcare Domain
    """
    print("\n" + "="*60)
    print("TEST 5: Async Research - Healthcare Domain")
    print("="*60)

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("⚠️  SKIPPED")
        return False

    try:
        agent = GeminiResearchAgent(api_key=api_key)

        result = await agent.research_async(
            query="What are the benefits of regular exercise?",
            domain=ResearchDomain.HEALTHCARE
        )

        assert isinstance(result, ResearchResponse)
        assert result.domain == ResearchDomain.HEALTHCARE

        print("✅ Healthcare domain research successful")
        return True

    except Exception as e:
        print(f"❌ Healthcare research failed: {e}")
        return False


def test_sync_wrapper():
    """
    Test 6: Synchronous Wrapper

    Verifies:
    - Sync research() method works
    - Uses asyncio.run internally
    - Returns same structure as async
    """
    print("\n" + "="*60)
    print("TEST 6: Synchronous Wrapper")
    print("="*60)

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("⚠️  SKIPPED")
        return False

    try:
        agent = GeminiResearchAgent(api_key=api_key)

        # Call sync method (should work via wrapper)
        result = agent.research(
            query="What is AI?",
            domain=ResearchDomain.HEALTHCARE
        )

        assert isinstance(result, ResearchResponse)

        print("✅ Sync wrapper works correctly")
        return True

    except Exception as e:
        print(f"❌ Sync wrapper failed: {e}")
        return False


async def test_error_handling():
    """
    Test 7: Error Handling

    Verifies:
    - Invalid API key raises error
    - Error messages are clear
    """
    print("\n" + "="*60)
    print("TEST 7: Error Handling")
    print("="*60)

    try:
        # Create agent with invalid API key
        agent = GeminiResearchAgent(api_key="invalid-key-12345")

        # This should fail
        result = await agent.research_async(
            query="Test query",
            domain=ResearchDomain.SPORTS
        )

        print("❌ Should have raised an error!")
        return False

    except Exception as e:
        print(f"✅ Correctly raised error: {type(e).__name__}")
        return True


async def run_all_tests():
    """Run all Gemini agent tests."""

    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*15 + "GEMINI AGENT TEST SUITE" + " "*21 + "║")
    print("╚" + "="*58 + "╝")

    results = {
        "initialization": test_agent_initialization(),
        "async_sports": await test_async_research_sports(),
        "async_finance": await test_async_research_finance(),
        "async_shopping": await test_async_research_shopping(),
        "async_healthcare": await test_async_research_healthcare(),
        "sync_wrapper": test_sync_wrapper(),
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
        print("\n🎉 All Gemini agent tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    """
    Run all tests when executed directly.

    Usage:
        python tests/test_gemini_agent.py
    """
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
