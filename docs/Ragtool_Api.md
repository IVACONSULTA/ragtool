# IVA Consulta Agent API

## Overview

The IVA Consulta Agent is a specialized CrewAI agent designed to provide expert VAT and indirect taxation consultation services for Spanish and international companies. It uses the RAG (Retrieval Augmented Generation) system with processed VAT documentation to provide accurate, up-to-date information.

The server is implemented in `agents/crewai/crew_agent_server_with_guard_rails.py` and includes comprehensive security, monitoring, and compliance features.

## Features

- **Expert VAT Knowledge**: Specialized in Spanish and European indirect taxation
- **RAG-Powered**: Uses processed VAT documentation from `data/raw` and `data/raw_sap`
- **Concise Responses**: Automatically limits responses to 600 characters maximum
- **Spain Default**: Uses Spain as default country unless another jurisdiction is specified
- **Multi-language Support**: Can handle questions in Spanish and English
- **EU AI Act Compliance**: Built-in guardrails for compliance validation
- **LangSmith Integration**: Comprehensive monitoring, tracing, and cost tracking
- **API Key Authentication**: Secure API access in production environments
- **Background Initialization**: Server starts immediately while agents initialize in background
- **Multi-Agent Support**: Supports both VAT Agent and SAP Agent roles

## API Endpoints

### 1. Health Check Endpoint

**GET** `/health`

Returns server health status and initialization state.

**Response:**

```json
{
  "status": "healthy",
  "initialization_status": "ready",
  "initialization_complete": true,
  "timestamp": "2025-02-17T10:30:00.000Z",
  "server": "CrewAI RAG Agent Server",
  "version": "1.0.0",
  "environment": "RAILWAY",
  "data_file": "./data/raw",
  "rag_enabled": true,
  "llm_model": "Model: gpt-4o-mini (OpenAI)",
  "rag_status": "RAG Tool: Available (ChromaDB)",
  "langsmith": {
    "enabled": true,
    "project": "rag-ivaconsulta-dev",
    "client_available": true
  },
  "description": "CrewAI insurance policy agent running on RAILWAY"
}
```

### 2. Chat Endpoint

**POST** `/chat`

Main endpoint for interacting with the agent. Requires API key in production.

**Request Headers:**
```
Content-Type: application/json
X-API-Key: your-api-key-here
```

**Request Body:**

```json
{
  "message": "¿Cuál es el IVA en España para servicios digitales?",
  "agent_type": "iva_consulta_agent",
  "context_country": "Spain"
}
```

**Parameters:**
- `message` (required): The user's question
- `agent_type` (optional): Agent to use. If not provided, uses default agent based on `AGENT_ROLE` environment variable
  - `"iva_consulta_agent"`: VAT and indirect taxation specialist
  - `"sap_consultant"`: SAP consulting specialist
- `context_country` (optional): Country context for the query. Defaults to "Spain"

**Response:**

```json
{
  "response": "En España, los servicios digitales están sujetos al IVA general del 21%. Para empresas no establecidas en la UE, aplica el régimen especial de servicios digitales...",
  "agent_type": "iva_consulta_agent",
  "timestamp": "2025-02-17T10:30:00.000Z"
}
```

**Error Responses:**

```json
{
  "error": "Server is still initializing. Please try again in a moment.",
  "initialization_status": "initializing_rag",
  "status": "initializing"
}
```

```json
{
  "error": "Unauthorized - Invalid API key",
  "error_type": "authentication_failed"
}
```

```json
{
  "error": "Compliance violation: [specific violation details]"
}
```

### 3. Root Endpoint

**GET** `/`

Returns server information and available endpoints. Requires API key in production.

**Response:**

```json
{
  "server": "CrewAI RAG Agent Server with Guardrails",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "chat": "/chat"
  },
  "status": "running",
  "timestamp": "2025-02-17T10:30:00.000Z",
  "description": "CrewAI-powered multi-agent system with RAG capabilities and EU AI Act compliance - Default: IVA Consulta VAT Specialist",
  "default_agent": "iva_consulta_agent",
  "guardrails": "EU AI Act compliance enabled",
  "agents": {
    "iva_consulta_agent": "VAT and indirect taxation specialist (DEFAULT)",
    "sap_consultant": "SAP consulting specialist",
    "senior_coverage_assistant": "Insurance coverage specialist"
  }
}
```

## Integration with Website

To integrate with the [IVA Consulta website](https://nexdevconsulting.com/), use the `/chat` endpoint:

```javascript
// Example JavaScript integration
async function askIVAQuestion(question, country = "Spain") {
  const response = await fetch(
    "https://your-railway-domain.railway.app/chat",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "your-api-key-here", // Required in production
      },
      body: JSON.stringify({
        message: question,
        agent_type: "iva_consulta_agent",
        context_country: country,
      }),
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to get response");
  }

  const data = await response.json();
  return data.response;
}

// Usage
try {
  const answer = await askIVAQuestion("¿Cuál es el IVA en España?");
  console.log(answer);
} catch (error) {
  console.error("Error:", error.message);
}

// With custom country context
const answerFrance = await askIVAQuestion(
  "What is the VAT rate for digital services?",
  "France"
);
```

## Architecture

### System Components

The RAG agent system consists of several key components:

1. **Flask Server** (`crew_agent_server_with_guard_rails.py`)
   - HTTP API endpoints
   - Request routing and validation
   - Background initialization
   - Rate limiting and CORS

2. **CrewAI Agents** (`crew_entities.py`)
   - `IVAConsultaCrew`: VAT and indirect taxation specialist
   - `SapCrew`: SAP consulting specialist
   - Agent orchestration and task execution

3. **RAG System** (`CustomRagTool`)
   - ChromaDB vector database
   - Document retrieval and ranking
   - Context augmentation

4. **LLM Integration** (`CustomLlm`)
   - OpenAI GPT-4o-mini
   - Fallback model support
   - Token optimization

5. **Compliance Layer** (`compliance_guardrails.py`)
   - EU AI Act validation
   - Content filtering
   - Risk assessment

6. **Security Layer** (`flask_security_integration.py`)
   - API key authentication
   - Rate limiting
   - Failed attempt tracking

7. **Monitoring** (`langsmith_integration.py`)
   - Request tracing
   - Cost tracking
   - Performance metrics
   - Error logging

### Request Flow

```
1. Client Request → Flask Server
2. API Key Validation (production only)
3. Rate Limit Check
4. EU AI Act Compliance Check
5. Agent Selection (based on agent_type or AGENT_ROLE)
6. RAG Tool: Document Retrieval
7. LLM: Response Generation
8. Response Truncation (600 chars for IVA Consulta)
9. LangSmith Logging
10. Response to Client
```

### Background Initialization

The server uses a background initialization pattern for fast startup:

```python
# Main thread: Start Flask server immediately
app.run(host="0.0.0.0", port=8001)

# Background thread: Initialize agents
- Initialize LangSmith
- Initialize LLM (with tracing)
- Initialize RAG Tool (load ChromaDB)
- Initialize Crew (based on AGENT_ROLE)
- Mark as ready
```

This ensures:
- Health checks work immediately
- Railway/Cloud Run deployment succeeds
- Agents initialize without blocking
- Graceful degradation during startup

## Agent Configuration

The agent is configured in `agents/crewai/agents.yaml`:

```yaml
iva_consulta_agent:
  role: IVA Consulta VAT Specialist
  goal: Provide expert VAT and indirect taxation consultation services
  backstory: |
    You are a specialized VAT consultant from IVA Consulta, expert in 
    Spanish and European indirect taxation. You use the RAG knowledge 
    base containing processed VAT documentation to provide accurate, 
    up-to-date information about VAT rules, procedures, and compliance 
    requirements. You always consider Spain as the default country unless 
    specifically asked about another jurisdiction.
```

## Task Configuration

The task is configured in `agents/crewai/tasks.yaml`:

```yaml
vat_consultation_task:
  description: |
    Provide expert VAT and indirect taxation consultation based on the user's question.
    Search the RAG knowledge base for relevant VAT documentation and regulations.
    If no specific country is mentioned, assume Spain as the default jurisdiction.
  expected_output: |
    A concise and professional response about VAT and indirect taxation 
    (maximum 600 characters). The response should include specific VAT rules, 
    compliance requirements, or procedures relevant to the user's question.
```

## Rate Limits

- **Chat Endpoint**: 15 requests per minute
- **Overall Limit**: 100 requests per hour, 20 requests per minute (default)

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (missing message or invalid parameters)
- `401`: Unauthorized (missing or invalid API key)
- `429`: Rate limit exceeded
- `500`: Internal server error
- `503`: Service unavailable (server still initializing or initialization failed)

### Error Response Format

All errors return a JSON object with an `error` field:

```json
{
  "error": "Error message description",
  "error_type": "error_category"
}
```

### Compliance Violations

If a message violates EU AI Act compliance rules, the server returns a 500 error with details:

```json
{
  "error": "Compliance violation: [specific violation details]"
}
```

## Testing

To test the IVA Consulta agent locally:

```bash
# Start the server
python3 agents/crewai/crew_agent_server_with_guard_rails.py

# In another terminal, test the health endpoint
curl http://localhost:8001/health

# Test the chat endpoint (no API key required in local development)
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuál es el IVA en España?"}'

# Test with custom country context
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the VAT rate for digital services?",
    "agent_type": "iva_consulta_agent",
    "context_country": "France"
  }'

# Test with API key (for testing production behavior)
export SECURITY_TEST_MODE=true
export API_KEY=your-test-api-key
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-test-api-key" \
  -d '{"message": "¿Cuál es el IVA en España?"}'
```

### Running Tests

```bash
# Run the test script
python3 test_iva_consulta.py

# Run SAP crew tests
python3 tests/test_sap_crew.py

# Run CrewAI compatibility tests
python3 tests/test_crewai_compatibility.py
```

## Deployment

The agent is ready for deployment on Railway/Google Cloud Run and will automatically:

1. Start Flask server immediately and accept health checks
2. Initialize agents in background thread (non-blocking startup)
3. Read `AGENT_ROLE` environment variable (defaults to `vat_agent`)
4. Build **only** the crew corresponding to `AGENT_ROLE`:
   - `AGENT_ROLE=vat_agent` → Builds **only** IVA Consulta Crew
   - `AGENT_ROLE=sap_agent` → Builds **only** SAP Crew
5. Initialize RAG tool with role-specific data path
6. Load the RAG knowledge base with processed documents
7. Initialize the LLM configuration with LangSmith tracing
8. Apply EU AI Act compliance guardrails to all requests
9. Handle requests from the website chatbot with API key authentication

### Environment Variables

#### Required Variables

```bash
# Agent role selection
AGENT_ROLE=vat_agent  # Options: vat_agent, sap_agent

# API key for production authentication
API_KEY=your-secure-api-key-here

# OpenAI API key for LLM
OPENAI_API_KEY=your-openai-api-key
```

#### Optional Variables

```bash
# Override default data path
RAG_DATA_PATH=./data/raw  # Default depends on AGENT_ROLE
# vat_agent default: ./data/raw
# sap_agent default: ./data/raw_sap

# LangSmith monitoring (optional but recommended)
LANGSMITH_API_KEY=your-langsmith-api-key
LANGSMITH_PROJECT=rag-ivaconsulta-dev
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# Railway deployment (automatically set by Railway)
RAILWAY_PUBLIC_DOMAIN=your-app.railway.app
RAILWAY_PRIVATE_DOMAIN=your-app.railway.internal
PORT=8001  # Default port, Railway overrides this

# Security testing
SECURITY_TEST_MODE=false  # Set to 'true' to require API key in local development
```

### Deployment Checklist

1. **Set Environment Variables**: Configure all required variables in your deployment platform
2. **API Key Security**: Use a strong, randomly generated API key
3. **LangSmith Setup**: Configure LangSmith for monitoring and cost tracking
4. **Health Checks**: Configure platform to use `/health` endpoint
5. **CORS Origins**: Verify Railway domains are properly configured
6. **Data Files**: Ensure RAG data files are present in the correct directory
7. **Port Configuration**: Let Railway set the PORT automatically

### Startup Behavior

The server uses background initialization to ensure fast startup:

1. **Immediate Start**: Flask server starts and responds to health checks immediately
2. **Background Init**: Agents initialize in a separate thread
3. **Status Tracking**: `/health` endpoint shows initialization progress
4. **Graceful Handling**: `/chat` endpoint returns 503 until initialization completes

Initialization stages tracked in `/health` response:
- `starting`: Server just started
- `initializing_langsmith`: Setting up monitoring
- `initializing_llm`: Loading language model
- `initializing_rag`: Loading RAG knowledge base
- `initializing_crew`: Building CrewAI agents
- `ready`: Fully initialized and ready
- `failed`: Initialization failed (check `initialization_error` field)

## Security and Compliance

### API Key Authentication

The server implements conditional API key authentication:

- **Local Development**: API key not required (detected via localhost/127.0.0.1)
- **Production**: API key required in `X-API-Key` header or `Authorization: Bearer` header
- **Security Test Mode**: Set `SECURITY_TEST_MODE=true` to require API key in local development

### EU AI Act Compliance Guardrails

All incoming messages are validated against EU AI Act compliance rules before processing:

- **Prohibited Content Detection**: Identifies and blocks prohibited AI applications
- **High-Risk Assessment**: Flags high-risk use cases requiring additional safeguards
- **Transparency Requirements**: Ensures proper disclosure and transparency
- **Data Protection**: Validates privacy and data protection compliance

Compliance violations return an error response with specific violation details.

### LangSmith Monitoring

Comprehensive monitoring and tracing via LangSmith integration:

- **Cost Tracking**: Monitor OpenAI API costs per request
- **Token Usage**: Track input/output tokens for optimization
- **Performance Metrics**: Measure response times and latency
- **Error Tracking**: Log and analyze errors and failures
- **Agent Tracing**: Full execution traces for debugging
- **Compliance Logging**: Track compliance violations and patterns

Access monitoring dashboard at: [https://smith.langchain.com](https://smith.langchain.com)

### Security Features

- **Rate Limiting**: Prevents abuse with configurable rate limits
- **CORS Protection**: Restricts origins to configured domains
- **Failed Attempt Tracking**: Records and monitors authentication failures
- **Input Validation**: Validates all incoming requests
- **Error Sanitization**: Prevents information leakage in error messages

## Monitoring and Observability

### Health Check Monitoring

Configure your deployment platform to monitor the `/health` endpoint:

```bash
# Example health check
curl https://your-app.railway.app/health
```

Monitor these fields:
- `status`: Overall health status (`healthy`, `initializing`, `unhealthy`)
- `initialization_complete`: Whether agents are ready
- `rag_enabled`: Whether RAG system is operational
- `langsmith.enabled`: Whether monitoring is active

### LangSmith Dashboard

View comprehensive metrics in LangSmith:

1. **Runs**: Individual agent executions with full traces
2. **Datasets**: Test datasets and evaluation results
3. **Monitoring**: Real-time metrics and alerts
4. **Costs**: OpenAI API usage and costs
5. **Feedback**: User feedback and quality metrics

### Logging

The server provides detailed console logging:

- 🚀 Server startup and configuration
- 🔄 Background initialization progress
- 📝 Incoming requests and messages
- 🛡️ Compliance check results
- 🤖 Agent execution details
- ✅ Successful responses
- ❌ Errors and failures
- 📊 LLM usage summaries

## Troubleshooting

### Common Issues

#### 1. Server Returns 503 "Still Initializing"

**Cause**: Agents are still loading in background thread

**Solution**: Wait 30-60 seconds and retry. Check `/health` endpoint for `initialization_status`

```bash
curl https://your-app.railway.app/health | jq '.initialization_status'
```

#### 2. 401 Unauthorized Error

**Cause**: Missing or invalid API key

**Solution**: 
- Ensure `X-API-Key` header is set
- Verify API key matches `API_KEY` environment variable
- Check if running in production (API key required)

```bash
# Correct usage
curl -H "X-API-Key: your-key" https://your-app.railway.app/chat
```

#### 3. Compliance Violation Error

**Cause**: Message violates EU AI Act compliance rules

**Solution**: Review message content and ensure it doesn't request:
- Prohibited AI applications
- Manipulation or deception
- Social scoring
- Biometric identification without consent

#### 4. RAG Tool Initialization Failed

**Cause**: Missing data files or ChromaDB issues

**Solution**:
- Verify data files exist in `RAG_DATA_PATH`
- Check file permissions
- Ensure ChromaDB dependencies installed
- Review logs for specific error

```bash
# Check data files
ls -la ./data/raw/
ls -la ./data/raw_sap/
```

#### 5. LangSmith Not Logging

**Cause**: Missing or invalid LangSmith configuration

**Solution**:
- Set `LANGSMITH_API_KEY` environment variable
- Verify project name in `LANGSMITH_PROJECT`
- Check `/health` endpoint for `langsmith.enabled: true`

#### 6. Rate Limit Exceeded (429)

**Cause**: Too many requests from same IP

**Solution**:
- Wait before retrying
- Implement exponential backoff
- Contact support for rate limit increase

### Debug Mode

For local debugging, the server provides detailed console output:

```bash
# Start server with verbose output
python3 agents/crewai/crew_agent_server_with_guard_rails.py

# Watch for:
# 🚀 Server startup messages
# 🔄 Initialization progress
# 📝 Request processing
# 🛡️ Compliance checks
# ✅ Success indicators
# ❌ Error details
```

### Health Check Interpretation

```json
{
  "status": "healthy",              // Overall status
  "initialization_complete": true,  // Agents ready
  "initialization_status": "ready", // Current stage
  "rag_enabled": true,              // RAG working
  "langsmith": {
    "enabled": true,                // Monitoring active
    "client_available": true        // Client connected
  }
}
```

Status values:
- `healthy`: All systems operational
- `initializing`: Startup in progress
- `unhealthy`: Initialization failed

Initialization stages:
- `starting`: Just started
- `initializing_langsmith`: Loading monitoring
- `initializing_llm`: Loading language model
- `initializing_rag`: Loading knowledge base
- `initializing_crew`: Building agents
- `ready`: Fully operational
- `failed`: Initialization error (see `initialization_error`)

## Performance Optimization

### Response Time

Typical response times:
- Health check: < 50ms
- Chat endpoint (cold): 2-5 seconds
- Chat endpoint (warm): 1-3 seconds

Factors affecting performance:
- RAG document retrieval time
- LLM generation speed
- Network latency
- ChromaDB query performance

### Cost Optimization

Monitor costs via LangSmith dashboard:

- **Token Usage**: Track input/output tokens per request
- **Model Selection**: GPT-4o-mini optimized for cost/performance
- **Response Length**: IVA Consulta responses limited to 600 chars
- **Caching**: ChromaDB caches frequently accessed documents

### Scaling Considerations

For high-traffic deployments:

1. **Horizontal Scaling**: Deploy multiple instances behind load balancer
2. **Rate Limiting**: Adjust limits based on capacity
3. **Caching**: Implement response caching for common queries
4. **Database**: Consider dedicated ChromaDB instance
5. **Monitoring**: Set up alerts for high latency/errors

## Support

For technical support or questions about the IVA Consulta agent, contact the development team.
