## 📝 Description

This PR adds support for the **Mistral Large 2411** model via OpenRouter, expanding the available LLM configuration options for the RAG tool. This allows users to leverage Mistral's powerful language model with improved long context understanding and more accurate function calling capabilities.

## 🎯 What does this PR do?

- [x] Feature addition
- [ ] Bug fix
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Other: __________

## 🔍 Changes Made

- Added new `MISTRAL_LARGE_MODEL` configuration set in `agents/utils/config.py`:
  - Provider: `openrouter`
  - Model: `mistralai/mistral-large-2411`
  - Max tokens: 4096
  - Uses OpenAI embeddings (`text-embedding-3-small`)

- Updated API key validation to support `OPENROUTER_API_KEY`:
  - Added validation in `ConfigurationSet.validate()`
  - Updated `_validate_api_keys()` function
  - Updated `_validate_llm_api_keys()` function
  - Added OpenRouter API key status to environment info and config output

- Fixed OpenRouter API key passing in `agents/crewai/crew_entities.py`:
  - Modified `CustomLlm.initialize_llm()` to pass `api_key` parameter when using OpenRouter
  - This fixes the 401 "Missing Authentication header" error

- Updated documentation in `.env.example`:
  - Added `MISTRAL_LARGE_MODEL` to available configuration options
  - Updated all configuration set descriptions
  - Added `OPENROUTER_API_KEY` documentation

- Updated docstrings in `agents/utils/config.py`:
  - Added `MISTRAL_LARGE_MODEL` to configuration sets list
  - Added `OPENROUTER_API_KEY` to environment variables documentation
  - Updated configuration examples

## 🧪 Testing

- [x] I have tested this locally
- [x] All tests pass
- [x] No breaking changes

**Test commands used:**
```bash
python3 -m agents.utils.config --list-sets
python3 -m agents.utils.config --show-set MISTRAL_LARGE_MODEL
python3 -m agents.utils.config --info
```

**Railway Deployment:**
- [x] Tested on Railway with `CONFIG_SET=MISTRAL_LARGE_MODEL`
- [x] Verified OpenRouter API key is properly passed to LLM
- [x] Confirmed no 401 authentication errors

## 📸 Screenshots (if applicable)

<!-- N/A - Configuration changes only -->

## 📋 Checklist

- [x] Code follows project style guidelines
- [x] Self-review completed
- [x] Code is commented where necessary
- [x] Documentation updated (if needed)

## 🚀 Deployment Notes

**New environment variable required when using Mistral Large:**
- `OPENROUTER_API_KEY` - Your OpenRouter API key (required for MISTRAL_LARGE_MODEL configuration)

**Usage:**
```bash
# Set in .env file or Railway dashboard
CONFIG_SET=MISTRAL_LARGE_MODEL
OPENROUTER_API_KEY=your-openrouter-api-key-here
```

The configuration works for both:
- **Local builds**: Set variables in `.env` file
- **Railway deploys**: Set variables in Railway dashboard

## 📞 Additional Notes

**Model Details:**
- **Model**: Mistral Large 2 2411 (`mistralai/mistral-large-2411`)
- **Provider**: OpenRouter
- **Context Window**: 131K tokens
- **Max Output Tokens**: 4096
- **Pricing**: $2/1M input tokens, $6/1M output tokens

**Benefits of Mistral Large 2411:**
- Significant upgrade over previous Mistral Large 24.07
- Notable improvements in long context understanding
- New system prompt support
- More accurate function calling
- 131K context window for handling larger documents

**Embedding Strategy:**
Since OpenRouter does not provide embedding models, this configuration uses OpenAI's `text-embedding-3-small` for embeddings while using Mistral Large for LLM operations. This requires having both `OPENROUTER_API_KEY` and `OPENAI_API_KEY` set.

---

**Related Links:**
- [Mistral Large 2411 on OpenRouter](https://openrouter.ai/mistralai/mistral-large-2411)
