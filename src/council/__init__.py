"""
Council Package
==============
Multi-agent orchestration for collaborative AI research.

Components:
- CouncilOrchestrator: Runs multiple agents in parallel
- ResponseAggregator: Compares and synthesizes responses
"""

from src.council.orchestrator import CouncilOrchestrator
from src.council.aggregator import ResponseAggregator

__all__ = ["CouncilOrchestrator", "ResponseAggregator"]
