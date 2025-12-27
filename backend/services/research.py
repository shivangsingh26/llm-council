"""
Research Service - Business Logic Layer

This service wraps the llm_council SDK (src/) and provides high-level
research orchestration functionality for the API endpoints.

It handles:
- Agent initialization based on available API keys
- Research execution via CouncilOrchestrator
- Response aggregation
- File output management
"""

import os
from typing import List
from src.agents.openai_agent import OpenAIAgent
from src.agents.gemini_agent import GeminiResearchAgent
from src.agents.deepseek_agent import DeepSeekAgent
from src.agents.base_agent import BaseResearchAgent
from src.council.orchestrator import CouncilOrchestrator
from src.council.aggregator import ResponseAggregator
from src.utils.output_manager import OutputManager
from src.models.schemas import ResearchDomain, ComparisonResult


class ResearchService:
    """
    High-level research service that wraps the llm_council SDK

    This is the bridge between the API layer (FastAPI routes) and
    the SDK layer (src/ package).
    """

    def __init__(self):
        """Initialize the research service"""
        self.output_manager = OutputManager()

    def _create_agents(self) -> List[BaseResearchAgent]:
        """
        Create agents based on available API keys in environment

        Returns:
            List of initialized agents (may be empty if no API keys)

        Agents:
            - OpenAIAgent (GPT-4o) - requires OPENAI_API_KEY
            - GeminiResearchAgent (Gemini 2.5 Flash) - requires GEMINI_API_KEY
            - DeepSeekAgent (DeepSeek R1) - requires Ollama running locally
        """
        agents = []

        # OpenAI Agent (GPT-4o)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                agents.append(OpenAIAgent(api_key=openai_key))
                print("✅ OpenAI Agent (GPT-4o) initialized")
            except Exception as e:
                print(f"⚠️  OpenAI Agent failed to initialize: {e}")

        # Gemini Agent (Gemini 2.5 Flash)
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                agents.append(GeminiResearchAgent(api_key=gemini_key))
                print("✅ Gemini Agent (Gemini 2.5 Flash) initialized")
            except Exception as e:
                print(f"⚠️  Gemini Agent failed to initialize: {e}")

        # DeepSeek Agent (DeepSeek R1 via Ollama)
        try:
            deepseek = DeepSeekAgent()
            if deepseek.check_ollama_status():
                agents.append(deepseek)
                print("✅ DeepSeek Agent (Ollama) initialized")
            else:
                print("ℹ️  DeepSeek Agent skipped (Ollama not running)")
        except Exception as e:
            print(f"ℹ️  DeepSeek Agent skipped: {e}")

        return agents

    async def execute_research(
        self,
        query: str,
        domain: ResearchDomain,
        max_tokens: int = 500,
        depth_mode: str = "auto"
    ) -> ComparisonResult:
        """
        Execute research with all available agents using adaptive routing

        This is the main method called by the API endpoint.
        It orchestrates the entire research flow:
        1. Create agents
        2. Run research with adaptive routing (council + disagreement analysis)
        3. Route to Fast/Medium/Deep path based on disagreement
        4. Synthesize final answer
        5. Save results to file

        Args:
            query: Research question
            domain: Research domain (health, finance, etc.)
            max_tokens: Maximum tokens per agent response
            depth_mode: Routing mode ("auto", "fast", "medium", "deep")

        Returns:
            ComparisonResult with all agent responses, routing info, and analysis

        Raises:
            ValueError: If no agents are available
            Exception: If research execution fails
        """
        # Create agents
        agents = self._create_agents()

        if not agents:
            raise ValueError(
                "No agents available. Please configure at least one API key:\n"
                "- OPENAI_API_KEY for GPT-4o\n"
                "- GEMINI_API_KEY for Gemini 2.5 Flash\n"
                "- Or start Ollama for DeepSeek R1"
            )

        print(f"\n🔬 Starting research with {len(agents)} agent(s)")
        print(f"   Query: {query}")
        print(f"   Domain: {domain}")
        print(f"   Depth Mode: {depth_mode}")

        # Create aggregator and council with adaptive routing
        aggregator = ResponseAggregator()
        council = CouncilOrchestrator(agents, aggregator=aggregator)

        # Execute research with adaptive routing
        result = await council.research_with_routing(
            query=query,
            domain=domain,
            max_tokens=max_tokens,
            depth_mode=depth_mode
        )

        print(f"✅ Research complete")
        print(f"   Routing: {result['routing_decision'].upper()}")
        print(f"   Disagreement: {result.get('disagreement_score', 'N/A')}")

        # Build ComparisonResult from routing result
        # Extract valid responses (filter out None)
        valid_responses = {
            model: response
            for model, response in result['responses'].items()
            if response is not None
        }

        # Calculate agent counts
        total_agents = len(result['responses'])
        successful_agents = len(valid_responses)
        failed_agents = [
            model for model, response in result['responses'].items()
            if response is None
        ]

        # Calculate totals
        total_tokens = sum(r.tokens_used or 0 for r in valid_responses.values())

        # Calculate cost based on model pricing
        total_cost = 0.0
        PRICING = {
            "gpt-4o": 2.50,  # $2.50 per 1M tokens (combined input+output average)
            "gemini-2.5-flash": 0.075,  # $0.075 per 1M tokens
            "deepseek-r1:14b": 0.0,  # Local model (free)
        }

        for model_name, response in valid_responses.items():
            if response.tokens_used:
                price_per_1m = PRICING.get(model_name, 0.0)
                cost = (response.tokens_used / 1_000_000) * price_per_1m
                total_cost += cost

        # Create ComparisonResult
        comparison = ComparisonResult(
            query=query,
            domain=domain,
            responses=valid_responses,
            total_agents=total_agents,
            successful_agents=successful_agents,
            failed_agents=failed_agents,
            synthesized_answer=result.get('synthesized_answer', ''),
            consensus_points=result.get('consensus_points', []),
            disagreement_points=result.get('disagreement_points', []),
            reasoning_trace=result.get('reasoning_trace'),
            knowledge_gaps=result.get('knowledge_gaps', []),
            verification_needed=result.get('verification_needed', []),
            confidence_reasoning=result.get('confidence_reasoning'),
            total_tokens=total_tokens,
            total_cost=total_cost,
            # Phase 1 fields
            disagreement_score=result.get('disagreement_score'),
            routing_decision=result.get('routing_decision'),
            latency_breakdown=result.get('latency_breakdown')
        )

        print(f"   Total tokens: {comparison.total_tokens}")
        print(f"   Total cost: ${comparison.total_cost:.6f}")

        # Save to file (outputs/council_comparisons/{domain}/)
        file_path = self.output_manager.save_comparison(comparison)
        print(f"💾 Results saved to: {file_path}")

        return comparison

    def get_active_agent_count(self) -> int:
        """
        Get the number of currently available agents

        Returns:
            Number of agents that can be initialized
        """
        return len(self._create_agents())
