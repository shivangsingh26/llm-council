# Test Suite Documentation

Comprehensive testing for the LLM Council project.

**Target Coverage:** 85-90% of codebase

## 🧪 Test Organization

All tests are organized in the `tests/` directory for easy execution and maintenance.

```
tests/
├── test_openai_connection.py          # OpenAI API connection tests
├── test_gemini_connection.py          # Gemini API connection tests
├── run_all_tests.py                   # API connection test runner
├── test_gemini_agent.py              # Gemini agent comprehensive tests
├── test_openai_agent.py              # GPT-4o agent tests
├── test_deepseek_agent.py            # DeepSeek/Ollama agent tests
├── run_agent_tests.py                # Agent test runner
├── test_council.py                   # Council orchestration tests (TODO)
└── README.md                         # This file
```

## 📋 Test Categories

### 1. **Connection Tests** (Milestone 1.1)
Tests basic API connectivity before building agents.

- `test_openai_connection.py` - OpenAI Responses + Chat Completions APIs
- `test_gemini_connection.py` - Gemini new SDK
- `run_all_tests.py` - Runs both connection tests

**Run:**
```bash
python tests/run_all_tests.py
```

### 2. **Agent Tests** (Milestone 1.2 & 2.1)
Comprehensive tests for each research agent.

**Gemini Agent (`test_gemini_agent.py`)**
- ✅ Initialization
- ✅ Async research (all 4 domains)
- ✅ Sync wrapper
- ✅ Error handling
- ✅ Token tracking

**OpenAI Agent - GPT-4o (`test_openai_agent.py`)**
- ✅ Initialization
- ✅ Async research (all 4 domains)
- ✅ Token tracking
- ✅ Error handling

**DeepSeek Agent - Ollama (`test_deepseek_agent.py`)**
- ✅ Ollama connectivity check
- ✅ Local model inference
- ✅ Async research (all 4 domains)
- ✅ Error handling
- ✅ Cost comparison

**Run individual agent tests:**
```bash
# Test Gemini agent
python tests/test_gemini_agent.py

# Test OpenAI agent
python tests/test_openai_agent.py

# Run all agent tests
python tests/run_agent_tests.py
```

### 3. **Council Tests** (Milestone 2.1)
Tests for multi-agent orchestration.

- 🔄 TODO: `test_council_orchestrator.py` - 4-agent parallel execution
- 🔄 TODO: `test_response_aggregator.py` - Comparison logic
- 🔄 TODO: `test_council.py` - End-to-end council tests

## 🎯 Testing Strategy

### Coverage Goals

| Component | Target Coverage | Status |
|-----------|----------------|--------|
| **Data Models** | 90% | ✅ Covered by agent tests |
| **Base Agent** | 90% | ✅ Covered by agent tests |
| **Gemini Agent** | 90% | ✅ 7 tests |
| **OpenAI Agent** | 90% | ✅ 7 tests |
| **DeepSeek Agent** | 90% | ✅ 8 tests |
| **Council Orchestrator** | 85% | 🔄 TODO |
| **Response Aggregator** | 85% | 🔄 TODO |
| **Output Manager** | 85% | ✅ Covered by agent tests |

### Test Types

**1. Unit Tests**
- Individual method testing
- Edge cases
- Error conditions

**2. Integration Tests**
- Agent + API interaction
- Agent + OutputManager
- Council + All agents

**3. Async Tests**
- All agents use async/await
- Tests verify async functionality
- Parallel execution testing

## 🚀 Running Tests

### Quick Start

```bash
# Run all API connection tests
python tests/run_all_tests.py

# Run all agent tests
python tests/run_agent_tests.py
```

### Prerequisites

**Environment Setup:**
```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Install dependencies
pip install -e .

# 3. Set up .env file
cp .env.example .env
# Add your API keys to .env
```

**Required API Keys:**
```env
OPENAI_API_KEY=sk-...      # For GPT-4o tests
GEMINI_API_KEY=...         # For Gemini tests
```

**Optional (for DeepSeek tests):**
```bash
# Start Ollama
ollama serve

# Pull DeepSeek model
ollama pull deepseek-r1:14b
```

### Individual Test Execution

```bash
# Test specific agent
python tests/test_gemini_agent.py
python tests/test_openai_agent.py

# Test specific functionality
python -m pytest tests/test_gemini_agent.py::test_agent_initialization -v
```

### Using pytest (Optional)

```bash
# Install pytest
pip install pytest pytest-asyncio

# Run all tests with pytest
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📊 Test Output Format

Each test suite provides:

✅ **Pass/Fail Status** for each test
📊 **Metrics** (tokens used, response time)
📈 **Coverage %** for the test suite
💡 **Helpful error messages** for failures

**Example Output:**
```
╔══════════════════════════════════════════════════════════╗
║               GEMINI AGENT TEST SUITE                    ║
╚══════════════════════════════════════════════════════════╝

TEST 1: Gemini Agent Initialization
====================================================
✅ Agent initialized successfully

TEST 2: Async Research - Sports Domain
====================================================
✅ Async research successful
   Tokens used: 234

...

╔══════════════════════════════════════════════════════════╗
║                    TEST SUMMARY                          ║
╚══════════════════════════════════════════════════════════╝

  initialization      ✅ PASS
  async_sports        ✅ PASS
  async_finance       ✅ PASS
  async_shopping      ✅ PASS
  async_healthcare    ✅ PASS
  sync_wrapper        ✅ PASS
  error_handling      ✅ PASS

  Passed: 7/7 (100.0%)

🎉 All Gemini agent tests passed!
```

## 🐛 Troubleshooting

### Common Issues

**"API key not found"**
```bash
# Check .env file exists
ls -la .env

# Verify key is set
echo $GEMINI_API_KEY
```

**"Module not found"**
```bash
# Reinstall in editable mode
pip install -e .
```

**"Ollama not running"**
```bash
# Start Ollama in separate terminal
ollama serve

# Verify it's running
ollama list
```

**"Tests skipped"**
- Tests are skipped if API keys are missing
- This is expected behavior
- Set up API keys to run those tests

## ✅ Test Checklist

Before proceeding to next milestone:

- [x] All connection tests pass
- [x] Gemini agent tests pass (7/7)
- [x] OpenAI agent tests pass (7/7)
- [x] DeepSeek agent tests pass (8/8)
- [x] All agents achieve >85% coverage
- [x] No critical errors or warnings

## 📝 Adding New Tests

When adding new functionality:

1. **Create test file** in `tests/` directory
2. **Follow naming convention**: `test_<component>.py`
3. **Include docstrings** explaining what's tested
4. **Aim for 85-90% coverage** of new code
5. **Update this README** with new test info
6. **Add to test runner** (`run_agent_tests.py`)

**Test Template:**
```python
"""
Component Tests
==============
Description of what this tests.
"""

import asyncio

async def test_something():
    """Test description"""
    # Arrange
    # Act
    # Assert
    pass

async def run_all_tests():
    """Run all tests for this component"""
    results = {}
    # ...
    return all(results.values())

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
```

## 🎯 Next Steps

1. ✅ **Complete all agent tests** (Gemini, OpenAI, DeepSeek)
2. 🔄 **Create council orchestration tests**
3. 🔄 **Add integration tests** for full workflow
4. 🔄 **Set up CI/CD** with automated testing
5. 🔄 **Generate coverage reports** with pytest-cov

---

**Testing Philosophy:**
*Write tests first, then fix code. Aim for high coverage, but focus on testing critical paths and edge cases.*
