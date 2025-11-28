# 🔧 RagTool Configuration Guide

This guide explains how to configure RagTool using environment variables for both local development and Railway deployment.

## 🎯 Overview

RagTool now uses a centralized configuration system that:

- **Supports environment variables** for easy customization
- **Works seamlessly** with local development and Railway
- **Provides fallback defaults** for all settings
- **Validates configuration** on startup
- **Centralizes all config logic** in one place

## 📋 Environment Variables

### Required Variables

| Variable         | Description                           | Example  |
| ---------------- | ------------------------------------- | -------- |
| `OPENAI_API_KEY` | OpenAI API key for LLM and embeddings | `sk-...` |

### Optional Variables (with defaults)

| Variable             | Default                                                  | Description                                       |
| -------------------- | -------------------------------------------------------- | ------------------------------------------------- |
| `AGENT_ROLE`         | `vat_agent`                                              | Agent type: `vat_agent` or `sap_agent`            |
| `RAG_DATA_PATH`      | `./data/raw` (vat_agent) or `./data/raw_sap` (sap_agent) | RAG data directory path                           |
| `LLM_MODEL`          | `gpt-4o-mini`                                            | OpenAI model for the LLM                          |
| `LLM_PROVIDER`       | `openai`                                                 | LLM provider                                      |
| `LLM_MAX_TOKENS`     | `1024`                                                   | Maximum tokens for LLM responses                  |
| `EMBEDDING_MODEL`    | `text-embedding-3-small`                                 | OpenAI embedding model                            |
| `EMBEDDING_PROVIDER` | `openai`                                                 | Embedding provider                                |
| `CONFIG_SET`         | (none)                                                   | Configuration set name (e.g., `GEMINI_2.5_FLASH`) |
| `API_KEY`            | (none)                                                   | API key for production security                   |

### Railway-Specific Variables (Auto-set)

| Variable                   | Description                            | Usage                          |
| -------------------------- | -------------------------------------- | ------------------------------ |
| `RAILWAY_PROJECT_NAME`     | Railway project name                   | Used for environment detection |
| `RAILWAY_ENVIRONMENT_NAME` | Railway environment name               | Used for environment detection |
| `RAILWAY_SERVICE_NAME`     | Railway service name                   | Used for environment detection |
| `RAILWAY_PROJECT_ID`       | Railway project ID                     | General Railway identification |
| `PORT`                     | Server port (auto-assigned by Railway) | Web service port configuration |

**Environment Detection**: The system automatically detects Railway environments by checking for the presence of `RAILWAY_PROJECT_NAME`, `RAILWAY_ENVIRONMENT_NAME`, and `RAILWAY_SERVICE_NAME`. This enables different behaviors for local development vs production deployment.

## 🚀 Setup Instructions

### 1. Local Development Setup

1. **Copy the example environment file**:

   ```bash
   cp env.example .env
   ```

2. **Edit `.env` file**:

   ```bash
   # Required
   OPENAI_API_KEY=sk-your-actual-openai-api-key
   # OR use Gemini
   CONFIG_SET=GEMINI_2.5_FLASH

   # Agent configuration
   AGENT_ROLE=vat_agent  # or sap_agent
   RAG_DATA_PATH=./data/raw  # Optional: override default path

   # Optional customizations
   LLM_MODEL=gpt-4o-mini
   LLM_MAX_TOKENS=2048
   EMBEDDING_MODEL=text-embedding-3-small
   ```

3. **Test configuration**:
   ```bash
   python3 -m agents.config --info
   ```

### 2. Railway Deployment Setup

1. **Set environment variables in Railway dashboard**:

   - Go to your Railway project
   - Click on your service
   - Go to **Variables** tab
   - Add the required variables:

   ```bash
   OPENAI_API_KEY=sk-your-actual-openai-api-key
   # OR use Gemini
   CONFIG_SET=GEMINI_2.5_FLASH

   # Agent configuration
   AGENT_ROLE=vat_agent  # or sap_agent
   RAG_DATA_PATH=./data/raw  # Optional: override default path

   LLM_MODEL=gpt-4o-mini
   LLM_MAX_TOKENS=1024
   API_KEY=your-secure-api-key
   ```

2. **Optional Railway-specific overrides**:
   ```bash
   RAG_DATA_PATH=/app/data/raw  # Custom data path
   ```

## 🛠️ Configuration Management

### Check Current Configuration

```bash
# Print current configuration
python3 -m agents.config --info

# Validate configuration
python3 -m agents.config --validate

# Test configuration loading
python3 -m agents.config --test

# Check PDF management configuration
python utils/files_manager.py --list
```

### Sample Output

**Local Environment**:

```
🏠 Local development detected - Railway env vars not set
🔧 RagTool Configuration
========================================
Environment: Local
Agent Role: VAT_AGENT
OpenAI API Key: ✅ Set
LLM Model: gpt-4o-mini
LLM Max Tokens: 1024
Embedding Model: text-embedding-3-small
RAG Data Path: ./data/raw
Storage Path: ./db
========================================
```

**Railway Environment**:

```
🛤️ Railway environment detected:
🛤️  - Project: 'rag-tool-production'
🛤️  - Environment: 'production'
🛤️  - Service: 'web'
🔧 RagTool Configuration
========================================
Environment: Railway
Agent Role: VAT_AGENT
OpenAI API Key: ✅ Set
LLM Model: gpt-4o-mini
LLM Max Tokens: 1024
Embedding Model: text-embedding-3-small
RAG Data Path: ./data/raw
Storage Path: ./db
========================================
```

### Programmatic Usage

```python
from agents.config import get_rag_config, get_environment_info
from utils.files_manager import is_running_on_railway

# Get configuration
config = get_rag_config()
print(f"Using model: {config['llm']['config']['model']}")

# Get environment info
env_info = get_environment_info()
print(f"Running on: {'Railway' if env_info['is_running_in_railway'] else 'Local'}")

# Check Railway environment (using PDF management utility)
if is_running_on_railway():
    print("Railway environment detected - using automated behavior")
else:
    print("Local development - interactive mode enabled")
```

## 🔄 Migration from Hardcoded Config

The old hardcoded configuration:

```python
# OLD - Hardcoded
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4.1-mini",
        }
    },
    "embedding_model": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small"
        }
    }
}
```

Is now replaced with:

```python
# NEW - Environment-based
from agents.config import get_rag_config
config = get_rag_config()
```

## 🎛️ Customization Examples

### Different Models for Different Environments

**Local Development (.env)**:

```bash
OPENAI_API_KEY=sk-your-key
LLM_MODEL=gpt-4o-mini
LLM_MAX_TOKENS=512
```

**Railway Production**:

```bash
OPENAI_API_KEY=sk-your-production-key
LLM_MODEL=gpt-4o
LLM_MAX_TOKENS=2048
```

### Agent Role Configuration

**VAT Agent (Default)**:

```bash
AGENT_ROLE=vat_agent
RAG_DATA_PATH=./data/raw  # Default for VAT agent
```

**SAP Agent**:

```bash
AGENT_ROLE=sap_agent
RAG_DATA_PATH=./data/raw_sap  # Default for SAP agent
```

**Custom Data Path**:

```bash
AGENT_ROLE=vat_agent
RAG_DATA_PATH=/app/custom/data/path  # Override default
```

## 🔍 Troubleshooting

### Common Issues

#### "OPENAI_API_KEY environment variable is required"

- **Cause**: OpenAI API key not set
- **Solution**: Set `OPENAI_API_KEY` in your environment or `.env` file

#### "Configuration validation failed"

- **Cause**: Missing required configuration or files
- **Solution**: Run `python3 -m agents.config --validate` to see specific issues

#### "Using fallback configuration"

- **Cause**: Error loading environment-based config
- **Solution**: Check your `.env` file format and environment variables

#### "Railway environment not detected properly"

- **Cause**: Missing or empty Railway environment variables
- **Solution**: Ensure `RAILWAY_PROJECT_NAME`, `RAILWAY_ENVIRONMENT_NAME`, and `RAILWAY_SERVICE_NAME` are set in Railway
- **Debug**: Run `python utils/files_manager.py` to see environment detection output

#### "PDF management behaves differently than expected"

- **Cause**: Environment detection affecting behavior (confirmations, processing)
- **Solution**: Check if you're in the expected environment using the detection utilities

### Debug Configuration

```python
# Add debug logging to see what's loaded
from agents.config import print_config_info, validate_config

print_config_info()
is_valid = validate_config()
print(f"Configuration valid: {is_valid}")
```

### Environment Detection Issues

```python
from agents.config import running_in_railway, get_environment_info
from utils.files_manager import is_running_on_railway

# Check via config module
print(f"Is Railway (config): {running_in_railway()}")
print(f"Environment info: {get_environment_info()}")

# Check via PDF management module
print(f"Is Railway (files_manager): {is_running_on_railway()}")

# Debug Railway environment variables
import os
print(f"RAILWAY_PROJECT_NAME: {os.getenv('RAILWAY_PROJECT_NAME', 'Not set')}")
print(f"RAILWAY_ENVIRONMENT_NAME: {os.getenv('RAILWAY_ENVIRONMENT_NAME', 'Not set')}")
print(f"RAILWAY_SERVICE_NAME: {os.getenv('RAILWAY_SERVICE_NAME', 'Not set')}")
```

## 📊 Configuration Comparison

| Aspect                    | Before                 | After                              |
| ------------------------- | ---------------------- | ---------------------------------- |
| **Configuration**         | Hardcoded in each file | Centralized in `utils/config.py`   |
| **Customization**         | Edit source code       | Set environment variables          |
| **Environment Detection** | Duplicated logic       | Multiple detection methods         |
| **Model Selection**       | Fixed in code          | Configurable via env vars          |
| **Validation**            | None                   | Built-in validation                |
| **Debugging**             | Manual inspection      | CLI tools and info functions       |
| **PDF Management**        | Manual reprocessing    | Smart reset with auto-reprocessing |
| **Railway Deployment**    | Generic behavior       | Environment-specific optimizations |

## 🔐 Security Best Practices

### Environment Variables

- **Never commit `.env` files** to version control
- **Use different API keys** for development and production
- **Rotate API keys** regularly
- **Use Railway's secret management** for production

### API Key Management

```bash
# Development
OPENAI_API_KEY=sk-dev-key-with-limited-quota

# Production
OPENAI_API_KEY=sk-prod-key-with-monitoring
```

### Configuration Validation

```python
# Always validate config on startup
from agents.config import validate_config

if not validate_config():
    print("❌ Configuration invalid - stopping")
    exit(1)
```

## 🚀 Advanced Usage

### Custom Configuration Overrides

```python
from agents.config import get_rag_config

# Override specific settings
config = get_rag_config(
    llm_model="gpt-4o",
    max_tokens=2048,
    embedding_model="text-embedding-3-large"
)
```

### Environment-Specific Defaults

```python
from agents.config import running_in_railway, get_rag_config
from utils.files_manager import is_running_on_railway

# Using config module detection
if running_in_railway():
    # Production settings
    config = get_rag_config(llm_model="gpt-4o", max_tokens=2048)
else:
    # Development settings
    config = get_rag_config(llm_model="gpt-4o-mini", max_tokens=512)

# Using PDF management detection for consistent behavior
if is_running_on_railway():
    print("Railway detected - using automated PDF management")
    # Auto-reset without confirmation
    # Force reprocessing enabled
else:
    print("Local development - interactive PDF management")
    # Prompt for confirmations
    # Manual control over processing
```

### Configuration Monitoring

```python
# Log configuration changes
import logging
from agents.config import get_environment_info

env_info = get_environment_info()
logging.info(f"Started with model: {env_info['llm_model']}")
logging.info(f"Environment: {'Railway' if env_info['is_running_in_railway'] else 'Local'}")
```

## 🛠️ PDF Management Configuration

### Environment-Aware PDF Processing

The PDF management system now adapts its behavior based on the detected environment:

#### Local Development Behavior

- **Interactive confirmations** for destructive operations
- **Detailed progress output** with user-friendly messages
- **Manual control** over processing and reset operations
- **Development-friendly** error messages and suggestions

#### Railway Production Behavior

- **Automated operations** without user prompts
- **Streamlined logging** optimized for deployment logs
- **Automatic reprocessing** after database resets
- **Production-optimized** error handling

### Configuration Example

```bash
# Local development with custom paths
DATA_FILE_PATH=./custom/data/documents.pdf
CHROMA_DB_PATH=./local_db

# Railway production with absolute paths
DATA_FILE_PATH=/app/utils/data/production-docs.pdf
CHROMA_DB_PATH=/app/storage/chromadb
```

### Agent and RAG Configuration Variables

| Variable        | Default                                                  | Description            | Environment Impact                   |
| --------------- | -------------------------------------------------------- | ---------------------- | ------------------------------------ |
| `AGENT_ROLE`    | `vat_agent`                                              | Agent type to build    | Determines which crew is initialized |
| `RAG_DATA_PATH` | `./data/raw` (vat_agent) or `./data/raw_sap` (sap_agent) | RAG data directory     | Role-specific default paths          |
| `RAILWAY_*`     | (auto-set)                                               | Railway detection vars | Enables automated behavior           |

**Important Notes:**

- Only **one crew** is built based on `AGENT_ROLE` (no fallback or secondary crews)
- If RAG tool initialization fails, the server initialization fails (no fallback RAG tool)
- The system uses **FAISS** vector database (not ChromaDB)

### Testing Environment Detection

```bash
# Test Railway detection
python utils/files_manager.py --list

# Check environment variables
python -c "from utils.files_manager import is_running_on_railway; print(f'Railway: {is_running_on_railway()}')"

# Validate complete configuration
python3 -m agents.config --validate
```

## 🛡️ EU AI Act Compliance Configuration

RagTool includes built-in EU AI Act compliance guardrails that require **no additional configuration**. The compliance system is automatically enabled and validates all requests.

### 🔧 Guardrails System Overview

The compliance system operates through three validation layers:

| Validation Layer         | Purpose                          | Regulatory Basis         |
| ------------------------ | -------------------------------- | ------------------------ |
| **Prohibited Practices** | Blocks illegal AI uses           | EU AI Act Article 5      |
| **Risk Classification**  | Identifies high-risk scenarios   | EU AI Act Article 6      |
| **AI Risk Management**   | Ensures transparency & oversight | EU AI Act Articles 9, 13 |

### 🚫 Automatic Compliance Validation

All `/chat` endpoint requests are automatically validated for:

- **Biometric identification attempts**
- **Social scoring systems**
- **Manipulation and deceptive practices**
- **High-risk decision making** (healthcare, employment, finance)
- **Transparency and human oversight requirements**

### ⚙️ Guardrails Integration

The guardrails are **pre-processing compliance checks** that run **before** any AI processing:

```python
# Automatic validation flow:
1. User sends request to /chat endpoint
2. 🛡️ EU AI Act compliance validation runs
3. ✅ If compliant: Continue to CrewAI processing
4. ❌ If violation: Return error response immediately
```

### 📊 Compliance Monitoring

The system automatically logs compliance events:

```bash
# Compliant request
🛡️ Running EU AI Act compliance checks...
✅ Message passed all compliance checks

# Compliance violation
🛡️ Running EU AI Act compliance checks...
❌ Compliance violation detected: EU AI Act Violation: [details]
```

### 🔗 Guardrails Files

The compliance system consists of:

- `agents/guardrails/compliance_guardrails.py` - Core validation logic
- `agents/guardrails/__init__.py` - Package exports
- `agents/guardrails/README.md` - Detailed documentation
- `agents/guardrails/test_guardrails.py` - Test suite

### 🧪 Testing Compliance

Test the guardrails system:

```bash
# Run comprehensive test suite
cd agents
python guardrails/test_guardrails.py

# Test specific compliance functions
python -c "from guardrails import validate_all_compliance_rules; print(validate_all_compliance_rules('What insurance do I need?'))"
```

**No additional environment variables or configuration required** - the guardrails are enabled by default! 🛡️

---

This enhanced configuration system with environment detection and EU AI Act compliance makes RagTool truly production-ready across different deployment scenarios! 🚀🎉
