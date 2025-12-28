"""
Council Orchestrator
===================
Coordinates multiple AI agents to conduct parallel research.

Learning Points:
- asyncio.gather() for parallel execution
- Multiple LLM providers working together
- Error handling in concurrent operations
- Performance optimization with async
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import time

from src.agents.base_agent import BaseResearchAgent
from src.models.schemas import ResearchResponse, ResearchDomain
from src.council.disagreement_analyzer import DisagreementAnalyzer
from src.council.adaptive_router import AdaptiveRouter


class CouncilOrchestrator:
    """
    Orchestrates multiple research agents to work in parallel.

    The orchestrator:
    1. Takes a query and runs it through all agents simultaneously
    2. Collects responses from each agent
    3. Handles failures gracefully (if one agent fails, others continue)
    4. Returns all responses for comparison/aggregation

    Example:
        from src.agents.gemini_agent import GeminiAgent
        from src.agents.openai_agent import OpenAIAgent

        # Create council
        council = CouncilOrchestrator([
            GeminiAgent(api_key="..."),
            OpenAIAgent(api_key="...")
        ])

        # Run parallel research
        results = await council.research_all(
            query="What are the benefits of exercise?",
            domain=ResearchDomain.HEALTHCARE
        )

        # results is a dict: {"gemini-2.5-flash": ResearchResponse, "gpt-4o": ResearchResponse}
    """

    def __init__(self, agents: List[BaseResearchAgent], aggregator=None):
        """
        Initialize the council with a list of agents.

        Args:
            agents: List of research agents (must inherit from BaseResearchAgent)
            aggregator: Optional ResponseAggregator for synthesis

        Raises:
            ValueError: If no agents provided or agents list is empty
        """
        if not agents or len(agents) == 0:
            raise ValueError("Council must have at least one agent")

        self.agents = agents
        self.agent_count = len(agents)
        self.aggregator = aggregator

        # Initialize disagreement analyzer for Phase 1
        self.disagreement_analyzer = DisagreementAnalyzer()

        # Initialize adaptive router for Phase 1
        self.router = AdaptiveRouter(aggregator=aggregator)

        print(f"✓ CouncilOrchestrator initialized with {self.agent_count} agents:")
        for agent in agents:
            print(f"   • {agent.model_name}")
        print(f"✓ Adaptive router enabled (Fast/Medium/Deep paths)")

    async def research_all(
        self,
        query: str,
        domain: ResearchDomain,
        max_tokens: Optional[int] = 500
    ) -> Dict[str, ResearchResponse]:
        """
        Run research query through all agents in parallel.

        Args:
            query: Research question
            domain: Research domain (sports, finance, shopping, healthcare)
            max_tokens: Maximum tokens per response

        Returns:
            Dict mapping model name to ResearchResponse
            Format: {"model-name": ResearchResponse, ...}

        Note: Uses asyncio.gather() for parallel execution!
              All agents run simultaneously, not sequentially.
        """

        print(f"\n{'='*70}")
        print(f"🏛️  COUNCIL RESEARCH SESSION")
        print(f"{'='*70}")
        print(f"📋 Query: {query}")
        print(f"📂 Domain: {domain.value}")
        print(f"👥 Agents: {self.agent_count}")
        print(f"⚡ Mode: PARALLEL (all agents run simultaneously)")
        print(f"{'='*70}\n")

        start_time = datetime.now()

        # Create tasks for all agents
        # Each task is an async call to research_async()
        tasks = []
        for agent in self.agents:
            task = self._research_with_agent(agent, query, domain, max_tokens)
            tasks.append(task)

        # Run all tasks in parallel using asyncio.gather()
        # return_exceptions=True ensures one failure doesn't stop others
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results into a dictionary
        responses = {}
        for agent, result in zip(self.agents, results):
            model_name = agent.model_name

            if isinstance(result, Exception):
                # Agent failed - log error but continue
                print(f"❌ [{model_name}] Failed: {result}")
                responses[model_name] = None
            else:
                # Agent succeeded
                print(f"✅ [{model_name}] Completed successfully")
                responses[model_name] = result

        # Calculate total time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Summary
        successful = sum(1 for r in responses.values() if r is not None)
        failed = self.agent_count - successful

        print(f"\n{'='*70}")
        print(f"📊 COUNCIL RESEARCH COMPLETE")
        print(f"{'='*70}")
        print(f"✅ Successful: {successful}/{self.agent_count}")
        if failed > 0:
            print(f"❌ Failed: {failed}/{self.agent_count}")
        print(f"⏱️  Total time: {duration:.2f}s (parallel execution)")
        print(f"{'='*70}\n")

        return responses

    async def research_with_routing(
        self,
        query: str,
        domain: ResearchDomain,
        max_tokens: Optional[int] = 500,
        depth_mode: str = "auto"
    ) -> Dict:
        """
        Run research with disagreement analysis and adaptive routing (Phase 1).

        This method:
        1. Runs council in parallel
        2. Analyzes disagreement between responses
        3. Routes to appropriate processing path (FAST/MEDIUM/DEEP)
        4. Executes path-specific synthesis

        Args:
            query: Research question
            domain: Research domain
            max_tokens: Maximum tokens per response
            depth_mode: "auto" (use disagreement score) or "fast"/"medium"/"deep" (override)

        Returns:
            Dict with:
                - responses: Dict[str, ResearchResponse]
                - disagreement_score: float (0.0-1.0)
                - disagreement_details: Dict with analysis breakdown
                - routing_decision: str ("fast", "medium", or "deep")
                - latency_breakdown: Dict with timing information
                - synthesized_answer: str (from router execution)
                - consensus_points: List[str]
                - disagreement_points: List[str]
        """
        print(f"\n{'='*70}")
        print(f"🏛️  COUNCIL RESEARCH WITH ADAPTIVE ROUTING")
        print(f"{'='*70}\n")

        overall_start = time.time()

        # Step 1: Execute council (parallel)
        council_start = time.time()
        responses = await self.research_all(query, domain, max_tokens)
        council_duration = (time.time() - council_start) * 1000

        # Filter out None responses (failed agents)
        valid_responses = {
            model: response
            for model, response in responses.items()
            if response is not None
        }

        if len(valid_responses) < 2:
            print("⚠️  Warning: Fewer than 2 valid responses, skipping routing")
            return {
                "responses": responses,
                "disagreement_score": 0.0,  # No disagreement with single agent
                "disagreement_details": {"explanation": "Single agent - no disagreement possible"},
                "routing_decision": "unknown",
                "latency_breakdown": {
                    "council_phase_ms": int(council_duration),
                    "disagreement_analysis_ms": 0,
                    "judge_phase_ms": 0,
                    "total_ms": int((time.time() - overall_start) * 1000)
                },
                "synthesized_answer": "Insufficient valid responses",
                "consensus_points": [],
                "disagreement_points": []
            }

        # Step 2: Analyze disagreement
        analysis_start = time.time()
        disagreement_result = await self.disagreement_analyzer.calculate_disagreement(
            valid_responses
        )
        analysis_duration = (time.time() - analysis_start) * 1000
        score = disagreement_result["score"]

        # Step 3: Determine routing path
        path = self.router.determine_path(score, user_preference=depth_mode)

        # Step 4: Execute appropriate path
        router_result = await self.router.execute_path(
            path=path,
            council_responses=valid_responses,
            disagreement_score=score,
            disagreement_details=disagreement_result["details"],
            query=query,
            domain=domain.value if hasattr(domain, 'value') else domain
        )
        judge_duration = router_result.get("judge_phase_ms", 0)

        # Step 5: Calculate total time
        total_duration = (time.time() - overall_start) * 1000

        # Step 6: Display routing information
        print(f"\n{'='*70}")
        print(f"📊 ADAPTIVE ROUTING RESULTS")
        print(f"{'='*70}")
        print(f"Disagreement Score: {score:.3f}")
        print(f"Routing Decision: {path.value.upper()}")
        print(f"Explanation: {disagreement_result['explanation']}")
        print(f"\nLatency Breakdown:")
        print(f"  • Council phase: {council_duration:.0f}ms")
        print(f"  • Disagreement analysis: {analysis_duration:.0f}ms")
        print(f"  • Judge phase ({path.value}): {judge_duration:.0f}ms")
        print(f"  • Total: {total_duration:.0f}ms")
        print(f"{'='*70}\n")

        return {
            "responses": responses,
            "disagreement_score": score,
            "disagreement_details": disagreement_result["details"],
            "routing_decision": path.value,
            "latency_breakdown": {
                "council_phase_ms": int(council_duration),
                "disagreement_analysis_ms": int(analysis_duration),
                "judge_phase_ms": int(judge_duration),
                "total_ms": int(total_duration)
            },
            "explanation": disagreement_result["explanation"],
            "synthesized_answer": router_result.get("synthesized_answer", ""),
            "consensus_points": router_result.get("consensus_points", []),
            "disagreement_points": router_result.get("disagreement_points", []),
            "reasoning_trace": router_result.get("reasoning_trace"),
            "knowledge_gaps": router_result.get("knowledge_gaps", []),
            "verification_needed": router_result.get("verification_needed", []),
            "confidence_reasoning": router_result.get("confidence_reasoning"),
            "synthesis_mode": router_result.get("synthesis_mode")
        }

    async def _research_with_agent(
        self,
        agent: BaseResearchAgent,
        query: str,
        domain: ResearchDomain,
        max_tokens: int
    ) -> ResearchResponse:
        """
        Internal helper to run research with a single agent.

        Wraps agent.research_async() to add error context.

        Args:
            agent: The research agent
            query: Research question
            domain: Research domain
            max_tokens: Maximum tokens

        Returns:
            ResearchResponse from the agent

        Raises:
            Exception: If agent fails (caught by gather with return_exceptions=True)
        """
        try:
            result = await agent.research_async(query, domain, max_tokens)
            return result
        except Exception as e:
            # Re-raise with agent context
            raise Exception(f"[{agent.model_name}] {str(e)}") from e

    def get_agent_models(self) -> List[str]:
        """
        Get list of model names in this council.

        Returns:
            List of model names (e.g., ["gemini-2.5-flash", "gpt-4o", "deepseek-r1:14b"])
        """
        return [agent.model_name for agent in self.agents]


# Example usage and testing
if __name__ == "__main__":
    """
    Example of using the Council Orchestrator.

    Run: python -m src.council.orchestrator
    """
    import os
    from dotenv import load_dotenv
    from src.agents.gemini_agent import GeminiResearchAgent
    from src.agents.openai_agent import OpenAIAgent

    load_dotenv()

    async def demo():
        # Create agents
        agents = []

        if os.getenv("GEMINI_API_KEY"):
            agents.append(GeminiResearchAgent(api_key=os.getenv("GEMINI_API_KEY")))

        if os.getenv("OPENAI_API_KEY"):
            agents.append(OpenAIAgent(api_key=os.getenv("OPENAI_API_KEY")))

        if not agents:
            print("❌ No API keys found. Set GEMINI_API_KEY or OPENAI_API_KEY")
            return

        # Create council
        council = CouncilOrchestrator(agents)

        # Run research
        results = await council.research_all(
            query="What are the key benefits of regular exercise?",
            domain=ResearchDomain.HEALTHCARE
        )

        # Display results
        print("\n" + "="*70)
        print("RESEARCH RESULTS COMPARISON")
        print("="*70)

        for model_name, response in results.items():
            if response:
                print(f"\n🤖 {model_name.upper()}")
                print(f"   Answer: {response.answer[:200]}...")
                print(f"   Confidence: {response.confidence.value}")
                print(f"   Key Points: {len(response.key_points)}")

    # Run demo
    asyncio.run(demo())
