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
        max_tokens: int = 500
    ) -> ComparisonResult:
        """
        Execute research with all available agents

        This is the main method called by the API endpoint.
        It orchestrates the entire research flow:
        1. Create agents
        2. Run research in parallel via CouncilOrchestrator
        3. Aggregate responses
        4. Save results to file

        Args:
            query: Research question
            domain: Research domain (health, finance, etc.)
            max_tokens: Maximum tokens per agent response

        Returns:
            ComparisonResult with all agent responses and analysis

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

        # Create council orchestrator and run research in parallel
        council = CouncilOrchestrator(agents)
        responses = await council.research_all(
            query=query,
            domain=domain,
            max_tokens=max_tokens
        )

        print(f"✅ Received {len(responses)} responses")

        # Aggregate responses (now async for Master Synthesizer support)
        aggregator = ResponseAggregator()
        comparison = await aggregator.aggregate(
            responses=responses,
            query=query,
            domain=domain
        )

        print(f"✅ Aggregation complete")
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
