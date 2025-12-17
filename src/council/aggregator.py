"""
Response Aggregator
==================
Compares and synthesizes responses from multiple AI agents.

Learning Points:
- Comparing outputs from different LLMs
- Finding consensus and disagreements
- Synthesizing multiple perspectives
- Statistical analysis of model outputs
"""

from typing import Dict, List, Optional, Set
from collections import Counter
import os

from src.models.schemas import (
    ResearchResponse,
    ComparisonResult,
    ResearchDomain,
    ConfidenceLevel
)

# Import master synthesizer (Phase A)
try:
    from src.council.master_synthesizer import MasterSynthesizer
    MASTER_SYNTHESIZER_AVAILABLE = True
except ImportError:
    MASTER_SYNTHESIZER_AVAILABLE = False
    print("⚠️  MasterSynthesizer not available - using rule-based aggregation")


class ResponseAggregator:
    """
    Aggregates and compares responses from multiple AI agents.

    The aggregator supports two modes:
    1. **Rule-Based (Legacy)**: Simple consensus/disagreement detection
    2. **Master Synthesizer (New)**: LLM-based deep reasoning with o1/o3

    The aggregator:
    1. Takes responses from all agents
    2. Identifies common themes (consensus)
    3. Highlights disagreements
    4. Synthesizes a final answer
    5. Calculates metrics (tokens, cost, etc.)

    Example:
        responses = {
            "gpt-4o": ResearchResponse(...),
            "gemini-2.5-flash": ResearchResponse(...)
        }

        # Use master synthesizer (recommended)
        aggregator = ResponseAggregator(use_master_synthesizer=True)
        result = await aggregator.aggregate(
            responses=responses,
            query="What are the benefits of exercise?",
            domain=ResearchDomain.HEALTHCARE
        )

        print(result.consensus_points)  # Points all models agree on
        print(result.synthesized_answer)  # Combined answer
        print(result.reasoning_trace)  # NEW: Reasoning from o1/o3
    """

    # Token pricing (per 1M tokens) for cost estimation
    PRICING = {
        "gpt-4o": 0.15,
        "gemini-2.5-flash": 0.0,  # Free tier
        "deepseek-r1:14b": 0.0,  # Local
    }

    def __init__(self, use_master_synthesizer: bool = True):
        """
        Initialize response aggregator.

        Args:
            use_master_synthesizer: If True, use o1/o3 for synthesis (default: True)
                                   If False, use rule-based aggregation (legacy)

        Note: Master synthesizer requires OPENAI_API_KEY with o1 access
        """
        self.use_master = use_master_synthesizer and MASTER_SYNTHESIZER_AVAILABLE
        self.master_synthesizer = None

        if self.use_master:
            try:
                self.master_synthesizer = MasterSynthesizer(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    model="gpt-4o"  # Excellent reasoning, widely available
                )
                print("✓ ResponseAggregator using Master Synthesizer (gpt-4o)")
            except Exception as e:
                print(f"⚠️  Master Synthesizer initialization failed: {e}")
                print("   Falling back to rule-based aggregation")
                self.use_master = False
        else:
            print("✓ ResponseAggregator using rule-based aggregation (legacy)")

    async def aggregate(
        self,
        responses: Dict[str, Optional[ResearchResponse]],
        query: str,
        domain: ResearchDomain
    ) -> ComparisonResult:
        """
        Aggregate responses from multiple agents into a comparison result.

        This method supports two modes:
        1. Master Synthesizer (async): Uses o1-mini for deep reasoning
        2. Rule-Based (sync): Uses simple heuristics

        Args:
            responses: Dict mapping model name to response (or None if failed)
            query: The original research question
            domain: Research domain

        Returns:
            ComparisonResult with aggregated analysis

        Note: This method is now async to support master synthesizer
        """

        # If master synthesizer is available, use it
        if self.use_master and self.master_synthesizer:
            return await self._aggregate_with_master(responses, query, domain)

        # Otherwise, use legacy rule-based aggregation
        return self._aggregate_rule_based(responses, query, domain)

    async def _aggregate_with_master(
        self,
        responses: Dict[str, Optional[ResearchResponse]],
        query: str,
        domain: ResearchDomain
    ) -> ComparisonResult:
        """
        Aggregate using master synthesizer (o1-mini).

        Args:
            responses: Agent responses
            query: Research question
            domain: Research domain

        Returns:
            ComparisonResult with deep reasoning
        """

        # Filter successful responses
        successful_responses = {
            model: resp for model, resp in responses.items()
            if resp is not None
        }

        if not successful_responses:
            # All failed - return empty result
            failed_models = list(responses.keys())
            return ComparisonResult(
                query=query,
                domain=domain,
                responses={},
                total_agents=len(responses),
                successful_agents=0,
                failed_agents=failed_models,
                consensus_points=[],
                disagreement_points=[],
                confidence_range="low",
                synthesized_answer="All agents failed to respond.",
                total_tokens=0,
                total_cost=0.0
            )

        # Use master synthesizer
        return await self.master_synthesizer.synthesize(
            query=query,
            responses=successful_responses,
            domain=domain
        )

    def _aggregate_rule_based(
        self,
        responses: Dict[str, Optional[ResearchResponse]],
        query: str,
        domain: ResearchDomain
    ) -> ComparisonResult:
        """
        Legacy rule-based aggregation.

        Args:
            responses: Agent responses
            query: Research question
            domain: Research domain

        Returns:
            ComparisonResult using simple heuristics
        """

        # Filter out failed responses
        successful_responses = {
            model: resp for model, resp in responses.items()
            if resp is not None
        }

        failed_models = [
            model for model, resp in responses.items()
            if resp is None
        ]

        total_agents = len(responses)
        successful_agents = len(successful_responses)

        print(f"\n{'='*70}")
        print(f"🔍 AGGREGATING RESPONSES")
        print(f"{'='*70}")
        print(f"✅ Successful: {successful_agents}/{total_agents}")
        if failed_models:
            print(f"❌ Failed: {', '.join(failed_models)}")

        # Analyze consensus and disagreements
        consensus_points = self._find_consensus(successful_responses)
        disagreement_points = self._find_disagreements(successful_responses)

        # Confidence analysis
        confidence_range = self._analyze_confidence(successful_responses)

        # Synthesize final answer
        synthesized_answer = self._synthesize_answer(
            successful_responses,
            consensus_points
        )

        # Calculate metrics
        total_tokens = self._calculate_total_tokens(successful_responses)
        total_cost = self._calculate_total_cost(successful_responses)

        print(f"\n📊 Analysis:")
        print(f"   Consensus points: {len(consensus_points)}")
        print(f"   Disagreement points: {len(disagreement_points)}")
        print(f"   Confidence range: {confidence_range}")
        print(f"   Total tokens: {total_tokens}")
        print(f"   Total cost: ${total_cost:.6f}")
        print(f"{'='*70}\n")

        # Create comparison result
        result = ComparisonResult(
            query=query,
            domain=domain,
            responses=successful_responses,
            total_agents=total_agents,
            successful_agents=successful_agents,
            failed_agents=failed_models,
            consensus_points=consensus_points,
            disagreement_points=disagreement_points,
            confidence_range=confidence_range,
            synthesized_answer=synthesized_answer,
            total_tokens=total_tokens,
            total_cost=total_cost
        )

        return result

    def _find_consensus(
        self,
        responses: Dict[str, ResearchResponse]
    ) -> List[str]:
        """
        Find key points where multiple models agree.

        Uses fuzzy matching to identify similar key points across models.

        Args:
            responses: Successful responses from agents

        Returns:
            List of consensus points
        """
        if len(responses) < 2:
            # Need at least 2 models to have consensus
            return []

        # Collect all key points from all models
        all_key_points = []
        for response in responses.values():
            all_key_points.extend(response.key_points)

        # Find points mentioned by multiple models
        # Simple approach: look for common words/themes
        # (In production, you'd use more sophisticated NLP)

        consensus = []

        # For now, return points that appear in multiple responses
        point_count = Counter(all_key_points)
        for point, count in point_count.items():
            if count >= 2:  # At least 2 models mentioned this
                consensus.append(point)

        return consensus[:5]  # Top 5 consensus points

    def _find_disagreements(
        self,
        responses: Dict[str, ResearchResponse]
    ) -> List[str]:
        """
        Find points where models disagree.

        Args:
            responses: Successful responses from agents

        Returns:
            List of disagreement descriptions
        """
        if len(responses) < 2:
            return []

        disagreements = []

        # Compare confidence levels
        confidences = [r.confidence for r in responses.values()]
        if len(set(confidences)) > 1:
            conf_str = ", ".join([
                f"{model}: {resp.confidence.value}"
                for model, resp in responses.items()
            ])
            disagreements.append(f"Confidence levels vary ({conf_str})")

        # Compare answer lengths (may indicate depth of analysis)
        answer_lengths = {
            model: len(resp.answer)
            for model, resp in responses.items()
        }
        max_len = max(answer_lengths.values())
        min_len = min(answer_lengths.values())

        if max_len > min_len * 1.5:  # Significant difference
            disagreements.append(
                f"Response depth varies significantly "
                f"(shortest: {min_len} chars, longest: {max_len} chars)"
            )

        return disagreements

    def _analyze_confidence(
        self,
        responses: Dict[str, ResearchResponse]
    ) -> str:
        """
        Analyze confidence range across all models.

        Args:
            responses: Successful responses from agents

        Returns:
            String describing confidence range (e.g., "medium to high")
        """
        if not responses:
            return "unknown"

        confidences = [r.confidence.value for r in responses.values()]
        unique_confidences = set(confidences)

        if len(unique_confidences) == 1:
            return confidences[0]  # All same

        # Map to numeric for range calculation
        conf_map = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "very_high": 4
        }

        conf_values = [conf_map.get(c, 2) for c in confidences]
        min_conf = min(conf_values)
        max_conf = max(conf_values)

        # Reverse map
        reverse_map = {v: k for k, v in conf_map.items()}

        return f"{reverse_map[min_conf]} to {reverse_map[max_conf]}"

    def _synthesize_answer(
        self,
        responses: Dict[str, ResearchResponse],
        consensus_points: List[str]
    ) -> str:
        """
        Synthesize a combined answer from all models.

        Simple approach: Combine consensus points with model answers.
        (In production, you might use an LLM to synthesize more naturally)

        Args:
            responses: Successful responses from agents
            consensus_points: Points where models agree

        Returns:
            Synthesized answer string
        """
        if not responses:
            return "No successful responses to synthesize"

        if len(responses) == 1:
            # Only one model - just return its answer
            return list(responses.values())[0].answer

        # Build synthesis
        synthesis_parts = []

        # Start with consensus
        if consensus_points:
            synthesis_parts.append("Key consensus points:")
            for i, point in enumerate(consensus_points[:3], 1):
                synthesis_parts.append(f"{i}. {point}")

        # Add note about model agreement
        synthesis_parts.append(
            f"\nBased on {len(responses)} AI models "
            f"({', '.join(responses.keys())}), "
            f"this represents a synthesized view of their findings."
        )

        return " ".join(synthesis_parts)

    def _calculate_total_tokens(
        self,
        responses: Dict[str, ResearchResponse]
    ) -> int:
        """
        Calculate total tokens used across all models.

        Args:
            responses: Successful responses from agents

        Returns:
            Total token count
        """
        total = 0
        for response in responses.values():
            if response.tokens_used:
                total += response.tokens_used

        return total

    def _calculate_total_cost(
        self,
        responses: Dict[str, ResearchResponse]
    ) -> float:
        """
        Calculate estimated total cost in USD.

        Args:
            responses: Successful responses from agents

        Returns:
            Estimated cost in USD
        """
        total_cost = 0.0

        for model_name, response in responses.items():
            if not response.tokens_used:
                continue

            # Get pricing for this model
            price_per_1m = self.PRICING.get(model_name, 0.0)

            # Calculate cost
            cost = (response.tokens_used / 1_000_000) * price_per_1m
            total_cost += cost

        return total_cost


# Example usage
if __name__ == "__main__":
    """
    Example of using the Response Aggregator.

    Run: python -m src.council.aggregator
    """
    from datetime import datetime

    # Create mock responses
    mock_responses = {
        "gpt-4o": ResearchResponse(
            query="What are the benefits of exercise?",
            answer="Regular exercise improves cardiovascular health, boosts mood, and enhances overall fitness.",
            domain=ResearchDomain.HEALTHCARE,
            confidence=ConfidenceLevel.HIGH,
            key_points=[
                "Improves cardiovascular health",
                "Boosts mood and mental health",
                "Enhances physical fitness"
            ],
            model_name="gpt-4o",
            timestamp=datetime.now(),
            tokens_used=500
        ),
        "gemini-2.5-flash": ResearchResponse(
            query="What are the benefits of exercise?",
            answer="Exercise has numerous benefits including better heart health, improved mood, weight management, and increased energy levels.",
            domain=ResearchDomain.HEALTHCARE,
            confidence=ConfidenceLevel.VERY_HIGH,
            key_points=[
                "Better heart health",
                "Improved mood",
                "Weight management",
                "Increased energy"
            ],
            model_name="gemini-2.5-flash",
            timestamp=datetime.now(),
            tokens_used=450
        )
    }

    # Aggregate
    aggregator = ResponseAggregator()
    result = aggregator.aggregate(
        responses=mock_responses,
        query="What are the benefits of exercise?",
        domain=ResearchDomain.HEALTHCARE
    )

    # Display
    print("\n" + "="*70)
    print("AGGREGATION RESULT")
    print("="*70)
    print(f"Query: {result.query}")
    print(f"Successful agents: {result.successful_agents}/{result.total_agents}")
    print(f"\nConsensus points:")
    for point in result.consensus_points:
        print(f"  • {point}")
    print(f"\nSynthesized answer:")
    print(f"  {result.synthesized_answer}")
    print(f"\nMetrics:")
    print(f"  Total tokens: {result.total_tokens}")
    print(f"  Total cost: ${result.total_cost:.6f}")
