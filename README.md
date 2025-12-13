# LLM Council - Deep Research AI System

Multi-model AI collaboration system for comprehensive research across four domains: Sports, Finance, Shopping, and Healthcare.

## 🎯 Current Status: Milestone 1.2 Complete

✅ **Completed:**
- Connection tests for OpenAI and Gemini
- Structured schemas with Pydantic
- Base agent architecture
- Gemini research agent
- Single-agent research across 4 domains

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
source .venv/bin/activate

# Install packages
uv pip install -e .
```

### 2. Set Up Environment

Create/update `.env` file:
```env
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Run Tests

```bash
# Test API connections
python tests/run_all_tests.py

# Test single-agent research (Milestone 1.2)
python test_single_agent.py
```

## 📁 Project Structure

```
llm-council/
├── src/
│   ├── agents/
│   │   ├── base_agent.py       # Abstract base class
│   │   └── gemini_agent.py     # Gemini implementation
│   ├── models/
│   │   └── schemas.py          # Pydantic data models
│   ├── council/                # Future: Multi-agent coordination
│   ├── workflows/              # Future: LangGraph workflows
│   ├── domains/                # Future: Domain-specific logic
│   └── tools/                  # Future: Web search, data tools
├── tests/
│   ├── test_openai_connection.py
│   ├── test_gemini_connection.py
│   └── run_all_tests.py
├── test_single_agent.py        # Milestone 1.2 test
├── pyproject.toml
└── .env
```

## 📚 What You've Learned So Far

### Milestone 1.1: Environment Setup
- ✅ Modern Python packaging with `pyproject.toml`
- ✅ Secure API key management with `.env`
- ✅ Latest SDK patterns (2025 standards)
- ✅ Error handling and token tracking

### Milestone 1.2: Single Agent Research
- ✅ Pydantic for structured data validation
- ✅ Abstract Base Classes for consistent architecture
- ✅ Domain-specific prompting
- ✅ Text parsing and response structuring
- ✅ OOP principles (inheritance, abstraction)

## 🔑 Key Concepts

### Pydantic Schemas
```python
from src.models.schemas import ResearchResponse, ResearchDomain

# Structured, validated data instead of raw text!
response = ResearchResponse(
    query="What are the benefits of exercise?",
    answer="Regular exercise improves...",
    domain=ResearchDomain.HEALTHCARE,
    confidence=ConfidenceLevel.HIGH,
    key_points=["Improves heart health", "Boosts mood", ...]
)
```

### Agent Architecture
```python
from src.agents.gemini_agent import GeminiResearchAgent

# Create agent
agent = GeminiResearchAgent(api_key="...")

# Conduct research
result = agent.research(
    query="What were the NBA playoff results?",
    domain=ResearchDomain.SPORTS
)

# Access structured data
print(result.answer)
print(result.key_points)
print(result.confidence)
```

## 🎓 Learning Resources

### Files with Educational Comments
- `src/models/schemas.py` - Pydantic models explained
- `src/agents/base_agent.py` - Abstract classes and OOP
- `src/agents/gemini_agent.py` - API integration and parsing
- `tests/test_openai_connection.py` - OpenAI API patterns
- `tests/test_gemini_connection.py` - Gemini new SDK

### Key Files to Study
1. **schemas.py**: Learn data validation and structure
2. **base_agent.py**: Understand abstraction and interfaces
3. **gemini_agent.py**: See real API integration
4. **test_single_agent.py**: Practical usage examples

## 📊 Development Roadmap

### ✅ Phase 1: Foundation (Weeks 1-2)
- [x] Milestone 1.1: Environment setup
- [x] Milestone 1.2: Single agent research

### 🔄 Phase 2: Multi-Model Council (Weeks 3-4)
- [ ] Milestone 2.1: Add OpenAI and Anthropic agents
- [ ] Milestone 2.2: Parallel execution with asyncio
- [ ] Milestone 2.3: Response aggregation

### 🔮 Phase 3: Advanced Reasoning (Weeks 5-6)
- [ ] Milestone 3.1: LangGraph state machine
- [ ] Milestone 3.2: Intelligent synthesis

### 🎯 Phase 4: Domain Specialization (Weeks 7-8)
- [ ] Milestone 4.1: Domain-specific prompts
- [ ] Milestone 4.2: Web search integration

## 💡 Next Steps

You're ready for **Milestone 2.1: Multi-Model Council**!

Next tasks:
1. Create OpenAI agent (`src/agents/openai_agent.py`)
2. Create Anthropic agent (`src/agents/anthropic_agent.py`)
3. Implement parallel execution
4. Compare responses from all three models

## 🔗 API Documentation

- [Google Gemini API](https://ai.google.dev/gemini-api/docs)
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic API](https://docs.anthropic.com)
- [Pydantic Documentation](https://docs.pydantic.dev)

## 📝 Notes

- Gemini has generous free tier (60 requests/minute)
- OpenAI charges per token (~$0.15/1M tokens for GPT-4o-mini)
- All code is heavily commented for learning
- Each milestone builds on the previous one

---

**Built with**: Python 3.12, Pydantic, OpenAI SDK, Google Genai SDK
**Project Type**: Learning project with production-grade patterns
