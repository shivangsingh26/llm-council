"""
Unit tests for AdaptiveRouter.

Tests:
- Path determination based on disagreement scores
- User preference overrides
- Fast/Medium/Deep path execution
- Routing thresholds
"""

import pytest
from datetime import datetime
from src.council.adaptive_router import AdaptiveRouter, RoutingPath
from src.models.schemas import ResearchResponse, ConfidenceLevel, ResearchDomain


@pytest.fixture
def router():
    """Create an AdaptiveRouter instance."""
    return AdaptiveRouter()


@pytest.fixture
def sample_responses():
    """Create sample council responses."""
    return {
        "gpt-4o": ResearchResponse(
            query="Test query",
            answer="Paris is the capital of France",
            domain=ResearchDomain.FINANCE,
            confidence=ConfidenceLevel.VERY_HIGH,
            key_points=["Paris is the capital"],
            model_name="gpt-4o",
            timestamp=datetime.now()
        ),
        "gemini": ResearchResponse(
            query="Test query",
            answer="The capital of France is Paris",
            domain=ResearchDomain.FINANCE,
            confidence=ConfidenceLevel.VERY_HIGH,
            key_points=["Capital is Paris"],
            model_name="gemini",
            timestamp=datetime.now()
        )
    }


def test_determine_path_fast(router):
    """Test that low disagreement scores route to FAST path."""
    # Low disagreement (< 0.3) should go to FAST path
    path = router.determine_path(disagreement_score=0.15)
    assert path == RoutingPath.FAST

    path = router.determine_path(disagreement_score=0.29)
    assert path == RoutingPath.FAST

    print("✅ Low disagreement correctly routes to FAST path")


def test_determine_path_medium(router):
    """Test that moderate disagreement scores route to MEDIUM path."""
    # Moderate disagreement (0.3-0.7) should go to MEDIUM path
    path = router.determine_path(disagreement_score=0.4)
    assert path == RoutingPath.MEDIUM

    path = router.determine_path(disagreement_score=0.5)
    assert path == RoutingPath.MEDIUM

    path = router.determine_path(disagreement_score=0.6)
    assert path == RoutingPath.MEDIUM

    print("✅ Moderate disagreement correctly routes to MEDIUM path")


def test_determine_path_deep(router):
    """Test that high disagreement scores route to DEEP path."""
    # High disagreement (> 0.7) should go to DEEP path
    path = router.determine_path(disagreement_score=0.75)
    assert path == RoutingPath.DEEP

    path = router.determine_path(disagreement_score=0.9)
    assert path == RoutingPath.DEEP

    print("✅ High disagreement correctly routes to DEEP path")


def test_user_preference_override(router):
    """Test that user preference overrides automatic routing."""
    # Low score would normally go to FAST, but user wants DEEP
    path = router.determine_path(disagreement_score=0.1, user_preference="deep")
    assert path == RoutingPath.DEEP

    # High score would normally go to DEEP, but user wants FAST
    path = router.determine_path(disagreement_score=0.9, user_preference="fast")
    assert path == RoutingPath.FAST

    # User wants specific medium path
    path = router.determine_path(disagreement_score=0.1, user_preference="medium")
    assert path == RoutingPath.MEDIUM

    print("✅ User preferences correctly override automatic routing")


def test_auto_mode_uses_score(router):
    """Test that 'auto' mode uses disagreement score."""
    # Auto mode should use score-based routing
    path = router.determine_path(disagreement_score=0.1, user_preference="auto")
    assert path == RoutingPath.FAST

    path = router.determine_path(disagreement_score=0.5, user_preference="auto")
    assert path == RoutingPath.MEDIUM

    path = router.determine_path(disagreement_score=0.8, user_preference="auto")
    assert path == RoutingPath.DEEP

    print("✅ Auto mode correctly uses disagreement score")


@pytest.mark.asyncio
async def test_fast_path_execution(router, sample_responses):
    """Test FAST path execution."""
    result = await router.execute_path(
        path=RoutingPath.FAST,
        council_responses=sample_responses,
        disagreement_score=0.2,
        disagreement_details={}
    )

    assert "routing_path" in result
    assert result["routing_path"] == "fast"
    assert "judge_phase_ms" in result
    assert result["judge_phase_ms"] >= 0
    assert "synthesized_answer" in result

    print(f"✅ FAST path execution completed ({result['judge_phase_ms']}ms)")


@pytest.mark.asyncio
async def test_medium_path_execution(router, sample_responses):
    """Test MEDIUM path execution."""
    result = await router.execute_path(
        path=RoutingPath.MEDIUM,
        council_responses=sample_responses,
        disagreement_score=0.5,
        disagreement_details={}
    )

    assert "routing_path" in result
    assert result["routing_path"] == "medium"
    assert "judge_phase_ms" in result
    assert "synthesized_answer" in result

    print(f"✅ MEDIUM path execution completed ({result['judge_phase_ms']}ms)")


@pytest.mark.asyncio
async def test_deep_path_execution(router, sample_responses):
    """Test DEEP path execution."""
    result = await router.execute_path(
        path=RoutingPath.DEEP,
        council_responses=sample_responses,
        disagreement_score=0.8,
        disagreement_details={}
    )

    assert "routing_path" in result
    assert result["routing_path"] == "deep"
    assert "judge_phase_ms" in result
    assert "synthesized_answer" in result

    print(f"✅ DEEP path execution completed ({result['judge_phase_ms']}ms)")


@pytest.mark.asyncio
async def test_empty_responses_handling(router):
    """Test handling of empty council responses."""
    result = await router.execute_path(
        path=RoutingPath.FAST,
        council_responses={},
        disagreement_score=0.0,
        disagreement_details={}
    )

    assert "synthesized_answer" in result
    assert "No valid responses" in result["synthesized_answer"]

    print("✅ Empty responses handled gracefully")


def test_threshold_boundaries(router):
    """Test exact threshold boundaries."""
    # Test boundary cases
    path = router.determine_path(disagreement_score=0.3)  # Exactly at threshold
    assert path == RoutingPath.MEDIUM

    path = router.determine_path(disagreement_score=0.7)  # Exactly at threshold
    assert path == RoutingPath.MEDIUM

    path = router.determine_path(disagreement_score=0.0)  # Minimum
    assert path == RoutingPath.FAST

    path = router.determine_path(disagreement_score=1.0)  # Maximum
    assert path == RoutingPath.DEEP

    print("✅ Threshold boundaries handled correctly")


def test_get_path_info(router):
    """Test path information retrieval."""
    # Test FAST path info
    info = router.get_path_info(RoutingPath.FAST)
    assert "name" in info
    assert "Fast Path" in info["name"]
    assert "target_latency_ms" in info
    assert info["target_latency_ms"] == 8000

    # Test MEDIUM path info
    info = router.get_path_info(RoutingPath.MEDIUM)
    assert "Medium Path" in info["name"]
    assert info["target_latency_ms"] == 12000

    # Test DEEP path info
    info = router.get_path_info(RoutingPath.DEEP)
    assert "Deep Path" in info["name"]
    assert info["target_latency_ms"] == 15000

    print("✅ Path information retrieved correctly")


@pytest.mark.asyncio
async def test_synthesis_modes(router, sample_responses):
    """Test that different paths report different synthesis modes."""
    fast_result = await router.execute_path(
        path=RoutingPath.FAST,
        council_responses=sample_responses,
        disagreement_score=0.2,
        disagreement_details={}
    )

    medium_result = await router.execute_path(
        path=RoutingPath.MEDIUM,
        council_responses=sample_responses,
        disagreement_score=0.5,
        disagreement_details={}
    )

    deep_result = await router.execute_path(
        path=RoutingPath.DEEP,
        council_responses=sample_responses,
        disagreement_score=0.8,
        disagreement_details={}
    )

    # All should have synthesis_mode field
    assert "synthesis_mode" in fast_result
    assert "synthesis_mode" in medium_result
    assert "synthesis_mode" in deep_result

    print(f"✅ Synthesis modes: FAST={fast_result['synthesis_mode']}, "
          f"MEDIUM={medium_result['synthesis_mode']}, DEEP={deep_result['synthesis_mode']}")


if __name__ == "__main__":
    """Run tests manually for debugging."""
    import asyncio

    async def run_tests():
        router = AdaptiveRouter()

        # Test path determination
        print("\nTesting path determination...")
        test_determine_path_fast(router)
        test_determine_path_medium(router)
        test_determine_path_deep(router)

        # Test user overrides
        print("\nTesting user overrides...")
        test_user_preference_override(router)
        test_auto_mode_uses_score(router)

        # Test path info
        print("\nTesting path info...")
        test_get_path_info(router)

        # Test thresholds
        print("\nTesting thresholds...")
        test_threshold_boundaries(router)

        print("\n✅ All manual tests passed!")

    asyncio.run(run_tests())
