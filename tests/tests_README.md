# Connection Tests (2025 - Latest SDKs)

This directory contains test scripts to verify your AI model API connections using the **latest 2025 SDKs**.

## 🆕 What's New

### Google Gemini - NEW SDK!
- **Old**: `google-generativeai` → **New**: `google-genai`
- **Old**: `GOOGLE_API_KEY` → **New**: `GEMINI_API_KEY`
- Simpler client-based API (similar to OpenAI)
- Latest model: `gemini-2.5-flash`

### OpenAI - New Responses API
- **Responses API**: Recommended for simple tasks (NEW in 2025)
- **Chat Completions API**: Still fully supported (use this for your project!)
- Better error handling with request IDs
- Built-in retry logic (2 retries by default)

## 📋 Prerequisites

### 1. Install dependencies

```bash
# Activate your virtual environment first
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Install packages (this installs the NEW SDKs)
pip install -e .
```

### 2. Set up API keys in `.env` file

**IMPORTANT**: Update your `.env` file with the correct variable names!

```env
# OpenAI API Key
OPENAI_API_KEY=sk-...

# Google Gemini API Key (NEW variable name!)
GEMINI_API_KEY=AIza...

# Anthropic API Key (for future use)
ANTHROPIC_API_KEY=sk-ant-...
```

**Migration Note**: If you had `GOOGLE_API_KEY`, rename it to `GEMINI_API_KEY`!

### 3. Get API Keys

| Service | Get Key From | Free Tier? |
|---------|-------------|------------|
| OpenAI | https://platform.openai.com/api-keys | $5 free trial |
| Gemini | https://aistudio.google.com/apikey | ✅ Yes (generous) |
| Anthropic | https://console.anthropic.com/ | For later |

## 🧪 Running Tests

### Run All Tests (Recommended)
```bash
python tests/run_all_tests.py
```

### Run Individual Tests
```bash
# Test OpenAI (both Responses and Chat Completions APIs)
python tests/test_openai_connection.py

# Test Gemini (NEW SDK)
python tests/test_gemini_connection.py
```

## 📚 What Each Test Does

### `test_openai_connection.py` (Updated 2025)
- Tests **Responses API** (NEW - simpler for single tasks)
- Tests **Chat Completions API** (traditional - better for conversations)
- Shows token usage and cost tracking
- Demonstrates request IDs for debugging
- **Uses**: `gpt-4o-mini` (cost-effective)

### `test_gemini_connection.py` (NEW SDK 2025)
- Tests with **NEW** `google-genai` package
- Uses client-based pattern (like OpenAI)
- Shows token usage metadata
- **Uses**: `gemini-2.5-flash` (latest, free)

### `run_all_tests.py`
- Runs both tests sequentially
- Provides summary report
- Exit code 0 = all passed, 1 = some failed

## 🔍 Expected Output

**Successful test:**
```
Testing OpenAI API Connection (2025 Best Practices)
============================================================

Test 1: OpenAI Responses API (NEW)
✓ API Key found
✓ OpenAI client initialized
🤖 Model Response: Hello! I'm working perfectly!
✅ Responses API test successful!

Test 2: OpenAI Chat Completions API (Traditional)
✓ Client initialized with retry logic
🤖 Model Response: Hello! The system is operational.
📊 Token Usage: 45 tokens
✅ Chat Completions API test successful!

🎉 All OpenAI tests passed!

Testing Google Gemini API Connection (NEW SDK)
✓ API Key found
✓ Gemini client initialized
🤖 Model Response: Hello! I'm up and running!
✅ Gemini connection successful!

🎉 All model connections are working!
```

## 🐛 Common Issues & Solutions

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'openai'` | Run `pip install -e .` |
| `ModuleNotFoundError: No module named 'google.genai'` | Run `pip install -U google-genai` (NEW SDK) |
| `GEMINI_API_KEY not found` | Update `.env` - it's `GEMINI_API_KEY` not `GOOGLE_API_KEY`! |
| `OPENAI_API_KEY not found` | Add key to `.env` file |
| `Invalid API key` | Verify keys are correct and active |
| `Insufficient credits` | Add credits to OpenAI account |
| `404 Model not found` | Wrong model name - use `gemini-2.5-flash` for Gemini |

## 📖 Learning Resources

### What You'll Learn From These Tests

1. **API Authentication**: Secure key management with `.env`
2. **Error Handling**: Try/except patterns, request IDs
3. **Token Tracking**: Understanding costs and usage
4. **API Differences**:
   - OpenAI: Message-based (system/user/assistant roles)
   - Gemini: Content-based (simpler input/output)
5. **Retry Logic**: Automatic retries on failures
6. **Request IDs**: Debugging failed requests

### Code Examples in Tests

- OpenAI Responses API: `test_openai_connection.py:24-85`
- OpenAI Chat Completions: `test_openai_connection.py:88-168`
- Gemini NEW SDK: `test_gemini_connection.py:22-110`

## ✨ Next Steps

Once all tests pass, you're ready for **Milestone 1.2**:
- ✅ Create a single agent research function with Claude
- ✅ Build structured output using Pydantic models
- ✅ Test with simple queries in all 4 domains

## 🔗 Documentation Links

- [OpenAI Chat Completions](https://platform.openai.com/docs/api-reference/chat)
- [Google Gemini Quickstart](https://ai.google.dev/gemini-api/docs/quickstart)
- [OpenAI Python SDK](https://github.com/openai/openai-python)

---

**Last Updated**: December 2025 - Using latest SDKs
