"""
DeepSeek-R1 Research Agent (via Ollama)
========================================
Research agent powered by DeepSeek-R1 running locally via Ollama.

Learning Points:
- Running LLMs locally with Ollama
- OpenAI-compatible API (same client, different endpoint)
- Cost-free inference (runs on your machine)
- Privacy benefits (data stays local)
- No rate limits!

Model: deepseek-r1:14b (local)
Strengths: Free, private, reasoning capability, no API costs
Use case: Cost-effective research, sensitive data, unlimited queries
"""

from openai import AsyncOpenAI
from typing import Optional
from datetime import datetime

from src.agents.base_agent import BaseResearchAgent
from src.models.schemas import ResearchResponse, ResearchDomain, ConfidenceLevel


class DeepSeekAgent(BaseResearchAgent):
    """
    Research agent using DeepSeek-R1 running locally via Ollama.

    Why local models?
    - ✅ FREE (no API costs)
    - ✅ PRIVATE (data never leaves your machine)
    - ✅ NO RATE LIMITS (unlimited queries)
    - ✅ OFFLINE (works without internet after model download)
    - ⚠️  SLOWER (local compute vs cloud infrastructure)
    - ⚠️  REQUIRES RAM (model needs ~11GB for 14b variant)

    Ollama provides an OpenAI-compatible API:
    - Same client library (AsyncOpenAI)
    - Same message format
    - Just different base_url!

    Example:
        agent = DeepSeekAgent()  # No API key needed!
        result = await agent.research_async(
            "What are the privacy implications of AI?",
            ResearchDomain.FINANCE
        )
        print(result.answer)
    """

    def __init__(
        self,
        model_name: str = "deepseek-r1:14b",
        base_url: str = "http://localhost:11434"
    ):
        """
        Initialize DeepSeek agent for local Ollama.

        Args:
            model_name: Ollama model to use (default: deepseek-r1:14b)
            base_url: Ollama server URL (default: localhost:11434)

        Learning: No API key needed for local models!
        """
        # Call parent with dummy API key (not used by Ollama)
        super().__init__(api_key="not-needed", model_name=model_name)

        self.base_url = base_url

        # Use AsyncOpenAI with custom base_url for Ollama
        # Ollama's API is OpenAI-compatible!
        self.client = AsyncOpenAI(
            base_url=f"{base_url}/v1",  # Ollama's OpenAI-compatible endpoint
            api_key="ollama"  # Dummy key, Ollama doesn't validate it
        )

        print(f"✓ DeepSeekAgent initialized with {model_name}")
        print(f"  🏠 Running locally via Ollama at {base_url}")
        print(f"  💰 Cost: FREE (local inference)")

    async def research_async(
        self,
        query: str,
        domain: ResearchDomain,
        max_tokens: Optional[int] = 500
    ) -> ResearchResponse:
        """
        Conduct research using local DeepSeek-R1 asynchronously.

        Args:
            query: Research question
            domain: Research domain
            max_tokens: Maximum response length

        Returns:
            ResearchResponse: Structured research findings

        Learning: This runs entirely on your local machine!
        No data is sent to external servers.
        """

        print(f"\n{'='*60}")
        print(f"🏠 [DeepSeek-Local] Researching: {query}")
        print(f"📂 Domain: {domain.value}")
        print(f"💻 Running on local machine...")
        print(f"{'='*60}")

        # Build the prompt
        system_prompt = self._build_system_prompt(domain)
        user_prompt = self._construct_research_prompt(query)

        try:
            # Call Ollama API (same interface as OpenAI!)
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

            # Token usage (Ollama provides this in OpenAI format)
            tokens_used = response.usage.total_tokens if response.usage else None

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

            print(f"✅ [DeepSeek-Local] Research completed")
            print(f"📊 Tokens: {tokens_used if tokens_used else 'N/A'}")
            print(f"💰 Cost: $0.00 (local)")
            print(f"📈 Confidence: {research_response.confidence.value}")

            return research_response

        except Exception as e:
            print(f"❌ [DeepSeek-Local] Research failed: {e}")
            print(f"   💡 Is Ollama running? Try: ollama serve")
            print(f"   💡 Is model pulled? Try: ollama pull {self.model_name}")
            raise

    def _construct_research_prompt(self, query: str) -> str:
        """
        Build the user prompt for DeepSeek.

        Args:
            query: User's research question

        Returns:
            str: Formatted prompt
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
        Parse DeepSeek's response into structured data.

        Args:
            response_text: Raw text from DeepSeek
            query: Original query

        Returns:
            dict: Parsed components
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
                cleaned = line.lstrip('•-*0123456789. ')
                if cleaned:
                    key_points.append(cleaned)
            elif current_section == 'sources':
                if line.startswith('http') or 'www.' in line:
                    sources.append(line)

        # Combine answer lines
        answer = ' '.join(answer_lines).strip()

        if not answer:
            answer = response_text

        if not key_points:
            sentences = answer.split('.')[:3]
            key_points = [s.strip() + '.' for s in sentences if s.strip()]

        return {
            'answer': answer,
            'key_points': key_points[:5],
            'confidence': confidence,
            'sources': sources if sources else None
        }

    @staticmethod
    async def check_ollama_status() -> bool:
        """
        Check if Ollama is running and accessible.

        Returns:
            bool: True if Ollama is running and responsive

        Learning: Always good to check dependencies before using them!
        """
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:11434/api/tags")
                return response.status_code == 200
        except Exception:
            return False


# Example usage
if __name__ == "__main__":
    """
    Test the DeepSeek agent with Ollama.

    Run: python -m src.agents.deepseek_agent
    """
    import asyncio

    async def test():
        # Check if Ollama is running
        print("Checking Ollama status...")
        is_running = await DeepSeekAgent.check_ollama_status()

        if not is_running:
            print("❌ Ollama is not running!")
            print("\n💡 To start Ollama:")
            print("   1. Open a new terminal")
            print("   2. Run: ollama serve")
            print("   3. In another terminal, run: ollama pull deepseek-r1:14b")
            print("   4. Then try this test again")
            return

        print("✅ Ollama is running!\n")

        # Create agent
        agent = DeepSeekAgent()

        # Test query
        result = await agent.research_async(
            query="What are the benefits of open-source AI models?",
            domain=ResearchDomain.HEALTHCARE
        )

        # Display results
        print("\n" + "="*60)
        print("LOCAL RESEARCH RESULTS")
        print("="*60)
        print(f"\nQuery: {result.query}")
        print(f"Domain: {result.domain.value}")
        print(f"\nAnswer:\n{result.answer}")
        print(f"\nKey Points:")
        for i, point in enumerate(result.key_points, 1):
            print(f"  {i}. {point}")
        print(f"\nConfidence: {result.confidence.value}")
        print(f"Tokens Used: {result.tokens_used}")
        print(f"💰 Cost: $0.00 (local inference)")

    # Run async test
    asyncio.run(test())
