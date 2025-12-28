"""
Base Juror: Abstract base class for jury specialists.

All jury members inherit from this class and implement the analyze() method.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime

from src.models.schemas import ResearchResponse


class JuryRole(str, Enum):
    """Jury specialist roles."""
    EVIDENCE_VALIDATOR = "evidence_validator"
    LOGIC_AUDITOR = "logic_auditor"
    ASSUMPTION_CRITIC = "assumption_critic"


class BaseJuror(ABC):
    """
    Abstract base class for jury specialists.

    Each juror:
    - Receives council responses
    - Performs specialized analysis
    - Returns structured findings
    - Contributes to final verdict
    """

    def __init__(self, api_key: str, model_name: str, role: JuryRole):
        """
        Initialize juror.

        Args:
            api_key: API key for the model
            model_name: Model to use (e.g., "o3", "gemini-2.5-pro")
            role: Jury role
        """
        self.api_key = api_key
        self.model_name = model_name
        self.role = role

    @abstractmethod
    async def analyze(
        self,
        query: str,
        council_responses: Dict[str, ResearchResponse],
        synthesized_answer: str
    ) -> Dict:
        """
        Perform specialized analysis.

        Args:
            query: Original research question
            council_responses: Responses from council members
            synthesized_answer: Judge's synthesized answer

        Returns:
            Dict with role-specific analysis results
        """
        pass

    def _extract_claims(self, text: str) -> List[str]:
        """
        Extract individual claims from text.

        Simple implementation - can be enhanced with NLP.

        Args:
            text: Text to extract claims from

        Returns:
            List of claim strings
        """
        # Split by sentences and filter
        sentences = text.split('.')
        claims = [s.strip() for s in sentences if len(s.strip()) > 20]
        return claims

    def _format_metadata(self) -> Dict:
        """Get common metadata for all jurors."""
        return {
            "role": self.role.value,
            "model": self.model_name,
            "timestamp": datetime.now().isoformat()
        }
