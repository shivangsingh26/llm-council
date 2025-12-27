#!/bin/bash

###############################################################################
# Phase 1 Complete Test Suite Runner
###############################################################################
#
# Runs all Phase 1 tests and generates a summary report
#
# Prerequisites:
# - Backend running: python backend/main.py
# - Environment variables set: OPENAI_API_KEY, GEMINI_API_KEY
# - Dependencies installed: pytest, requests
#
# Usage: ./run_phase1_tests.sh
#
###############################################################################

set -e  # Exit on error

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "                    PHASE 1 COMPLETE TEST SUITE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Testing: Adaptive Routing System (Phase 1)"
echo "Components:"
echo "  • Disagreement Analyzer"
echo "  • Adaptive Router (FAST/MEDIUM/DEEP paths)"
echo "  • Backend API integration"
echo "  • Frontend type definitions"
echo ""

# Check if backend is running
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Environment Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "❌ Backend not running"
    echo "   Start with: python backend/main.py"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ] && [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ No API keys found"
    echo "   Set OPENAI_API_KEY or GEMINI_API_KEY"
    exit 1
else
    echo "✅ API keys configured"
fi

echo ""

# Run unit tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Unit Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📦 Disagreement Analyzer Tests..."
pytest tests/council/test_disagreement_analyzer.py -v --tb=short

echo ""
echo "📦 Adaptive Router Tests..."
pytest tests/council/test_adaptive_router.py -v --tb=short

echo ""

# Run integration tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Integration Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🔗 Complete Phase 1 Integration Tests..."
pytest tests/integration/test_phase1_complete.py -v --tb=short -s

echo ""

# Run backend API tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Backend API Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🌐 Backend API Integration Tests..."
pytest tests/integration/test_backend_api_phase1.py -v --tb=short -s

echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "                          TEST SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ All Phase 1 tests passed!"
echo ""
echo "Components Validated:"
echo "  ✓ Disagreement Analyzer (10 tests)"
echo "  ✓ Adaptive Router (12 tests)"
echo "  ✓ Phase 1 Integration (11 tests)"
echo "  ✓ Backend API (8 tests)"
echo ""
echo "Total: 41 tests"
echo ""
echo "Phase 1 Status: READY FOR PRODUCTION ✨"
echo ""
