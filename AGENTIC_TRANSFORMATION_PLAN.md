# 🤖 Agentic LLM Council Transformation Plan
**From Rule-Based Aggregation to Intelligent Orchestration**

---

## 📊 Current State vs Target State

### Current Architecture (Rule-Based)
```
┌─────────────────────────────────────────────────────┐
│           CouncilOrchestrator                       │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│   │  GPT-4o  │  │  Gemini  │  │ DeepSeek │        │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│        │             │              │               │
│        └─────────────┴──────────────┘               │
│                      │                               │
│           ┌──────────▼──────────┐                   │
│           │  ResponseAggregator │                   │
│           │  (Rule-Based Logic) │                   │
│           │  - Simple synthesis │                   │
│           │  - No tools         │                   │
│           │  - No reasoning     │                   │
│           └─────────────────────┘                   │
└─────────────────────────────────────────────────────┘
```

**Limitations:**
- ❌ Simple string matching for consensus
- ❌ No deep reasoning about disagreements
- ❌ No tool use (web search, calculations, etc.)
- ❌ No multi-step reasoning or planning
- ❌ Static, linear flow

---

### Target Architecture (Agentic + LangGraph)
```
┌──────────────────────────────────────────────────────────────┐
│                    LangGraph Orchestrator                    │
│                  (State Machine + Reasoning)                 │
└────────┬─────────────────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────────────────┐
│  Phase 1: Planning (Reasoning Agent)                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  OpenAI o1/o3 Reasoning Model                          │  │
│  │  - Analyze query complexity                            │  │
│  │  - Decide which agents to use                          │  │
│  │  - Determine if tools are needed                       │  │
│  │  - Create research plan                                │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────────────────┐
│  Phase 2: Tool-Augmented Research (Worker Agents)           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  GPT-4o  │  │  Gemini  │  │ DeepSeek │  │  Claude  │   │
│  │  + Tools │  │  + Tools │  │  + Tools │  │  + Tools │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │              │              │          │
│       ├─────────────┴──────────────┴──────────────┘          │
│       │                                                       │
│  ┌────▼──────────────────────────────────────────────────┐  │
│  │ Shared Tool Suite:                                    │  │
│  │  • Web Search (Tavily API)                           │  │
│  │  • Wikipedia Search                                   │  │
│  │  • Calculator / Code Interpreter                     │  │
│  │  • Document Retrieval (RAG)                          │  │
│  │  • API Calls (custom integrations)                   │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────────────────┐
│  Phase 3: Intelligent Synthesis (Master Agent)              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  OpenAI o1/o3 Master Orchestrator                     │  │
│  │  - Reason about all responses                         │  │
│  │  - Identify deep consensus & conflicts                │  │
│  │  - Request clarifications if needed (iterative)       │  │
│  │  - Synthesize coherent final answer                   │  │
│  │  - Generate confidence scores with reasoning          │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────────────────┐
│  Phase 4: Quality Check & Verification (Optional)           │
│  - Fact-check against retrieved sources                     │
│  - Identify potential hallucinations                        │
│  - Generate citations and references                        │
└──────────────────────────────────────────────────────────────┘
```

**New Capabilities:**
- ✅ Deep reasoning with o1/o3 models
- ✅ Tool use for grounding in real data
- ✅ Multi-step, iterative research
- ✅ Dynamic agent selection
- ✅ State management with LangGraph
- ✅ Automatic quality checks
- ✅ Citation generation

---

## 🎯 Transformation Phases

### Phase A: LLM-Based Master Synthesizer (High Priority)
**Goal:** Replace rule-based aggregator with OpenAI o1/o3 reasoning model

**Estimated Time:** 4-6 hours

**Key Changes:**
1. Create `MasterSynthesizer` class using o1-mini or o3-mini
2. Feed all agent responses to the master for deep analysis
3. Use chain-of-thought reasoning to identify:
   - True consensus (semantic similarity, not string matching)
   - Meaningful disagreements (not superficial differences)
   - Knowledge gaps requiring more research
4. Generate natural, synthesized answer
5. Provide reasoning trace for transparency

---

### Phase B: Tool Integration (High Priority)
**Goal:** Augment agents with real-world tools for grounded research

**Estimated Time:** 6-8 hours

**Tools to Integrate:**
1. **Web Search** (Tavily API) - Real-time information
2. **Wikipedia** - Reliable reference data
3. **Calculator** - Mathematical computations
4. **Code Interpreter** - Execute Python for analysis
5. **Custom APIs** - Domain-specific integrations

**Implementation:**
- Use LangChain tool abstractions
- Implement tool calling for OpenAI/Gemini
- Create tool selection logic (when to use which tool)

---

### Phase C: LangGraph Integration (Medium Priority)
**Goal:** Transform into stateful, multi-step agentic system

**Estimated Time:** 8-10 hours

**LangGraph Features:**
1. **State Management** - Track research progress
2. **Conditional Flows** - Different paths based on query type
3. **Iterative Refinement** - Request more info if needed
4. **Human-in-the-Loop** - Optional user confirmation steps
5. **Checkpointing** - Resume long-running research

---

### Phase D: Automation Opportunities (Low Priority)
**Goal:** Identify and automate repetitive workflows

**Estimated Time:** 4-6 hours

**Automation Ideas:**
1. Auto-categorize queries into domains
2. Auto-select optimal agents based on query type
3. Auto-generate follow-up questions
4. Auto-fact-check with external sources
5. Auto-generate citations and references
6. Scheduled research jobs (cron-like)

---

## 📋 Detailed Implementation Plan

### **PHASE A: LLM-Based Master Synthesizer**

#### Step 1: Create Master Synthesizer Agent
**File:** `src/council/master_synthesizer.py`

**Core Responsibilities:**
1. Receive all agent responses
2. Use o1-mini for deep reasoning
3. Generate synthesis with chain-of-thought
4. Provide confidence scores with explanations

**Key Implementation Details:**

```python
from openai import AsyncOpenAI
from typing import Dict, List
from src.models.schemas import ResearchResponse, ComparisonResult

class MasterSynthesizer:
    """
    Master orchestrator using OpenAI o1/o3 reasoning models.

    The master agent:
    1. Receives responses from all worker agents
    2. Reasons deeply about consensus and conflicts
    3. Synthesizes a coherent, well-reasoned answer
    4. Provides transparency through reasoning traces
    """

    def __init__(self, api_key: str, model: str = "o1-mini"):
        """
        Initialize master synthesizer.

        Models:
        - o1-mini: Fast reasoning ($3/$12 per 1M tokens)
        - o1: Deep reasoning ($15/$60 per 1M tokens)
        - o3-mini: Latest reasoning model (pricing TBD)
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def synthesize(
        self,
        query: str,
        responses: Dict[str, ResearchResponse],
        context: Optional[Dict] = None
    ) -> ComparisonResult:
        """
        Synthesize responses using advanced reasoning.

        Args:
            query: Original research question
            responses: Dict of model_name -> ResearchResponse
            context: Optional additional context (tools used, etc.)

        Returns:
            ComparisonResult with deep synthesis
        """

        # Build comprehensive prompt for reasoning model
        prompt = self._build_synthesis_prompt(query, responses, context)

        # Call o1/o3 reasoning model
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            # Note: o1 models don't support temperature/top_p
            # They use internal reasoning optimization
        )

        # Parse structured output
        synthesis_text = response.choices[0].message.content
        parsed = self._parse_synthesis(synthesis_text)

        # Build ComparisonResult
        return ComparisonResult(
            query=query,
            domain=list(responses.values())[0].domain,
            responses=responses,
            total_agents=len(responses),
            successful_agents=len(responses),
            failed_agents=[],
            consensus_points=parsed["consensus_points"],
            disagreement_points=parsed["disagreement_points"],
            confidence_range=parsed["confidence_range"],
            synthesized_answer=parsed["synthesized_answer"],
            reasoning_trace=parsed["reasoning_trace"],  # NEW!
            total_tokens=self._calculate_tokens(responses, response),
            total_cost=self._calculate_cost(responses, response)
        )

    def _build_synthesis_prompt(
        self,
        query: str,
        responses: Dict[str, ResearchResponse],
        context: Optional[Dict]
    ) -> str:
        """
        Build comprehensive prompt for reasoning model.
        """

        prompt_parts = [
            "# Research Synthesis Task",
            f"\n## Original Query\n{query}",
            "\n## Agent Responses"
        ]

        # Add each agent's response
        for model_name, response in responses.items():
            prompt_parts.append(f"\n### {model_name}")
            prompt_parts.append(f"**Answer:** {response.answer}")
            prompt_parts.append(f"**Confidence:** {response.confidence.value}")
            prompt_parts.append(f"**Key Points:**")
            for point in response.key_points:
                prompt_parts.append(f"  - {point}")

        # Add context if available
        if context and context.get("tools_used"):
            prompt_parts.append("\n## Tools Used")
            for tool, result in context["tools_used"].items():
                prompt_parts.append(f"- {tool}: {result}")

        # Add instructions
        prompt_parts.append("""
## Your Task

As a master research synthesizer, deeply analyze all agent responses and provide:

1. **Consensus Analysis**
   - Identify points where agents genuinely agree (semantic agreement, not just word matching)
   - Explain WHY these points represent consensus
   - Rank by importance and confidence

2. **Disagreement Analysis**
   - Identify meaningful disagreements (not superficial differences)
   - Explain the root cause of each disagreement
   - Assess which perspective is more credible (with reasoning)

3. **Knowledge Gaps**
   - Identify areas where agents lack information
   - Note if additional research or tools are needed

4. **Synthesized Answer**
   - Provide a coherent, well-reasoned synthesis
   - Integrate insights from all agents
   - Resolve disagreements with clear reasoning
   - Add your own insights where appropriate

5. **Confidence Assessment**
   - Overall confidence level (low/medium/high/very_high)
   - Reasoning for this confidence score
   - Key uncertainties or limitations

6. **Citations & Verification**
   - Flag claims that need verification
   - Suggest sources for fact-checking

## Output Format (JSON)

```json
{
  "consensus_points": [
    "Point 1 with explanation...",
    "Point 2 with explanation..."
  ],
  "disagreement_points": [
    "Disagreement 1 with analysis...",
    "Disagreement 2 with resolution..."
  ],
  "knowledge_gaps": [
    "Gap 1...",
    "Gap 2..."
  ],
  "synthesized_answer": "Your well-reasoned synthesis here...",
  "confidence_range": "high",
  "confidence_reasoning": "Explanation for confidence score...",
  "verification_needed": [
    "Claim 1 to verify...",
    "Claim 2 to verify..."
  ],
  "reasoning_trace": "Your internal reasoning process..."
}
```

Think deeply, reason carefully, and provide your best synthesis.
""")

        return "\n".join(prompt_parts)

    def _parse_synthesis(self, synthesis_text: str) -> Dict:
        """
        Parse structured output from reasoning model.

        Handles both JSON and natural language outputs.
        """
        # Try to extract JSON
        try:
            import json
            import re

            # Find JSON block
            json_match = re.search(r'```json\n(.*?)\n```', synthesis_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(1))
                return parsed
            else:
                # Try direct JSON parse
                parsed = json.loads(synthesis_text)
                return parsed

        except json.JSONDecodeError:
            # Fallback: parse natural language
            # (implement NLP parsing here)
            return self._parse_natural_language(synthesis_text)

    def _parse_natural_language(self, text: str) -> Dict:
        """
        Fallback parser for natural language output.
        """
        # Simple section extraction
        # In production, use more robust NLP
        return {
            "consensus_points": [],
            "disagreement_points": [],
            "synthesized_answer": text,
            "confidence_range": "medium",
            "reasoning_trace": text
        }
```

---

#### Step 2: Update ResponseAggregator to use MasterSynthesizer
**File:** `src/council/aggregator.py`

**Changes:**
- Keep backward compatibility (flag to use old vs new)
- Add `use_master_synthesizer: bool = True` parameter
- If True, delegate to `MasterSynthesizer`
- If False, use old rule-based logic

```python
class ResponseAggregator:
    def __init__(self, use_master_synthesizer: bool = True):
        self.use_master = use_master_synthesizer
        if use_master:
            self.master = MasterSynthesizer(
                api_key=os.getenv("OPENAI_API_KEY"),
                model="o1-mini"  # Fast reasoning
            )

    async def aggregate(self, ...):
        if self.use_master:
            return await self.master.synthesize(query, responses)
        else:
            # Old rule-based logic
            return self._old_aggregate(...)
```

---

#### Step 3: Update Schema for New Fields
**File:** `src/models/schemas.py`

**Add new fields to `ComparisonResult`:**
```python
class ComparisonResult(BaseModel):
    # ... existing fields ...

    # NEW: Advanced reasoning fields
    reasoning_trace: Optional[str] = None
    knowledge_gaps: List[str] = Field(default_factory=list)
    verification_needed: List[str] = Field(default_factory=list)
    confidence_reasoning: Optional[str] = None
```

---

#### Step 4: Update Frontend to Display Reasoning
**Files:**
- `frontend/components/research/results-display.tsx`
- Add new sections for:
  - Reasoning trace (collapsible)
  - Knowledge gaps
  - Verification needed

---

### **PHASE B: Tool Integration**

#### Step 1: Setup Tool Infrastructure
**File:** `src/tools/__init__.py`

**Install Dependencies:**
```bash
pip install langchain langchain-community tavily-python wikipedia
```

---

#### Step 2: Implement Tool Suite
**File:** `src/tools/tool_suite.py`

```python
from langchain.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import StructuredTool
import os

class ToolSuite:
    """
    Collection of tools available to research agents.
    """

    def __init__(self):
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> List[Tool]:
        tools = []

        # 1. Web Search (Tavily)
        if os.getenv("TAVILY_API_KEY"):
            tools.append(
                TavilySearchResults(
                    api_key=os.getenv("TAVILY_API_KEY"),
                    max_results=5,
                    search_depth="advanced"
                )
            )

        # 2. Wikipedia
        tools.append(
            Tool(
                name="Wikipedia",
                func=WikipediaAPIWrapper().run,
                description="Search Wikipedia for factual information"
            )
        )

        # 3. Calculator
        tools.append(
            Tool(
                name="Calculator",
                func=self._calculator,
                description="Perform mathematical calculations"
            )
        )

        # 4. Code Interpreter (Python REPL)
        tools.append(
            Tool(
                name="PythonREPL",
                func=self._python_repl,
                description="Execute Python code for data analysis"
            )
        )

        return tools

    def _calculator(self, expression: str) -> str:
        """Safe calculator using Python's eval"""
        try:
            # Only allow safe math operations
            allowed = {
                '__builtins__': {},
                'abs': abs, 'round': round,
                'pow': pow, 'sum': sum,
                'min': min, 'max': max
            }
            result = eval(expression, allowed, {})
            return str(result)
        except Exception as e:
            return f"Error: {e}"

    def _python_repl(self, code: str) -> str:
        """Execute Python code in sandboxed environment"""
        # Use restricted execution environment
        # See: https://docs.python.org/3/library/functions.html#exec
        try:
            import io
            import sys

            # Capture output
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()

            # Execute code
            exec(code, {'__builtins__': __builtins__})

            # Get output
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout

            return output
        except Exception as e:
            sys.stdout = old_stdout
            return f"Error: {e}"

    def get_tools_for_agent(self, agent_type: str) -> List[Tool]:
        """
        Get relevant tools for specific agent type.

        Different agents may need different tool subsets.
        """
        # All agents get all tools for now
        # Later: customize based on agent capabilities
        return self.tools
```

---

#### Step 3: Update Agents to Use Tools
**File:** `src/agents/openai_agent.py`

**Add tool calling capability:**
```python
from src.tools.tool_suite import ToolSuite

class OpenAIAgent(BaseResearchAgent):
    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        super().__init__(api_key, model_name)
        self.tool_suite = ToolSuite()
        self.tools = self.tool_suite.get_tools_for_agent("openai")

    async def research_async(self, query: str, ...):
        # Convert tools to OpenAI function calling format
        functions = self._tools_to_functions(self.tools)

        # Call model with function calling
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[...],
            functions=functions,
            function_call="auto"
        )

        # Handle function calls
        while response.choices[0].finish_reason == "function_call":
            function_call = response.choices[0].message.function_call
            result = await self._execute_tool(function_call)

            # Continue conversation with tool result
            response = await self.client.chat.completions.create(...)

        # Parse final answer
        return self._parse_response(...)
```

---

#### Step 4: Track Tool Usage
**Update schemas to include tool usage:**
```python
class ResearchResponse(BaseModel):
    # ... existing fields ...

    # NEW: Tool usage tracking
    tools_used: Optional[List[Dict]] = None
    tool_results: Optional[Dict[str, str]] = None
```

---

### **PHASE C: LangGraph Integration**

#### Step 1: Install LangGraph
```bash
pip install langgraph langchain-openai
```

---

#### Step 2: Define State Schema
**File:** `src/langgraph/state.py`

```python
from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import add_messages
from src.models.schemas import ResearchResponse

class ResearchState(TypedDict):
    """
    State for the research graph.

    LangGraph manages this state across all nodes.
    """
    # Input
    query: str
    domain: str
    max_tokens: int

    # Planning
    research_plan: str
    agents_to_use: List[str]
    tools_needed: List[str]

    # Research phase
    messages: Annotated[List, add_messages]  # Conversation history
    agent_responses: Dict[str, ResearchResponse]
    tool_results: Dict[str, str]

    # Synthesis
    synthesis: str
    reasoning_trace: str
    confidence: str

    # Quality check
    verification_status: str
    citations: List[str]

    # Control flow
    iteration_count: int
    needs_more_research: bool
    error: Optional[str]
```

---

#### Step 3: Define Graph Nodes
**File:** `src/langgraph/nodes.py`

```python
from langgraph.graph import StateGraph, END
from src.langgraph.state import ResearchState

# Node 1: Planning
async def planning_node(state: ResearchState) -> ResearchState:
    """
    Planner agent decides research strategy.

    Uses o1-mini to:
    - Analyze query complexity
    - Select which agents to use
    - Determine which tools are needed
    """
    planner = MasterSynthesizer(model="o1-mini")

    plan_prompt = f"""
    Query: {state['query']}
    Domain: {state['domain']}

    Create a research plan:
    1. Which agents should research this? (gpt-4o, gemini, deepseek, claude)
    2. Which tools are needed? (web_search, wikipedia, calculator, etc.)
    3. What are the key questions to answer?
    4. Any special considerations?

    Output JSON with: agents_to_use, tools_needed, research_plan
    """

    # Get plan
    plan = await planner.reason(plan_prompt)

    # Update state
    state['research_plan'] = plan['research_plan']
    state['agents_to_use'] = plan['agents_to_use']
    state['tools_needed'] = plan['tools_needed']

    return state

# Node 2: Research Execution
async def research_node(state: ResearchState) -> ResearchState:
    """
    Execute research with selected agents.
    """
    responses = {}

    for agent_name in state['agents_to_use']:
        agent = create_agent(agent_name)
        response = await agent.research_async(
            query=state['query'],
            domain=state['domain'],
            tools=state['tools_needed']
        )
        responses[agent_name] = response

    state['agent_responses'] = responses
    return state

# Node 3: Master Synthesis
async def synthesis_node(state: ResearchState) -> ResearchState:
    """
    Master agent synthesizes all responses.
    """
    master = MasterSynthesizer(model="o1")

    result = await master.synthesize(
        query=state['query'],
        responses=state['agent_responses'],
        context={
            'plan': state['research_plan'],
            'tools_used': state['tool_results']
        }
    )

    state['synthesis'] = result.synthesized_answer
    state['reasoning_trace'] = result.reasoning_trace
    state['confidence'] = result.confidence_range

    # Check if more research is needed
    state['needs_more_research'] = result.knowledge_gaps and state['iteration_count'] < 2

    return state

# Node 4: Quality Check
async def quality_check_node(state: ResearchState) -> ResearchState:
    """
    Verify facts and generate citations.
    """
    # Use web search to verify key claims
    verifier = FactVerifier()

    verification = await verifier.verify(
        synthesis=state['synthesis'],
        claims_to_check=state.get('verification_needed', [])
    )

    state['verification_status'] = verification['status']
    state['citations'] = verification['citations']

    return state
```

---

#### Step 4: Build the Graph
**File:** `src/langgraph/graph.py`

```python
from langgraph.graph import StateGraph, END

def create_research_graph():
    """
    Build the LangGraph research workflow.
    """

    # Create graph
    workflow = StateGraph(ResearchState)

    # Add nodes
    workflow.add_node("planning", planning_node)
    workflow.add_node("research", research_node)
    workflow.add_node("synthesis", synthesis_node)
    workflow.add_node("quality_check", quality_check_node)

    # Define edges (control flow)
    workflow.set_entry_point("planning")

    workflow.add_edge("planning", "research")
    workflow.add_edge("research", "synthesis")

    # Conditional edge: iterate or finish
    workflow.add_conditional_edges(
        "synthesis",
        lambda state: "research" if state['needs_more_research'] else "quality_check"
    )

    workflow.add_edge("quality_check", END)

    # Compile
    app = workflow.compile()

    return app
```

---

#### Step 5: Use Graph in Backend
**File:** `backend/services/research.py`

**Replace current orchestrator:**
```python
from src.langgraph.graph import create_research_graph

class ResearchService:
    def __init__(self):
        self.graph = create_research_graph()

    async def execute_research(self, query, domain, max_tokens):
        # Initialize state
        initial_state = {
            "query": query,
            "domain": domain,
            "max_tokens": max_tokens,
            "iteration_count": 0
        }

        # Run graph
        final_state = await self.graph.ainvoke(initial_state)

        # Convert to ComparisonResult
        return self._state_to_result(final_state)
```

---

### **PHASE D: Automation Opportunities**

#### 1. Auto-Domain Classification
**File:** `src/automation/domain_classifier.py`

```python
class DomainClassifier:
    """
    Automatically classify query into domain.
    """

    async def classify(self, query: str) -> ResearchDomain:
        # Use fast LLM (gpt-4o-mini) for classification
        prompt = f"""
        Classify this query into one domain:
        - healthcare
        - sports
        - finance
        - shopping

        Query: {query}

        Output only the domain name.
        """

        # Call LLM
        result = await self.llm.ainvoke(prompt)

        return ResearchDomain(result.strip().lower())
```

---

#### 2. Auto-Agent Selection
**Already covered in LangGraph planning node!**

---

#### 3. Auto-Follow-Up Questions
**File:** `src/automation/follow_up_generator.py`

```python
class FollowUpGenerator:
    """
    Generate clarifying questions when synthesis is uncertain.
    """

    async def generate(self, synthesis: ComparisonResult) -> List[str]:
        if synthesis.confidence_range in ["low", "medium"]:
            prompt = f"""
            The research has {synthesis.confidence_range} confidence.
            Knowledge gaps: {synthesis.knowledge_gaps}

            Generate 3 follow-up questions to improve confidence.
            """

            questions = await self.llm.ainvoke(prompt)
            return questions.split('\n')

        return []
```

---

#### 4. Auto-Citation Generation
**File:** `src/automation/citation_generator.py`

```python
class CitationGenerator:
    """
    Automatically generate citations for claims.
    """

    async def generate_citations(
        self,
        synthesis: str,
        tool_results: Dict[str, str]
    ) -> List[str]:
        """
        Extract URLs and facts from tool results,
        match them to claims in synthesis,
        generate proper citations.
        """

        citations = []

        # Extract URLs from web search results
        if "web_search" in tool_results:
            urls = self._extract_urls(tool_results["web_search"])

            for url in urls:
                # Generate citation
                citation = await self._create_citation(url)
                citations.append(citation)

        return citations
```

---

#### 5. Scheduled Research Jobs
**File:** `src/automation/scheduler.py`

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class ResearchScheduler:
    """
    Schedule recurring research queries.

    Use cases:
    - Daily market summaries
    - Weekly health tips
    - Monthly financial reports
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def schedule_research(
        self,
        query: str,
        domain: str,
        cron: str,  # "0 9 * * *" = 9 AM daily
        callback: Callable
    ):
        """
        Schedule a recurring research query.
        """

        async def job():
            result = await execute_research(query, domain)
            await callback(result)

        self.scheduler.add_job(job, 'cron', **parse_cron(cron))

    def start(self):
        self.scheduler.start()
```

---

## 🧪 Testing Strategy

### Unit Tests
```bash
# Test master synthesizer
pytest tests/test_master_synthesizer.py

# Test tools
pytest tests/test_tools.py

# Test LangGraph nodes
pytest tests/test_langgraph_nodes.py
```

---

### Integration Tests
```bash
# Test full pipeline
pytest tests/test_full_pipeline.py

# Test with real APIs (requires keys)
pytest tests/test_with_real_apis.py --real-apis
```

---

### Performance Tests
```python
# Measure latency improvements
# Compare old vs new aggregator
# Track token usage and costs
```

---

## 📊 Success Metrics

### Quality Metrics
- [ ] Synthesis coherence score (human eval)
- [ ] Consensus accuracy (vs ground truth)
- [ ] Citation accuracy
- [ ] Fact verification pass rate

### Performance Metrics
- [ ] Average latency per research
- [ ] Token usage per research
- [ ] Cost per research
- [ ] Tool call success rate

### User Experience Metrics
- [ ] User satisfaction score
- [ ] Reasoning trace helpfulness
- [ ] Iteration rate (how often needs more research)

---

## 💰 Cost Estimation

### Per Research Query (Average)

**Current System:**
- GPT-4o: ~500 tokens × $0.15/1M = $0.000075
- Gemini: Free
- DeepSeek: Free (local)
- **Total: ~$0.000075**

**New System:**
- Planning (o1-mini): ~200 tokens × $3/1M = $0.0006
- Worker agents (3 × 500 tokens): ~$0.000225
- Master synthesis (o1): ~1000 tokens × $15/1M = $0.015
- Tools (Tavily): ~5 searches × $0.001 = $0.005
- **Total: ~$0.021 per query**

**Cost increase: ~280x**

**But value increase:**
- Much higher quality synthesis
- Grounded in real-time data
- Deep reasoning and verification
- Multi-step refinement

**Optimization options:**
- Use o1-mini instead of o1 for synthesis (reduce to $0.003)
- Cache tool results
- Skip planning for simple queries
- **Optimized total: ~$0.008 per query** (still 100x better quality)

---

## 🗓️ Implementation Timeline

### Week 1: Master Synthesizer
- Days 1-2: Implement MasterSynthesizer class
- Days 3-4: Update aggregator and schemas
- Day 5: Test and iterate

### Week 2: Tool Integration
- Days 1-2: Setup tool infrastructure
- Days 3-4: Update agents for tool calling
- Day 5: Test tools end-to-end

### Week 3: LangGraph Integration
- Days 1-2: Define state and nodes
- Days 3-4: Build and test graph
- Day 5: Integrate with backend

### Week 4: Automation & Polish
- Days 1-2: Implement automations
- Days 3-4: Frontend updates for new features
- Day 5: End-to-end testing and docs

---

## 🚀 Quick Start (After Implementation)

```bash
# 1. Install new dependencies
pip install langgraph langchain tavily-python

# 2. Add new API keys to .env
echo "TAVILY_API_KEY=your_key" >> .env

# 3. Run migration
python scripts/migrate_to_langgraph.py

# 4. Start servers
./start-all.sh

# 5. Test new features
curl -X POST http://localhost:8000/api/research \
  -d '{"query": "Latest AI news", "use_master": true, "use_tools": true}'
```

---

## 📚 Key Files Reference

### New Files to Create
| File | Purpose |
|------|---------|
| `src/council/master_synthesizer.py` | LLM-based master orchestrator |
| `src/tools/tool_suite.py` | Tool collection |
| `src/langgraph/state.py` | State schema |
| `src/langgraph/nodes.py` | Graph nodes |
| `src/langgraph/graph.py` | Graph builder |
| `src/automation/domain_classifier.py` | Auto domain classification |
| `src/automation/citation_generator.py` | Auto citation generation |
| `src/automation/scheduler.py` | Scheduled research |

### Files to Modify
| File | Changes |
|------|---------|
| `src/council/aggregator.py` | Add master synthesizer option |
| `src/agents/*.py` | Add tool calling |
| `src/models/schemas.py` | Add new fields |
| `backend/services/research.py` | Use LangGraph |
| `frontend/components/research/results-display.tsx` | Show reasoning trace |

---

## 🎯 Next Steps

1. **Review this plan** - Discuss priorities and scope
2. **Decide on phases** - Which to implement first?
3. **Setup API keys** - Tavily, OpenAI (o1 access)
4. **Start with Phase A** - Master synthesizer (highest impact)
5. **Iterate based on feedback** - Add features incrementally

---

**Ready to build the future of LLM orchestration?** 🚀

Let me know which phase you want to start with!
