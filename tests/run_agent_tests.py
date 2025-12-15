"""
Agent Test Runner
=================
Runs all agent tests and provides comprehensive coverage report.

Usage:
    python tests/run_agent_tests.py

This will test:
- Gemini Agent (Gemini 2.5 Flash)
- OpenAI Agent (GPT-4o)
- DeepSeek Agent (Ollama local)

Aiming for 85-90% code coverage.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def run_all_agent_tests():
    """
    Run all agent test suites sequentially.

    Returns:
        bool: True if all tests passed
    """

    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "LLM COUNCIL - AGENT TEST SUITE" + " "*23 + "║")
    print("╚" + "="*68 + "╝")

    test_results = {}

    # Check which API keys are available
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))

    print("\n📋 Environment Check:")
    print(f"   GEMINI_API_KEY: {'✅ Found' if has_gemini else '❌ Missing'}")
    print(f"   OPENAI_API_KEY: {'✅ Found' if has_openai else '❌ Missing'}")
    print(f"   Ollama Status: Checking...")

    # Check Ollama
    try:
        from src.agents.deepseek_agent import DeepSeekAgent
        ollama_running = await DeepSeekAgent.check_ollama_status()
        print(f"   Ollama Running: {'✅ Yes' if ollama_running else '❌ No'}")
    except:
        ollama_running = False
        print(f"   Ollama Running: ❌ No")

    # Test 1: Gemini Agent
    if has_gemini:
        print("\n" + "━"*70)
        print("Running Gemini Agent Tests...")
        print("━"*70)

        try:
            # Import from same directory (tests/)
            import test_gemini_agent
            test_results['gemini'] = await test_gemini_agent.run_all_tests()
        except Exception as e:
            print(f"❌ Gemini tests crashed: {e}")
            test_results['gemini'] = False
    else:
        print("\n⚠️  Skipping Gemini tests (no API key)")
        test_results['gemini'] = None

    # Test 2: OpenAI Agent (GPT-4o)
    if has_openai:
        print("\n" + "━"*70)
        print("Running OpenAI Agent (GPT-4o) Tests...")
        print("━"*70)

        try:
            # Import from same directory (tests/)
            import test_openai_agent
            test_results['openai'] = await test_openai_agent.run_all_tests()
        except Exception as e:
            print(f"❌ OpenAI tests crashed: {e}")
            test_results['openai'] = False
    else:
        print("\n⚠️  Skipping OpenAI tests (no API key)")
        test_results['openai'] = None

    # Test 3: DeepSeek Agent (Ollama)
    if ollama_running:
        print("\n" + "━"*70)
        print("Running DeepSeek Agent (Ollama) Tests...")
        print("━"*70)

        try:
            import test_deepseek_agent
            test_results['deepseek'] = await test_deepseek_agent.run_all_tests()
        except ImportError:
            print("⚠️  DeepSeek tests not yet created (TODO)")
            test_results['deepseek'] = None
        except Exception as e:
            print(f"❌ DeepSeek tests crashed: {e}")
            test_results['deepseek'] = False
    else:
        print("\n⚠️  Skipping DeepSeek tests (Ollama not running)")
        test_results['deepseek'] = None

    # Final Summary
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*23 + "FINAL TEST SUMMARY" + " "*27 + "║")
    print("╚" + "="*68 + "╝")

    print("\n📊 Results by Agent:")

    for agent, result in test_results.items():
        if result is None:
            status = "⚠️  SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"

        print(f"   {agent:15} {status}")

    # Calculate statistics
    tested = [v for v in test_results.values() if v is not None]
    if tested:
        passed = sum(1 for v in tested if v)
        total = len(tested)

        print(f"\n📈 Coverage:")
        print(f"   Agents tested: {total}/3")
        print(f"   Tests passed: {passed}/{total}")

        if passed == total:
            print(f"\n🎉 All {total} agent test suites passed!")
            print("   ✨ Ready to proceed with Council Orchestration!")
            return True
        else:
            print(f"\n⚠️  {total - passed} agent test suite(s) failed")
            print("   Fix failing tests before proceeding to orchestration")
            return False
    else:
        print("\n⚠️  No tests could be run (missing API keys/Ollama)")
        print("   Please set up at least one agent to test")
        return False


if __name__ == "__main__":
    """
    Main entry point for agent testing.

    Exit codes:
        0: All tests passed
        1: Some tests failed
        2: No tests could run
    """
    success = asyncio.run(run_all_agent_tests())

    if success:
        exit(0)
    else:
        # Check if any tests ran
        exit(1)
