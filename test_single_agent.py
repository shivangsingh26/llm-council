"""
Single Agent Research Test
===========================
Test the Gemini research agent across all 4 domains.

This is Milestone 1.2: Single Agent Research

Run: python test_single_agent.py

Learning Goals:
- See how Pydantic structures work in practice
- Understand domain-specific prompting
- Learn to evaluate AI research quality
- Track token usage and costs
"""

import os
from dotenv import load_dotenv

from src.agents.gemini_agent import GeminiResearchAgent
from src.models.schemas import ResearchDomain
from src.utils.output_manager import OutputManager

# Load API keys
load_dotenv()


def print_result(result, domain_name: str):
    """
    Pretty-print a research result.

    Args:
        result: ResearchResponse object
        domain_name: Name of the domain for display
    """
    print("\n" + "="*70)
    print(f"📊 {domain_name.upper()} DOMAIN RESEARCH")
    print("="*70)
    print(f"\n❓ Query: {result.query}")
    print(f"\n💡 Answer:\n{result.answer}")
    print(f"\n🎯 Key Points:")
    for i, point in enumerate(result.key_points, 1):
        print(f"   {i}. {point}")
    print(f"\n📈 Confidence: {result.confidence.value.upper()}")
    if result.sources:
        print(f"\n📚 Sources:")
        for source in result.sources:
            print(f"   • {source}")
    print(f"\n⚙️  Metadata:")
    print(f"   Model: {result.model_name}")
    print(f"   Tokens: {result.tokens_used if result.tokens_used else 'N/A'}")
    print(f"   Time: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """
    Main test function - runs research queries across all 4 domains.
    """

    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "MILESTONE 1.2: SINGLE AGENT RESEARCH" + " "*17 + "║")
    print("╚" + "="*68 + "╝")

    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n❌ ERROR: GEMINI_API_KEY not found in .env file")
        print("Please add your Gemini API key to continue.")
        return

    # Initialize agent
    print("\n🚀 Initializing Gemini Research Agent...")
    agent = GeminiResearchAgent(api_key=api_key)

    # Initialize output manager for saving results
    print("\n💾 Initializing Output Manager...")
    output_manager = OutputManager()

    # Test queries for each domain
    test_queries = {
        ResearchDomain.SPORTS: "What were the highlights from the latest FIFA World Cup?",

        ResearchDomain.FINANCE: "What are the current trends in the cryptocurrency market?",

        ResearchDomain.SHOPPING: "What are the best budget smartphones available in 2024?",

        ResearchDomain.HEALTHCARE: "What are the proven benefits of a Mediterranean diet?"
    }

    results = []
    successful = 0
    failed = 0

    print("\n📋 Testing across 4 domains...")
    print("   This will make 4 API calls to Gemini.")

    # Run research for each domain
    for domain, query in test_queries.items():
        try:
            result = agent.research(query=query, domain=domain)
            print_result(result, domain.value)
            results.append(result)
            successful += 1

            # Save result to JSON file
            try:
                saved_path = output_manager.save_research(result)
                print(f"   💾 Saved to: {saved_path.relative_to(output_manager.base_dir)}")
            except Exception as save_error:
                print(f"   ⚠️  Failed to save output: {save_error}")

        except Exception as e:
            print(f"\n❌ Failed to research {domain.value}: {e}")
            failed += 1

        # Add a small separator
        print("\n" + "-"*70)

    # Summary
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*25 + "TEST SUMMARY" + " "*31 + "║")
    print("╚" + "="*68 + "╝")

    print(f"\n✅ Successful queries: {successful}/4")
    if failed > 0:
        print(f"❌ Failed queries: {failed}/4")

    # Token usage summary
    total_tokens = sum(r.tokens_used for r in results if r.tokens_used)
    if total_tokens > 0:
        print(f"\n📊 Total tokens used: {total_tokens}")
        print(f"💰 Estimated cost: ~${total_tokens * 0.00001:.4f} (Gemini is very cheap!)")

    # Confidence analysis
    confidence_counts = {}
    for result in results:
        conf = result.confidence.value
        confidence_counts[conf] = confidence_counts.get(conf, 0) + 1

    print(f"\n📈 Confidence Breakdown:")
    for conf, count in sorted(confidence_counts.items()):
        print(f"   {conf}: {count} queries")

    # Domain analysis
    print(f"\n📂 Domains Tested:")
    for result in results:
        print(f"   • {result.domain.value}: {len(result.key_points)} key points")

    # Output statistics
    if successful > 0:
        print(f"\n💾 Output Files:")
        stats = output_manager.get_statistics()
        print(f"   Total saved: {stats['total_outputs']}")
        print(f"   Location: {output_manager.base_dir.absolute()}")
        print(f"\n   Files by domain:")
        for domain, count in stats['by_domain'].items():
            if count > 0:
                print(f"     • {domain}/: {count} files")

    # Next steps
    if successful == 4:
        print("\n" + "="*70)
        print("🎉 MILESTONE 1.2 COMPLETE!")
        print("="*70)
        print("\n✨ What you've accomplished:")
        print("   ✓ Built structured schemas with Pydantic")
        print("   ✓ Created base agent architecture")
        print("   ✓ Implemented Gemini research agent")
        print("   ✓ Tested across all 4 domains")
        print("   ✓ Validated structured outputs")
        print("   ✓ Saved all outputs to organized JSON files")
        print("\n🚀 Ready for Milestone 2.1: Multi-Model Council")
        print("   Next: Add OpenAI and Anthropic agents for comparison!")
    else:
        print("\n⚠️  Some queries failed. Check errors above.")
        print("💡 Common issues:")
        print("   - API key issues")
        print("   - Network connectivity")
        print("   - Rate limits")

    print("\n" + "="*70)

if __name__ == "__main__":
    main()
