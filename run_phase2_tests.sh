#!/bin/bash

# Phase 2 Test Runner
# Runs all Jury layer tests and Phase 2 integration tests

echo "🏛️  Phase 2 - Jury Layer Tests"
echo "================================"
echo ""

# Check for API keys
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not set"
    echo "   Please set: export OPENAI_API_KEY='your-key'"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY not set"
    echo "   Please set: export GEMINI_API_KEY='your-key'"
    exit 1
fi

echo "✓ API keys configured"
echo ""

# Run jury unit tests
echo "📋 Running Jury Unit Tests..."
echo "------------------------------"

echo ""
echo "1️⃣  Evidence Validator Tests"
pytest tests/jury/test_evidence_validator.py -v --tb=short

echo ""
echo "2️⃣  Logic Auditor Tests"
pytest tests/jury/test_logic_auditor.py -v --tb=short

echo ""
echo "3️⃣  Assumption Critic Tests"
pytest tests/jury/test_assumption_critic.py -v --tb=short

echo ""
echo "4️⃣  Jury Orchestrator Tests"
pytest tests/jury/test_jury_orchestrator.py -v --tb=short

echo ""
echo "------------------------------"

# Run Phase 2 integration tests
echo ""
echo "🔗 Running Phase 2 Integration Tests..."
echo "------------------------------"
pytest tests/integration/test_phase2_complete.py -v --tb=short

echo ""
echo "================================"
echo "✅ Phase 2 Test Suite Complete"
echo ""
