"""
Demo: Enhanced Finance Research with Tools

Shows the difference between:
1. Old approach: Generic LLM knowledge only
2. New approach: Dynamic prompts + Real-time Yahoo Finance data
"""

import asyncio
import os
from dotenv import load_dotenv

from src.agents.openai_agent import OpenAIAgent
from src.models.schemas import ResearchDomain

load_dotenv()


async def test_finance_research():
    """Test finance research with tool augmentation."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        return

    print("=" * 80)
    print("🚀 ENHANCED FINANCE RESEARCH DEMO")
    print("=" * 80)

    # Create enhanced agent
    agent = OpenAIAgent(api_key=api_key, use_tools=True)

    # Test queries
    test_queries = [
        {
            "query": "What's the current price of AAPL stock?",
            "domain": ResearchDomain.FINANCE
        },
        {
            "query": "How are the major market indices performing today?",
            "domain": ResearchDomain.FINANCE
        },
        {
            "query": "Compare TSLA and MSFT stock prices",
            "domain": ResearchDomain.FINANCE
        }
    ]

    for i, test in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {test['query']}")
        print(f"{'='*80}")

        result = await agent.research_async(
            query=test['query'],
            domain=test['domain'],
            max_tokens=500
        )

        print(f"\n📊 RESULTS:")
        print(f"{'='*80}")
        print(f"\n✨ Answer:\n{result.answer}\n")
        print(f"🔑 Key Points:")
        for j, point in enumerate(result.key_points, 1):
            print(f"   {j}. {point}")
        print(f"\n📈 Confidence: {result.confidence.value}")
        print(f"🔧 Tools Used: {result.tools_used or 'None'}")
        print(f"💰 Tokens: {result.tokens_used}")

        if result.tool_results:
            print(f"\n📊 Tool Results:")
            for tool_name, tool_data in result.tool_results.items():
                print(f"   • {tool_name}: {list(tool_data.keys())}")

    print(f"\n{'='*80}")
    print("🎉 DEMO COMPLETE!")
    print("=" * 80)
    print("\n💡 Notice how the agent now:")
    print("   ✅ Uses domain-specific finance expertise")
    print("   ✅ Fetches real-time stock prices from Yahoo Finance")
    print("   ✅ Cites specific numbers and data")
    print("   ✅ Provides professional financial disclaimers")


if __name__ == "__main__":
    asyncio.run(test_finance_research())
