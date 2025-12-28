# Phase 2 Jury Layer Tests

## Overview

This directory contains comprehensive tests for the Phase 2 Jury layer implementation.

## Test Files

### Unit Tests

1. **test_evidence_validator.py**
   - Tests Evidence Validator jury specialist
   - Source verification
   - Citation hallucination detection
   - Source quality assessment
   - Error handling

2. **test_logic_auditor.py**
   - Tests Logic Auditor jury specialist
   - Contradiction detection
   - Consistency checking
   - Reasoning gap identification
   - Circular reasoning detection

3. **test_assumption_critic.py**
   - Tests Assumption Critic jury specialist
   - Hidden assumption detection
   - Edge case generation
   - Bias identification
   - Robustness scoring

4. **test_jury_orchestrator.py**
   - Integration tests for Jury Orchestrator
   - Sequential execution (Evidence → Logic → Assumptions)
   - Overall quality score calculation
   - Verdict determination
   - Graceful degradation

### Integration Tests

Located in `tests/integration/test_phase2_complete.py`:

- End-to-end DEEP path with Jury deliberation
- Fast/Medium path verification (no jury)
- Performance benchmarks with Jury
- Quality improvement validation

## Running Tests

### Run All Phase 2 Tests

```bash
./run_phase2_tests.sh
```

### Run Individual Test Suites

```bash
# Evidence Validator tests
pytest tests/jury/test_evidence_validator.py -v

# Logic Auditor tests
pytest tests/jury/test_logic_auditor.py -v

# Assumption Critic tests
pytest tests/jury/test_assumption_critic.py -v

# Jury Orchestrator tests
pytest tests/jury/test_jury_orchestrator.py -v

# Phase 2 integration tests
pytest tests/integration/test_phase2_complete.py -v
```

## Requirements

### API Keys

Both API keys are required for full test suite:

```bash
export OPENAI_API_KEY="your-openai-key"
export GEMINI_API_KEY="your-gemini-key"
```

### Dependencies

- `openai` - For Evidence Validator and Assumption Critic
- `google-genai` - For Logic Auditor
- `pytest` - Test framework
- `pytest-asyncio` - Async test support

## Test Coverage

### Evidence Validator (test_evidence_validator.py)

- ✅ Initialization and configuration
- ✅ Valid source analysis
- ✅ Controversial claim detection
- ✅ Missing source handling
- ✅ High-quality academic source recognition
- ✅ JSON parsing and fallback
- ✅ Error handling

### Logic Auditor (test_logic_auditor.py)

- ✅ Initialization and configuration
- ✅ Consistent logic analysis
- ✅ Contradiction detection
- ✅ Statement compilation
- ✅ Circular reasoning detection
- ✅ Severity classification
- ✅ Empty response handling
- ✅ Error handling

### Assumption Critic (test_assumption_critic.py)

- ✅ Initialization and configuration
- ✅ Hidden assumption detection
- ✅ Robust claim analysis
- ✅ Bias detection
- ✅ Edge case generation
- ✅ Fragile claim identification
- ✅ Recommendation generation
- ✅ Error handling

### Jury Orchestrator (test_jury_orchestrator.py)

- ✅ Sequential jury execution
- ✅ Quality score calculation
- ✅ Verdict determination (approved/needs_revision/rejected)
- ✅ Critical issue aggregation
- ✅ Recommendation collection
- ✅ Partial execution with missing API keys
- ✅ Citation hallucination detection
- ✅ Contradiction detection

### Phase 2 Integration (test_phase2_complete.py)

- ✅ DEEP path triggers jury deliberation
- ✅ FAST path skips jury
- ✅ Evidence validation integration
- ✅ Logic consistency checking
- ✅ Assumption critique integration
- ✅ Jury verdict validation
- ✅ Critical issue detection
- ✅ Recommendation generation
- ✅ Graceful degradation
- ✅ Performance benchmarking

## Expected Results

### Verdict Thresholds

**Approved:**
- Overall quality score ≥ 0.6
- Critical issues < 1

**Needs Revision:**
- Overall quality score 0.4-0.6
- Critical issues 1-2

**Rejected:**
- Overall quality score < 0.4
- Critical issues ≥ 3

### Performance Targets

- **FAST path:** < 12s (no jury)
- **MEDIUM path:** < 15s (no jury in Phase 2)
- **DEEP path:** < 30s (with jury deliberation)

## Test Architecture

```
Phase 2 Test Flow:
┌─────────────────────────────────────────┐
│     Council Research (3 agents)         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│   Disagreement Analysis & Routing       │
└────────────────┬────────────────────────┘
                 │
                 ▼
     ┌───────────┴───────────┐
     │                       │
     ▼                       ▼
  FAST/MEDIUM            DEEP PATH
  (no jury)          (jury deliberation)
                           │
                           ▼
              ┌────────────────────────┐
              │  Evidence Validator    │
              └────────────┬───────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Logic Auditor        │
              └────────────┬───────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  Assumption Critic     │
              └────────────┬───────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Jury Orchestrator    │
              │  (verdict + quality)   │
              └────────────────────────┘
```

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`, ensure you're running from project root:

```bash
cd /Users/shivangsingh/Desktop/llm-council
python -m pytest tests/jury/
```

### API Key Errors

Verify both keys are set:

```bash
echo $OPENAI_API_KEY
echo $GEMINI_API_KEY
```

### Async Test Errors

Ensure `pytest-asyncio` is installed:

```bash
pip install pytest-asyncio
```

## Future Enhancements

- [ ] Add mock tests to reduce API calls
- [ ] Add performance regression tests
- [ ] Add coverage reporting
- [ ] Add integration with CI/CD
- [ ] Add load testing for jury layer
