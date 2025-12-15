"""
DeepSeek Agent Tests (Ollama Local)
===================================
Comprehensive test suite for DeepSeekAgent running via Ollama.

Test Coverage:
- Ollama connectivity check
- Agent initialization (no API key needed!)
- Local model inference
- Async research functionality
- Response parsing
- Error handling
- All 4 domains

Prerequisites:
- Ollama must be running: `ollama serve`
- DeepSeek model must be pulled: `ollama pull deepseek-r1:14b`

Run: python tests/test_deepseek_agent.py

Note: Tests use local compute - FREE but slower than cloud APIs
"""

import os
import asyncio
from dotenv import load_dotenv

from src.agents.deepseek_agent import DeepSeekAgent
from src.models.schemas import ResearchDomain, ResearchResponse, ConfidenceLevel

load_dotenv()


async def test_ollama_connectivity():
    """
    Test 1: Ollama Connectivity Check

    Verifies Ollama is running and accessible
    """
    print("\n" + "="*60)
    print("TEST 1: Ollama Connectivity Check")
    print("="*60)

    try:
        is_running = await DeepSeekAgent.check_ollama_status()

        if is_running:
            print("✅ Ollama is running and accessible")
            print("   Endpoint: http://localhost:11434")
            return True
        else:
            print("❌ Ollama is not running")
            print("\n💡 To start Ollama:")
            print("   1. Open new terminal")
            print("   2. Run: ollama serve")
            print("   3. Keep it running")
            return False

    except Exception as e:
        print(f"❌ Connectivity check failed: {e}")
        return False


def test_agent_initialization():
    """
    Test 2: DeepSeek Agent Initialization

    Note: No API key needed for local Ollama!
    """
    print("\n" + "="*60)
    print("TEST 2: DeepSeek Agent Initialization")
    print("="*60)

    try:
        agent = DeepSeekAgent()

        # No API key needed for local models
        assert agent.model_name == "deepseek-r1:14b"
        assert agent.client is not None
        assert agent.base_url == "http://localhost:11434"

        print("✅ Agent initialized successfully")
        print(f"   Model: {agent.model_name}")
        print(f"   Location: LOCAL (Ollama)")
        print(f"   Cost: $0.00 (free!)")
        return True

    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


async def test_async_research_sports():
    """Test 3: Async Research - Sports Domain"""
    print("\n" + "="*60)
    print("TEST 3: Async Local Research - Sports Domain")
    print("⏳ (Local inference - may take 20-30 seconds)")
    print("="*60)

    try:
        agent = DeepSeekAgent()

        result = await agent.research_async(
            query="What makes a successful basketball team?",
            domain=ResearchDomain.SPORTS,
            max_tokens=300
        )

        # Verify response
        assert isinstance(result, ResearchResponse)
        assert result.domain == ResearchDomain.SPORTS
        assert result.model_name == "deepseek-r1:14b"
        assert len(result.answer) > 0
        assert len(result.key_points) > 0

        print("✅ Local research successful")
        print(f"   Answer length: {len(result.answer)} chars")
        print(f"   Key points: {len(result.key_points)}")
        print(f"   Tokens: {result.tokens_used if result.tokens_used else 'N/A'}")
        print(f"   Cost: $0.00 (local)")

        return True

    except Exception as e:
        print(f"❌ Research failed: {e}")
        print("   💡 Is DeepSeek model pulled? Run: ollama pull deepseek-r1:14b")
        return False


async def test_async_research_finance():
    """Test 4: Async Research - Finance Domain"""
    print("\n" + "="*60)
    print("TEST 4: Async Local Research - Finance Domain")
    print("="*60)

    try:
        agent = DeepSeekAgent()

        result = await agent.research_async(
            query="What are the principles of value investing?",
            domain=ResearchDomain.FINANCE
        )

        assert isinstance(result, ResearchResponse)
        assert result.domain == ResearchDomain.FINANCE

        print("✅ Finance domain research successful")
        print(f"   Key points: {len(result.key_points)}")

        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_async_research_shopping():
    """Test 5: Async Research - Shopping Domain"""
    print("\n" + "="*60)
    print("TEST 5: Async Local Research - Shopping Domain")
    print("="*60)

    try:
        agent = DeepSeekAgent()

        result = await agent.research_async(
            query="What features should I look for in a laptop?",
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
    """Test 6: Async Research - Healthcare Domain"""
    print("\n" + "="*60)
    print("TEST 6: Async Local Research - Healthcare Domain")
    print("="*60)

    try:
        agent = DeepSeekAgent()

        result = await agent.research_async(
            query="What are the benefits of staying hydrated?",
            domain=ResearchDomain.HEALTHCARE
        )

        assert isinstance(result, ResearchResponse)
        assert result.domain == ResearchDomain.HEALTHCARE

        print("✅ Healthcare domain research successful")
        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_cost_comparison():
    """
    Test 7: Cost Comparison

    Highlight that DeepSeek is FREE (local inference)
    """
    print("\n" + "="*60)
    print("TEST 7: Cost Analysis (Local vs Cloud)")
    print("="*60)

    try:
        agent = DeepSeekAgent()

        result = await agent.research_async(
            query="Explain artificial intelligence",
            domain=ResearchDomain.HEALTHCARE,
            max_tokens=200
        )

        print("✅ Cost analysis complete")
        print(f"\n💰 Cost Breakdown:")
        print(f"   DeepSeek (local): $0.00 (FREE - unlimited)")
        print(f"   Gemini (cloud):   $0.00 (free tier)")
        print(f"   GPT-4o (cloud):   ~$0.0005 per query")
        print(f"\n💡 Local inference advantages:")
        print(f"   ✓ Zero API costs")
        print(f"   ✓ Data privacy (stays on your machine)")
        print(f"   ✓ No rate limits")
        print(f"   ✓ Works offline")

        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_error_handling():
    """Test 8: Error Handling"""
    print("\n" + "="*60)
    print("TEST 8: Error Handling (Model Not Available)")
    print("="*60)

    try:
        # Try to use non-existent model
        agent = DeepSeekAgent(model_name="nonexistent-model:latest")

        result = await agent.research_async(
            query="Test",
            domain=ResearchDomain.SPORTS
        )

        print("❌ Should have raised an error!")
        return False

    except Exception as e:
        print(f"✅ Correctly raised error: {type(e).__name__}")
        print("   (Expected - model doesn't exist)")
        return True


async def run_all_tests():
    """Run all DeepSeek agent tests."""

    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*10 + "DEEPSEEK AGENT (LOCAL OLLAMA) TEST SUITE" + " "*8 + "║")
    print("╚" + "="*58 + "╝")

    # First check if Ollama is running
    ollama_running = await test_ollama_connectivity()

    if not ollama_running:
        print("\n⚠️  Ollama is not running - skipping remaining tests")
        print("\n💡 To run these tests:")
        print("   1. Open new terminal")
        print("   2. Run: ollama serve")
        print("   3. Run: ollama pull deepseek-r1:14b")
        print("   4. Re-run this test")
        return False

    results = {
        "ollama_connectivity": ollama_running,
        "initialization": test_agent_initialization(),
        "async_sports": await test_async_research_sports(),
        "async_finance": await test_async_research_finance(),
        "async_shopping": await test_async_research_shopping(),
        "async_healthcare": await test_async_research_healthcare(),
        "cost_comparison": await test_cost_comparison(),
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
        print("\n🎉 All DeepSeek local agent tests passed!")
        print("   🏠 Local inference working perfectly!")
        print("   💰 Zero API costs - unlimited queries!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
