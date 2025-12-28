"""
Logic Auditor: Checks reasoning consistency and finds contradictions.

Responsibilities:
- Find logical contradictions between claims
- Check internal consistency
- Identify circular reasoning
- Flag non-sequiturs and reasoning gaps
"""

import json
import asyncio
from typing import Dict, List
from google import genai
from google.genai import types

from src.jury.base_juror import BaseJuror, JuryRole
from src.models.schemas import ResearchResponse


class LogicAuditor(BaseJuror):
    """
    Jury specialist that audits logical consistency.

    Uses Gemini 2.5 Pro (specialized thinking model for complex reasoning) for:
    - Contradiction detection
    - Consistency verification
    - Reasoning chain validation
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-pro"):
        """
        Initialize logic auditor.

        Args:
            api_key: Google AI API key
            model_name: Model to use (default: gemini-2.5-pro)
        """
        super().__init__(api_key, model_name, JuryRole.LOGIC_AUDITOR)
        self.client = genai.Client(api_key=api_key)

    async def analyze(
        self,
        query: str,
        council_responses: Dict[str, ResearchResponse],
        synthesized_answer: str
    ) -> Dict:
        """
        Audit logical consistency of responses.

        Args:
            query: Original research question
            council_responses: Responses from council members
            synthesized_answer: Judge's synthesized answer

        Returns:
            Dict with logic analysis results
        """
        # Compile all statements
        all_statements = self._compile_statements(
            council_responses,
            synthesized_answer
        )

        # Build audit prompt
        prompt = self._build_audit_prompt(query, all_statements)

        try:
            # Call Gemini for logic analysis (using asyncio.to_thread for sync API)
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,  # Low temperature for logical analysis
                    max_output_tokens=2000
                )
            )

            # Parse response
            audit_text = response.text
            audit_result = self._parse_audit(audit_text)

            # Add metadata
            return {
                **self._format_metadata(),
                **audit_result,
                "tokens_used": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            }

        except Exception as e:
            # Return error state
            return {
                **self._format_metadata(),
                "error": str(e),
                "contradictions": [],
                "reasoning_gaps": [],
                "consistency_score": 0.5
            }

    def _get_system_prompt(self) -> str:
        """Get system prompt for logic auditor."""
        return """You are an expert logic auditor for a research council.

Your role:
1. Find logical contradictions between claims
2. Check internal consistency of arguments
3. Identify circular reasoning
4. Flag non-sequiturs and reasoning gaps

For each issue found, provide:
- Type: "contradiction" | "circular_reasoning" | "non_sequitur" | "reasoning_gap"
- Description: What's the problem?
- Severity: "critical" | "major" | "minor"
- Affected claims/statements

Output as JSON:
{
  "contradictions": [
    {
      "claim_ids": ["c1", "c5"],
      "conflict": "Claim c1 states X, but c5 implies not-X",
      "severity": "major"
    }
  ],
  "reasoning_gaps": [
    "Conclusion doesn't follow from premises"
  ],
  "circular_reasoning_detected": false,
  "consistency_score": 0.75,
  "critical_issues": []
}

Be thorough in your analysis. Focus on logic, not content accuracy."""

    def _build_audit_prompt(self, query: str, statements: List[str]) -> str:
        """Build logic audit prompt."""
        system_prompt = self._get_system_prompt()

        prompt_parts = [
            system_prompt,
            f"\n# Research Question\n{query}\n",
            "\n# Statements to Audit\n"
        ]

        for i, statement in enumerate(statements, 1):
            prompt_parts.append(f"{i}. (ID: c{i}) {statement}")

        prompt_parts.append("\n\nAnalyze these statements for logical consistency.")
        prompt_parts.append("Identify contradictions, reasoning gaps, and consistency issues.")

        return "\n".join(prompt_parts)

    def _compile_statements(
        self,
        council_responses: Dict[str, ResearchResponse],
        synthesized_answer: str
    ) -> List[str]:
        """
        Compile all statements from responses.

        Args:
            council_responses: Council member responses
            synthesized_answer: Final synthesized answer

        Returns:
            List of statement strings
        """
        statements = []

        # Extract from synthesized answer
        statements.extend(self._extract_claims(synthesized_answer))

        # Extract from council responses
        for model_name, response in council_responses.items():
            if response and response.answer:
                statements.extend(self._extract_claims(response.answer))

        # Remove duplicates and limit
        unique_statements = list(dict.fromkeys(statements))
        return unique_statements[:15]  # Limit to 15 statements

    def _parse_audit(self, audit_text: str) -> Dict:
        """
        Parse audit results from model output.

        Args:
            audit_text: JSON or text output from model

        Returns:
            Parsed audit dict
        """
        try:
            # Try to parse as JSON
            if "```json" in audit_text:
                json_start = audit_text.find("```json") + 7
                json_end = audit_text.find("```", json_start)
                json_str = audit_text[json_start:json_end].strip()
            elif "{" in audit_text:
                json_start = audit_text.find("{")
                json_end = audit_text.rfind("}") + 1
                json_str = audit_text[json_start:json_end]
            else:
                json_str = audit_text

            result = json.loads(json_str)

            # Ensure required fields
            if "consistency_score" not in result:
                result["consistency_score"] = 0.7

            return result

        except json.JSONDecodeError:
            # Fallback: return basic structure
            return {
                "contradictions": [],
                "reasoning_gaps": [],
                "circular_reasoning_detected": False,
                "consistency_score": 0.7,
                "critical_issues": ["Failed to parse audit results"]
            }
