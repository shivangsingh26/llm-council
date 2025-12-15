"""
Council Integration Tests
=========================
End-to-end tests for the LLM Council orchestration system.

Test Coverage:
- Council orchestrator initialization
- Parallel agent execution
- Response aggregation
- Error handling with partial failures
- All 4 domains
- Cost and token tracking

Run: python tests/test_council.py
"""

import os
import asyncio
from dotenv import load_dotenv

from src.council.orchestrator import CouncilOrchestrator
from src.council.aggregator import ResponseAggregator
from src.agents.gemini_agent import GeminiResearchAgent
from src.agents.openai_agent import OpenAIAgent
from src.agents.deepseek_agent import DeepSeekAgent
from src.models.schemas import ResearchDomain

load_dotenv()


def create_available_agents():
    """
    Create agents based on available API keys.

    Returns:
        List of initialized agents
    """
    agents = []

    if os.getenv("GEMINI_API_KEY"):
        agents.append(GeminiResearchAgent(api_key=os.getenv("GEMINI_API_KEY")))

    if os.getenv("OPENAI_API_KEY"):
        agents.append(OpenAIAgent(api_key=os.getenv("OPENAI_API_KEY")))

    # Check if Ollama is running
    try:
        import asyncio
        ollama_available = asyncio.run(DeepSeekAgent.check_ollama_status())
        if ollama_available:
            agents.append(DeepSeekAgent())
    except:
        pass

    return agents


async def test_council_initialization():
    """Test 1: Council Initialization"""
    print("\n" + "="*60)
    print("TEST 1: Council Initialization")
    print("="*60)

    agents = create_available_agents()

    if not agents:
        print("⚠️  SKIPPED: No agents available")
        return False

    try:
        council = CouncilOrchestrator(agents)

        assert council.agent_count == len(agents)
        assert len(council.get_agent_models()) == len(agents)

        print(f"✅ Council initialized with {council.agent_count} agents")
        return True

    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


async def test_parallel_research_sports():
    """Test 2: Parallel Research - Sports Domain"""
    print("\n" + "="*60)
    print("TEST 2: Parallel Research - Sports Domain")
    print("="*60)

    agents = create_available_agents()

    if len(agents) < 2:
        print("⚠️  SKIPPED: Need at least 2 agents for comparison")
        return False

    try:
        council = CouncilOrchestrator(agents)

        results = await council.research_all(
            query="What are the key factors in building a championship sports team?",
            domain=ResearchDomain.SPORTS,
            max_tokens=400
        )

        # Verify responses
        assert isinstance(results, dict)
        assert len(results) == council.agent_count

        successful = sum(1 for r in results.values() if r is not None)

        print(f"✅ Parallel research successful")
        print(f"   Successful agents: {successful}/{council.agent_count}")

        return True

    except Exception as e:
        print(f"❌ Research failed: {e}")
        return False


async def test_response_aggregation():
    """Test 3: Response Aggregation"""
    print("\n" + "="*60)
    print("TEST 3: Response Aggregation")
    print("="*60)

    agents = create_available_agents()

    if len(agents) < 2:
        print("⚠️  SKIPPED: Need at least 2 agents for aggregation")
        return False

    try:
        council = CouncilOrchestrator(agents)

        # Get responses
        responses = await council.research_all(
            query="What are the benefits of diversified investment portfolios?",
            domain=ResearchDomain.FINANCE,
            max_tokens=400
        )

        # Aggregate
        aggregator = ResponseAggregator()
        comparison = aggregator.aggregate(
            responses=responses,
            query="What are the benefits of diversified investment portfolios?",
            domain=ResearchDomain.FINANCE
        )

        # Verify aggregation
        assert comparison.total_agents == council.agent_count
        assert comparison.successful_agents > 0
        assert comparison.total_tokens is not None
        assert comparison.total_cost is not None

        print(f"✅ Aggregation successful")
        print(f"   Consensus points: {len(comparison.consensus_points)}")
        print(f"   Disagreements: {len(comparison.disagreement_points)}")
        print(f"   Total tokens: {comparison.total_tokens}")
        print(f"   Total cost: ${comparison.total_cost:.6f}")

        return True

    except Exception as e:
        print(f"❌ Aggregation failed: {e}")
        return False


async def test_all_domains():
    """Test 4: All Research Domains"""
    print("\n" + "="*60)
    print("TEST 4: All Research Domains")
    print("="*60)

    agents = create_available_agents()

    if not agents:
        print("⚠️  SKIPPED: No agents available")
        return False

    try:
        council = CouncilOrchestrator(agents)
        aggregator = ResponseAggregator()

        # Test all 4 domains
        test_queries = {
            ResearchDomain.SPORTS: "What makes a successful basketball team?",
            ResearchDomain.FINANCE: "What are the principles of value investing?",
            ResearchDomain.SHOPPING: "What features matter most in a laptop?",
            ResearchDomain.HEALTHCARE: "What are the benefits of staying hydrated?"
        }

        results = {}

        for domain, query in test_queries.items():
            responses = await council.research_all(
                query=query,
                domain=domain,
                max_tokens=300
            )

            comparison = aggregator.aggregate(
                responses=responses,
                query=query,
                domain=domain
            )

            results[domain.value] = comparison.successful_agents > 0

        # Check all passed
        all_passed = all(results.values())

        print(f"✅ All domains tested")
        for domain, success in results.items():
            status = "✅" if success else "❌"
            print(f"   {status} {domain}")

        return all_passed

    except Exception as e:
        print(f"❌ Domain testing failed: {e}")
        return False


async def test_partial_failure_handling():
    """Test 5: Graceful Handling of Partial Failures"""
    print("\n" + "="*60)
    print("TEST 5: Partial Failure Handling")
    print("="*60)

    agents = create_available_agents()

    if not agents:
        print("⚠️  SKIPPED: No agents available")
        return False

    try:
        # Add an agent with invalid API key (will fail)
        if os.getenv("GEMINI_API_KEY"):
            bad_agent = GeminiResearchAgent(api_key="invalid-key-12345")
            agents_with_bad = agents + [bad_agent]
        else:
            # Can't test without at least one working agent
            print("⚠️  SKIPPED: Need valid agent to test failure handling")
            return False

        council = CouncilOrchestrator(agents_with_bad)

        results = await council.research_all(
            query="Test query",
            domain=ResearchDomain.SPORTS,
            max_tokens=200
        )

        # Should have some successes and some failures
        successful = sum(1 for r in results.values() if r is not None)
        failed = sum(1 for r in results.values() if r is None)

        assert successful > 0  # At least one should succeed
        assert failed > 0  # At least one should fail (the bad agent)

        print(f"✅ Partial failure handled gracefully")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")

        return True

    except Exception as e:
        print(f"❌ Failure handling failed: {e}")
        return False


async def test_cost_tracking():
    """Test 6: Cost and Token Tracking"""
    print("\n" + "="*60)
    print("TEST 6: Cost and Token Tracking")
    print("="*60)

    agents = create_available_agents()

    if not agents:
        print("⚠️  SKIPPED: No agents available")
        return False

    try:
        council = CouncilOrchestrator(agents)
        aggregator = ResponseAggregator()

        responses = await council.research_all(
            query="Explain artificial intelligence in simple terms",
            domain=ResearchDomain.HEALTHCARE,
            max_tokens=200
        )

        comparison = aggregator.aggregate(
            responses=responses,
            query="Explain artificial intelligence in simple terms",
            domain=ResearchDomain.HEALTHCARE
        )

        # Verify cost tracking
        assert comparison.total_tokens is not None
        assert comparison.total_cost is not None
        assert comparison.total_cost >= 0.0

        print(f"✅ Cost tracking works")
        print(f"   Total tokens: {comparison.total_tokens}")
        print(f"   Total cost: ${comparison.total_cost:.6f}")

        # Show per-model breakdown
        print(f"\n   Per-model breakdown:")
        for model_name, response in comparison.responses.items():
            if response and response.tokens_used:
                price = aggregator.PRICING.get(model_name, 0.0)
                cost = (response.tokens_used / 1_000_000) * price
                print(f"     {model_name}: {response.tokens_used} tokens (${cost:.6f})")

        return True

    except Exception as e:
        print(f"❌ Cost tracking failed: {e}")
        return False


async def run_all_tests():
    """Run all council integration tests."""

    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*12 + "COUNCIL INTEGRATION TEST SUITE" + " "*16 + "║")
    print("╚" + "="*58 + "╝")

    # Check prerequisites
    agents = create_available_agents()

    print(f"\n📋 Environment Check:")
    print(f"   Available agents: {len(agents)}")
    if agents:
        for agent in agents:
            print(f"     • {agent.model_name}")
    else:
        print("   ❌ No agents available - set API keys or start Ollama")
        return False

    if len(agents) < 2:
        print(f"\n⚠️  Warning: Only {len(agents)} agent available")
        print("   Multi-agent comparison features will be limited")

    # Run tests
    results = {
        "initialization": await test_council_initialization(),
        "parallel_research": await test_parallel_research_sports(),
        "aggregation": await test_response_aggregation(),
        "all_domains": await test_all_domains(),
        "partial_failures": await test_partial_failure_handling(),
        "cost_tracking": await test_cost_tracking()
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
        print("\n🎉 All council integration tests passed!")
        print("   🏛️  Council orchestration is working perfectly!")
        print("   ✨ Ready for production use!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
