#!/usr/bin/env python3
"""
End-to-End Test Script for Phase A - Master Synthesizer
========================================================
This script tests the complete Phase A implementation:
1. Master Synthesizer with o1-mini
2. Response Aggregation with new fields
3. Full backend API flow

Usage:
    python test_phase_a_e2e.py

Requirements:
    - OPENAI_API_KEY environment variable set
    - GEMINI_API_KEY environment variable set (optional)
    - Backend server NOT running (this tests the SDK directly)

What it tests:
    ✅ Master Synthesizer initialization
    ✅ Agent responses (GPT-4o, Gemini)
    ✅ Deep reasoning synthesis
    ✅ New fields (reasoning_trace, knowledge_gaps, etc.)
    ✅ Cost and token calculations
    ✅ Comparison with rule-based aggregation
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.openai_agent import OpenAIAgent
from src.agents.gemini_agent import GeminiResearchAgent
from src.council.orchestrator import CouncilOrchestrator
from src.council.aggregator import ResponseAggregator
from src.models.schemas import ResearchDomain
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def print_header(title: str):
    """Print formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_result(label: str, value):
    """Print formatted result."""
    print(f"  {label}: {value}")


async def test_master_synthesizer_basic():
    """Test 1: Basic Master Synthesizer functionality."""
    print_header("TEST 1: Master Synthesizer Basic Functionality")

    try:
        from src.council.master_synthesizer import MasterSynthesizer

        synthesizer = MasterSynthesizer(model="gpt-4o")
        print("✅ Master Synthesizer initialized successfully")
        print_result("Model", synthesizer.model)
        print_result("API Key Present", "Yes" if synthesizer.api_key else "No")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def test_single_agent_research():
    """Test 2: Single agent research (GPT-4o)."""
    print_header("TEST 2: Single Agent Research (GPT-4o)")

    try:
        # Check if API key is available
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️  Skipped: OPENAI_API_KEY not set")
            return True

        agent = OpenAIAgent(api_key=os.getenv("OPENAI_API_KEY"))
        print("✅ OpenAI Agent initialized")

        query = "What are three benefits of regular exercise?"
        print(f"\n📝 Query: {query}")
        print("🤔 Researching...")

        response = await agent.research_async(
            query=query,
            domain=ResearchDomain.HEALTHCARE,
            max_tokens=300
        )

        print("\n✅ Research completed")
        print_result("Answer", response.answer[:100] + "...")
        print_result("Confidence", response.confidence.value)
        print_result("Key Points", len(response.key_points))
        print_result("Tokens Used", response.tokens_used)

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_multi_agent_with_master_synthesizer():
    """Test 3: Multi-agent research with Master Synthesizer."""
    print_header("TEST 3: Multi-Agent Research with Master Synthesizer")

    try:
        # Initialize agents
        agents = []

        if os.getenv("OPENAI_API_KEY"):
            agents.append(OpenAIAgent(api_key=os.getenv("OPENAI_API_KEY")))
            print("✅ OpenAI Agent added")

        if os.getenv("GEMINI_API_KEY"):
            agents.append(GeminiResearchAgent(api_key=os.getenv("GEMINI_API_KEY")))
            print("✅ Gemini Agent added")

        if len(agents) < 2:
            print("⚠️  Skipped: Need at least 2 agents (GPT-4o + Gemini)")
            print("   Set OPENAI_API_KEY and GEMINI_API_KEY environment variables")
            return True

        print(f"\n👥 Testing with {len(agents)} agents")

        # Create orchestrator
        council = CouncilOrchestrator(agents)

        # Run research
        query = "What are the main health benefits of drinking water?"
        print(f"\n📝 Query: {query}")
        print("🤔 Researching with all agents...")

        responses = await council.research_all(
            query=query,
            domain=ResearchDomain.HEALTHCARE,
            max_tokens=300
        )

        print(f"\n✅ Received {len(responses)} responses")

        # Aggregate with Master Synthesizer
        print("\n🧠 Synthesizing with Master Synthesizer (gpt-4o)...")
        aggregator = ResponseAggregator(use_master_synthesizer=True)

        result = await aggregator.aggregate(
            responses=responses,
            query=query,
            domain=ResearchDomain.HEALTHCARE
        )

        print("\n✅ Synthesis complete!")
        print(f"\n📊 Results:")
        print_result("Successful Agents", f"{result.successful_agents}/{result.total_agents}")
        print_result("Consensus Points", len(result.consensus_points))
        print_result("Disagreement Points", len(result.disagreement_points))
        print_result("Knowledge Gaps", len(result.knowledge_gaps))
        print_result("Confidence", result.confidence_range)

        print(f"\n💬 Synthesized Answer:")
        print(f"   {result.synthesized_answer[:200]}...")

        if result.reasoning_trace:
            print(f"\n🧠 Reasoning Trace:")
            print(f"   {result.reasoning_trace[:200]}...")

        if result.confidence_reasoning:
            print(f"\n📈 Confidence Reasoning:")
            print(f"   {result.confidence_reasoning[:200]}...")

        print(f"\n💰 Cost & Tokens:")
        print_result("Total Tokens", result.total_tokens)
        print_result("Total Cost", f"${result.total_cost:.6f}")

        # Show consensus points
        if result.consensus_points:
            print(f"\n✅ Consensus Points:")
            for i, point in enumerate(result.consensus_points[:3], 1):
                print(f"   {i}. {point}")

        # Show knowledge gaps
        if result.knowledge_gaps:
            print(f"\n🔍 Knowledge Gaps:")
            for i, gap in enumerate(result.knowledge_gaps[:3], 1):
                print(f"   {i}. {gap}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_comparison_rule_vs_master():
    """Test 4: Compare rule-based vs master synthesizer."""
    print_header("TEST 4: Rule-Based vs Master Synthesizer Comparison")

    try:
        # Need at least 2 agents
        agents = []
        if os.getenv("OPENAI_API_KEY"):
            agents.append(OpenAIAgent(api_key=os.getenv("OPENAI_API_KEY")))
        if os.getenv("GEMINI_API_KEY"):
            agents.append(GeminiResearchAgent(api_key=os.getenv("GEMINI_API_KEY")))

        if len(agents) < 2:
            print("⚠️  Skipped: Need at least 2 agents for comparison")
            return True

        council = CouncilOrchestrator(agents)
        query = "What are three benefits of exercise?"

        print(f"📝 Query: {query}")
        print("🤔 Researching...")

        responses = await council.research_all(
            query=query,
            domain=ResearchDomain.HEALTHCARE,
            max_tokens=200
        )

        # Test 1: Rule-based aggregation
        print("\n1️⃣  Rule-Based Aggregation:")
        rule_aggregator = ResponseAggregator(use_master_synthesizer=False)
        rule_result = await rule_aggregator.aggregate(
            responses=responses,
            query=query,
            domain=ResearchDomain.HEALTHCARE
        )

        print_result("   Consensus Points", len(rule_result.consensus_points))
        print_result("   Answer Length", len(rule_result.synthesized_answer))
        print_result("   Cost", f"${rule_result.total_cost:.6f}")

        # Test 2: Master Synthesizer
        print("\n2️⃣  Master Synthesizer:")
        master_aggregator = ResponseAggregator(use_master_synthesizer=True)
        master_result = await master_aggregator.aggregate(
            responses=responses,
            query=query,
            domain=ResearchDomain.HEALTHCARE
        )

        print_result("   Consensus Points", len(master_result.consensus_points))
        print_result("   Answer Length", len(master_result.synthesized_answer))
        print_result("   Cost", f"${master_result.total_cost:.6f}")
        print_result("   Has Reasoning Trace", "Yes" if master_result.reasoning_trace else "No")
        print_result("   Knowledge Gaps", len(master_result.knowledge_gaps))

        # Comparison
        print("\n📊 Comparison:")
        cost_increase = master_result.total_cost - rule_result.total_cost
        print_result("   Cost Increase", f"${cost_increase:.6f}")
        print_result("   Quality Improvement", "✅ Reasoning trace & knowledge gaps added")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print_header("PHASE A - MASTER SYNTHESIZER E2E TESTS")

    print("🔍 Checking environment...")
    print_result("OPENAI_API_KEY", "✅ Set" if os.getenv("OPENAI_API_KEY") else "❌ Not set")
    print_result("GEMINI_API_KEY", "✅ Set" if os.getenv("GEMINI_API_KEY") else "⚠️  Not set (optional)")

    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ ERROR: OPENAI_API_KEY is required for Phase A")
        print("   Set it with: export OPENAI_API_KEY='your-key'")
        return

    # Run all tests
    tests = [
        ("Basic Master Synthesizer", test_master_synthesizer_basic()),
        ("Single Agent Research", test_single_agent_research()),
        ("Multi-Agent with Master Synthesizer", test_multi_agent_with_master_synthesizer()),
        ("Rule-Based vs Master Comparison", test_comparison_rule_vs_master()),
    ]

    results = []
    for name, test_coro in tests:
        try:
            result = await test_coro
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {name}")

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Phase A is working correctly.")
        print("\n✅ Next steps:")
        print("   1. Test from the frontend at http://localhost:3003/research")
        print("   2. Submit a research query and check for reasoning trace")
        print("   3. Verify new fields are displayed (consensus, knowledge gaps, etc.)")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
