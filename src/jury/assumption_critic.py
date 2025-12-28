"""
Assumption Critic: Challenges assumptions and finds edge cases.

Responsibilities:
- Surface hidden assumptions
- Test edge cases where claims might fail
- Identify bias in framing
- Generate counter-examples
"""

import json
from typing import Dict, List
from openai import AsyncOpenAI

from src.jury.base_juror import BaseJuror, JuryRole
from src.models.schemas import ResearchResponse


class AssumptionCritic(BaseJuror):
    """
    Jury specialist that challenges assumptions and finds edge cases.

    Uses GPT-4o (can be upgraded to o4-mini later) for:
    - Hidden assumption detection
    - Edge case generation
    - Bias identification
    - Robustness testing
    """

    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        """
        Initialize assumption critic.

        Args:
            api_key: OpenAI API key
            model_name: Model to use (default: gpt-4o)
        """
        super().__init__(api_key, model_name, JuryRole.ASSUMPTION_CRITIC)
        self.client = AsyncOpenAI(api_key=api_key)

    async def analyze(
        self,
        query: str,
        council_responses: Dict[str, ResearchResponse],
        synthesized_answer: str
    ) -> Dict:
        """
        Challenge assumptions and find edge cases.

        Args:
            query: Original research question
            council_responses: Responses from council members
            synthesized_answer: Judge's synthesized answer

        Returns:
            Dict with assumption critique results
        """
        # Build critique prompt
        prompt = self._build_critique_prompt(
            query,
            synthesized_answer,
            council_responses
        )

        try:
            # Call GPT-4o for assumption analysis
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
                temperature=0.7,  # Higher temperature for creative thinking
                max_tokens=2000
            )

            # Parse response
            critique_text = response.choices[0].message.content
            critique_result = self._parse_critique(critique_text)

            # Add metadata
            return {
                **self._format_metadata(),
                **critique_result,
                "tokens_used": response.usage.total_tokens
            }

        except Exception as e:
            # Return error state
            return {
                **self._format_metadata(),
                "error": str(e),
                "hidden_assumptions": [],
                "edge_cases": [],
                "robustness_score": 0.5
            }

    def _get_system_prompt(self) -> str:
        """Get system prompt for assumption critic."""
        return """You are an expert assumption critic and devil's advocate.

Your role:
1. Surface hidden assumptions in arguments
2. Generate edge cases where claims might fail
3. Identify bias in framing or perspective
4. Test robustness of conclusions

For each finding, provide:
- Type: "hidden_assumption" | "edge_case" | "bias" | "fragile_claim"
- Description: What's the issue?
- Impact: How does this affect the conclusion?

Output as JSON:
{
  "hidden_assumptions": [
    "Assumes Western legal framework",
    "Presumes current geopolitical status"
  ],
  "edge_cases": [
    {
      "scenario": "What if interest rates go negative?",
      "impact": "Claim would not hold"
    }
  ],
  "bias_detected": {
    "type": "confirmation_bias",
    "description": "Only considers supporting evidence"
  },
  "fragile_claims": ["Claim X breaks under scenario Y"],
  "robustness_score": 0.65,
  "recommendations": ["Consider alternative frameworks"]
}

Be creative but constructive. Your goal is to strengthen the research."""

    def _build_critique_prompt(
        self,
        query: str,
        synthesized_answer: str,
        council_responses: Dict[str, ResearchResponse]
    ) -> str:
        """Build assumption critique prompt."""
        prompt_parts = [
            f"# Research Question\n{query}\n",
            f"\n# Synthesized Answer\n{synthesized_answer}\n",
            "\n# Council Responses\n"
        ]

        for model_name, response in council_responses.items():
            if response and response.answer:
                prompt_parts.append(f"## {model_name}")
                prompt_parts.append(response.answer)
                prompt_parts.append("")

        prompt_parts.append("\n# Your Task")
        prompt_parts.append("As a devil's advocate, challenge this research:")
        prompt_parts.append("1. What assumptions are being made?")
        prompt_parts.append("2. What edge cases might break these claims?")
        prompt_parts.append("3. What biases might be present?")
        prompt_parts.append("4. How robust are the conclusions?")

        return "\n".join(prompt_parts)

    def _parse_critique(self, critique_text: str) -> Dict:
        """
        Parse critique results from model output.

        Args:
            critique_text: JSON or text output from model

        Returns:
            Parsed critique dict
        """
        try:
            # Try to parse as JSON
            if "```json" in critique_text:
                json_start = critique_text.find("```json") + 7
                json_end = critique_text.find("```", json_start)
                json_str = critique_text[json_start:json_end].strip()
            elif "{" in critique_text:
                json_start = critique_text.find("{")
                json_end = critique_text.rfind("}") + 1
                json_str = critique_text[json_start:json_end]
            else:
                json_str = critique_text

            result = json.loads(json_str)

            # Ensure required fields
            if "robustness_score" not in result:
                result["robustness_score"] = 0.6

            if "hidden_assumptions" not in result:
                result["hidden_assumptions"] = []

            if "edge_cases" not in result:
                result["edge_cases"] = []

            return result

        except json.JSONDecodeError:
            # Fallback: return basic structure
            return {
                "hidden_assumptions": [],
                "edge_cases": [],
                "bias_detected": None,
                "fragile_claims": [],
                "robustness_score": 0.6,
                "recommendations": ["Failed to parse critique results"]
            }
