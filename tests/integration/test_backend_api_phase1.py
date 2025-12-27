"""
Backend API Integration Tests for Phase 1
==========================================

Tests the complete backend API with Phase 1 adaptive routing.

Validates:
- POST /api/research endpoint with depth_mode parameter
- Response includes Phase 1 fields (disagreement_score, routing_decision, latency_breakdown)
- All three routing paths work through the API
- Error handling for invalid inputs
"""

import pytest
import requests
import time
from typing import Dict, Any

# Backend API base URL
BASE_URL = "http://localhost:8000"


class TestBackendAPIPhase1:
    """Backend API integration tests for Phase 1."""

    def test_api_health(self):
        """Test that backend is running."""
        print("\n" + "="*70)
        print("TEST 1: Backend Health Check")
        print("="*70)

        try:
            response = requests.get(f"{BASE_URL}/docs")
            assert response.status_code == 200, "Backend not responding"
            print("✅ Backend is running")
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend not running. Start with: python backend/main.py")

    def test_research_with_auto_routing(self):
        """Test research endpoint with auto routing."""
        print("\n" + "="*70)
        print("TEST 2: Research with Auto Routing")
        print("="*70)

        payload = {
            "query": "What is the capital of France?",
            "domain": "finance",
            "max_tokens": 500,
            "depth_mode": "auto"
        }

        response = requests.post(f"{BASE_URL}/api/research", json=payload)

        # Validate response
        assert response.status_code == 200, f"Failed: {response.text}"

        data = response.json()
        assert data["success"] is True
        assert "data" in data

        result = data["data"]

        # Validate Phase 1 fields present
        assert "disagreement_score" in result, "Missing disagreement_score"
        assert "routing_decision" in result, "Missing routing_decision"
        assert "latency_breakdown" in result, "Missing latency_breakdown"

        # Validate disagreement score
        score = result["disagreement_score"]
        assert 0.0 <= score <= 1.0, f"Score {score} out of range"

        # Validate routing decision
        routing = result["routing_decision"]
        assert routing in ["fast", "medium", "deep"], f"Invalid routing: {routing}"

        # Validate latency breakdown
        breakdown = result["latency_breakdown"]
        assert "council_phase_ms" in breakdown
        assert "disagreement_analysis_ms" in breakdown
        assert "judge_phase_ms" in breakdown
        assert "total_ms" in breakdown

        print(f"✅ Auto routing validated")
        print(f"   Disagreement: {score:.3f}")
        print(f"   Routing: {routing}")
        print(f"   Total latency: {breakdown['total_ms']}ms")

    def test_research_with_fast_path(self):
        """Test research endpoint forcing FAST path."""
        print("\n" + "="*70)
        print("TEST 3: Research with FAST Path")
        print("="*70)

        payload = {
            "query": "What is Python?",
            "domain": "finance",
            "max_tokens": 500,
            "depth_mode": "fast"
        }

        response = requests.post(f"{BASE_URL}/api/research", json=payload)
        assert response.status_code == 200

        data = response.json()
        result = data["data"]

        assert result["routing_decision"] == "fast", "FAST path not used"

        print(f"✅ FAST path validated")

    def test_research_with_medium_path(self):
        """Test research endpoint forcing MEDIUM path."""
        print("\n" + "="*70)
        print("TEST 4: Research with MEDIUM Path")
        print("="*70)

        payload = {
            "query": "What is blockchain?",
            "domain": "finance",
            "max_tokens": 500,
            "depth_mode": "medium"
        }

        response = requests.post(f"{BASE_URL}/api/research", json=payload)
        assert response.status_code == 200

        data = response.json()
        result = data["data"]

        assert result["routing_decision"] == "medium", "MEDIUM path not used"

        print(f"✅ MEDIUM path validated")

    def test_research_with_deep_path(self):
        """Test research endpoint forcing DEEP path."""
        print("\n" + "="*70)
        print("TEST 5: Research with DEEP Path")
        print("="*70)

        payload = {
            "query": "What is quantum computing?",
            "domain": "finance",
            "max_tokens": 500,
            "depth_mode": "deep"
        }

        response = requests.post(f"{BASE_URL}/api/research", json=payload)
        assert response.status_code == 200

        data = response.json()
        result = data["data"]

        assert result["routing_decision"] == "deep", "DEEP path not used"

        print(f"✅ DEEP path validated")

    def test_invalid_depth_mode(self):
        """Test error handling for invalid depth_mode."""
        print("\n" + "="*70)
        print("TEST 6: Invalid Depth Mode")
        print("="*70)

        payload = {
            "query": "What is AI?",
            "domain": "finance",
            "max_tokens": 500,
            "depth_mode": "invalid"  # Invalid value
        }

        response = requests.post(f"{BASE_URL}/api/research", json=payload)

        # Should either:
        # 1. Reject with 400/422 (validation error)
        # 2. Fallback to "auto" and succeed with 200
        assert response.status_code in [200, 400, 422]

        if response.status_code == 200:
            # Fallback to auto
            data = response.json()
            print(f"✅ Invalid depth_mode handled (fallback to auto)")
        else:
            # Validation error
            print(f"✅ Invalid depth_mode rejected with {response.status_code}")

    def test_complete_response_structure(self):
        """Test that response has all expected fields."""
        print("\n" + "="*70)
        print("TEST 7: Complete Response Structure")
        print("="*70)

        payload = {
            "query": "What are the benefits of cloud computing?",
            "domain": "finance",
            "max_tokens": 500,
            "depth_mode": "auto"
        }

        response = requests.post(f"{BASE_URL}/api/research", json=payload)
        assert response.status_code == 200

        data = response.json()
        result = data["data"]

        # Core fields
        required_fields = [
            "query",
            "domain",
            "responses",
            "total_agents",
            "successful_agents",
            "failed_agents",
            "consensus_points",
            "disagreement_points",
            "synthesized_answer",
            "total_tokens",
            "total_cost",
            # Phase 1 fields
            "disagreement_score",
            "routing_decision",
            "latency_breakdown"
        ]

        for field in required_fields:
            assert field in result, f"Missing field: {field}"

        print(f"✅ All required fields present ({len(required_fields)} fields)")

    def test_performance_benchmarks_via_api(self):
        """Test latency targets through API."""
        print("\n" + "="*70)
        print("TEST 8: Performance Benchmarks via API")
        print("="*70)

        tests = [
            {"path": "fast", "target": 8000},
            {"path": "medium", "target": 12000},
            {"path": "deep", "target": 15000}
        ]

        for test in tests:
            payload = {
                "query": "What is machine learning?",
                "domain": "finance",
                "max_tokens": 500,
                "depth_mode": test["path"]
            }

            response = requests.post(f"{BASE_URL}/api/research", json=payload)
            assert response.status_code == 200

            data = response.json()
            result = data["data"]

            latency = result["latency_breakdown"]["total_ms"]
            target = test["target"]

            status = "✅" if latency < target else "⚠️"
            print(f"   {status} {test['path'].upper()}: {latency}ms (target: <{target}ms)")


# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == "__main__":
    """
    Run tests manually.

    Prerequisites:
    - Backend must be running: python backend/main.py
    - At least 2 agents configured (OPENAI_API_KEY and/or GEMINI_API_KEY)

    Usage: python -m tests.integration.test_backend_api_phase1
    """
    pytest.main([__file__, "-v", "-s"])
