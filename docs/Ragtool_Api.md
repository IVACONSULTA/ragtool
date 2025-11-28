# IVA Consulta Agent API

## Overview

The IVA Consulta Agent is a specialized CrewAI agent designed to provide expert VAT and indirect taxation consultation services for Spanish and international companies. It uses the RAG (Retrieval Augmented Generation) system with processed VAT documentation to provide accurate, up-to-date information.

## Features

- **Expert VAT Knowledge**: Specialized in Spanish and European indirect taxation
- **RAG-Powered**: Uses processed VAT documentation from `data/raw` and `data/raw_ocr`
- **Concise Responses**: Automatically limits responses to 600 characters maximum
- **Spain Default**: Uses Spain as default country unless another jurisdiction is specified
- **Multi-language Support**: Can handle questions in Spanish and English

## API Endpoints

### 1. General Chat Endpoint

**POST** `/chat`

```json
{
  "message": "¿Cuál es el IVA en España para servicios digitales?",
  "agent_type": "iva_consulta_agent"
}
```

**Response:**

```json
{
  "response": "En España, los servicios digitales están sujetos al IVA general del 21%. Para empresas no establecidas en la UE, aplica el régimen especial de servicios digitales...",
  "agent_type": "iva_consulta_agent",
  "timestamp": "2025-01-22T10:30:00.000Z"
}
```

### 2. IVA Consulta Specific Endpoint

**POST** `/iva-consulta`

```json
{
  "message": "¿Qué documentos necesito para la declaración de IVA?"
}
```

**Response:**

```json
{
  "response": "Para la declaración de IVA necesitas: 1) Facturas emitidas y recibidas, 2) Libros registro de IVA, 3) Certificados de retenciones, 4) Documentación de operaciones intracomunitarias...",
  "agent_type": "iva_consulta_agent",
  "timestamp": "2025-01-22T10:30:00.000Z",
  "source": "IVA Consulta VAT Specialist"
}
```

## Integration with Website

To integrate with the [IVA Consulta website](https://nexdevconsulting.com/), use the `/iva-consulta` endpoint:

```javascript
// Example JavaScript integration
async function askIVAQuestion(question) {
  const response = await fetch(
    "https://your-railway-domain.railway.app/iva-consulta",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: question,
      }),
    }
  );

  const data = await response.json();
  return data.response;
}

// Usage
const answer = await askIVAQuestion("¿Cuál es el IVA en España?");
console.log(answer);
```

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

- **General Chat**: 5 requests per minute
- **IVA Consulta Endpoint**: 10 requests per minute

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (missing message)
- `429`: Rate limit exceeded
- `500`: Internal server error

## Testing

To test the IVA Consulta agent locally:

```bash
# Run the test script
python3 test_iva_consulta.py

# Or start the server and test via HTTP
python3 agents/crewai/crew_agent_server.py
curl -X POST http://localhost:8003/iva-consulta \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuál es el IVA en España?"}'
```

## Deployment

The agent is ready for deployment on Railway/Google Cloud Run and will automatically:

1. Read `AGENT_ROLE` environment variable (defaults to `vat_agent`)
2. Build **only** the crew corresponding to `AGENT_ROLE`:
   - `AGENT_ROLE=vat_agent` → Builds **only** IVA Consulta Crew
   - `AGENT_ROLE=sap_agent` → Builds **only** SAP Crew
3. Initialize RAG tool with role-specific data path (fails immediately if initialization fails, no fallback)
4. Load the RAG knowledge base with processed documents
5. Initialize the LLM configuration
6. Start the Flask server with the chat endpoint
7. Handle requests from the website chatbot

### Environment Variables

```bash
# Required: Set agent role
AGENT_ROLE=vat_agent  # or sap_agent

# Optional: Override data path
RAG_DATA_PATH=./data/raw  # Default depends on AGENT_ROLE
```

## Support

For technical support or questions about the IVA Consulta agent, contact the development team.
