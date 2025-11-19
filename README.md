# RagTool - CrewAI RAG Agent Server

A CrewAI-powered VAT (Value Added Tax) consultation agent that uses RAG (Retrieval Augmented Generation) to provide expert advice on VAT and indirect taxation matters. This project provides a simple HTTP server with a `/chat` endpoint for direct access to the CrewAI agent.

**Deployment & Integration**: The agent is deployed on Railway and can be called via HTTPS by:

- **Orchestrator Agents**: Other agents on Railway that coordinate multi-agent workflows
- **External Clients**: Any HTTPS client that needs VAT consultation services

## 🚀 Features

- **VAT Expertise**: Specialized in VAT and indirect taxation consultation (default role)
- **CrewAI Integration**: Powered by CrewAI for intelligent agent conversations
- **EU AI Act Compliance**: Built-in guardrails ensuring compliance with EU AI Act regulations
- **Advanced RAG Capabilities**: Smart PDF processing with FAISS vector database
- **LangSmith Monitoring**: Comprehensive tracing, debugging, and performance monitoring
- **HTTPS API**: REST endpoints accessible via HTTPS for orchestrator agents and external clients
- **Railway Deployment**: Pre-configured for Railway deployment with orchestrator agent integration
- **Multi-Agent Ready**: Designed to be called by orchestrator agents in multi-agent workflows
- **Smart Environment Detection**: Automatically adjusts behavior for local vs production environments
- **Intelligent PDF Management**: Automated processing, reset, and reprocessing capabilities
- **Persistent Vector Storage**: FAISS for efficient and scalable document retrieval
- **Configuration Management**: Environment-based configuration with validation
- **Production Optimized**: Automated deployment workflows and health monitoring

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key (for LLM and embedding models)
- LangSmith API key (optional, for monitoring and debugging)
- Git (for cloning the repository)

## 🛠️ Local Development Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd RagTool
```

### 2. Create a Python Virtual Environment

#### On Linux/macOS:

```bash
# Install python3-venv if not already installed (Ubuntu/Debian)
sudo apt update
sudo apt install -y python3-venv

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip

python -m pip install --upgrade pip
```

#### On Windows:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

### 3. Install Dependencies

```bash
# Install required packages for production
python3 -m pip install -r requirements.txt

# OR install with development tools (includes testing, linting)
python3 -m pip install -r requirements-dev.txt
```

### 4. Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp env.example .env

# Edit with your settings
OPENAI_API_KEY=your_openai_api_key_here
# OR use Gemini
CONFIG_SET=GEMINI_2.5_FLASH

# Agent configuration (default: VAT agent)
AGENT_ROLE=vat_agent  # Default role: VAT consultation specialist
RAG_DATA_PATH=./data/raw  # VAT agent data path

LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
```

For complete configuration options, see [Configuration Guide](docs/Configuration_Guide.md).

### 5. Process PDF Documents

```bash
# Process PDF documents for RAG (VAT agent uses ./data/raw by default)
python3 files_manager_runner.py process

# Add new PDFs
python3 files_manager_runner.py add-file path/to/new.pdf

# Reset and reprocess all PDFs
python3 files_manager_runner.py --reset

# List processed files
python3 files_manager_runner.py list
```

For detailed PDF management, see [Files Management Guide](docs/Files_Management.md).

### 6. Set Up LangSmith Monitoring (Optional)

LangSmith provides powerful monitoring and debugging capabilities for your AI agent.

```bash
# Get your LangSmith API key from https://smith.langchain.com/
# Add to your .env file:
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=sap-rag-tool
LANGCHAIN_TRACING_V2=true

# Test your LangSmith setup
python scripts/setup_langsmith.py
```

For detailed LangSmith integration, see [LANGSMITH_INTEGRATION.md](docs/LANGSMITH_INTEGRATION.md).

### 7. Run the Server Locally

```bash
# Option 1: Direct Python execution (with guardrails)
python agents/crewai/crew_agent_server_with_guard_rails.py

# Option 2: Using the provided script
chmod +x start_guardrails_server.sh
./start_guardrails_server.sh
```

The server will start on `http://localhost:8001` by default. The default agent role is **VAT Agent** (`vat_agent`), providing VAT and indirect taxation consultation.

## ☁️ Railway Deployment

Railway is the primary deployment platform for this agent. The agent is designed to be deployed on Railway and can be called via HTTPS by:

- **Orchestrator Agents**: Other agents on Railway that coordinate multi-agent workflows
- **External Clients**: Any HTTPS client that needs VAT consultation services

This project is pre-configured for Railway deployment with orchestrator agent integration support.

### Prerequisites for Railway Deployment

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **OpenAI API Key**: Required for the AI functionality

### Deployment Steps

#### Method 1: Deploy from GitHub (Recommended)

1. **Connect Repository to Railway**:

   - Go to [railway.app](https://railway.app) and log in
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your RagTool repository

2. **Configure Environment Variables**:

   - In your Railway project dashboard, go to the "Variables" tab

   - Add the following environment variables:

     ```
     # LLM Configuration
     OPENAI_API_KEY=your_openai_api_key_here
     # OR use Gemini
     CONFIG_SET=GEMINI_2.5_FLASH

     # Agent Configuration (default: VAT agent)
     AGENT_ROLE=vat_agent
     RAG_DATA_PATH=./data/raw

     # LangSmith Monitoring (optional)
     LANGSMITH_API_KEY=your_langsmith_api_key_here
     LANGSMITH_PROJECT=rag-ivaconsulta-dev
     LANGCHAIN_TRACING_V2=true

     # Production Security
     API_KEY=your_secure_api_key_here
     ```

3. **Deploy**:
   - Railway will automatically detect the `railway.json` configuration
   - The deployment will start automatically
   - Railway will install dependencies and start the server

#### Method 2: Railway CLI

1. **Install Railway CLI**:

   ```bash
   # npm
   npm install -g @railway/cli

   # or curl
   curl -fsSL https://railway.app/install.sh | sh
   ```

2. **Login and Deploy**:

   ```bash
   # Login to Railway
   railway login

   # Initialize project (in your RagTool directory)
   railway link

   # Set environment variables
   railway variables set OPENAI_API_KEY=your_openai_api_key_here

   # Deploy
   railway up
   ```

### Railway Configuration

The project includes a `railway.json` file with the following configuration:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

This configuration:

- Sets up health checks on the `/health` endpoint
- Configures a 30-second timeout for health checks
- Restarts the service on failure

### Environment Detection

The application automatically detects whether it's running on Railway or locally:

- **Railway Environment**: Detected by checking `RAILWAY_PROJECT_NAME`, `RAILWAY_ENVIRONMENT_NAME`, and `RAILWAY_SERVICE_NAME`
- **Local Environment**: Default fallback for development
- **Behavior Adaptation**: PDF management, confirmations, and logging adapt based on environment

**Railway Detection Features**:

- Automated PDF processing without manual confirmation
- Production-optimized logging and error handling
- Automatic database reset and reprocessing for clean deployments
- Environment-specific configuration validation

## 🔗 API Endpoints

Once deployed, your agent will be accessible via the public Railway URL.

### Health Check

```bash
GET https://your-railway-app.railway.app/health
```

Response:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "server": "CrewAI RAG Agent Server",
  "version": "1.0.0",
  "environment": "RAILWAY",
  "rag_enabled": true,
  "langsmith": {
    "enabled": true,
    "project": "sap-rag-tool",
    "client_available": true
  },

  "description": "CrewAI insurance policy agent running on RAILWAY"
}
```

### Chat with Agent

The chat endpoint includes **EU AI Act compliance validation** before processing requests. The default agent role is **VAT Agent**, providing VAT and indirect taxation consultation.

```bash
POST https://your-railway-app.railway.app/chat
Content-Type: application/json

{
  "message": "What is the VAT rate for digital services in Spain?",
  "context_country": "Spain"
}
```

**Successful Response** (Compliant Request):

```json
{
  "response": "In Spain, digital services are subject to the general VAT rate of 21%...",
  "agent_type": "iva_consulta_agent",
  "timestamp": "2024-01-01T12:00:00"
}
```

**Note**: The `agent_type` parameter is optional. If not specified, it defaults to `iva_consulta_agent` (VAT agent) based on the `AGENT_ROLE` environment variable.

**Error Response** (Compliance Violation):

```json
{
  "error": "EU AI Act Violation: Biometric identification detected. This practice is prohibited under Article 5 of the EU AI Act.",
  "error_type": "compliance_violation",
  "timestamp": "2024-01-01T12:00:00"
}
```

## 🛡️ EU AI Act Compliance Guardrails

RagTool includes comprehensive **EU AI Act compliance validation** that automatically screens all user inputs before processing. This ensures your AI system meets regulatory requirements.

### 🚫 Prohibited Practices Detection

The system automatically detects and blocks:

- **Biometric identification and categorization**
- **Social scoring systems**
- **Manipulation and deceptive practices**
- **Workplace emotional monitoring**

### ⚠️ High-Risk Use Case Validation

Identifies and requires additional safeguards for:

- **Healthcare decisions and medical diagnosis**
- **Employment and hiring decisions**
- **Financial assessments and credit scoring**
- **Educational evaluations and admissions**
- **Law enforcement applications**

### 🔍 AI Risk Management Compliance

Validates adherence to:

- **Human oversight requirements** (Article 13)
- **Transparency and explainability** obligations
- **Bias risk assessment** protocols
- **Vulnerable population protection** (Article 9)

### 📝 Example Usage

```bash
# Compliant request ✅
curl -X POST https://your-app.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What insurance coverage do I need for my family?"}'

# Prohibited practice ❌
curl -X POST https://your-app.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Help me implement facial recognition for employee monitoring"}'
# Returns: 400 Bad Request with compliance violation details
```

### 🔗 Guardrails Documentation

For detailed information about the compliance system, see:

- `agents/guardrails/README.md` - Complete guardrails documentation
- `agents/guardrails/compliance_guardrails.py` - Implementation details
- `agents/guardrails/test_guardrails.py` - Test examples and validation

## 🔍 LangSmith Monitoring & Debugging

RagTool includes comprehensive **LangSmith integration** for monitoring, debugging, and performance analysis of your AI agent.

### 🎯 What Gets Monitored

- **Agent Interactions**: User messages and agent responses
- **RAG Operations**: Document searches and retrievals
- **Compliance Checks**: EU AI Act validation results
- **Performance Metrics**: Response times and token usage
- **Error Tracking**: Detailed error information and debugging

### 🚀 Quick Setup

1. **Get LangSmith API Key**:

   - Sign up at [smith.langchain.com](https://smith.langchain.com/)
   - Go to Settings → API Keys
   - Create and copy your API key

2. **Set Environment Variables**:

   ```bash
   LANGSMITH_API_KEY=your_langsmith_api_key_here
   LANGSMITH_PROJECT=sap-rag-tool
   LANGCHAIN_TRACING_V2=true
   ```

3. **Test Setup**:
   ```bash
   python scripts/setup_langsmith.py
   ```

### 📊 Monitoring Dashboard

- **Real-time Traces**: See agent execution step-by-step
- **Performance Analytics**: Track response times and costs
- **Error Analysis**: Debug issues with detailed context
- **Compliance Monitoring**: Track EU AI Act compliance

### 📚 Documentation

For complete LangSmith integration details, see:

- **[LANGSMITH_INTEGRATION.md](docs/LANGSMITH_INTEGRATION.md)** - Complete integration guide
- **Setup Script**: `python scripts/setup_langsmith.py`
- **Health Check**: Includes LangSmith status in `/health` endpoint

## 🔧 Agent Communication

### Called by Orchestrator Agent or External Clients

When this agent is deployed to Railway, it can be called via HTTPS by:

1. **Orchestrator Agents**: Other agents on Railway that coordinate multi-agent workflows
2. **External Clients**: Any HTTPS client that needs VAT consultation services

#### Example: Orchestrator Agent Calling VAT Agent

```python
import requests

# Example: Orchestrator agent calling this VAT RAG agent
response = requests.post(
    "https://your-railway-app.railway.app/chat",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": "your_api_key_here"  # Required in production
    },
    json={
        "message": "What is the VAT rate for digital services in Spain?",
        "context_country": "Spain"
    }
)

if response.status_code == 200:
    agent_response = response.json()["response"]
    agent_type = response.json()["agent_type"]
    print(f"VAT Agent ({agent_type}) Response: {agent_response}")
else:
    print(f"Error: {response.status_code} - {response.json()}")
```

### Integration Example: External Client

```javascript
// Example: External client calling VAT agent via HTTPS
const askVATAgent = async (question, country = "Spain") => {
  const response = await fetch("https://your-railway-app.railway.app/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": "your_api_key_here", // Required in production
    },
    body: JSON.stringify({
      message: question,
      context_country: country,
    }),
  });

  const data = await response.json();
  return {
    response: data.response,
    agentType: data.agent_type,
    timestamp: data.timestamp,
  };
};

// Usage: VAT consultation
const answer = await askVATAgent(
  "What is the VAT rate for digital services in Spain?",
  "Spain"
);
console.log(`VAT Agent (${answer.agentType}): ${answer.response}`);
```

## 📁 Project Structure

```
RagTool/
├── agents/
│   ├── crewai/
│   │   ├── crew_agent_server_with_guard_rails.py  # Main server (VAT agent default)
│   │   └── crew_entities.py                      # Agent and crew definitions
│   ├── guardrails/                                # EU AI Act compliance
│   ├── langsmith_integration.py                   # LangSmith monitoring
│   └── rag/                                       # RAG tool implementation
├── data/
│   ├── raw/                      # VAT agent documents (default)
│   ├── raw_sap/                  # SAP agent documents
│   └── processed/                # Processing metadata
├── db/                           # FAISS vector database storage
├── docs/                         # Documentation
│   ├── Configuration_Guide.md   # Configuration documentation
│   ├── Files_Management.md      # PDF management guide
│   └── ...                      # Other documentation
├── scripts/                      # Utility scripts
├── tests/                        # Test files
├── files_manager_runner.py       # PDF processing CLI
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Development dependencies
├── railway.json                 # Railway deployment configuration
├── env.example                  # Environment variables template
├── start_guardrails_server.sh   # Server startup script
├── .env                         # Environment variables (create this)
└── README.md                    # This file
```

## 🛡️ Environment Variables

### Required Variables

| Variable         | Description                                  | Default |
| ---------------- | -------------------------------------------- | ------- |
| `OPENAI_API_KEY` | OpenAI API key for LLM and embeddings        | None    |
| OR `CONFIG_SET`  | Configuration set (e.g., `GEMINI_2.5_FLASH`) | None    |

### Agent Configuration

| Variable        | Description                                      | Default                                                  |
| --------------- | ------------------------------------------------ | -------------------------------------------------------- |
| `AGENT_ROLE`    | Agent type: `vat_agent` (default) or `sap_agent` | `vat_agent`                                              |
| `RAG_DATA_PATH` | RAG data directory path                          | `./data/raw` (vat_agent) or `./data/raw_sap` (sap_agent) |

### Optional Variables

| Variable          | Description                     | Default                       |
| ----------------- | ------------------------------- | ----------------------------- |
| `LLM_MODEL`       | OpenAI model for the LLM        | `gpt-4o-mini`                 |
| `LLM_MAX_TOKENS`  | Maximum tokens for responses    | `1024`                        |
| `EMBEDDING_MODEL` | OpenAI embedding model          | `text-embedding-3-small`      |
| `PORT`            | Server port                     | `8001`                        |
| `API_KEY`         | API key for production security | None (required in production) |

### Railway Auto-Set Variables

| Variable                   | Description              | Usage                 |
| -------------------------- | ------------------------ | --------------------- |
| `RAILWAY_PROJECT_NAME`     | Railway project name     | Environment detection |
| `RAILWAY_ENVIRONMENT_NAME` | Railway environment name | Environment detection |
| `RAILWAY_SERVICE_NAME`     | Railway service name     | Environment detection |

For complete configuration details, see [Configuration Guide](docs/Configuration_Guide.md).

## 🔍 Troubleshooting

### Common Issues

1. **"Could not load documents"**:

   - Ensure PDF files exist in the `data/raw/` directory (for VAT agent)
   - Run `python3 files_manager_runner.py list` to check processed files
   - Use `python3 files_manager_runner.py process` to process PDFs

2. **"No existing FAISS vector database found"**:

   - First time setup: Run `python3 files_manager_runner.py process` to create database
   - Database corruption: Use `python3 files_manager_runner.py --reset`

3. **OpenAI API Errors**:

   - Verify your API key: `python3 -m agents.config --validate`
   - Check your OpenAI account has sufficient credits

4. **Railway Environment Detection Issues**:

   - Check Railway environment variables are set
   - Use `python utils/files_manager.py` to see environment detection output

5. **Railway Deployment Issues**:
   - Ensure environment variables are set in Railway dashboard
   - Check Railway logs for detailed error messages
   - Use automated reset: include `--reset` in deployment scripts

### Debugging

- **Configuration Check**: `python3 -m agents.config --info`
- **PDF Management**: `python3 files_manager_runner.py list`
- **Environment Detection**: Check for Railway-specific logs in output
- **Local Development**: Detailed logging with confirmations
- **Railway Production**: Streamlined logging optimized for deployment
- **Health Check**: Use the `/health` endpoint to verify service status

### Quick Fixes

```bash
# Reset everything and start fresh
python3 files_manager_runner.py --reset

# Validate configuration
python3 -m agents.config --validate

# Process PDFs manually
python3 files_manager_runner.py process

# Check agent role and data path
echo "AGENT_ROLE: ${AGENT_ROLE:-vat_agent}"
echo "RAG_DATA_PATH: ${RAG_DATA_PATH:-./data/raw}"
```

## 📝 Dependencies

The project uses the following key dependencies:

### Core Dependencies

- **crewai**: AI agent framework for intelligent conversations
- **crewai-tools**: RAG tool for document processing and vector search
- **flask**: Web framework for HTTP API
- **flask-cors**: CORS support for web requests
- **faiss-cpu**: FAISS vector database for document embeddings
- **openai**: OpenAI API integration for LLM and embeddings (or Gemini via CONFIG_SET)

### Utility Dependencies

- **python-dotenv**: Environment variable management
- **nest-asyncio**: Async support for Jupyter/interactive environments
- **pypdf**: PDF document processing
- **python-multipart**: File upload support

### Development Dependencies (requirements-dev.txt)

- **pytest**: Testing framework
- **pytest-cov**: Test coverage reporting
- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Code linting

For complete dependency management, see `requirements.txt` and `requirements-dev.txt`.

## 📚 Documentation

Detailed documentation is available in the `docs/` folder:

- **[Configuration Guide](docs/Configuration_Guide.md)**: Complete environment and configuration setup
- **[Files Management Guide](docs/Files_Management.md)**: Document processing and management
- **[IVA Consulta API](docs/IVA_CONSULTA_API.md)**: VAT agent API documentation
- **[Guardrails API](docs/GUARDRAILS_IVA_CONSULTA_API.md)**: API with EU AI Act compliance
- **[LangSmith Integration](docs/Langsmith_Integration.md)**: Monitoring and debugging setup
- **[Documentation Consolidation Summary](docs/DOCUMENTATION_CONSOLIDATION_SUMMARY.md)**: Recent documentation updates

## 🚀 Quick Start Commands

```bash
# Complete setup (first time)
cp env.example .env
# Edit .env with your OPENAI_API_KEY or CONFIG_SET
# Set AGENT_ROLE=vat_agent (default) for VAT consultation

python3 files_manager_runner.py process  # Process PDFs for VAT agent
python agents/crewai/crew_agent_server_with_guard_rails.py  # Start server

# Reset and restart (clean slate)
python3 files_manager_runner.py --reset  # Reset DB and reprocess
python agents/crewai/crew_agent_server_with_guard_rails.py  # Start server

# Check system status
python3 files_manager_runner.py list     # List processed files
python3 -m agents.config --validate     # Validate configuration
curl http://localhost:8001/health       # Check server health

# Test VAT consultation
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the VAT rate in Spain?", "context_country": "Spain"}'
```

## 📄 License

[Add your license information here]

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contributing guidelines.

## 📞 Support

For issues related to:

- **Railway Deployment**: Check Railway documentation or deployment logs
- **PDF Management**: Check [Files Management Guide](docs/Files_Management.md)
- **Configuration**: Check [Configuration Guide](docs/Configuration_Guide.md)
- **VAT Agent API**: Check [IVA Consulta API](docs/IVA_CONSULTA_API.md)
- **Orchestrator Integration**: Ensure HTTPS endpoint is accessible and API key is configured
- **OpenAI/Gemini API**: Check respective API documentation
- **CrewAI**: Check CrewAI documentation
- **This Project**: See documentation in `docs/` folder
