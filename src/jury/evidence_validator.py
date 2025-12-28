"""
Evidence Validator: Verifies sources and citations.

Responsibilities:
- Check if sources exist and are correctly quoted
- Detect citation hallucinations
- Assess source quality (peer-reviewed > blog post)
- Flag missing evidence for strong claims
"""

import json
from typing import Dict, List
from openai import AsyncOpenAI

from src.jury.base_juror import BaseJuror, JuryRole
from src.models.schemas import ResearchResponse


class EvidenceValidator(BaseJuror):
    """
    Jury specialist that validates evidence and sources.

    Uses o3 (advanced reasoning model) for:
    - Source verification
    - Citation quality assessment
    - Hallucination detection
    """

    def __init__(self, api_key: str, model_name: str = "o3"):
        """
        Initialize evidence validator.

        Args:
            api_key: OpenAI API key
            model_name: Model to use (default: o3)
        """
        super().__init__(api_key, model_name, JuryRole.EVIDENCE_VALIDATOR)
        self.client = AsyncOpenAI(api_key=api_key)

    async def analyze(
        self,
        query: str,
        council_responses: Dict[str, ResearchResponse],
        synthesized_answer: str
    ) -> Dict:
        """
        Validate evidence and sources in council responses.

        Args:
            query: Original research question
            council_responses: Responses from council members
            synthesized_answer: Judge's synthesized answer

        Returns:
            Dict with validation results
        """
        # Extract all claims and sources
        claims_with_sources = self._extract_claims_and_sources(
            council_responses,
            synthesized_answer
        )

        # Build validation prompt
        prompt = self._build_validation_prompt(
            query,
            claims_with_sources
        )

        try:
            # Call GPT-4o for validation
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Low temperature for factual validation
                max_tokens=2000
            )

            # Parse response
            validation_text = response.choices[0].message.content
            validation_result = self._parse_validation(validation_text)

            # Add metadata
            return {
                **self._format_metadata(),
                **validation_result,
                "tokens_used": response.usage.total_tokens
            }

        except Exception as e:
            # Return error state
            return {
                **self._format_metadata(),
                "error": str(e),
                "validations": [],
                "overall_source_quality": 0.0,
                "citation_hallucinations_detected": True
            }

    def _get_system_prompt(self) -> str:
        """Get system prompt for evidence validator."""
        return """You are an expert evidence validator for a research council.

Your role:
1. Verify if sources exist and are correctly quoted
2. Detect citation hallucinations (fake sources)
3. Assess source quality (academic > news > blog)
4. Flag unsupported claims

For each claim, provide:
- evidence_status: "verified" | "unverifiable" | "contradicted"
- issues: list of specific problems found
- source_quality_score: 0.0-1.0 (1.0 = peer-reviewed, 0.5 = news, 0.2 = blog)

Output as JSON:
{
  "validations": [
    {
      "claim_id": "c1",
      "claim_text": "...",
      "evidence_status": "verified",
      "issues": [],
      "source_quality_score": 0.85
    }
  ],
  "overall_source_quality": 0.75,
  "citation_hallucinations_detected": false,
  "critical_issues": []
}

Be rigorous but fair. Focus on facts, not opinions."""

    def _build_validation_prompt(
        self,
        query: str,
        claims_with_sources: List[Dict]
    ) -> str:
        """Build validation prompt."""
        prompt_parts = [
            f"# Research Question\n{query}\n",
            "\n# Claims to Validate\n"
        ]

        for i, item in enumerate(claims_with_sources, 1):
            prompt_parts.append(f"## Claim {i} (ID: c{i})")
            prompt_parts.append(f"**Claim:** {item['claim']}")
            prompt_parts.append(f"**Source:** {item.get('source', 'No source provided')}")
            prompt_parts.append("")

        prompt_parts.append("\nValidate each claim's evidence and sources.")

        return "\n".join(prompt_parts)

    def _extract_claims_and_sources(
        self,
        council_responses: Dict[str, ResearchResponse],
        synthesized_answer: str
    ) -> List[Dict]:
        """
        Extract claims and their sources from responses.

        Args:
            council_responses: Council member responses
            synthesized_answer: Final synthesized answer

        Returns:
            List of {claim, source} dicts
        """
        claims_with_sources = []

        # Extract from synthesized answer
        claims = self._extract_claims(synthesized_answer)
        for claim in claims:
            claims_with_sources.append({
                "claim": claim,
                "source": "synthesized",
                "origin": "judge"
            })

        # Extract from council responses
        for model_name, response in council_responses.items():
            if response and response.answer:
                claims = self._extract_claims(response.answer)
                for claim in claims:
                    claims_with_sources.append({
                        "claim": claim,
                        "source": response.sources[0] if response.sources else None,
                        "origin": model_name
                    })

        return claims_with_sources[:10]  # Limit to 10 claims for cost

    def _parse_validation(self, validation_text: str) -> Dict:
        """
        Parse validation results from model output.

        Args:
            validation_text: JSON or text output from model

        Returns:
            Parsed validation dict
        """
        try:
            # Try to parse as JSON
            if "```json" in validation_text:
                json_start = validation_text.find("```json") + 7
                json_end = validation_text.find("```", json_start)
                json_str = validation_text[json_start:json_end].strip()
            elif "{" in validation_text:
                json_start = validation_text.find("{")
                json_end = validation_text.rfind("}") + 1
                json_str = validation_text[json_start:json_end]
            else:
                json_str = validation_text

            result = json.loads(json_str)
            return result

        except json.JSONDecodeError:
            # Fallback: return basic structure
            return {
                "validations": [],
                "overall_source_quality": 0.5,
                "citation_hallucinations_detected": False,
                "critical_issues": ["Failed to parse validation results"]
            }
