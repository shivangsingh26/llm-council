"""
Jury Orchestrator: Coordinates the three jury specialists.

Executes jury deliberation in sequence:
1. Evidence Validator (verify sources)
2. Logic Auditor (check consistency)
3. Assumption Critic (challenge assumptions)

Combines results into final jury verdict.
"""

import logging
from typing import Dict, List, Optional
import os

from src.jury.evidence_validator import EvidenceValidator
from src.jury.logic_auditor import LogicAuditor
from src.jury.assumption_critic import AssumptionCritic
from src.models.schemas import ResearchResponse, JuryResult

logger = logging.getLogger(__name__)


class JuryOrchestrator:
    """
    Orchestrates the jury deliberation process.

    Coordinates three specialists:
    1. Evidence Validator
    2. Logic Auditor
    3. Assumption Critic

    Runs them sequentially and combines results.
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        google_api_key: Optional[str] = None
    ):
        """
        Initialize jury orchestrator.

        Args:
            openai_api_key: OpenAI API key (for Evidence Validator & Assumption Critic)
            google_api_key: Google AI API key (for Logic Auditor)
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.google_api_key = google_api_key or os.getenv("GEMINI_API_KEY")

        # Initialize jury members
        if self.openai_api_key:
            self.evidence_validator = EvidenceValidator(self.openai_api_key)
            self.assumption_critic = AssumptionCritic(self.openai_api_key)
        else:
            self.evidence_validator = None
            self.assumption_critic = None
            logger.warning("OpenAI API key not found - Evidence Validator and Assumption Critic disabled")

        if self.google_api_key:
            self.logic_auditor = LogicAuditor(self.google_api_key)
        else:
            self.logic_auditor = None
            logger.warning("Google API key not found - Logic Auditor disabled")

        logger.info("JuryOrchestrator initialized")

    async def deliberate(
        self,
        query: str,
        council_responses: Dict[str, ResearchResponse],
        synthesized_answer: str
    ) -> Dict:
        """
        Execute full jury deliberation.

        Args:
            query: Original research question
            council_responses: Responses from council members
            synthesized_answer: Judge's synthesized answer

        Returns:
            Dict with combined jury results
        """
        logger.info("🏛️  Starting jury deliberation")

        results = {
            "evidence_validation": None,
            "logic_analysis": None,
            "assumption_critique": None,
            "overall_quality_score": 0.0,
            "critical_issues": [],
            "recommendations": [],
            "jury_verdict": "approved"
        }

        # Step 1: Evidence Validator
        if self.evidence_validator:
            logger.info("📋 Running Evidence Validator...")
            try:
                evidence_result = await self.evidence_validator.analyze(
                    query,
                    council_responses,
                    synthesized_answer
                )
                results["evidence_validation"] = evidence_result

                # Check for critical issues
                if evidence_result.get("citation_hallucinations_detected"):
                    results["critical_issues"].append("Citation hallucinations detected")

                if evidence_result.get("overall_source_quality", 1.0) < 0.5:
                    results["critical_issues"].append("Low source quality")

                logger.info(f"✓ Evidence validation complete (quality: {evidence_result.get('overall_source_quality', 0):.2f})")

            except Exception as e:
                logger.error(f"Evidence validation failed: {e}")
                results["critical_issues"].append(f"Evidence validation error: {str(e)}")

        # Step 2: Logic Auditor
        if self.logic_auditor:
            logger.info("🔍 Running Logic Auditor...")
            try:
                logic_result = await self.logic_auditor.analyze(
                    query,
                    council_responses,
                    synthesized_answer
                )
                results["logic_analysis"] = logic_result

                # Check for contradictions
                contradictions = logic_result.get("contradictions", [])
                if contradictions:
                    major_contradictions = [c for c in contradictions if c.get("severity") in ["critical", "major"]]
                    if major_contradictions:
                        results["critical_issues"].append(f"{len(major_contradictions)} major contradictions found")

                logger.info(f"✓ Logic audit complete (consistency: {logic_result.get('consistency_score', 0):.2f})")

            except Exception as e:
                logger.error(f"Logic audit failed: {e}")
                results["critical_issues"].append(f"Logic audit error: {str(e)}")

        # Step 3: Assumption Critic
        if self.assumption_critic:
            logger.info("🤔 Running Assumption Critic...")
            try:
                assumption_result = await self.assumption_critic.analyze(
                    query,
                    council_responses,
                    synthesized_answer
                )
                results["assumption_critique"] = assumption_result

                # Check robustness
                robustness = assumption_result.get("robustness_score", 1.0)
                if robustness < 0.5:
                    results["critical_issues"].append("Low robustness - fragile claims detected")

                # Add recommendations
                if assumption_result.get("recommendations"):
                    results["recommendations"].extend(assumption_result["recommendations"])

                logger.info(f"✓ Assumption critique complete (robustness: {robustness:.2f})")

            except Exception as e:
                logger.error(f"Assumption critique failed: {e}")
                results["critical_issues"].append(f"Assumption critique error: {str(e)}")

        # Calculate overall quality score
        results["overall_quality_score"] = self._calculate_overall_quality(results)

        # Determine jury verdict
        results["jury_verdict"] = self._determine_verdict(results)

        logger.info(f"🏛️  Jury deliberation complete - Verdict: {results['jury_verdict']}")
        logger.info(f"   Overall quality: {results['overall_quality_score']:.2f}")
        logger.info(f"   Critical issues: {len(results['critical_issues'])}")

        return results

    def _calculate_overall_quality(self, results: Dict) -> float:
        """
        Calculate overall quality score from jury results.

        Args:
            results: Combined jury results

        Returns:
            Quality score 0.0-1.0
        """
        scores = []

        # Evidence quality
        if results.get("evidence_validation"):
            evidence_quality = results["evidence_validation"].get("overall_source_quality", 0.5)
            scores.append(evidence_quality)

        # Logic consistency
        if results.get("logic_analysis"):
            consistency = results["logic_analysis"].get("consistency_score", 0.7)
            scores.append(consistency)

        # Robustness
        if results.get("assumption_critique"):
            robustness = results["assumption_critique"].get("robustness_score", 0.6)
            scores.append(robustness)

        # Average scores
        if scores:
            return sum(scores) / len(scores)
        else:
            return 0.5  # Default if no scores available

    def _determine_verdict(self, results: Dict) -> str:
        """
        Determine final jury verdict.

        Args:
            results: Combined jury results

        Returns:
            Verdict: "approved" | "needs_revision" | "rejected"
        """
        critical_issues = len(results["critical_issues"])
        overall_quality = results["overall_quality_score"]

        # Rejected: Critical issues and low quality
        if critical_issues >= 3 or overall_quality < 0.4:
            return "rejected"

        # Needs revision: Some issues or moderate quality
        elif critical_issues >= 1 or overall_quality < 0.6:
            return "needs_revision"

        # Approved: No critical issues and good quality
        else:
            return "approved"
