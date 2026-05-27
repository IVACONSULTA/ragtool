# Free Tier LLM Models for RAG — Top 5 Options

This guide covers the best free tier LLM models for this RAG system, selected specifically for:
- ~100 daily consultations (VAT/IVA queries)
- High availability and reliability
- Compatible with the existing `ConfigurationSet` system in `agents/utils/config.py`
- Spanish/EU multilingual content

---

## Quick Summary

| # | Model | Provider | Free Req/Day | Speed | Best Embedding | CONFIG_SET |
|---|-------|----------|-------------|-------|---------------|-----------|
| 1 | Gemini 2.5 Flash | Google AI Studio | 1,500 | Fast | `gemini-embedding-001` | `GEMINI_2.5_FLASH` ✅ |
| 2 | Llama 3.3 70B | Groq | 1,000 | Fastest (840 tok/s) | `gemini-embedding-001` | `GROQ_LLAMA_3_3_70B` ⚙️ |
| 3 | Gemini 2.0 Flash | Google AI Studio | 1,500 | Fast | `gemini-embedding-001` | `GEMINI_2.0_FLASH` ✅ |
| 4 | DeepSeek R1 / Llama 4 Scout | OpenRouter (free) | 200/day or 1M/mo BYOK | Medium | `gemini-embedding-001` | `OPENROUTER_FREE` ⚙️ |
| 5 | Mistral Small 3.1 | Mistral La Plateforme | ~500 | Medium | `gemini-embedding-001` | `MISTRAL_FREE_MODEL` ⚙️ |

> ✅ = Already configured in `config.py`  
> ⚙️ = Requires adding a new `ConfigurationSet` (see instructions below)

---

## Option 1 — Google Gemini 2.5 Flash (Recommended)

**Best for:** Primary model. Most generous free limits, excellent RAG performance, already configured.

### Why it's the top pick
- **1,500 requests/day** — covers 100 daily consultations with 15x headroom
- **1M token context window** — ideal for large VAT document retrieval
- Multilingual (Spanish + EU languages) — critical for IVA Consulta use case
- Already integrated: `CONFIG_SET=GEMINI_2.5_FLASH` works out of the box

### Rate Limits (Free Tier)
| Limit | Value |
|-------|-------|
| Requests per day | 1,500 |
| Requests per minute | 15 RPM |
| Tokens per minute | 1,000,000 TPM |

### Get API Key
1. Go to [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Sign in with a Google account
3. Click **Create API key** → select a Google Cloud project (or create one)
4. Copy the key (starts with `AIza...`)
5. No credit card required

### Configure in `.env`
```bash
CONFIG_SET=GEMINI_2.5_FLASH

GEMINI_API_KEY=AIzaSy...your_key_here
GOOGLE_API_KEY=AIzaSy...your_key_here
EMBEDDINGS_GOOGLE_API_KEY=AIzaSy...your_key_here
```

### Best Embedding Option
`gemini-embedding-001` — already set in this config. Free on the Google AI Studio tier.
- MTEB score: 68.3
- 768 dimensions
- Supports 100+ languages
- Zero extra cost if you're already using the Gemini API key

---

## Option 2 — Groq Llama 3.3 70B

**Best for:** Fallback or primary when speed is critical. Fastest free inference available (840 tokens/sec).

### Why it's a strong pick
- **1,000 req/day** — sufficient for 100 daily consultations with 10x headroom
- Fastest free LLM inference available in 2026 (Groq hardware)
- OpenAI-compatible API — integrates seamlessly
- Existing `GROQ_API_KEY` already in the project

> **Note:** The project currently has `GROQ_LLAMA__MODEL` (Llama 3.1 70B). Llama 3.3 70B is a newer version with better instruction following — worth adding.

### Rate Limits (Free Tier)
| Limit | Value |
|-------|-------|
| Requests per day | 1,000 |
| Requests per minute | 30 RPM |
| Tokens per minute | 6,000 TPM |

### Get API Key
1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up (no credit card required)
3. Navigate to **API Keys** → click **Create API Key**
4. Copy the key (starts with `gsk_...`)

> You already have a Groq key in the project (`GROQ_API_KEY`). It works for all Groq models.

### Configure in `.env`
```bash
CONFIG_SET=GROQ_LLAMA_3_3_70B

GROQ_API_KEY=gsk_...your_key_here

# Groq does not offer embeddings — use Google for free embeddings
GEMINI_API_KEY=AIzaSy...your_key_here
EMBEDDINGS_GOOGLE_API_KEY=AIzaSy...your_key_here
```

### Add the ConfigurationSet to `config.py`

Add this inside `_initialize_default_sets()` in `ConfigurationManager`, alongside the existing Groq sets:

```python
"GROQ_LLAMA_3_3_70B": ConfigurationSet(
    name="llama-3.3-70b-versatile",
    llm_provider="groq",
    llm_model="llama-3.3-70b-versatile",
    llm_max_tokens=2048,
    rag_provider="groq",
    rag_model="llama-3.3-70b-versatile",
    embedding_provider="google-generativeai",
    embedding_model="gemini-embedding-001",
    chunk_size=1200,
    chunk_overlap=200,
    chroma_db_path="./db",
    environment_type="auto",
    langsmith_enabled=bool(os.getenv("LANGSMITH_API_KEY")),
    langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
    langsmith_project=os.getenv("LANGSMITH_PROJECT", "rag-ivaconsulta-dev"),
    langsmith_endpoint=os.getenv("LANGCHAIN_ENDPOINT"),
),
```

### Best Embedding Option
Since Groq doesn't offer embeddings, pair it with **`gemini-embedding-001`** (free) or **`text-embedding-3-small`** (OpenAI, $0.02/1M tokens). The config above uses Gemini embeddings at zero cost.

---

## Option 3 — Google Gemini 2.0 Flash

**Best for:** Secondary/backup option. Largest context window of any free model (1M tokens).

### Why it's a solid backup
- **1,500 req/day** — same generous limits as Gemini 2.5 Flash
- **1,000,000 token context window** — unmatched for large VAT document sets
- Already configured as `GEMINI_2.0_FLASH`
- Slightly lower quality than 2.5 Flash but faster

### Rate Limits (Free Tier)
Same as Gemini 2.5 Flash — 1,500 req/day, 15 RPM, 1M TPM.

### Get API Key
Same process as Option 1 — same Google AI Studio key works for all Gemini models.

### Configure in `.env`
```bash
CONFIG_SET=GEMINI_2.0_FLASH

GEMINI_API_KEY=AIzaSy...your_key_here
GOOGLE_API_KEY=AIzaSy...your_key_here
EMBEDDINGS_GOOGLE_API_KEY=AIzaSy...your_key_here
```

### Best Embedding Option
`gemini-embedding-001` — same key, zero additional cost.

---

## Option 4 — OpenRouter Free Models (DeepSeek R1 / Llama 4 Scout)

**Best for:** Access to 28+ models via a single key. BYOK mode gives 1M free routing requests/month.

### Why it's useful
- **28+ free models** from a single API key and endpoint
- Models include: DeepSeek R1 (128K context, GPT-4 class reasoning), Llama 4 Scout (10M context!), Gemma 3 12B, Mistral Small 24B
- You already have an `OPENROUTER_API_KEY` in the project
- **BYOK mode**: bring your own provider key (e.g., Groq or Gemini key) → 1,000,000 free routing requests/month

### Rate Limits (Free Tier)
| Limit | Value |
|-------|-------|
| Requests per day | ~200 (free models) |
| Requests per minute | 20 RPM |
| BYOK routing requests | 1,000,000/month |

> ⚠️ The base 200 req/day limit is tight for 100 daily consultations — use BYOK mode or combine with another primary provider.

### Get API Key
1. Go to [https://openrouter.ai](https://openrouter.ai)
2. Sign up (no credit card required for free tier)
3. Navigate to **Keys** → click **Create Key**
4. Copy the key (starts with `sk-or-...`)

> You already have `OPENROUTER_API_KEY` in the project. Verify it's a valid `sk-or-...` format key.

### Configure in `.env`
```bash
CONFIG_SET=OPENROUTER_FREE

OPENROUTER_API_KEY=sk-or-...your_key_here
GEMINI_API_KEY=AIzaSy...your_key_here
EMBEDDINGS_GOOGLE_API_KEY=AIzaSy...your_key_here
```

### Add the ConfigurationSet to `config.py`

```python
"OPENROUTER_FREE": ConfigurationSet(
    name="deepseek/deepseek-r1:free",
    llm_provider="openrouter",
    llm_model="deepseek/deepseek-r1:free",
    llm_max_tokens=4096,
    rag_provider="openrouter",
    rag_model="deepseek/deepseek-r1:free",
    embedding_provider="google-generativeai",
    embedding_model="gemini-embedding-001",
    chunk_size=1200,
    chunk_overlap=200,
    chroma_db_path="./db",
    environment_type="auto",
    langsmith_enabled=bool(os.getenv("LANGSMITH_API_KEY")),
    langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
    langsmith_project=os.getenv("LANGSMITH_PROJECT", "rag-ivaconsulta-dev"),
    langsmith_endpoint=os.getenv("LANGCHAIN_ENDPOINT"),
),
```

> To switch to Llama 4 Scout (10M context), change `llm_model` and `rag_model` to `"meta-llama/llama-4-scout:free"`.

### Free Models Available via OpenRouter (May 2026)

| Model | Context | Strength |
|-------|---------|---------|
| `deepseek/deepseek-r1:free` | 128K | Reasoning, GPT-4 class |
| `meta-llama/llama-4-scout:free` | 10M | Largest context available |
| `meta-llama/llama-3.3-70b-instruct:free` | 128K | General purpose |
| `google/gemini-2.0-flash-exp:free` | 1M | Multimodal, large context |
| `mistralai/mistral-small-24b-instruct-2501:free` | 128K | EU-hosted |

### Best Embedding Option
OpenRouter does not offer embeddings. Use **`gemini-embedding-001`** (free) as configured above.

---

## Option 5 — Mistral La Plateforme (Free Tier)

**Best for:** EU-hosted alternative. Ideal for EU VAT content compliance and data residency concerns.

### Why it's relevant for this project
- EU-based infrastructure — relevant for GDPR/EU AI Act compliance
- Mistral Small 3.1 offers strong multilingual performance for Spanish/EU languages
- Free tier available — no credit card required to start
- The existing `MISTRAL_LARGE_MODEL` config uses OpenRouter (paid); this adds a direct free Mistral option

### Rate Limits (Free Tier — La Plateforme)
| Limit | Value |
|-------|-------|
| Requests per second | 1 RPS |
| Tokens per minute | 500,000 TPM |
| Daily requests | ~500 (estimated) |

### Get API Key
1. Go to [https://console.mistral.ai](https://console.mistral.ai)
2. Sign up (no credit card required for free tier)
3. Navigate to **API Keys** → click **Create new key**
4. Copy the key (starts with `...`)

### Configure in `.env`
```bash
CONFIG_SET=MISTRAL_FREE_MODEL

MISTRAL_API_KEY=...your_key_here
GEMINI_API_KEY=AIzaSy...your_key_here
EMBEDDINGS_GOOGLE_API_KEY=AIzaSy...your_key_here
```

### Add the ConfigurationSet to `config.py`

```python
"MISTRAL_FREE_MODEL": ConfigurationSet(
    name="mistral-small-3.1",
    llm_provider="mistral",
    llm_model="mistral-small-latest",
    llm_max_tokens=2048,
    rag_provider="mistral",
    rag_model="mistral-small-latest",
    embedding_provider="google-generativeai",
    embedding_model="gemini-embedding-001",
    chunk_size=1200,
    chunk_overlap=200,
    chroma_db_path="./db",
    environment_type="auto",
    langsmith_enabled=bool(os.getenv("LANGSMITH_API_KEY")),
    langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
    langsmith_project=os.getenv("LANGSMITH_PROJECT", "rag-ivaconsulta-dev"),
    langsmith_endpoint=os.getenv("LANGCHAIN_ENDPOINT"),
),
```

> **Note:** You also need to add `MISTRAL_API_KEY` to the API key validation logic in `_validate_api_keys()` in `config.py` since Mistral direct is not yet a recognized provider there.

### Best Embedding Option
Mistral does not offer standalone embedding models via free tier. Use **`gemini-embedding-001`** (free) as configured above.

---

## Embedding Options Comparison

All options above use `gemini-embedding-001` as the recommended free embedding. Here's why and the alternatives:

| Model | Provider | Cost | MTEB Score | Dimensions | Notes |
|-------|----------|------|------------|-----------|-------|
| `gemini-embedding-001` | Google | **Free** (Gemini API key) | 68.3 | 768 | ✅ Best free option, multilingual, already in project |
| `text-embedding-004` | Google | **Free** / $0.025/1M paid | 63.0 | 768 | Free alternative if you hit gemini-embedding-001 limits |
| `text-embedding-3-small` | OpenAI | $0.02/1M tokens | 62.3 | 1,536 | Already in project (Groq configs), very low cost |
| `embed-v4` | Cohere | $0.10/1M tokens | 66.3 | 1,024 | Paid, best multilingual API option |

> **Recommendation for 100 req/day:** Use `gemini-embedding-001`. The free Gemini API tier is generous enough that embeddings will never be a bottleneck, and it performs best on multilingual (Spanish/EU) content.

---

## Recommended Setup for 100 Daily Consultations

For maximum reliability at zero cost:

**Primary:** `GEMINI_2.5_FLASH` — covers 100 req/day with 15x headroom  
**Fallback:** `GROQ_LLAMA_3_3_70B` — add if Gemini rate limits are ever hit  
**Embedding:** `gemini-embedding-001` — free with your existing Gemini key  

```bash
# .env — recommended configuration
CONFIG_SET=GEMINI_2.5_FLASH

GEMINI_API_KEY=AIzaSy...
GOOGLE_API_KEY=AIzaSy...
EMBEDDINGS_GOOGLE_API_KEY=AIzaSy...
GROQ_API_KEY=gsk_...   # Keep as fallback
```

---

## Switching Between Models

All model switches are done via a single `.env` change — no code changes needed:

```bash
# Switch to fastest (Groq)
CONFIG_SET=GROQ_LLAMA_3_3_70B

# Switch to most context (Gemini 2.0 Flash)
CONFIG_SET=GEMINI_2.0_FLASH

# Switch to best quality (Gemini 2.5 Flash)
CONFIG_SET=GEMINI_2.5_FLASH

# Switch to OpenRouter free models
CONFIG_SET=OPENROUTER_FREE
```

See `docs/Local_setup_Configuration_Guide.md` for full configuration reference and all available `CONFIG_SET` values.

---

## Availability Notes (May 2026)

- Free tier limits reset at **UTC midnight** daily
- Groq and Gemini are the most stable free tiers — limits rarely change without notice
- OpenRouter free model availability can change; always check [openrouter.ai/models](https://openrouter.ai/models) for current `:free` models
- Mistral's free tier is suitable for development/low-volume; check [console.mistral.ai](https://console.mistral.ai) for current limits
- If you hit rate limits, implement a simple retry with exponential backoff or rotate between providers
