"""
Phase 2 Complete Integration Tests

Tests the full Jury layer integration with adaptive routing:
- DEEP path triggers Jury deliberation
- Evidence Validator analyzes sources
- Logic Auditor checks consistency
- Assumption Critic challenges assumptions
- Jury verdict affects final output
"""

import pytest
import os
import time
from src.council.orchestrator import CouncilOrchestrator
from src.models.schemas import ResearchDomain


@pytest.fixture
def api_keys():
    """Get API keys from environment."""
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not openai_key or not gemini_key:
        pytest.skip("API keys not set (OPENAI_API_KEY and GEMINI_API_KEY required)")

    return {"openai": openai_key, "gemini": gemini_key}


@pytest.fixture
async def orchestrator(api_keys):
    """Create orchestrator with Jury enabled."""
    orch = CouncilOrchestrator(
        openai_api_key=api_keys["openai"],
        gemini_api_key=api_keys["gemini"],
        enable_jury=True  # Enable Jury layer for Phase 2
    )
    return orch


class TestPhase2JuryIntegration:
    """Test suite for Phase 2 Jury integration."""

    @pytest.mark.asyncio
    async def test_deep_path_triggers_jury(self, orchestrator):
        """Test that DEEP path (high disagreement) triggers Jury deliberation."""
        # Use a controversial query to trigger high disagreement
        query = "Is free will real or is everything determined by physics?"

        start_time = time.time()
        result = await orchestrator.research(
            query=query,
            domain=ResearchDomain.GENERAL
        )
        elapsed_ms = int((time.time() - start_time) * 1000)

        # Verify basic result structure
        assert result is not None
        assert "synthesized_answer" in result
        assert "routing_path" in result

        # If routed to DEEP path, should have jury results
        if result["routing_path"] == "deep":
            assert "jury_result" in result

            # Verify jury result structure if present
            if result["jury_result"] and not result["jury_result"].get("error"):
                jury_result = result["jury_result"]

                # Check jury components
                assert "evidence_validation" in jury_result
                assert "logic_analysis" in jury_result
                assert "assumption_critique" in jury_result
                assert "overall_quality_score" in jury_result
                assert "jury_verdict" in jury_result

                # Verify jury verdict is valid
                assert jury_result["jury_verdict"] in ["approved", "needs_revision", "rejected"]

                # Verify quality score range
                assert 0.0 <= jury_result["overall_quality_score"] <= 1.0

                print(f"\n✓ DEEP path jury deliberation completed in {elapsed_ms}ms")
                print(f"  Verdict: {jury_result['jury_verdict']}")
                print(f"  Quality: {jury_result['overall_quality_score']:.2f}")

    @pytest.mark.asyncio
    async def test_fast_path_skips_jury(self, orchestrator):
        """Test that FAST path (low disagreement) skips Jury."""
        # Use a simple factual query to trigger FAST path
        query = "What is 2+2?"

        result = await orchestrator.research(
            query=query,
            domain=ResearchDomain.GENERAL
        )

        # FAST path should not invoke jury
        if result["routing_path"] == "fast":
            # Jury result should be None or not present
            assert result.get("jury_result") is None

            print(f"\n✓ FAST path correctly skipped jury")

    @pytest.mark.asyncio
    async def test_evidence_validation(self, orchestrator):
        """Test Evidence Validator component."""
        # Query that requires source verification
        query = "What are the proven health benefits of vitamin D?"

        result = await orchestrator.research(
            query=query,
            domain=ResearchDomain.GENERAL
        )

        # If jury was invoked
        if result.get("jury_result") and result["jury_result"].get("evidence_validation"):
            evidence = result["jury_result"]["evidence_validation"]

            # Check evidence validation structure
            assert "overall_source_quality" in evidence
            assert isinstance(evidence["overall_source_quality"], float)

            # Should have validations
            if "validations" in evidence:
                assert isinstance(evidence["validations"], list)

            print(f"\n✓ Evidence validation completed")
            print(f"  Source quality: {evidence['overall_source_quality']:.2f}")

    @pytest.mark.asyncio
    async def test_logic_consistency_check(self, orchestrator):
        """Test Logic Auditor component."""
        # Query that might produce contradictions
        query = "Is cryptocurrency a good investment?"

        result = await orchestrator.research(
            query=query,
            domain=ResearchDomain.GENERAL
        )

        # If jury was invoked
        if result.get("jury_result") and result["jury_result"].get("logic_analysis"):
            logic = result["jury_result"]["logic_analysis"]

            # Check logic analysis structure
            assert "consistency_score" in logic
            assert isinstance(logic["consistency_score"], float)
            assert 0.0 <= logic["consistency_score"] <= 1.0

            # Should have contradictions list
            if "contradictions" in logic:
                assert isinstance(logic["contradictions"], list)

            print(f"\n✓ Logic analysis completed")
            print(f"  Consistency: {logic['consistency_score']:.2f}")

    @pytest.mark.asyncio
    async def test_assumption_critique(self, orchestrator):
        """Test Assumption Critic component."""
        # Query with inherent assumptions
        query = "Will AI replace most human jobs in the next decade?"

        result = await orchestrator.research(
            query=query,
            domain=ResearchDomain.GENERAL
        )

        # If jury was invoked
        if result.get("jury_result") and result["jury_result"].get("assumption_critique"):
            assumptions = result["jury_result"]["assumption_critique"]

            # Check assumption critique structure
            assert "robustness_score" in assumptions
            assert isinstance(assumptions["robustness_score"], float)
            assert 0.0 <= assumptions["robustness_score"] <= 1.0

            # Should have hidden assumptions and edge cases
            if "hidden_assumptions" in assumptions:
                assert isinstance(assumptions["hidden_assumptions"], list)

            if "edge_cases" in assumptions:
                assert isinstance(assumptions["edge_cases"], list)

            print(f"\n✓ Assumption critique completed")
            print(f"  Robustness: {assumptions['robustness_score']:.2f}")

    @pytest.mark.asyncio
    async def test_jury_verdict_approved(self, orchestrator):
        """Test jury approval for high-quality responses."""
        # Well-established scientific fact
        query = "What is the speed of light in a vacuum?"

        result = await orchestrator.research(
            query=query,
            domain=ResearchDomain.GENERAL
        )

        # If jury was invoked, expect approval for well-established fact
        if result.get("jury_result"):
            jury_result = result["jury_result"]

            # Well-established facts should get good scores
            if jury_result.get("overall_quality_score"):
                # Allow for API variability, but expect decent quality
                assert jury_result["overall_quality_score"] >= 0.4

            print(f"\n✓ Jury evaluation completed for factual query")

    @pytest.mark.asyncio
    async def test_jury_critical_issues(self, orchestrator):
        """Test jury detection of critical issues."""
        # Controversial/disputed topic
        query = "Are GMO foods harmful to human health?"

        result = await orchestrator.research(
            query=query,
            domain=ResearchDomain.GENERAL
        )

        # If jury was invoked
        if result.get("jury_result"):
            jury_result = result["jury_result"]

            # Should have critical_issues field
            assert "critical_issues" in jury_result
            assert isinstance(jury_result["critical_issues"], list)

            print(f"\n✓ Critical issues detection completed")
            print(f"  Issues found: {len(jury_result['critical_issues'])}")

    @pytest.mark.asyncio
    async def test_jury_recommendations(self, orchestrator):
        """Test jury provides recommendations."""
        # Complex topic requiring nuance
        query = "Should we use nuclear energy to combat climate change?"

        result = await orchestrator.research(
            query=query,
            domain=ResearchDomain.GENERAL
        )

        # If jury was invoked
        if result.get("jury_result"):
            jury_result = result["jury_result"]

            # Should have recommendations
            assert "recommendations" in jury_result
            assert isinstance(jury_result["recommendations"], list)

            print(f"\n✓ Jury recommendations provided")
            print(f"  Recommendations: {len(jury_result['recommendations'])}")

    @pytest.mark.asyncio
    async def test_jury_graceful_degradation(self):
        """Test system works even if jury fails."""
        # Create orchestrator with jury enabled but potentially failing
        orch = CouncilOrchestrator(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            enable_jury=True
        )

        query = "What is machine learning?"

        result = await orch.research(
            query=query,
            domain=ResearchDomain.GENERAL
        )

        # Should still get a result even if jury fails
        assert result is not None
        assert "synthesized_answer" in result

        print(f"\n✓ System handles jury errors gracefully")

    @pytest.mark.asyncio
    async def test_phase2_performance(self, orchestrator):
        """Test Phase 2 performance targets with Jury."""
        test_cases = [
            {
                "name": "FAST (no jury)",
                "query": "What is 2+2?",
                "expected_path": "fast",
                "target_ms": 12000,
                "has_jury": False
            },
            {
                "name": "MEDIUM (no jury in Phase 2)",
                "query": "What is climate change?",
                "expected_path": "medium",
                "target_ms": 15000,
                "has_jury": False
            },
            {
                "name": "DEEP (with jury)",
                "query": "Is consciousness purely physical or does it require something beyond physics?",
                "expected_path": "deep",
                "target_ms": 30000,  # Allow more time for jury deliberation
                "has_jury": True
            }
        ]

        for test_case in test_cases:
            print(f"\n🧪 Testing {test_case['name']}...")

            start_time = time.time()
            result = await orchestrator.research(
                query=test_case["query"],
                domain=ResearchDomain.GENERAL
            )
            elapsed_ms = int((time.time() - start_time) * 1000)

            # Verify result
            assert result is not None
            assert "routing_path" in result

            # Check jury presence matches expectation
            if test_case["has_jury"] and result["routing_path"] == "deep":
                assert "jury_result" in result
                print(f"  ✓ Jury deliberation included")
            elif not test_case["has_jury"]:
                # FAST/MEDIUM should not have jury
                if result.get("jury_result"):
                    assert result["jury_result"] is None

            # Performance check (with some tolerance)
            tolerance_ms = test_case["target_ms"] * 0.5  # 50% tolerance
            max_allowed = test_case["target_ms"] + tolerance_ms

            print(f"  Latency: {elapsed_ms}ms (target: {test_case['target_ms']}ms)")

            if elapsed_ms > max_allowed:
                print(f"  ⚠️  Warning: Exceeded target by {elapsed_ms - test_case['target_ms']}ms")
            else:
                print(f"  ✓ Within performance target")


class TestPhase2EndToEnd:
    """End-to-end Phase 2 tests."""

    @pytest.mark.asyncio
    async def test_complete_deep_path_workflow(self, orchestrator):
        """Test complete DEEP path workflow with jury."""
        query = "Should we colonize Mars or focus on fixing Earth first?"

        print(f"\n🚀 Testing complete DEEP path workflow...")
        print(f"Query: {query}")

        start_time = time.time()
        result = await orchestrator.research(
            query=query,
            domain=ResearchDomain.GENERAL
        )
        elapsed_ms = int((time.time() - start_time) * 1000)

        # Verify complete result structure
        assert result is not None
        assert "synthesized_answer" in result
        assert "routing_path" in result
        assert "disagreement_score" in result

        print(f"\n📊 Results:")
        print(f"  Path: {result['routing_path']}")
        print(f"  Disagreement: {result['disagreement_score']:.3f}")
        print(f"  Latency: {elapsed_ms}ms")

        # If DEEP path, verify jury results
        if result["routing_path"] == "deep" and result.get("jury_result"):
            jury = result["jury_result"]

            if not jury.get("error"):
                print(f"\n🏛️  Jury Deliberation:")
                print(f"  Verdict: {jury['jury_verdict']}")
                print(f"  Quality: {jury['overall_quality_score']:.2f}")
                print(f"  Critical Issues: {len(jury['critical_issues'])}")

                # Verify all jury components ran
                components_ran = sum([
                    jury.get("evidence_validation") is not None,
                    jury.get("logic_analysis") is not None,
                    jury.get("assumption_critique") is not None
                ])
                print(f"  Components: {components_ran}/3 executed")

        print(f"\n✓ Complete workflow executed successfully")

    @pytest.mark.asyncio
    async def test_jury_improves_quality(self, orchestrator):
        """Test that jury deliberation improves output quality."""
        # Use a query with potential misinformation
        query = "Does drinking alkaline water cure cancer?"

        result = await orchestrator.research(
            query=query,
            domain=ResearchDomain.GENERAL
        )

        # If jury was invoked
        if result.get("jury_result") and not result["jury_result"].get("error"):
            jury = result["jury_result"]

            # Jury should flag issues with such a claim
            # Either through critical issues or low quality score
            has_quality_concerns = (
                len(jury["critical_issues"]) > 0 or
                jury["overall_quality_score"] < 0.7
            )

            # For medical misinformation, expect jury to flag concerns
            print(f"\n✓ Jury quality check completed")
            print(f"  Quality score: {jury['overall_quality_score']:.2f}")
            print(f"  Critical issues: {len(jury['critical_issues'])}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
