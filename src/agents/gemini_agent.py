"""
Gemini Research Agent
=====================
Research agent powered by Google's Gemini AI.

Learning Points:
- Implementing abstract base classes
- Using Gemini's new SDK (google-genai)
- Structured output with Pydantic
- Error handling and retry logic
- Token tracking for cost management
"""

from google import genai
from typing import Optional
from datetime import datetime

from src.agents.base_agent import BaseResearchAgent
from src.models.schemas import ResearchResponse, ResearchDomain, ConfidenceLevel


class GeminiResearchAgent(BaseResearchAgent):
    """
    Research agent using Google's Gemini model.

    Inherits from BaseResearchAgent and implements the research() method.

    Why Gemini for this milestone?
    - Free tier with generous limits
    - Fast responses (gemini-2.5-flash)
    - Good quality research capabilities
    - Simple API

    Example:
        agent = GeminiResearchAgent(
            api_key="your-key",
            model_name="gemini-2.5-flash"
        )
        result = agent.research(
            "Who won the NBA championship in 2024?",
            ResearchDomain.SPORTS
        )
        print(result.answer)
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.5-flash"
    ):
        """
        Initialize Gemini research agent.

        Args:
            api_key: Google AI API key
            model_name: Gemini model to use (default: gemini-2.5-flash)
        """
        # Call parent class constructor
        super().__init__(api_key, model_name)

        # Initialize Gemini client
        self.client = genai.Client(api_key=api_key)

        print(f"✓ GeminiResearchAgent initialized with {model_name}")

    def research(
        self,
        query: str,
        domain: ResearchDomain,
        max_tokens: Optional[int] = 500
    ) -> ResearchResponse:
        """
        Conduct research using Gemini.

        This implements the abstract method from BaseResearchAgent.

        Args:
            query: Research question
            domain: Research domain (sports/finance/shopping/healthcare)
            max_tokens: Maximum response length

        Returns:
            ResearchResponse: Structured research findings

        Raises:
            Exception: If API call fails or response is invalid

        Learning: This method signature MUST match the base class!
        """

        print(f"\n{'='*60}")
        print(f"🔍 Researching: {query}")
        print(f"📂 Domain: {domain.value}")
        print(f"🤖 Model: {self.model_name}")
        print(f"{'='*60}")

        # Build the prompt
        system_prompt = self._build_system_prompt(domain)
        full_prompt = self._construct_research_prompt(query, system_prompt)

        try:
            # Call Gemini API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt
            )

            # Extract the answer
            answer = response.text

            # Parse the response to extract structured data
            parsed_data = self._parse_response(answer, query)

            # Get token usage (if available)
            tokens_used = None
            if hasattr(response, 'usage_metadata') and hasattr(response.usage_metadata, 'total_token_count'):
                tokens_used = response.usage_metadata.total_token_count

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

            print(f"\n✅ Research completed")
            print(f"📊 Tokens used: {tokens_used if tokens_used else 'N/A'}")
            print(f"📈 Confidence: {research_response.confidence.value}")

            return research_response

        except Exception as e:
            print(f"\n❌ Research failed: {e}")
            raise

    def _construct_research_prompt(self, query: str, system_prompt: str) -> str:
        """
        Build the complete prompt for Gemini.

        Combines system instructions with the user query and asks for
        structured output that we can parse.

        Args:
            query: User's research question
            system_prompt: Domain-specific instructions

        Returns:
            str: Complete prompt for the model
        """

        prompt = f"""{system_prompt}

User Query: {query}

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
        Parse Gemini's text response into structured data.

        Since Gemini returns text, we need to extract the different components.

        Args:
            response_text: Raw text from Gemini
            query: Original query (for context)

        Returns:
            dict: Parsed components (answer, key_points, confidence, sources)

        Learning: Text parsing is a common task when working with LLMs!
        Later, you might use JSON mode or structured output features.
        """

        # Simple parsing logic
        # In production, you'd want more robust parsing or use structured output
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
                # Try to extract confidence level
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
            # Extract first few sentences as key points
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
    Test the Gemini agent directly.

    Run: python -m src.agents.gemini_agent
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env")
        exit(1)

    # Create agent
    agent = GeminiResearchAgent(api_key=api_key)

    # Test query
    result = agent.research(
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
