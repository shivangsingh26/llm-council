"""
Phase 1 Complete Integration Test Suite
========================================

Comprehensive tests for Phase 1: Adaptive Routing System

Tests:
1. End-to-end routing flow (all paths)
2. Disagreement scoring accuracy
3. Latency validation against targets
4. User preference overrides
5. Edge cases (no agents, single agent, failures)
6. Backend API integration

Success Criteria (from ARCHITECTURE.md):
- FAST path: < 8s total latency
- MEDIUM path: < 12s total latency
- DEEP path: < 15s total latency (without jury)
- Disagreement scoring: 0.0-1.0 range
- Routing thresholds: FAST < 0.3, MEDIUM 0.3-0.7, DEEP > 0.7
"""

import pytest
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime

from src.council.orchestrator import CouncilOrchestrator
from src.council.aggregator import ResponseAggregator
from src.agents.openai_agent import OpenAIAgent
from src.agents.gemini_agent import GeminiResearchAgent
from src.models.schemas import ResearchDomain

load_dotenv()


class TestPhase1Complete:
    """Complete Phase 1 integration test suite."""

    @pytest.fixture
    async def council(self):
        """Create a council with all available agents."""
        agents = []

        if os.getenv("OPENAI_API_KEY"):
            agents.append(OpenAIAgent(api_key=os.getenv("OPENAI_API_KEY")))

        if os.getenv("GEMINI_API_KEY"):
            agents.append(GeminiResearchAgent(api_key=os.getenv("GEMINI_API_KEY")))

        if len(agents) < 2:
            pytest.skip("Need at least 2 agents for Phase 1 tests")

        aggregator = ResponseAggregator()
        return CouncilOrchestrator(agents, aggregator=aggregator)

    # =========================================================================
    # Test 1: FAST Path Routing
    # =========================================================================

    @pytest.mark.asyncio
    async def test_fast_path_automatic_routing(self, council):
        """Test FAST path with high agreement query (automatic routing)."""
        print("\n" + "="*70)
        print("TEST 1: FAST PATH (Automatic Routing)")
        print("="*70)

        # High agreement query
        result = await council.research_with_routing(
            query="What is the capital of France?",
            domain=ResearchDomain.FINANCE,
            depth_mode="auto"
        )

        # Validate routing decision
        assert result["routing_decision"] == "fast", \
            f"Expected FAST path, got {result['routing_decision']}"

        # Validate disagreement score
        score = result["disagreement_score"]
        assert 0.0 <= score <= 1.0, "Disagreement score out of range"
        assert score < 0.3, f"Expected low disagreement (<0.3), got {score:.3f}"

        # Validate latency (FAST target: < 8s = 8000ms)
        total_latency = result["latency_breakdown"]["total_ms"]
        assert total_latency < 8000, \
            f"FAST path exceeded 8s target: {total_latency}ms"

        # Validate synthesis
        assert result["synthesized_answer"], "Missing synthesized answer"
        assert len(result["consensus_points"]) > 0, "Missing consensus points"

        print(f"✅ FAST path validated")
        print(f"   Disagreement: {score:.3f}")
        print(f"   Latency: {total_latency}ms (target: <8000ms)")
        print(f"   Routing: {result['routing_decision']}")

    @pytest.mark.asyncio
    async def test_fast_path_forced_routing(self, council):
        """Test FAST path with user override (forced routing)."""
        print("\n" + "="*70)
        print("TEST 2: FAST PATH (Forced Routing)")
        print("="*70)

        # Force FAST path even on complex query
        result = await council.research_with_routing(
            query="What are the implications of quantum computing?",
            domain=ResearchDomain.FINANCE,
            depth_mode="fast"
        )

        # Validate user preference was respected
        assert result["routing_decision"] == "fast", \
            "User preference override failed"

        print(f"✅ User preference override validated")
        print(f"   Routing: {result['routing_decision']}")

    # =========================================================================
    # Test 2: MEDIUM Path Routing
    # =========================================================================

    @pytest.mark.asyncio
    async def test_medium_path_automatic_routing(self, council):
        """Test MEDIUM path with moderate disagreement query."""
        print("\n" + "="*70)
        print("TEST 3: MEDIUM PATH (Automatic Routing)")
        print("="*70)

        # Moderate disagreement query
        result = await council.research_with_routing(
            query="Should I invest in stocks or bonds?",
            domain=ResearchDomain.FINANCE,
            depth_mode="auto"
        )

        # Note: This might route to FAST or MEDIUM depending on actual disagreement
        # We'll validate the routing logic is correct
        score = result["disagreement_score"]
        routing = result["routing_decision"]

        if 0.3 <= score <= 0.7:
            assert routing == "medium", \
                f"Score {score:.3f} should route to MEDIUM, got {routing}"

        # Validate latency (MEDIUM target: < 12s = 12000ms)
        total_latency = result["latency_breakdown"]["total_ms"]
        if routing == "medium":
            assert total_latency < 12000, \
                f"MEDIUM path exceeded 12s target: {total_latency}ms"

        print(f"✅ MEDIUM path logic validated")
        print(f"   Disagreement: {score:.3f}")
        print(f"   Latency: {total_latency}ms")
        print(f"   Routing: {routing}")

    @pytest.mark.asyncio
    async def test_medium_path_forced_routing(self, council):
        """Test MEDIUM path with user override."""
        print("\n" + "="*70)
        print("TEST 4: MEDIUM PATH (Forced Routing)")
        print("="*70)

        result = await council.research_with_routing(
            query="What is machine learning?",
            domain=ResearchDomain.FINANCE,
            depth_mode="medium"
        )

        assert result["routing_decision"] == "medium"

        print(f"✅ MEDIUM path forced routing validated")

    # =========================================================================
    # Test 3: DEEP Path Routing
    # =========================================================================

    @pytest.mark.asyncio
    async def test_deep_path_automatic_routing(self, council):
        """Test DEEP path with high disagreement query."""
        print("\n" + "="*70)
        print("TEST 5: DEEP PATH (Automatic Routing)")
        print("="*70)

        # High disagreement query
        result = await council.research_with_routing(
            query="Is artificial intelligence a threat to humanity?",
            domain=ResearchDomain.FINANCE,
            depth_mode="auto"
        )

        score = result["disagreement_score"]
        routing = result["routing_decision"]

        if score > 0.7:
            assert routing == "deep", \
                f"Score {score:.3f} should route to DEEP, got {routing}"

        # Validate latency (DEEP target: < 15s = 15000ms without jury)
        total_latency = result["latency_breakdown"]["total_ms"]
        if routing == "deep":
            assert total_latency < 15000, \
                f"DEEP path exceeded 15s target: {total_latency}ms"

        print(f"✅ DEEP path logic validated")
        print(f"   Disagreement: {score:.3f}")
        print(f"   Latency: {total_latency}ms")
        print(f"   Routing: {routing}")

    @pytest.mark.asyncio
    async def test_deep_path_forced_routing(self, council):
        """Test DEEP path with user override."""
        print("\n" + "="*70)
        print("TEST 6: DEEP PATH (Forced Routing)")
        print("="*70)

        result = await council.research_with_routing(
            query="What is Python?",
            domain=ResearchDomain.FINANCE,
            depth_mode="deep"
        )

        assert result["routing_decision"] == "deep"

        print(f"✅ DEEP path forced routing validated")

    # =========================================================================
    # Test 4: Disagreement Scoring Accuracy
    # =========================================================================

    @pytest.mark.asyncio
    async def test_disagreement_scoring_range(self, council):
        """Test disagreement scores are within valid range."""
        print("\n" + "="*70)
        print("TEST 7: Disagreement Scoring Range")
        print("="*70)

        queries = [
            "What is 2+2?",
            "What are the benefits of exercise?",
            "Is cryptocurrency a good investment?"
        ]

        for query in queries:
            result = await council.research_with_routing(
                query=query,
                domain=ResearchDomain.FINANCE,
                depth_mode="auto"
            )

            score = result["disagreement_score"]
            assert 0.0 <= score <= 1.0, \
                f"Score {score} out of range [0.0, 1.0]"

            print(f"   ✓ Query: '{query[:30]}...'")
            print(f"     Score: {score:.3f}")

    # =========================================================================
    # Test 5: Latency Validation
    # =========================================================================

    @pytest.mark.asyncio
    async def test_latency_breakdown_completeness(self, council):
        """Test latency breakdown includes all phases."""
        print("\n" + "="*70)
        print("TEST 8: Latency Breakdown Completeness")
        print("="*70)

        result = await council.research_with_routing(
            query="What is Node.js?",
            domain=ResearchDomain.FINANCE,
            depth_mode="auto"
        )

        breakdown = result["latency_breakdown"]

        # Validate all phases present
        assert "council_phase_ms" in breakdown
        assert "disagreement_analysis_ms" in breakdown
        assert "judge_phase_ms" in breakdown
        assert "total_ms" in breakdown

        # Validate total equals sum of parts
        sum_parts = (
            breakdown["council_phase_ms"] +
            breakdown["disagreement_analysis_ms"] +
            breakdown["judge_phase_ms"]
        )

        # Allow for small timing discrepancies (within 100ms)
        assert abs(breakdown["total_ms"] - sum_parts) < 100, \
            f"Total {breakdown['total_ms']}ms != sum {sum_parts}ms"

        print(f"✅ Latency breakdown validated")
        print(f"   Council: {breakdown['council_phase_ms']}ms")
        print(f"   Analysis: {breakdown['disagreement_analysis_ms']}ms")
        print(f"   Judge: {breakdown['judge_phase_ms']}ms")
        print(f"   Total: {breakdown['total_ms']}ms")

    # =========================================================================
    # Test 6: Edge Cases
    # =========================================================================

    @pytest.mark.asyncio
    async def test_insufficient_agents(self):
        """Test graceful handling when insufficient agents."""
        print("\n" + "="*70)
        print("TEST 9: Insufficient Agents")
        print("="*70)

        # Create council with only 1 agent
        agents = []
        if os.getenv("OPENAI_API_KEY"):
            agents.append(OpenAIAgent(api_key=os.getenv("OPENAI_API_KEY")))

        if len(agents) == 0:
            pytest.skip("Need at least 1 agent")

        aggregator = ResponseAggregator()
        council = CouncilOrchestrator(agents, aggregator=aggregator)

        result = await council.research_with_routing(
            query="What is Python?",
            domain=ResearchDomain.FINANCE,
            depth_mode="auto"
        )

        # With only 1 agent, disagreement should be None or 0
        # System should still produce a result
        assert result["synthesized_answer"], "Should produce answer with 1 agent"

        print(f"✅ Single agent handled gracefully")

    # =========================================================================
    # Test 7: Synthesis Quality
    # =========================================================================

    @pytest.mark.asyncio
    async def test_synthesis_quality_across_paths(self, council):
        """Test synthesis quality for all paths."""
        print("\n" + "="*70)
        print("TEST 10: Synthesis Quality")
        print("="*70)

        paths = ["fast", "medium", "deep"]

        for path in paths:
            result = await council.research_with_routing(
                query="What are the benefits of renewable energy?",
                domain=ResearchDomain.FINANCE,
                depth_mode=path
            )

            # Validate synthesis exists
            assert result["synthesized_answer"], f"Missing answer for {path}"
            assert len(result["synthesized_answer"]) > 50, \
                f"Answer too short for {path}"

            # Validate structure
            assert result["consensus_points"], f"Missing consensus for {path}"

            print(f"   ✓ {path.upper()} path: {len(result['synthesized_answer'])} chars")

    # =========================================================================
    # Test 8: Performance Benchmarks
    # =========================================================================

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, council):
        """Benchmark all three paths against targets."""
        print("\n" + "="*70)
        print("TEST 11: Performance Benchmarks")
        print("="*70)

        benchmarks = {
            "fast": {"target": 8000, "query": "What is 2+2?"},
            "medium": {"target": 12000, "query": "What is climate change?"},
            "deep": {"target": 15000, "query": "What is consciousness?"}
        }

        results = {}

        for path, config in benchmarks.items():
            result = await council.research_with_routing(
                query=config["query"],
                domain=ResearchDomain.FINANCE,
                depth_mode=path
            )

            latency = result["latency_breakdown"]["total_ms"]
            target = config["target"]

            results[path] = {
                "latency": latency,
                "target": target,
                "passed": latency < target
            }

            status = "✅" if latency < target else "⚠️"
            print(f"   {status} {path.upper()}: {latency}ms (target: <{target}ms)")

        # All paths should meet their targets
        for path, data in results.items():
            assert data["passed"], \
                f"{path.upper()} exceeded target: {data['latency']}ms > {data['target']}ms"


# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == "__main__":
    """
    Run tests manually for debugging.

    Usage: python -m tests.integration.test_phase1_complete
    """
    pytest.main([__file__, "-v", "-s"])
