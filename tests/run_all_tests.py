"""
Combined Model Connection Test Runner
====================================
This script runs all model connection tests at once.

Learning Point:
- How to organize and run multiple tests
- Import and reuse test functions from other modules
"""

import sys

# Import our test functions
from test_openai_connection import test_openai_connection
from test_gemini_connection import test_gemini_connection


def main():
    """Run all connection tests and report results."""

    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "LLM COUNCIL - CONNECTION TESTS" + " " * 16 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")

    results = {}

    # Test 1: OpenAI
    print("Test 1/2: OpenAI")
    results['openai'] = test_openai_connection()
    print("\n")

    # Test 2: Gemini
    print("Test 2/2: Gemini")
    results['gemini'] = test_gemini_connection()
    print("\n")

    # Summary Report
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 20 + "TEST SUMMARY" + " " * 26 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    for model, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {model.upper():15} {status}")

    print()

    # Overall result
    all_passed = all(results.values())
    if all_passed:
        print("🎉 All model connections are working!")
        print("\n✨ You're ready to move to Milestone 1.2:")
        print("   → Single Agent Research with Claude")
        return 0
    else:
        print("⚠️  Some connections failed. Please check errors above.")
        print("\n💡 Next steps:")
        print("   1. Verify API keys in .env file")
        print("   2. Check you have credits/quota for each service")
        print("   3. Ensure packages are installed: pip install -e .")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
