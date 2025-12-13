"""
Gemini Connection Test Script (2025 - Latest SDK)
=================================================
This script tests your Google Gemini API connection using the NEW google-genai SDK.

Learning Points:
- NEW google-genai SDK (released 2024-2025)
- Client-based pattern (similar to OpenAI)
- Environment variable: GEMINI_API_KEY
- Latest model: gemini-2.5-flash
- Simpler API compared to old google-generativeai
"""

import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()


def test_gemini_connection():
    """
    Test Google Gemini API connection using the NEW SDK.

    Key Changes in New SDK (2025):
    - Package: google-genai (not google-generativeai)
    - Import: from google import genai
    - Client pattern: genai.Client()
    - Env variable: GEMINI_API_KEY (not GOOGLE_API_KEY)
    - Method: client.models.generate_content()
    """

    print("=" * 60)
    print("Testing Google Gemini API Connection (NEW SDK)")
    print("=" * 60)

    # Step 1: Get API key from environment
    # NEW: Environment variable is now GEMINI_API_KEY
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in .env file")
        print("Please add: GEMINI_API_KEY=your-key-here to your .env file")
        print("\nGet your key from: https://aistudio.google.com/apikey")
        return False

    print(f"✓ API Key found (ends with: ...{api_key[-4:]})")

    # Step 2: Initialize Gemini Client
    # NEW: Client-based pattern (similar to OpenAI)
    try:
        client = genai.Client(api_key=api_key)
        print("✓ Gemini client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return False

    # Step 3: Generate content
    try:
        print("\n" + "-" * 60)
        print("Sending test message to gemini-2.5-flash...")
        print("-" * 60)

        # NEW: Simple generate_content method
        # The API is much cleaner now - just model name and contents
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say hello and confirm you're working! Respond in one sentence."
        )

        # Extract response text
        # Response structure is simpler now
        ai_response = response.text

        print("\n🤖 Model Response:")
        print(f"   {ai_response}")

        # The new SDK has a cleaner response structure
        print(f"\n📊 Response Metadata:")
        print(f"   Model used: gemini-2.5-flash")
        print(f"   Response received: ✓")

        # Usage information (if available in response)
        # Note: The new SDK may have different metadata structure
        try:
            if hasattr(response, 'usage_metadata'):
                print(f"\n📝 Token Usage:")
                usage = response.usage_metadata
                if hasattr(usage, 'prompt_token_count'):
                    print(f"   Prompt tokens: {usage.prompt_token_count}")
                if hasattr(usage, 'candidates_token_count'):
                    print(f"   Response tokens: {usage.candidates_token_count}")
                if hasattr(usage, 'total_token_count'):
                    print(f"   Total tokens: {usage.total_token_count}")
        except Exception as e:
            print(f"\n📝 Usage metadata not available in this response")

        print("\n✅ Gemini connection successful!")
        return True

    except Exception as e:
        print(f"\n❌ API call failed: {e}")
        print("\nCommon issues:")
        print("  - Invalid API key")
        print("  - Wrong environment variable (use GEMINI_API_KEY)")
        print("  - Network connectivity")
        print("  - Model not available in your region")
        print("  - Old SDK installed (run: pip install -U google-genai)")
        return False


if __name__ == "__main__":
    success = test_gemini_connection()

    if success:
        print("\n" + "=" * 60)
        print("🎉 All Gemini tests passed!")
        print("=" * 60)
        print("\n💡 What's New in This SDK:")
        print("   - Simpler client-based API")
        print("   - Better alignment with OpenAI patterns")
        print("   - gemini-2.5-flash model (latest)")
        print("   - Cleaner response structure")
    else:
        print("\n" + "=" * 60)
        print("⚠️  Gemini tests failed - check errors above")
        print("=" * 60)
