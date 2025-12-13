"""
OpenAI Connection Test Script (2025 - Latest Patterns)
=====================================================
This script tests your OpenAI API connection using both the NEW Responses API
and the traditional Chat Completions API.

Learning Points:
- NEW Responses API (recommended for simple tasks)
- Chat Completions API (still fully supported, better for conversations)
- Error handling with request IDs
- Built-in retry logic
- Token usage tracking
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
# This keeps your API keys secret and out of your code
load_dotenv()


def test_openai_responses_api():
    """
    Test OpenAI's NEW Responses API (2025 recommended approach).

    The Responses API is:
    - Simpler for single-turn interactions
    - Optimized for common use cases
    - Easier to use than Chat Completions for simple tasks

    When to use: Quick lookups, simple Q&A, single-shot tasks
    """

    print("\n" + "=" * 60)
    print("Test 1: OpenAI Responses API (NEW)")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in .env file")
        return False

    print(f"✓ API Key found (ends with: ...{api_key[-4:]})")

    try:
        client = OpenAI(api_key=api_key)
        print("✓ OpenAI client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return False

    try:
        print("\n" + "-" * 60)
        print("Sending test via Responses API...")
        print("-" * 60)

        # NEW Responses API - Much simpler!
        # Just pass your input directly, no message formatting needed
        response = client.responses.create(
            model="gpt-4o-mini",
            input="Say hello and confirm you're working! Respond in one sentence."
        )

        # Extract response - simple .output_text attribute
        ai_response = response.output_text

        print("\n🤖 Model Response:")
        print(f"   {ai_response}")

        # NEW: Request ID for debugging and support
        # Every response includes a unique ID for troubleshooting
        print(f"\n🔍 Request ID: {response._request_id}")
        print("   (Use this ID when reporting issues to OpenAI)")

        print("\n✅ Responses API test successful!")
        return True

    except Exception as e:
        print(f"\n❌ Responses API call failed: {e}")
        if hasattr(e, 'response'):
            print(f"Request ID: {getattr(e.response, '_request_id', 'N/A')}")
        return False


def test_openai_chat_completions_api():
    """
    Test OpenAI's Chat Completions API (traditional, still fully supported).

    The Chat Completions API is:
    - Better for multi-turn conversations
    - Supports system/user/assistant roles
    - More control over conversation flow

    When to use: Chatbots, multi-agent systems, complex conversations
    This is what you'll use for your AI Research Council!
    """

    print("\n" + "=" * 60)
    print("Test 2: OpenAI Chat Completions API (Traditional)")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in .env file")
        return False

    try:
        client = OpenAI(api_key=api_key)
        print("✓ Client initialized with retry logic (2 retries by default)")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return False

    try:
        print("\n" + "-" * 60)
        print("Sending test via Chat Completions API...")
        print("-" * 60)

        # Chat Completions API - More powerful message structure
        # Roles: "system" (instructions), "user" (input), "assistant" (AI)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant in a research council. Be concise."
                },
                {
                    "role": "user",
                    "content": "Say hello and confirm you're working! Respond in one sentence."
                }
            ],
            max_tokens=50,
            temperature=0.7
        )

        # Extract response from the message structure
        ai_response = response.choices[0].message.content

        print("\n🤖 Model Response:")
        print(f"   {ai_response}")

        # Token usage - important for cost tracking!
        print(f"\n📊 Token Usage:")
        print(f"   Input tokens:  {response.usage.prompt_tokens}")
        print(f"   Output tokens: {response.usage.completion_tokens}")
        print(f"   Total tokens:  {response.usage.total_tokens}")

        # Finish reason tells you WHY the model stopped
        print(f"\n🏁 Finish Reason: {response.choices[0].finish_reason}")
        print("   'stop' = natural completion")
        print("   'length' = hit max_tokens limit")

        # Request ID for troubleshooting
        print(f"\n🔍 Request ID: {response._request_id}")

        print("\n✅ Chat Completions API test successful!")
        return True

    except Exception as e:
        print(f"\n❌ Chat Completions API call failed: {e}")
        if hasattr(e, 'response'):
            print(f"Request ID: {getattr(e.response, '_request_id', 'N/A')}")
        return False


def test_openai_connection():
    """
    Run both API tests and return overall result.
    """

    print("=" * 60)
    print("Testing OpenAI API Connection (2025 Best Practices)")
    print("=" * 60)

    # Test both APIs
    responses_result = test_openai_responses_api()
    chat_result = test_openai_chat_completions_api()

    # Summary
    if responses_result and chat_result:
        print("\n" + "=" * 60)
        print("🎉 All OpenAI tests passed!")
        print("=" * 60)
        print("\n💡 Which API should you use?")
        print("   • Responses API: Simple tasks, quick lookups")
        print("   • Chat Completions: Conversations, multi-agent (YOUR PROJECT!)")
        return True
    else:
        print("\n" + "=" * 60)
        print("⚠️  Some OpenAI tests failed")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_openai_connection()

    if not success:
        print("\n💡 Common issues:")
        print("  - Invalid API key")
        print("  - Insufficient credits")
        print("  - Network connectivity")
        print("  - Rate limits (retry automatically happens)")
