"""
Base Research Agent
===================
Abstract base class that defines the interface for all AI research agents.

Learning Points:
- Abstract Base Classes (ABC): Enforce that all agents implement specific methods
- Type hints: Make code more maintainable and catch errors early
- Docstrings: Document your code for others (and future you!)

Why use a base class?
- Consistency: All agents work the same way
- Flexibility: Easy to add new AI models later
- Testing: Can mock agents for unit tests
"""

from abc import ABC, abstractmethod
from typing import Optional
import asyncio
from src.models.schemas import ResearchResponse, ResearchDomain


class BaseResearchAgent(ABC):
    """
    Abstract base class for all research agents.

    Any new AI model (GPT, Claude, Gemini, etc.) must extend this class
    and implement the research() method.

    Why ABC?
    - Forces all agents to implement research()
    - Python will raise an error if you forget to implement it
    - Makes your code predictable and consistent

    Example:
        class MyAgent(BaseResearchAgent):
            def research(self, query: str, domain: ResearchDomain) -> ResearchResponse:
                # Your implementation here
                pass
    """

    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the research agent.

        Args:
            api_key: API key for the AI service
            model_name: Specific model to use (e.g., "gemini-2.5-flash")

        Learning: __init__ is the constructor - runs when you create an agent
        """
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    async def research_async(
        self,
        query: str,
        domain: ResearchDomain,
        max_tokens: Optional[int] = 500
    ) -> ResearchResponse:
        """
        Conduct research asynchronously on a query and return structured results.

        This is an abstract method - each agent MUST implement it!

        Args:
            query: The research question to answer
            domain: Which domain (sports/finance/shopping/healthcare)
            max_tokens: Maximum response length (controls cost and length)

        Returns:
            ResearchResponse: Structured research findings

        Raises:
            Exception: If the API call fails

        Learning: async/await allows concurrent execution without blocking!
        Using asyncio is the modern Python way for I/O-bound operations.
        """
        pass

    def research(
        self,
        query: str,
        domain: ResearchDomain,
        max_tokens: Optional[int] = 500
    ) -> ResearchResponse:
        """
        Synchronous wrapper around research_async for backwards compatibility.

        Runs the async research method in an event loop.

        Args:
            query: The research question to answer
            domain: Which domain (sports/finance/shopping/healthcare)
            max_tokens: Maximum response length (controls cost and length)

        Returns:
            ResearchResponse: Structured research findings

        Learning: This allows using agents in both sync and async contexts!
        """
        return asyncio.run(self.research_async(query, domain, max_tokens))

    def _build_system_prompt(self, domain: ResearchDomain) -> str:
        """
        Build a system prompt tailored to the research domain.

        System prompts guide the AI's behavior and expertise level.

        Args:
            domain: The research domain

        Returns:
            str: A specialized system prompt

        Learning: The underscore prefix (_build) means this is a "private" method
        meant for internal use only. It's a Python convention, not enforced.
        """

        # Domain-specific instructions
        domain_instructions = {
            ResearchDomain.SPORTS: """
You are a sports research expert. Provide accurate, up-to-date information about:
- Game scores and statistics
- Player performances and records
- Team standings and rankings
- Sports news and analysis

Focus on facts and verifiable data.
""",
            ResearchDomain.FINANCE: """
You are a financial research analyst. Provide informed insights about:
- Market trends and stock performance
- Economic indicators and forecasts
- Investment opportunities and risks
- Financial news and analysis

Always mention that this is for informational purposes, not financial advice.
""",
            ResearchDomain.SHOPPING: """
You are a product research specialist. Help users make informed purchasing decisions by providing:
- Product comparisons and reviews
- Price trends and value analysis
- Feature breakdowns
- Pros and cons of different options

Be objective and highlight both positives and negatives.
""",
            ResearchDomain.HEALTHCARE: """
You are a health information researcher. Provide evidence-based information about:
- General health topics and wellness
- Treatment options and approaches
- Medical research summaries
- Health trends and recommendations

ALWAYS emphasize that this is educational information, not medical advice.
Recommend consulting healthcare professionals for personal medical decisions.
"""
        }

        base_prompt = domain_instructions.get(
            domain,
            "You are a helpful research assistant. Provide accurate, well-researched answers."
        )

        # Common instructions for all domains
        base_prompt += """

Research Guidelines:
1. Be concise but thorough
2. Focus on the most relevant and recent information
3. Provide 3-5 key points as takeaways
4. Rate your confidence level honestly
5. If you're uncertain, say so
"""

        return base_prompt.strip()

    def __repr__(self) -> str:
        """
        String representation of the agent.

        Learning: __repr__ is called when you print() an object
        """
        return f"{self.__class__.__name__}(model='{self.model_name}')"


# Example of what NOT to do (Python will prevent this)
if __name__ == "__main__":
    """
    This demonstrates why abstract classes are useful.
    """
    print("This module defines the BaseResearchAgent abstract class.")
    print("\nYou cannot instantiate it directly:")
    print("  agent = BaseResearchAgent(...)  # ❌ This raises TypeError!")
    print("\nYou must create a subclass that implements research():")
    print("  class GeminiAgent(BaseResearchAgent):")
    print("      def research(self, query, domain):")
    print("          # Implementation here")
    print("\n  agent = GeminiAgent(...)  # ✅ This works!")
