"""
OpenAI GPT-5 Research Agent
============================
Research agent powered by OpenAI's GPT-5 model (latest flagship model).

Learning Points:
- Using OpenAI's async client (AsyncOpenAI)
- Chat Completions API with async/await
- Message formatting (system/user/assistant roles)
- Token tracking and cost management
- Error handling with retries

Model: gpt-5
Strengths: State-of-the-art reasoning, excellent general knowledge, strong multimodal
Use case: General research across all domains
"""

from openai import AsyncOpenAI
from typing import Optional
from datetime import datetime
import re

from src.agents.base_agent import BaseResearchAgent
from src.models.schemas import ResearchResponse, ResearchDomain, ConfidenceLevel
from src.prompts.prompt_selector import PromptSelector
from src.tools.finance_api import FinanceAPI


class OpenAIAgent(BaseResearchAgent):
    """
    Research agent using OpenAI's GPT-5 model.

    GPT-5 is OpenAI's latest flagship model:
    - Advanced reasoning capabilities
    - Excellent general knowledge
    - Strong multimodal understanding
    - State-of-the-art performance across all domains

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
        model_name: str = "gpt-5",
        use_tools: bool = True
    ):
        """
        Initialize OpenAI GPT-5 research agent.

        Args:
            api_key: OpenAI API key
            model_name: Model to use (default: gpt-5)
            use_tools: Enable tool augmentation (default: True)

        Learning: AsyncOpenAI provides native async support!
        """
        super().__init__(api_key, model_name)

        # Use async client for non-blocking API calls
        self.client = AsyncOpenAI(api_key=api_key)

        # Initialize tools
        self.use_tools = use_tools
        self.prompt_selector = PromptSelector()
        self.finance_api = FinanceAPI() if use_tools else None

        print(f"✓ OpenAIAgent initialized with {model_name}")
        if use_tools:
            print(f"  🔧 Tools enabled: Dynamic Prompts, Finance API")

    async def research_async(
        self,
        query: str,
        domain: ResearchDomain,
        max_tokens: Optional[int] = 500
    ) -> ResearchResponse:
        """
        Conduct research using GPT-5 asynchronously with tool augmentation.

        Args:
            query: Research question
            domain: Research domain
            max_tokens: Maximum response length

        Returns:
            ResearchResponse: Structured research findings with tool results

        Learning: async/await allows this to run concurrently with other agents!
        """

        print(f"\n{'='*60}")
        print(f"🔍 [GPT-5] Researching: {query}")
        print(f"📂 Domain: {domain.value}")
        print(f"{'='*60}")

        # Step 1: Check if we should use Finance API tool
        tool_results = {}
        tools_used = []

        if self.use_tools and domain == ResearchDomain.FINANCE:
            finance_data = await self._use_finance_tools(query)
            if finance_data:
                tool_results['finance'] = finance_data
                tools_used.append('finance_api')
                print(f"  🔧 Used Finance API: {list(finance_data.keys())}")

        # Step 2: Build dynamic prompt with tool context
        available_tools = ['finance_api'] if domain == ResearchDomain.FINANCE else []
        prompts = self.prompt_selector.get_prompt(
            query=query,
            domain=domain,
            available_tools=available_tools,
            max_tokens=max_tokens
        )

        system_prompt = prompts['system']
        user_prompt = prompts['user']

        # Step 3: Add tool results to user prompt if available
        if tool_results:
            tool_context = self._format_tool_context(tool_results)
            user_prompt = f"{user_prompt}\n\n{tool_context}"

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

            # Create structured response with tool information
            research_response = ResearchResponse(
                query=query,
                answer=parsed_data['answer'],
                domain=domain,
                confidence=parsed_data['confidence'],
                key_points=parsed_data['key_points'],
                sources=parsed_data.get('sources'),
                model_name=self.model_name,
                timestamp=datetime.now(),
                tokens_used=tokens_used,
                tools_used=tools_used if tools_used else None,
                tool_results=tool_results if tool_results else None
            )

            print(f"✅ [GPT-5] Research completed")
            print(f"📊 Tokens used: {tokens_used}")
            print(f"📈 Confidence: {research_response.confidence.value}")

            return research_response

        except Exception as e:
            print(f"❌ [GPT-5] Research failed: {e}")
            raise

    async def _use_finance_tools(self, query: str) -> dict:
        """
        Use Finance API tools when query is about stocks/markets.

        Args:
            query: Research query

        Returns:
            Dict with finance data if relevant, empty dict otherwise
        """
        if not self.finance_api:
            return {}

        results = {}
        query_lower = query.lower()

        # Detect stock symbols (e.g., AAPL, TSLA, MSFT)
        stock_pattern = r'\b([A-Z]{1,5})\b'
        potential_symbols = re.findall(stock_pattern, query)

        # Common stock keywords
        if any(word in query_lower for word in ['stock', 'share', 'ticker']):
            for symbol in potential_symbols[:3]:  # Limit to 3 stocks
                try:
                    data = await self.finance_api.get_stock_price(symbol)
                    if data.get('success'):
                        results[f'stock_{symbol}'] = data
                except:
                    pass

        # Market summary keywords
        if any(word in query_lower for word in ['market', 's&p', 'dow', 'nasdaq', 'indices']):
            try:
                market_data = await self.finance_api.get_market_summary()
                if market_data.get('success'):
                    results['market_summary'] = market_data
            except:
                pass

        return results

    def _format_tool_context(self, tool_results: dict) -> str:
        """
        Format tool results for inclusion in LLM prompt.

        Args:
            tool_results: Dict of tool_name -> result_data

        Returns:
            Formatted string for prompt context
        """
        context_parts = ["\n## 📊 Real-Time Data (from tools):"]

        if 'finance' in tool_results:
            finance_data = tool_results['finance']

            for key, data in finance_data.items():
                if key.startswith('stock_'):
                    formatted = self.finance_api.format_for_prompt(data)
                    context_parts.append(f"\n{formatted}")
                elif key == 'market_summary':
                    formatted = self.finance_api.format_for_prompt(data)
                    context_parts.append(f"\n{formatted}")

        context_parts.append("\nUse this real-time data in your answer. Cite specific numbers and sources.")

        return "\n".join(context_parts)

    def _construct_research_prompt(self, query: str) -> str:
        """
        Build the user prompt for GPT-5.

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
        Parse GPT-5's text response into structured data.

        Args:
            response_text: Raw text from GPT-5
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
