## 📝 Description

This PR represents the **initial release** of the RagIvaconsulta Agent - a production-ready CrewAI-powered RAG agent for VAT (IVA) consultation with comprehensive EU AI Act compliance, LangSmith monitoring, and Railway deployment capabilities.

**Key Focus**: VAT consultation specialist agent designed for Railway deployment, accessible via HTTPS by orchestrator agents and external clients.

## 🎯 What does this PR do?

- [x] Feature addition - **Complete RAG Agent Implementation**
- [x] Documentation update - **Comprehensive setup and deployment guides**
- [x] Security Enhancement - **EU AI Act compliance guardrails**
- [x] Infrastructure - **CI/CD pipeline and deployment configuration**

## 🚀 Key Features

### Core Agent Functionality

- **CrewAI RAG Agent System**: Specialized VAT (IVA) consultation agent with YAML-based configuration
- **Single Crew Initialization**: Only one crew is built based on `AGENT_ROLE` environment variable:
  - `vat_agent` (default): VAT documentation specialist - **Primary role**
  - `sap_agent`: SAP integration consultant (optional)
  - **No fallback or secondary crews** - clean, focused initialization
- **Advanced RAG Capabilities**:
  - **FAISS vector database** for efficient document retrieval (migrated from ChromaDB)
  - Support for multiple file formats (PDF, TXT, DOCX, MD, HTML)
  - Intelligent document processing with chunking and embeddings
  - Files management system with metadata tracking
  - **No fallback RAG tool** - initialization fails immediately if RAG setup fails
- **Role-Based Configuration**:
  - Default: `vat_agent` with `./data/raw` data path
  - SAP agent: `sap_agent` with `./data/raw_sap` data path
  - Environment-specific settings and validation

### EU AI Act Compliance

- **Prohibited Practices Prevention**: Built-in guardrails preventing manipulative AI practices
- **Risk Assessment Framework**: Automatic classification and compliance validation
- **Compliance Guardrails Module**: Real-time validation of user requests against EU AI Act Article 5
- **Comprehensive Documentation**: Complete compliance guidelines and implementation guides

### Monitoring & Observability

- **LangSmith Integration**:
  - Automatic LLM tracing and cost tracking
  - Token usage monitoring and performance metrics
  - Error tracking and debugging capabilities
  - Custom run annotation and metadata
- **Monitoring Dashboard**: Real-time visibility into agent performance
- **Health Check Endpoints**: Production-ready health monitoring

### Production-Ready Infrastructure

- **Railway Deployment**:
  - **Primary deployment platform** - optimized for Railway hosting
  - Automatic environment detection (Railway vs Local)
  - Pre-configured `railway.json` with health checks
  - `Procfile` for seamless deployment
  - **Orchestrator Agent Integration**: Designed to be called by orchestrator agents on Railway
  - **HTTPS Access**: Accessible via HTTPS by external clients and orchestrator agents
- **CI/CD Pipeline**:
  - Automated testing on pull requests
  - Code structure validation
  - Linting and formatting checks
  - Script syntax validation
- **Environment Management**:
  - Configuration sets for different LLM providers (OpenAI, Gemini)
  - Flexible environment variable handling
  - Role-based data path support (`AGENT_ROLE` determines data path)

### API & Server

- **Flask REST API** (HTTPS-enabled):
  - `/health` - Health check with detailed system status
  - `/chat` - Main agent interaction endpoint with compliance validation
    - Default agent: `iva_consulta_agent` (VAT specialist)
    - Optional `agent_type` parameter for flexibility
    - `context_country` parameter for jurisdictional context
  - `/` - API documentation and capabilities
- **Multi-Client Support**:
  - **Orchestrator Agents**: Designed for Railway orchestrator agent integration
  - **External Clients**: HTTPS access for any external client
  - API key authentication for production security
- **CORS Support**: Configurable for Railway and local development
- **Rate Limiting**: Built-in protection with Flask-Limiter (15 requests/minute)
- **Security**: API key validation and production-ready security measures

## 🔍 Major Components Added

### Agent System (`agents/`)

```
agents/
├── crewai/
│   ├── crew_agent_server_with_guard_rails.py  # Main Flask server with guardrails
│   ├── crew_entities.py                        # Agent and tool definitions
│   ├── agents.yaml                              # Agent configurations
│   └── tasks.yaml                               # Task definitions
├── rag/
│   ├── ragtool.py                               # Base RAG tool implementation
│   ├── files_ragtool.py                         # Multi-format file processor
│   └── rag_wrapper.py                           # CrewAI compatibility wrapper
├── guardrails/
│   └── compliance_guardrails.py                 # EU AI Act validation
├── utils/
│   ├── config.py                                # Configuration management
│   └── files_manager.py                         # CLI for file processing
└── langsmith_integration.py                      # LangSmith monitoring
```

### Compliance Framework (`.cursor/rules/compliance/`)

- EU AI Act high-risk classification guidelines
- Prohibited practices prevention rules
- Risk management framework (Articles 9, 13, 60, 72)
- Copyright compliance for private use

### Documentation (`docs/`)

- Configuration guides (environment setup, API keys)
- Files management documentation
- LangSmith integration and monitoring guides
- Compliance module documentation
- Manual content addition guides

### Infrastructure

- **CI/CD**: GitHub Actions workflow with comprehensive testing
- **Railway**: Deployment configuration and health checks
- **Development Tools**:
  - Makefile with common commands
  - Pre-commit hooks for code quality
  - Testing framework with pytest

## 🧪 Testing

- [x] Tested locally with both OpenAI and Gemini models
- [x] All core features validated
- [x] **FAISS vector database** initialization and file processing verified
- [x] Single crew initialization tested (no fallback behavior)
- [x] RAG tool failure handling verified (no fallback RAG tool)
- [x] API endpoints tested (health check, chat)
- [x] EU AI Act compliance validation working
- [x] LangSmith tracing operational
- [x] Railway deployment configuration validated
- [x] Orchestrator agent integration tested
- [x] HTTPS client access verified
- [x] CI pipeline passes

## 📋 Configuration

### Required Environment Variables

```bash
# LLM Configuration (choose one)
CONFIG_SET=GEMINI_2.5_FLASH  # or GEMINI_2.0_FLASH, OPENAI_4o_MINI
# OR
OPENAI_API_KEY=your_openai_key_here     # For OpenAI models
GEMINI_API_KEY=your_gemini_key_here     # For Gemini models
GOOGLE_API_KEY=your_google_key_here     # Alternative for Gemini

# Agent Configuration (default: VAT agent)
AGENT_ROLE=vat_agent                    # Default: vat_agent (VAT specialist)
RAG_DATA_PATH=./data/raw                # Default for vat_agent (auto-set based on AGENT_ROLE)

# LangSmith Monitoring (optional but recommended)
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT=rag-ivaconsulta-dev
LANGCHAIN_TRACING_V2=true

# Production Security
API_KEY=your_secure_api_key_here        # Required for production HTTPS access

# Railway (auto-set on Railway platform)
PORT=8001
RAILWAY_PUBLIC_DOMAIN=your-domain.railway.app
```

### Supported File Formats

- PDF documents (with OCR preprocessing)
- Plain text files (.txt)
- Markdown files (.md)
- Word documents (.docx)
- HTML files (.html)
- URLs (web scraping)

## 🚀 Deployment Notes

### Railway Deployment

1. Connect GitHub repository to Railway
2. Configure environment variables in Railway dashboard
3. Railway auto-detects configuration from `railway.json`
4. Health checks run on `/health` endpoint
5. Automatic deployment on push to main

### Local Development

```bash
# Setup
cp .env.example .env
# Edit .env with your API keys

# Install dependencies
pip install -r requirements-dev.txt

# Process documents
python agents/utils/files_manager.py

# Start server
python agents/crewai/crew_agent_server_with_guard_rails.py

# Or use Makefile
make dev-server
```

### First-Time Setup

The agent automatically:

1. Reads `AGENT_ROLE` environment variable (defaults to `vat_agent`)
2. Detects environment (Railway vs Local)
3. Initializes **FAISS vector database** if needed
4. Processes documents in role-specific data path (`./data/raw` for VAT agent)
5. **Builds only one crew** based on `AGENT_ROLE` (no fallback/secondary crews)
6. **Fails immediately** if RAG tool initialization fails (no fallback RAG tool)
7. Wraps RAG tool for CrewAI compatibility
8. Starts Flask server with health checks
9. Ready for HTTPS access by orchestrator agents and external clients

## 📦 Dependencies

### Core Dependencies

- `crewai[google-genai]>=0.121.0` - Multi-agent framework
- `crewai-tools>=0.45.0` - RAG and tool integrations
- `flask>=3.0.0` - HTTP server
- `flask-cors>=4.0.0` - CORS support
- `flask-limiter>=3.8.0` - Rate limiting
- `faiss-cpu>=1.7.4` - **FAISS vector database** (migrated from ChromaDB)
- `langchain>=0.1.0` - LLM framework
- `langsmith>=0.1.0` - Monitoring and tracing

### Development Dependencies

- `pytest>=7.0.0` - Testing framework
- `flake8>=6.0.0` - Code linting
- `black>=23.0.0` - Code formatting
- `isort>=5.12.0` - Import sorting

## 📸 Key Capabilities Demonstrated

### 1. Agent Interaction (VAT Consultation)

```bash
# Local development
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuál es el tipo de IVA reducido en España?", "context_country": "Spain"}'

# Production (HTTPS with API key)
curl -X POST https://your-railway-app.railway.app/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{"message": "What is the VAT rate for digital services in Spain?", "context_country": "Spain"}'
```

**Default Agent**: `iva_consulta_agent` (VAT specialist) - automatically selected based on `AGENT_ROLE=vat_agent`

### 2. Health Monitoring

```bash
curl http://localhost:8001/health
```

Returns comprehensive system status including:

- RAG tool availability
- LLM configuration
- LangSmith integration status
- Environment type
- Data paths

### 3. Compliance Validation

Automatically validates all requests against EU AI Act:

- Rejects manipulative practices
- Prevents subliminal techniques
- Blocks social scoring requests
- Ensures transparent AI interaction

## 🔐 Security & Compliance

- ✅ EU AI Act Article 5 compliance (Prohibited Practices)
- ✅ Risk classification framework
- ✅ Input validation and sanitization
- ✅ Rate limiting and abuse prevention
- ✅ Secure API key management
- ✅ Environment-specific security configurations
- ✅ Comprehensive audit logging

## 📚 Documentation Added

- `README.md` - Complete setup and usage guide (updated for VAT focus and Railway deployment)
- `docs/GUARDRAILS_IVA_CONSULTA_API.md` - Compliance API documentation
- `docs/IVA_CONSULTA_API.md` - VAT agent API reference
- `docs/Configuration_Guide.md` - Environment setup (updated with AGENT_ROLE)
- `docs/Files_Management.md` - Document processing guide (updated for FAISS)
- `docs/Langsmith_Integration.md` - Monitoring setup
- `docs/Compliance_guardrails.md` - EU AI Act implementation
- `docs/DOCUMENTATION_CONSOLIDATION_SUMMARY.md` - Documentation consolidation summary
- `.cursor/rules/` - Comprehensive development and compliance rules

**Documentation Consolidation**: Removed duplicate files and consolidated documentation to reflect:

- Single crew initialization (no fallback/secondary crews)
- FAISS vector database (not ChromaDB)
- VAT consultation as default role
- Railway deployment with orchestrator agent integration

## 🎓 Example Use Cases

1. **VAT Consultation** (Primary Use Case): Query VAT rates, regulations, and compliance requirements
   - Spanish VAT rates and regulations
   - European VAT directives
   - VAT compliance procedures
   - Indirect taxation guidance
2. **Orchestrator Agent Integration**: Called by orchestrator agents on Railway for multi-agent workflows
3. **External Client Integration**: HTTPS access for external applications needing VAT consultation
4. **Document Search**: Retrieve relevant information from processed VAT documentation
5. **Compliance-Safe AI**: Interact with AI while maintaining EU AI Act compliance

## 📞 Additional Notes

This initial release establishes a solid foundation for a production-ready VAT consultation RAG agent with:

- **Focused Design**: Single crew initialization for VAT consultation (default role)
- **Clean Initialization**: No fallback or secondary crews - fails fast if initialization fails
- **Railway-Optimized**: Designed for Railway deployment with orchestrator agent integration
- **HTTPS-Ready**: Accessible via HTTPS by orchestrator agents and external clients
- **Compliance-First**: Built with EU AI Act compliance from the ground up
- **Observable**: Comprehensive monitoring and debugging capabilities
- **FAISS-Powered**: Efficient FAISS vector database for document retrieval
- **Well-Documented**: Extensive documentation consolidated and updated
- **Maintainable**: Clean code structure with development tools

The agent is ready for:

- ✅ Production deployment on Railway
- ✅ Integration with orchestrator agents on Railway
- ✅ HTTPS access by external clients
- ✅ VAT consultation services (primary use case)
- ✅ Scaling with more VAT documents and data sources
- ✅ Monitoring and performance optimization

## 🔗 Related Issues

- Closes #[issue-number] (if applicable)

## 👥 Contributors

Initial implementation by the RagIvaconsulta development team.

---

**Merge Checklist:**

- [x] All tests pass
- [x] Documentation is complete
- [x] CI/CD pipeline is green
- [x] Code follows project guidelines
- [x] Security and compliance measures verified
- [x] Ready for production deployment
