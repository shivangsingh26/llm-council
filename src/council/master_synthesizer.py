"""
Master Synthesizer using OpenAI o1/o3 Reasoning Models
========================================================
Replaces rule-based aggregation with deep LLM reasoning.

Key Features:
- Uses OpenAI o1-mini for fast reasoning
- Deep consensus & disagreement analysis
- Reasoning transparency with chain-of-thought
- Natural synthesis (not string concatenation)
- Confidence scoring with explanations

Learning Points:
- Reasoning models (o1/o3) for synthesis
- Structured output parsing
- Advanced prompt engineering
- Cost-effective reasoning (o1-mini)
"""

from openai import AsyncOpenAI
from typing import Dict, List, Optional
import json
import re
import os
from datetime import datetime

from src.models.schemas import (
    ResearchResponse,
    ComparisonResult,
    ResearchDomain,
    ConfidenceLevel
)


class MasterSynthesizer:
    """
    Master orchestrator using OpenAI o1/o3 reasoning models.

    The master agent:
    1. Receives responses from all worker agents
    2. Reasons deeply about consensus and conflicts
    3. Synthesizes a coherent, well-reasoned answer
    4. Provides transparency through reasoning traces

    Why o1/o3 models?
    - Extended thinking time for complex reasoning
    - Better at identifying nuanced agreements/disagreements
    - Natural synthesis without explicit instructions
    - Chain-of-thought reasoning built-in

    Models available:
    - o1-mini: Fast reasoning ($3/$12 per 1M tokens) - Default
    - o1: Deep reasoning ($15/$60 per 1M tokens)
    - o3-mini: Latest reasoning model (pricing TBD)

    Example:
        synthesizer = MasterSynthesizer(api_key="sk-...")
        result = await synthesizer.synthesize(
            query="What are AI benefits?",
            responses={
                "gpt-4o": ResearchResponse(...),
                "gemini": ResearchResponse(...)
            }
        )
        print(result.synthesized_answer)
        print(result.reasoning_trace)
    """

    # Pricing per 1M tokens (input/output)
    PRICING = {
        "gpt-4o": (2.5, 10.0),  # $2.50/$10.00 per 1M tokens
        "o1-mini": (3.0, 12.0),
        "o1": (15.0, 60.0),
        "o3-mini": (3.0, 12.0),  # Estimated
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o"
    ):
        """
        Initialize master synthesizer.

        Args:
            api_key: OpenAI API key (or reads from OPENAI_API_KEY env)
            model: Model to use (gpt-4o, o1-mini, o1, o3-mini)
                   Default: gpt-4o (o1 models require special access)

        Note: o1/o3 models are in beta and may require special access
              Using gpt-4o provides excellent reasoning at lower cost
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required for MasterSynthesizer")

        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)

        print(f"✓ MasterSynthesizer initialized with {model}")
        print(f"  💭 Reasoning model: {model}")
        print(f"  💰 Cost: ${self.PRICING[model][0]}/{self.PRICING[model][1]} per 1M tokens (in/out)")

    async def synthesize(
        self,
        query: str,
        responses: Dict[str, ResearchResponse],
        domain: ResearchDomain,
        context: Optional[Dict] = None
    ) -> ComparisonResult:
        """
        Synthesize responses using advanced reasoning.

        This is the main method that orchestrates the synthesis:
        1. Build comprehensive prompt with all agent responses
        2. Call o1/o3 reasoning model
        3. Parse structured output (JSON)
        4. Calculate metrics (tokens, cost)
        5. Return enriched ComparisonResult

        Args:
            query: Original research question
            responses: Dict of model_name -> ResearchResponse
            domain: Research domain
            context: Optional context (tools used, research plan, etc.)

        Returns:
            ComparisonResult with deep synthesis and reasoning trace

        Raises:
            ValueError: If no responses provided
            Exception: If OpenAI API call fails
        """

        if not responses:
            raise ValueError("No responses to synthesize")

        print(f"\n{'='*70}")
        print(f"🧠 MASTER SYNTHESIZER - Deep Reasoning")
        print(f"{'='*70}")
        print(f"📋 Query: {query}")
        print(f"👥 Agents: {len(responses)}")
        print(f"🤖 Model: {self.model}")

        # Filter out None responses
        successful_responses = {
            model: resp for model, resp in responses.items()
            if resp is not None
        }

        failed_models = [
            model for model, resp in responses.items()
            if resp is None
        ]

        if not successful_responses:
            # All agents failed - return empty result
            return self._create_failed_result(query, domain, responses)

        # Build synthesis prompt
        prompt = self._build_synthesis_prompt(
            query=query,
            responses=successful_responses,
            context=context
        )

        try:
            # Call reasoning model
            print(f"🤔 Reasoning... (this may take 10-30 seconds)")

            # Build API call parameters
            api_params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            # Add temperature and max_tokens for non-o1 models
            if not self.model.startswith("o1") and not self.model.startswith("o3"):
                api_params["temperature"] = 0.7
                api_params["max_tokens"] = 4000

            response = await self.client.chat.completions.create(**api_params)

            synthesis_text = response.choices[0].message.content
            print(f"✅ Reasoning complete!")

            # Parse structured output
            parsed = self._parse_synthesis(synthesis_text)

            # Calculate metrics
            total_tokens = self._calculate_total_tokens(
                successful_responses,
                response
            )
            total_cost = self._calculate_total_cost(
                successful_responses,
                response
            )

            print(f"\n📊 Synthesis Metrics:")
            print(f"   Consensus points: {len(parsed['consensus_points'])}")
            print(f"   Disagreements: {len(parsed['disagreement_points'])}")
            print(f"   Knowledge gaps: {len(parsed['knowledge_gaps'])}")
            print(f"   Confidence: {parsed['confidence_range']}")
            print(f"   Total tokens: {total_tokens}")
            print(f"   Total cost: ${total_cost:.6f}")
            print(f"{'='*70}\n")

            # Build ComparisonResult
            result = ComparisonResult(
                query=query,
                domain=domain,
                responses=successful_responses,
                total_agents=len(responses),
                successful_agents=len(successful_responses),
                failed_agents=failed_models,
                consensus_points=parsed["consensus_points"],
                disagreement_points=parsed["disagreement_points"],
                confidence_range=parsed["confidence_range"],
                synthesized_answer=parsed["synthesized_answer"],
                reasoning_trace=parsed.get("reasoning_trace"),
                knowledge_gaps=parsed.get("knowledge_gaps", []),
                verification_needed=parsed.get("verification_needed", []),
                confidence_reasoning=parsed.get("confidence_reasoning"),
                total_tokens=total_tokens,
                total_cost=total_cost,
                timestamp=datetime.now()
            )

            return result

        except Exception as e:
            print(f"❌ Synthesis failed: {e}")
            raise

    def _build_synthesis_prompt(
        self,
        query: str,
        responses: Dict[str, ResearchResponse],
        context: Optional[Dict]
    ) -> str:
        """
        Build comprehensive prompt for reasoning model.

        The prompt includes:
        - Original query
        - All agent responses with details
        - Tools used (if available)
        - Clear instructions for structured output

        Args:
            query: Original research question
            responses: Successful agent responses
            context: Optional context (tools, plan, etc.)

        Returns:
            Formatted prompt string
        """

        prompt_parts = [
            "# Research Synthesis Task",
            f"\n## Original Query\n{query}",
            "\n## Agent Responses\n"
        ]

        # Add each agent's response
        for model_name, response in responses.items():
            prompt_parts.append(f"### {model_name}")
            prompt_parts.append(f"**Answer:** {response.answer}")
            prompt_parts.append(f"**Confidence:** {response.confidence.value}")
            prompt_parts.append(f"**Key Points:**")
            for point in response.key_points:
                prompt_parts.append(f"  - {point}")
            prompt_parts.append("")

        # Add context if available
        if context:
            if context.get("tools_used"):
                prompt_parts.append("\n## Tools Used")
                for tool, result in context["tools_used"].items():
                    prompt_parts.append(f"- **{tool}**: {result}")
                prompt_parts.append("")

            if context.get("research_plan"):
                prompt_parts.append(f"\n## Research Plan\n{context['research_plan']}\n")

        # Add instructions
        prompt_parts.append("""
## Your Task

As a master research synthesizer with advanced reasoning capabilities, deeply analyze all agent responses and provide:

### 1. Consensus Analysis
- Identify points where agents genuinely agree (semantic agreement, not just word matching)
- Explain WHY these points represent true consensus
- Rank by importance and confidence
- Consider the depth and quality of agreement

### 2. Disagreement Analysis
- Identify meaningful disagreements (not superficial differences in wording)
- Explain the root cause of each disagreement
- Assess which perspective is more credible (with reasoning)
- Note if disagreements are complementary rather than contradictory

### 3. Knowledge Gaps
- Identify areas where agents lack complete information
- Note claims that need verification
- Suggest what additional research would be valuable

### 4. Synthesized Answer
- Provide a coherent, well-reasoned synthesis
- Integrate insights from all agents naturally
- Resolve disagreements with clear reasoning
- Add your own insights where appropriate
- Write in a clear, accessible style

### 5. Confidence Assessment
- Overall confidence level: low, medium, high, or very_high
- Detailed reasoning for this confidence score
- Key uncertainties or limitations
- What would increase confidence

### 6. Verification Needs
- Flag specific claims that need fact-checking
- Suggest reliable sources for verification
- Note areas where tool use (web search) would help

## Output Format

Provide your response as a JSON object with this exact structure:

```json
{
  "consensus_points": [
    "First consensus point with explanation of why agents agree...",
    "Second consensus point with reasoning..."
  ],
  "disagreement_points": [
    "Description of disagreement with analysis of root cause...",
    "Another disagreement with resolution reasoning..."
  ],
  "knowledge_gaps": [
    "First gap in knowledge...",
    "Second area needing more research..."
  ],
  "synthesized_answer": "Your comprehensive, well-reasoned synthesis here. This should be natural prose that integrates all insights, resolves disagreements, and provides a clear answer to the original query.",
  "confidence_range": "medium",
  "confidence_reasoning": "Detailed explanation of why you assigned this confidence level, including key factors and uncertainties.",
  "verification_needed": [
    "Specific claim that needs verification...",
    "Another claim to fact-check..."
  ],
  "reasoning_trace": "Brief summary of your reasoning process and key considerations in reaching this synthesis."
}
```

**Important:**
- Think deeply and reason carefully
- Be honest about uncertainties
- Prioritize accuracy over confidence
- Explain your reasoning clearly
- Output ONLY the JSON, no additional text
""")

        return "\n".join(prompt_parts)

    def _parse_synthesis(self, synthesis_text: str) -> Dict:
        """
        Parse structured output from reasoning model.

        Handles both JSON and natural language outputs.
        Tries multiple parsing strategies:
        1. Extract JSON from code blocks
        2. Direct JSON parse
        3. Fallback to natural language parsing

        Args:
            synthesis_text: Raw text from reasoning model

        Returns:
            Dict with parsed fields

        Raises:
            ValueError: If parsing completely fails
        """

        # Strategy 1: Try to extract JSON from code blocks
        try:
            json_match = re.search(
                r'```json\s*\n(.*?)\n```',
                synthesis_text,
                re.DOTALL
            )
            if json_match:
                parsed = json.loads(json_match.group(1))
                return self._validate_parsed_output(parsed)
        except json.JSONDecodeError:
            pass

        # Strategy 2: Try direct JSON parse
        try:
            parsed = json.loads(synthesis_text)
            return self._validate_parsed_output(parsed)
        except json.JSONDecodeError:
            pass

        # Strategy 3: Fallback to natural language parsing
        print("⚠️  JSON parsing failed, using natural language fallback")
        return self._parse_natural_language(synthesis_text)

    def _validate_parsed_output(self, parsed: Dict) -> Dict:
        """
        Validate and fill in missing fields.

        Args:
            parsed: Parsed JSON dict

        Returns:
            Validated dict with all required fields
        """

        # Ensure required fields exist
        required_fields = {
            "consensus_points": [],
            "disagreement_points": [],
            "knowledge_gaps": [],
            "synthesized_answer": "",
            "confidence_range": "medium",
            "confidence_reasoning": "",
            "verification_needed": [],
            "reasoning_trace": ""
        }

        for field, default in required_fields.items():
            if field not in parsed:
                parsed[field] = default

        return parsed

    def _parse_natural_language(self, text: str) -> Dict:
        """
        Fallback parser for natural language output.

        Uses simple heuristics to extract structured data.
        This is a backup when JSON parsing fails.

        Args:
            text: Natural language synthesis

        Returns:
            Dict with extracted fields
        """

        return {
            "consensus_points": [],
            "disagreement_points": [],
            "knowledge_gaps": [],
            "synthesized_answer": text[:1000],  # Use first 1000 chars
            "confidence_range": "medium",
            "confidence_reasoning": "Based on natural language synthesis",
            "verification_needed": [],
            "reasoning_trace": text[:500]  # First 500 chars as reasoning
        }

    def _calculate_total_tokens(
        self,
        responses: Dict[str, ResearchResponse],
        synthesis_response
    ) -> int:
        """
        Calculate total tokens used across all models.

        Includes:
        - Tokens from all worker agents
        - Tokens from master synthesizer

        Args:
            responses: Worker agent responses
            synthesis_response: OpenAI response object

        Returns:
            Total token count
        """

        total = 0

        # Worker agent tokens
        for response in responses.values():
            if response.tokens_used:
                total += response.tokens_used

        # Master synthesizer tokens
        if hasattr(synthesis_response, 'usage') and synthesis_response.usage:
            total += synthesis_response.usage.total_tokens

        return total

    def _calculate_total_cost(
        self,
        responses: Dict[str, ResearchResponse],
        synthesis_response
    ) -> float:
        """
        Calculate estimated total cost in USD.

        Includes:
        - Cost from all worker agents
        - Cost from master synthesizer

        Args:
            responses: Worker agent responses
            synthesis_response: OpenAI response object

        Returns:
            Estimated cost in USD
        """

        # Worker agent costs (using existing pricing)
        from src.council.aggregator import ResponseAggregator
        worker_cost = ResponseAggregator()._calculate_total_cost(responses)

        # Master synthesizer cost
        master_cost = 0.0
        if hasattr(synthesis_response, 'usage') and synthesis_response.usage:
            input_tokens = synthesis_response.usage.prompt_tokens
            output_tokens = synthesis_response.usage.completion_tokens

            input_price, output_price = self.PRICING[self.model]

            master_cost = (
                (input_tokens / 1_000_000) * input_price +
                (output_tokens / 1_000_000) * output_price
            )

        return worker_cost + master_cost

    def _create_failed_result(
        self,
        query: str,
        domain: ResearchDomain,
        responses: Dict
    ) -> ComparisonResult:
        """
        Create result when all agents failed.

        Args:
            query: Original query
            domain: Research domain
            responses: All responses (all None)

        Returns:
            ComparisonResult indicating failure
        """

        return ComparisonResult(
            query=query,
            domain=domain,
            responses={},
            total_agents=len(responses),
            successful_agents=0,
            failed_agents=list(responses.keys()),
            consensus_points=[],
            disagreement_points=[],
            confidence_range="low",
            synthesized_answer="All agents failed to provide responses. Please check API keys and try again.",
            reasoning_trace="No responses available for synthesis.",
            total_tokens=0,
            total_cost=0.0,
            timestamp=datetime.now()
        )


# Example usage
if __name__ == "__main__":
    """
    Test the MasterSynthesizer with mock data.

    Run: python -m src.council.master_synthesizer
    """
    import asyncio

    async def test():
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

        # Create synthesizer
        synthesizer = MasterSynthesizer()

        # Synthesize
        result = await synthesizer.synthesize(
            query="What are the benefits of exercise?",
            responses=mock_responses,
            domain=ResearchDomain.HEALTHCARE
        )

        # Display results
        print("\n" + "="*70)
        print("MASTER SYNTHESIS RESULT")
        print("="*70)
        print(f"\nQuery: {result.query}")
        print(f"Successful agents: {result.successful_agents}/{result.total_agents}")
        print(f"\nConsensus points: {len(result.consensus_points)}")
        for point in result.consensus_points:
            print(f"  • {point}")
        print(f"\nDisagreement points: {len(result.disagreement_points)}")
        for point in result.disagreement_points:
            print(f"  • {point}")
        print(f"\nSynthesized answer:")
        print(f"  {result.synthesized_answer}")
        print(f"\nConfidence: {result.confidence_range}")
        if result.confidence_reasoning:
            print(f"Reasoning: {result.confidence_reasoning}")
        print(f"\nMetrics:")
        print(f"  Total tokens: {result.total_tokens}")
        print(f"  Total cost: ${result.total_cost:.6f}")

    # Run async test
    asyncio.run(test())
