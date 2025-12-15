"""
OpenAI GPT-4o Research Agent
============================
Research agent powered by OpenAI's GPT-4o model (latest SOTA).

Learning Points:
- Using OpenAI's async client (AsyncOpenAI)
- Chat Completions API with async/await
- Message formatting (system/user/assistant roles)
- Token tracking and cost management
- Error handling with retries

Model: gpt-4o
Strengths: Fast, versatile, excellent general knowledge, cost-effective
Use case: General research across all domains
"""

from openai import AsyncOpenAI
from typing import Optional
from datetime import datetime

from src.agents.base_agent import BaseResearchAgent
from src.models.schemas import ResearchResponse, ResearchDomain, ConfidenceLevel


class OpenAIAgent(BaseResearchAgent):
    """
    Research agent using OpenAI's GPT-4o model.

    GPT-4o is OpenAI's latest general-purpose model:
    - Fast inference (~1-2s)
    - Excellent general knowledge
    - Good at following instructions
    - Cost-effective ($2.50/1M input tokens)

    Example:
        agent = OpenAIAgent(api_key="sk-...")
        result = await agent.research_async(
            "What are the latest NBA scores?",
            ResearchDomain.SPORTS
        )
        print(result.answer)
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "gpt-4o"
    ):
        """
        Initialize OpenAI GPT-4o research agent.

        Args:
            api_key: OpenAI API key
            model_name: Model to use (default: gpt-4o)

        Learning: AsyncOpenAI provides native async support!
        """
        super().__init__(api_key, model_name)

        # Use async client for non-blocking API calls
        self.client = AsyncOpenAI(api_key=api_key)

        print(f"✓ OpenAIAgent initialized with {model_name}")

    async def research_async(
        self,
        query: str,
        domain: ResearchDomain,
        max_tokens: Optional[int] = 500
    ) -> ResearchResponse:
        """
        Conduct research using GPT-4o asynchronously.

        Args:
            query: Research question
            domain: Research domain
            max_tokens: Maximum response length

        Returns:
            ResearchResponse: Structured research findings

        Learning: async/await allows this to run concurrently with other agents!
        """

        print(f"\n{'='*60}")
        print(f"🔍 [GPT-4o] Researching: {query}")
        print(f"📂 Domain: {domain.value}")
        print(f"{'='*60}")

        # Build the prompt
        system_prompt = self._build_system_prompt(domain)
        user_prompt = self._construct_research_prompt(query)

        try:
            # Call OpenAI API asynchronously
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )

            # Extract the answer
            answer = response.choices[0].message.content

            # Parse the response
            parsed_data = self._parse_response(answer, query)

            # Get token usage
            tokens_used = response.usage.total_tokens

            # Create structured response
            research_response = ResearchResponse(
                query=query,
                answer=parsed_data['answer'],
                domain=domain,
                confidence=parsed_data['confidence'],
                key_points=parsed_data['key_points'],
                sources=parsed_data.get('sources'),
                model_name=self.model_name,
                timestamp=datetime.now(),
                tokens_used=tokens_used
            )

            print(f"✅ [GPT-4o] Research completed")
            print(f"📊 Tokens used: {tokens_used}")
            print(f"📈 Confidence: {research_response.confidence.value}")

            return research_response

        except Exception as e:
            print(f"❌ [GPT-4o] Research failed: {e}")
            raise

    def _construct_research_prompt(self, query: str) -> str:
        """
        Build the user prompt for GPT-4o.

        Args:
            query: User's research question

        Returns:
            str: Formatted prompt requesting structured output
        """

        prompt = f"""{query}

Please provide a comprehensive research response with the following structure:

1. ANSWER: A clear, detailed answer to the query (2-4 sentences)

2. KEY POINTS: List 3-5 main takeaways as bullet points

3. CONFIDENCE: Rate your confidence as one of: low, medium, high, very_high

4. SOURCES (optional): If you can reference specific sources, list them

Format your response clearly with these sections labeled.
"""
        return prompt

    def _parse_response(self, response_text: str, query: str) -> dict:
        """
        Parse GPT-4o's text response into structured data.

        Args:
            response_text: Raw text from GPT-4o
            query: Original query

        Returns:
            dict: Parsed components (answer, key_points, confidence, sources)

        Learning: Text parsing is common when working with LLMs.
        Future: Could use JSON mode or structured outputs for cleaner parsing.
        """

        lines = response_text.split('\n')

        answer_lines = []
        key_points = []
        confidence = ConfidenceLevel.MEDIUM  # default
        sources = []

        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect sections
            upper_line = line.upper()
            if 'ANSWER' in upper_line or line.startswith('1.'):
                current_section = 'answer'
                continue
            elif 'KEY POINTS' in upper_line or 'KEY POINT' in upper_line or line.startswith('2.'):
                current_section = 'key_points'
                continue
            elif 'CONFIDENCE' in upper_line or line.startswith('3.'):
                current_section = 'confidence'
                # Extract confidence level
                for level in ['very_high', 'high', 'medium', 'low']:
                    if level.replace('_', ' ') in line.lower() or level in line.lower():
                        confidence = ConfidenceLevel(level)
                        break
                continue
            elif 'SOURCE' in upper_line or line.startswith('4.'):
                current_section = 'sources'
                continue

            # Add content to current section
            if current_section == 'answer':
                answer_lines.append(line)
            elif current_section == 'key_points':
                # Remove bullet points and numbering
                cleaned = line.lstrip('•-*0123456789. ')
                if cleaned:
                    key_points.append(cleaned)
            elif current_section == 'sources':
                if line.startswith('http') or 'www.' in line:
                    sources.append(line)

        # Combine answer lines
        answer = ' '.join(answer_lines).strip()

        # If parsing failed, use the whole response as answer
        if not answer:
            answer = response_text

        # Ensure we have at least some key points
        if not key_points:
            sentences = answer.split('.')[:3]
            key_points = [s.strip() + '.' for s in sentences if s.strip()]

        return {
            'answer': answer,
            'key_points': key_points[:5],  # Limit to 5 points
            'confidence': confidence,
            'sources': sources if sources else None
        }


# Example usage
if __name__ == "__main__":
    """
    Test the OpenAI agent directly.

    Run: python -m src.agents.openai_agent
    """
    import os
    import asyncio
    from dotenv import load_dotenv

    load_dotenv()

    async def test():
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not found in .env")
            return

        # Create agent
        agent = OpenAIAgent(api_key=api_key)

        # Test query
        result = await agent.research_async(
            query="What are the health benefits of regular exercise?",
            domain=ResearchDomain.HEALTHCARE
        )

        # Display results
        print("\n" + "="*60)
        print("RESEARCH RESULTS")
        print("="*60)
        print(f"\nQuery: {result.query}")
        print(f"Domain: {result.domain.value}")
        print(f"\nAnswer:\n{result.answer}")
        print(f"\nKey Points:")
        for i, point in enumerate(result.key_points, 1):
            print(f"  {i}. {point}")
        print(f"\nConfidence: {result.confidence.value}")
        print(f"Tokens Used: {result.tokens_used}")

    # Run async test
    asyncio.run(test())
