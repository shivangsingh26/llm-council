"""
Adaptive Router: Routes queries to Fast/Medium/Deep processing paths.

Routes based on disagreement score:
- Fast path (< 0.3): High agreement, lightweight judge
- Medium path (0.3-0.7): Moderate disagreement, standard judge
- Deep path (> 0.7): High disagreement, full judge + jury (Phase 2)

This enables cost and latency optimization by using simpler processing
for queries where the council already agrees.
"""

from typing import Dict, Optional, Literal
from enum import Enum
import time
import logging

from src.models.schemas import ResearchResponse, ComparisonResult

logger = logging.getLogger(__name__)


class RoutingPath(str, Enum):
    """Routing path options."""
    FAST = "fast"
    MEDIUM = "medium"
    DEEP = "deep"


class AdaptiveRouter:
    """
    Routes queries to appropriate processing paths based on disagreement.

    Thresholds (from ARCHITECTURE.md):
    - < 0.3: FAST path (skip jury, lightweight judge)
    - 0.3-0.7: MEDIUM path (partial jury, full judge)
    - > 0.7: DEEP path (full jury, full judge)
    """

    # Routing thresholds
    FAST_THRESHOLD = 0.3
    DEEP_THRESHOLD = 0.7

    def __init__(self, aggregator=None):
        """
        Initialize the adaptive router.

        Args:
            aggregator: ResponseAggregator instance for synthesis
                       (will be injected by orchestrator)
        """
        self.aggregator = aggregator
        logger.info("AdaptiveRouter initialized")

    def determine_path(
        self,
        disagreement_score: float,
        user_preference: Optional[Literal["auto", "fast", "medium", "deep"]] = "auto"
    ) -> RoutingPath:
        """
        Determine which processing path to use.

        Args:
            disagreement_score: Score from DisagreementAnalyzer (0.0-1.0)
            user_preference: Optional user override ("auto", "fast", "medium", "deep")

        Returns:
            RoutingPath enum (FAST, MEDIUM, or DEEP)
        """
        # User preference overrides automatic routing
        if user_preference and user_preference != "auto":
            if user_preference == "fast":
                logger.info("User requested fast path (override)")
                return RoutingPath.FAST
            elif user_preference == "medium":
                logger.info("User requested medium path (override)")
                return RoutingPath.MEDIUM
            elif user_preference == "deep":
                logger.info("User requested deep path (override)")
                return RoutingPath.DEEP

        # Automatic routing based on disagreement score
        if disagreement_score < self.FAST_THRESHOLD:
            logger.info(f"Routing to FAST path (score: {disagreement_score:.3f} < {self.FAST_THRESHOLD})")
            return RoutingPath.FAST
        elif disagreement_score > self.DEEP_THRESHOLD:
            logger.info(f"Routing to DEEP path (score: {disagreement_score:.3f} > {self.DEEP_THRESHOLD})")
            return RoutingPath.DEEP
        else:
            logger.info(f"Routing to MEDIUM path (score: {disagreement_score:.3f} in range {self.FAST_THRESHOLD}-{self.DEEP_THRESHOLD})")
            return RoutingPath.MEDIUM

    async def execute_path(
        self,
        path: RoutingPath,
        council_responses: Dict[str, ResearchResponse],
        disagreement_score: float,
        disagreement_details: Dict,
        query: str = "",
        domain: str = "general"
    ) -> Dict:
        """
        Execute the appropriate processing path.

        Args:
            path: Which path to execute (FAST, MEDIUM, DEEP)
            council_responses: Responses from council members
            disagreement_score: Disagreement score
            disagreement_details: Detailed disagreement analysis

        Returns:
            Dict with synthesis results and metadata
        """
        start_time = time.time()

        if path == RoutingPath.FAST:
            result = await self._fast_path(council_responses, disagreement_score, disagreement_details, query, domain)
        elif path == RoutingPath.MEDIUM:
            result = await self._medium_path(council_responses, disagreement_score, disagreement_details, query, domain)
        else:  # DEEP
            result = await self._deep_path(council_responses, disagreement_score, disagreement_details, query, domain)

        # Add timing information
        result["judge_phase_ms"] = int((time.time() - start_time) * 1000)

        logger.info(f"Path execution complete: {path.value} ({result['judge_phase_ms']}ms)")

        return result

    async def _fast_path(
        self,
        council_responses: Dict[str, ResearchResponse],
        disagreement_score: float,
        disagreement_details: Dict,
        query: str,
        domain: str
    ) -> Dict:
        """
        Fast path: High agreement, lightweight processing.

        Optimizations:
        - Simpler synthesis (models already agree)
        - Minimal conflict resolution needed
        - Faster response time
        - Lower token usage

        Target latency: < 8s total (including council)
        """
        logger.info("Executing FAST path (lightweight synthesis)")

        # Filter valid responses
        valid_responses = {
            model: response
            for model, response in council_responses.items()
            if response is not None
        }

        if not valid_responses:
            return {
                "synthesized_answer": "No valid responses from council",
                "consensus_points": [],
                "disagreement_points": [],
                "routing_path": "fast",
                "synthesis_mode": "none"
            }

        # Use aggregator if available, otherwise simple synthesis
        if self.aggregator:
            # Use existing aggregator for synthesis with FAST path optimization
            result = await self.aggregator.aggregate(valid_responses, query, domain, routing_path="fast")

            return {
                "synthesized_answer": result.synthesized_answer,
                "consensus_points": result.consensus_points,
                "disagreement_points": result.disagreement_points,
                "reasoning_trace": result.reasoning_trace,
                "knowledge_gaps": result.knowledge_gaps,
                "verification_needed": result.verification_needed,
                "confidence_reasoning": result.confidence_reasoning,
                "routing_path": "fast",
                "synthesis_mode": "lightweight"
            }
        else:
            # Simple fallback synthesis (no aggregator)
            first_response = next(iter(valid_responses.values()))

            return {
                "synthesized_answer": first_response.answer,
                "consensus_points": first_response.key_points,
                "disagreement_points": [],
                "routing_path": "fast",
                "synthesis_mode": "simple"
            }

    async def _medium_path(
        self,
        council_responses: Dict[str, ResearchResponse],
        disagreement_score: float,
        disagreement_details: Dict,
        query: str,
        domain: str
    ) -> Dict:
        """
        Medium path: Moderate disagreement, standard processing.

        Processing:
        - Full synthesis with conflict resolution
        - Standard judge prompt
        - No jury (jury in Phase 2)

        Target latency: < 12s total
        """
        logger.info("Executing MEDIUM path (standard synthesis)")

        # Filter valid responses
        valid_responses = {
            model: response
            for model, response in council_responses.items()
            if response is not None
        }

        if not valid_responses:
            return {
                "synthesized_answer": "No valid responses from council",
                "consensus_points": [],
                "disagreement_points": [],
                "routing_path": "medium",
                "synthesis_mode": "none"
            }

        # Use full aggregator synthesis with MEDIUM path optimization
        if self.aggregator:
            result = await self.aggregator.aggregate(valid_responses, query, domain, routing_path="medium")

            return {
                "synthesized_answer": result.synthesized_answer,
                "consensus_points": result.consensus_points,
                "disagreement_points": result.disagreement_points,
                "reasoning_trace": result.reasoning_trace,
                "knowledge_gaps": result.knowledge_gaps,
                "verification_needed": result.verification_needed,
                "confidence_reasoning": result.confidence_reasoning,
                "routing_path": "medium",
                "synthesis_mode": "standard"
            }
        else:
            # Fallback
            first_response = next(iter(valid_responses.values()))

            return {
                "synthesized_answer": first_response.answer,
                "consensus_points": first_response.key_points,
                "disagreement_points": ["No aggregator available"],
                "routing_path": "medium",
                "synthesis_mode": "fallback"
            }

    async def _deep_path(
        self,
        council_responses: Dict[str, ResearchResponse],
        disagreement_score: float,
        disagreement_details: Dict,
        query: str,
        domain: str
    ) -> Dict:
        """
        Deep path: High disagreement, full processing.

        Processing:
        - Full synthesis with detailed conflict resolution
        - Jury analysis (Phase 2 - not implemented yet)
        - Comprehensive reasoning

        Target latency: < 15s total (without jury)
        Target latency: < 30s total (with jury in Phase 2)
        """
        logger.info("Executing DEEP path (full synthesis)")
        logger.warning("Note: Jury layer not yet implemented (Phase 2)")

        # Filter valid responses
        valid_responses = {
            model: response
            for model, response in council_responses.items()
            if response is not None
        }

        if not valid_responses:
            return {
                "synthesized_answer": "No valid responses from council",
                "consensus_points": [],
                "disagreement_points": [],
                "routing_path": "deep",
                "synthesis_mode": "none"
            }

        # For now, deep path uses same synthesis as medium
        # In Phase 2, this will include jury analysis
        if self.aggregator:
            result = await self.aggregator.aggregate(valid_responses, query, domain, routing_path="deep")

            return {
                "synthesized_answer": result.synthesized_answer,
                "consensus_points": result.consensus_points,
                "disagreement_points": result.disagreement_points,
                "reasoning_trace": result.reasoning_trace,
                "knowledge_gaps": result.knowledge_gaps,
                "verification_needed": result.verification_needed,
                "confidence_reasoning": result.confidence_reasoning,
                "routing_path": "deep",
                "synthesis_mode": "full",
                "jury_analysis": "Not yet implemented (Phase 2)"
            }
        else:
            # Fallback
            first_response = next(iter(valid_responses.values()))

            return {
                "synthesized_answer": first_response.answer,
                "consensus_points": first_response.key_points,
                "disagreement_points": ["High disagreement detected"],
                "routing_path": "deep",
                "synthesis_mode": "fallback"
            }

    def get_path_info(self, path: RoutingPath) -> Dict:
        """
        Get information about a routing path.

        Args:
            path: RoutingPath enum

        Returns:
            Dict with path description and characteristics
        """
        info = {
            RoutingPath.FAST: {
                "name": "Fast Path",
                "description": "High agreement - lightweight processing",
                "target_latency_ms": 8000,
                "features": ["Lightweight judge", "Skip jury", "Quick synthesis"],
                "use_case": "Factual queries with clear answers"
            },
            RoutingPath.MEDIUM: {
                "name": "Medium Path",
                "description": "Moderate disagreement - standard processing",
                "target_latency_ms": 12000,
                "features": ["Standard judge", "No jury (Phase 1)", "Full synthesis"],
                "use_case": "Balanced queries with some ambiguity"
            },
            RoutingPath.DEEP: {
                "name": "Deep Path",
                "description": "High disagreement - comprehensive processing",
                "target_latency_ms": 15000,  # 30000 with jury in Phase 2
                "features": ["Full judge", "Jury analysis (Phase 2)", "Deep synthesis"],
                "use_case": "Complex queries with significant disagreement"
            }
        }

        return info.get(path, {})
