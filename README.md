# LLM Council - Deep Research AI System

Multi-model AI collaboration system for comprehensive research across four domains: Sports, Finance, Shopping, and Healthcare.

## 🎯 Current Status: Phase 3 - Council Orchestration Complete

✅ **Completed:**
- ✅ Connection tests for OpenAI and Gemini
- ✅ Structured schemas with Pydantic
- ✅ Base agent architecture with async support
- ✅ Gemini 2.5 Flash agent (cloud)
- ✅ GPT-4o agent (cloud)
- ✅ DeepSeek-R1 agent (local via Ollama)
- ✅ Comprehensive test coverage (85%+)
- ✅ All 3 agents tested and working
- ✅ Council orchestrator with parallel execution
- ✅ Response aggregation and comparison
- ✅ Consensus/disagreement analysis
- ✅ Council integration tests (100% passing)

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
```

### 3. Set Up Ollama (Optional - for DeepSeek local agent)

```bash
# Install Ollama (macOS/Linux)
# Visit: https://ollama.com

# Start Ollama
ollama serve

# Pull DeepSeek model
ollama pull deepseek-r1:14b
```

### 4. Run Tests

```bash
# Test API connections
python tests/run_all_tests.py

# Test all agents
python tests/run_agent_tests.py

# Test council orchestration (multi-agent)
python tests/test_council.py
```

## 📁 Project Structure

```
llm-council/
├── src/
│   ├── agents/
│   │   ├── base_agent.py       # Abstract base class (async support)
│   │   ├── gemini_agent.py     # Gemini 2.5 Flash (cloud)
│   │   ├── openai_agent.py     # GPT-4o (cloud)
│   │   └── deepseek_agent.py   # DeepSeek-R1 (local via Ollama)
│   ├── models/
│   │   └── schemas.py          # Pydantic data models
│   ├── utils/
│   │   └── output_manager.py   # JSON file persistence
│   ├── council/
│   │   ├── orchestrator.py     # Multi-agent parallel execution
│   │   ├── aggregator.py       # Response comparison & synthesis
│   │   └── __init__.py
│   └── workflows/              # TODO: Advanced orchestration logic
├── tests/
│   ├── test_openai_connection.py
│   ├── test_gemini_connection.py
│   ├── test_gemini_agent.py
│   ├── test_openai_agent.py
│   ├── test_deepseek_agent.py
│   ├── test_council.py         # Council integration tests
│   ├── run_all_tests.py        # API connection tests
│   ├── run_agent_tests.py      # All agent tests
│   └── README.md               # Testing documentation
├── outputs/                    # Research results (JSON)
│   ├── sports/
│   ├── finance/
│   ├── shopping/
│   ├── healthcare/
│   └── council_comparisons/    # Multi-agent comparison results
│       ├── sports/
│       ├── finance/
│       ├── shopping/
│       └── healthcare/
├── pyproject.toml
└── .env
```

## 📚 What You've Learned

### Phase 1: Foundation & Single Agent
- ✅ Modern Python packaging with `pyproject.toml`
- ✅ Secure API key management with `.env`
- ✅ Latest SDK patterns (2025 standards)
- ✅ Pydantic for structured data validation
- ✅ Abstract Base Classes for consistent architecture
- ✅ Domain-specific prompting
- ✅ Text parsing and response structuring
- ✅ OOP principles (inheritance, abstraction)

### Phase 2: Multi-Agent Architecture
- ✅ Async/await for concurrent API calls
- ✅ Multiple LLM providers (OpenAI, Google, local)
- ✅ OpenAI AsyncOpenAI client
- ✅ Google Gemini new SDK (`google-genai`)
- ✅ Local LLM inference with Ollama
- ✅ Comprehensive testing (85%+ coverage)
- ✅ JSON file persistence for research outputs

### Phase 3: Council Orchestration
- ✅ asyncio.gather() for parallel execution
- ✅ Multiple agents running simultaneously
- ✅ Response aggregation and comparison
- ✅ Consensus/disagreement detection
- ✅ Cost tracking across multiple models
- ✅ ComparisonResult schema for council outputs
- ✅ Graceful failure handling (partial agent failures)
- ✅ Integration testing (100% passing)

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

### Agent Architecture (3 Models)
```python
from src.agents.gemini_agent import GeminiResearchAgent
from src.agents.openai_agent import OpenAIAgent
from src.agents.deepseek_agent import DeepSeekAgent
import asyncio

# Create agents
gemini = GeminiResearchAgent(api_key="...")
openai = OpenAIAgent(api_key="...")
deepseek = DeepSeekAgent()  # Local - no API key needed!

# Conduct async research
async def research():
    result = await openai.research_async(
        query="What were the NBA playoff results?",
        domain=ResearchDomain.SPORTS
    )

    # Access structured data
    print(result.answer)
    print(result.key_points)
    print(result.confidence)
    print(f"Cost: ${result.tokens_used * 0.00000015}")  # GPT-4o pricing

asyncio.run(research())
```

### Council Orchestration (Multi-Agent Parallel Research)
```python
from src.council.orchestrator import CouncilOrchestrator
from src.council.aggregator import ResponseAggregator
from src.agents.gemini_agent import GeminiResearchAgent
from src.agents.openai_agent import OpenAIAgent
from src.agents.deepseek_agent import DeepSeekAgent
from src.models.schemas import ResearchDomain
from src.utils.output_manager import OutputManager
import asyncio

async def council_research():
    # Create all 3 agents
    agents = [
        GeminiResearchAgent(api_key="..."),
        OpenAIAgent(api_key="..."),
        DeepSeekAgent()  # Local - no API key!
    ]

    # Create council orchestrator
    council = CouncilOrchestrator(agents)

    # Run all agents in parallel (simultaneously!)
    responses = await council.research_all(
        query="What are the benefits of regular exercise?",
        domain=ResearchDomain.HEALTHCARE,
        max_tokens=500
    )

    # Aggregate and compare responses
    aggregator = ResponseAggregator()
    comparison = aggregator.aggregate(
        responses=responses,
        query="What are the benefits of regular exercise?",
        domain=ResearchDomain.HEALTHCARE
    )

    # Access aggregated results
    print(f"Successful agents: {comparison.successful_agents}/{comparison.total_agents}")
    print(f"Consensus points: {comparison.consensus_points}")
    print(f"Disagreements: {comparison.disagreement_points}")
    print(f"Total cost: ${comparison.total_cost:.6f}")

    # Save comparison result
    manager = OutputManager()
    manager.save_comparison(comparison)

asyncio.run(council_research())
```

**Key Benefits:**
- ⚡ **Parallel execution**: All 3 agents run simultaneously (~6-8 seconds total)
- 🤝 **Consensus detection**: Find where models agree
- ⚖️ **Disagreement analysis**: Identify where models differ
- 💰 **Cost tracking**: Track tokens and costs across all models
- 🛡️ **Graceful failures**: If one agent fails, others continue

## 🎓 Learning Resources

### Files with Educational Comments
- `src/models/schemas.py` - Pydantic models explained
- `src/agents/base_agent.py` - Abstract classes, OOP, async patterns
- `src/agents/gemini_agent.py` - Google Gemini integration
- `src/agents/openai_agent.py` - OpenAI AsyncOpenAI client
- `src/agents/deepseek_agent.py` - Local Ollama integration
- `src/council/orchestrator.py` - Parallel execution with asyncio.gather()
- `src/council/aggregator.py` - Response comparison and synthesis
- `src/utils/output_manager.py` - JSON persistence for outputs
- `tests/test_openai_connection.py` - OpenAI Responses API
- `tests/test_gemini_connection.py` - Gemini new SDK
- `tests/test_council.py` - Council integration tests
- `tests/README.md` - Comprehensive testing guide

### Key Files to Study
1. **schemas.py**: Data validation with Pydantic
2. **base_agent.py**: Abstraction, interfaces, async/await
3. **openai_agent.py**: AsyncOpenAI and structured responses
4. **deepseek_agent.py**: Local LLM inference with Ollama
5. **orchestrator.py**: Parallel multi-agent execution
6. **aggregator.py**: Response comparison and consensus
7. **test_council.py**: End-to-end integration testing

## 📊 Development Roadmap

### ✅ Phase 1: Foundation
- [x] Environment setup (pyproject.toml, .env)
- [x] Pydantic schemas and data models
- [x] Abstract base agent with async support
- [x] Single agent research (Gemini)

### ✅ Phase 2: Multi-Agent Architecture
- [x] Gemini 2.5 Flash agent (cloud)
- [x] GPT-4o agent (cloud)
- [x] DeepSeek-R1 agent (local via Ollama)
- [x] Comprehensive test coverage (85%+)
- [x] JSON output persistence

### ✅ Phase 3: Council Orchestration
- [x] Council orchestrator with asyncio.gather()
- [x] Parallel execution of all 3 agents
- [x] Response aggregation and comparison
- [x] Consensus/disagreement detection
- [x] Integration tests (100% passing)
- [x] ComparisonResult saving to JSON

### 🔮 Phase 4: Advanced Features (NEXT)
- [ ] Web search integration (Tavily)
- [ ] LangGraph state machine
- [ ] Domain-specific specialized prompts
- [ ] Streaming responses
- [ ] API endpoint (FastAPI)
- [ ] Advanced consensus algorithms (voting, weighted scoring)
- [ ] Caching layer for repeated queries

## 💡 Next Steps

You're ready for **Phase 4: Advanced Features**!

Recommended next tasks:
1. **Web Search Integration**: Add Tavily for real-time web search
2. **LangGraph**: Build state machine for complex workflows
3. **Specialized Prompts**: Domain-specific prompt engineering
4. **Streaming**: Implement streaming responses for better UX
5. **API**: Build FastAPI endpoint for production deployment

## 🔗 API Documentation

- [Google Gemini API](https://ai.google.dev/gemini-api/docs)
- [OpenAI API](https://platform.openai.com/docs)
- [Ollama Documentation](https://ollama.com)
- [Pydantic Documentation](https://docs.pydantic.dev)

## 📝 Notes

### Cost Comparison (per 1M tokens)
- **DeepSeek (local)**: $0.00 - FREE unlimited
- **Gemini 2.5 Flash**: $0.00 - Generous free tier (60 req/min)
- **GPT-4o**: ~$0.15 - Pay per token

### Model Characteristics
- **Gemini**: Fast, efficient, great for general queries
- **GPT-4o**: High quality, reliable, best for complex analysis
- **DeepSeek**: Local privacy, offline capable, no rate limits

### Architecture Highlights
- All agents implement async/await for parallel execution
- Comprehensive test coverage (85%+)
- Production-grade error handling
- All code heavily commented for learning

---

**Built with**: Python 3.12, Pydantic, OpenAI SDK, Google Genai SDK, Ollama
**Models**: Gemini 2.5 Flash, GPT-4o, DeepSeek-R1
**Project Type**: Learning project with production-grade patterns
