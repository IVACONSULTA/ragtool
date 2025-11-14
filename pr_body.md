## 📝 Description

This PR represents the **initial release** of the RagIvaconsulta Agent - a production-ready CrewAI-powered RAG agent for VAT (IVA) consultation with comprehensive EU AI Act compliance, LangSmith monitoring, and Railway deployment capabilities.

## 🎯 What does this PR do?

- [x] Feature addition - **Complete RAG Agent Implementation**
- [x] Documentation update - **Comprehensive setup and deployment guides**
- [x] Security Enhancement - **EU AI Act compliance guardrails**
- [x] Infrastructure - **CI/CD pipeline and deployment configuration**

## 🚀 Key Features

### Core Agent Functionality

- **CrewAI Multi-Agent System**: IVA Consulta (VAT specialist) and SAP consultant agents with YAML-based configuration
- **Advanced RAG Capabilities**:
  - ChromaDB vector storage for efficient document retrieval
  - Support for multiple file formats (PDF, TXT, DOCX, MD, HTML)
  - Intelligent document processing with chunking and embeddings
  - Files management system with metadata tracking
- **Dual Agent Roles**:
  - `iva_consulta`/`vat_agent`: VAT documentation specialist (default)
  - `sap`: SAP integration consultant
- **Flexible Configuration**: Role-based data path selection and environment-specific settings

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
  - Automatic environment detection (Railway vs Local)
  - Pre-configured `railway.json` with health checks
  - `Procfile` for seamless deployment
- **CI/CD Pipeline**:
  - Automated testing on pull requests
  - Code structure validation
  - Linting and formatting checks
  - Script syntax validation
- **Environment Management**:
  - Configuration sets for different LLM providers (OpenAI, Gemini)
  - Flexible environment variable handling
  - Multiple data path support

### API & Server

- **Flask REST API**:
  - `/health` - Health check with detailed system status
  - `/chat` - Main agent interaction endpoint with compliance validation
  - `/` - API documentation and capabilities
- **CORS Support**: Configurable for Railway and local development
- **Rate Limiting**: Built-in protection with Flask-Limiter
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
- [x] ChromaDB initialization and file processing verified
- [x] API endpoints tested (health check, chat)
- [x] EU AI Act compliance validation working
- [x] LangSmith tracing operational
- [x] Railway deployment configuration validated
- [x] CI pipeline passes

## 📋 Configuration

### Required Environment Variables

```bash
# LLM Configuration (choose one)
CONFIG_SET=gemini-2.0-flash  # or gpt-4o-mini

# API Keys
OPENAI_API_KEY=your_openai_key_here     # For OpenAI models
GEMINI_API_KEY=your_gemini_key_here     # For Gemini models
GOOGLE_API_KEY=your_google_key_here     # Alternative for Gemini

# LangSmith Monitoring (optional but recommended)
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT=your_project_name
LANGCHAIN_TRACING_V2=true

# Agent Configuration
RAG_ROLE=vat_agent                      # or iva_consulta, sap
RAG_DATA_PATH=./data/raw
CHROMA_DB_PATH=./db

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

1. Detects environment (Railway vs Local)
2. Initializes ChromaDB if needed
3. Processes documents in `data/raw/`
4. Wraps RAG tool for CrewAI compatibility
5. Starts Flask server with health checks

## 📦 Dependencies

### Core Dependencies

- `crewai[google-genai]>=0.121.0` - Multi-agent framework
- `crewai-tools>=0.45.0` - RAG and tool integrations
- `flask>=3.0.0` - HTTP server
- `flask-cors>=4.0.0` - CORS support
- `flask-limiter>=3.8.0` - Rate limiting
- `chromadb>=0.4.0` - Vector database
- `langchain>=0.1.0` - LLM framework
- `langsmith>=0.1.0` - Monitoring and tracing

### Development Dependencies

- `pytest>=7.0.0` - Testing framework
- `flake8>=6.0.0` - Code linting
- `black>=23.0.0` - Code formatting
- `isort>=5.12.0` - Import sorting

## 📸 Key Capabilities Demonstrated

### 1. Agent Interaction

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuál es el tipo de IVA reducido en España?"}'
```

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

- `README.md` - Complete setup and usage guide
- `GUARDRAILS_IVA_CONSULTA_API.md` - Compliance API documentation
- `IVA_CONSULTA_API.md` - VAT agent API reference
- `docs/Configuration_Guide.md` - Environment setup
- `docs/Files_Management.md` - Document processing guide
- `docs/Langsmith_Integration.md` - Monitoring setup
- `docs/Compliance_Module.md` - EU AI Act implementation
- `.cursor/rules/` - Comprehensive development and compliance rules

## 🎓 Example Use Cases

1. **VAT Consultation**: Query Spanish VAT rates and regulations
2. **SAP Integration**: Get guidance on SAP integration patterns
3. **Document Search**: Retrieve relevant information from processed documents
4. **Compliance-Safe AI**: Interact with AI while maintaining EU AI Act compliance

## 📞 Additional Notes

This initial release establishes a solid foundation for a production-ready RAG agent with:

- **Modularity**: Easy to extend with new agents and tools
- **Compliance-First**: Built with EU AI Act compliance from the ground up
- **Observable**: Comprehensive monitoring and debugging capabilities
- **Deployment-Ready**: Pre-configured for Railway with CI/CD pipeline
- **Well-Documented**: Extensive documentation for developers and users
- **Maintainable**: Clean code structure with development tools

The agent is ready for:

- ✅ Production deployment on Railway
- ✅ Integration with front-end applications
- ✅ Extension with additional agent roles
- ✅ Scaling with more documents and data sources
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
