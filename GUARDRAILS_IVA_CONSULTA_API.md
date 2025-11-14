# IVA Consulta Agent API with Guardrails

## Overview

The IVA Consulta Agent with Guardrails is the **DEFAULT** specialized CrewAI agent designed to provide expert VAT and indirect taxation consultation services for Spanish and international companies. This version includes **EU AI Act compliance guardrails** to ensure all interactions meet regulatory requirements.

**🎯 This agent is now the default for all chat requests unless another agent type is specified.**
**🛡️ All requests are automatically validated against EU AI Act compliance rules.**

## Features

- **Expert VAT Knowledge**: Specialized in Spanish and European indirect taxation
- **RAG-Powered**: Uses processed VAT documentation from `data/raw` and `data/raw_ocr`
- **Concise Responses**: Automatically limits responses to 600 characters maximum
- **Spain Default**: Uses Spain as default country unless another jurisdiction is specified
- **Multi-language Support**: Can handle questions in Spanish and English
- **EU AI Act Compliance**: Automatic validation against EU AI Act requirements
- **Guardrails Protection**: Prevents non-compliant responses and logs violations
- **LangSmith Integration**: Comprehensive monitoring and tracing

## API Endpoints

### 1. General Chat Endpoint (Default: IVA Consulta with Guardrails)

**POST** `/chat`

```json
{
  "message": "¿Cuál es el IVA en España para servicios digitales?"
}
```

**Note**: The `agent_type` parameter is optional. If not specified, it defaults to `iva_consulta_agent`.

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

### 2. IVA Consulta Specific Endpoint (With Guardrails)

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

### 3. Health Check Endpoint

**GET** `/health`

Returns comprehensive system status including:

- RAG tool availability
- LLM model information
- LangSmith tracing status
- Guardrails compliance status

## Guardrails and Compliance

### EU AI Act Compliance

- **Automatic Validation**: All user messages are validated against EU AI Act requirements
- **Violation Detection**: Non-compliant requests are blocked and logged
- **Error Handling**: Clear error messages for compliance violations
- **Audit Trail**: All compliance checks are logged to LangSmith

### Response Safety

- **Content Filtering**: Responses are checked for compliance
- **Character Limiting**: Automatic 600-character limit for IVA Consulta responses
- **Error Logging**: All errors are tracked and monitored

## Integration with Website

To integrate with the [IVA Consulta website](https://nexdevconsulting.com/), use the `/iva-consulta` endpoint:

```javascript
// Example JavaScript integration with guardrails
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
    A concise and professional response about VAT and indirect taxation.
    The response should include specific VAT rules, compliance requirements, or procedures
    relevant to the user's question. If referencing another country, clearly specify the jurisdiction.
    The response should be practical, accurate, and directly helpful for business decision-making.
  agent: iva_consulta_agent
```

## Rate Limits

- **General Chat**: 15 requests per minute
- **IVA Consulta Endpoint**: 20 requests per minute
- **Health Check**: No limits

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (missing message or compliance violation)
- `401`: Unauthorized (missing or invalid API key)
- `429`: Rate limit exceeded
- `500`: Internal server error

## Compliance Violations

When a compliance violation is detected:

```json
{
  "error": "Compliance violation: [specific violation details]",
  "timestamp": "2025-01-22T10:30:00.000Z"
}
```

## Monitoring and Logging

### LangSmith Integration

- **Automatic Tracing**: All LLM calls are automatically traced
- **Performance Monitoring**: Response times and token usage tracked
- **Error Tracking**: All errors and compliance violations logged
- **Cost Monitoring**: LLM usage costs tracked and reported

### Compliance Logging

- **Violation Tracking**: All compliance violations are logged
- **Audit Trail**: Complete audit trail of all interactions
- **Performance Metrics**: Response quality and compliance metrics

## Testing

To test the IVA Consulta agent with guardrails:

```bash
# Run the test script
python3 test_guardrails_iva_consulta.py

# Or start the server and test via HTTP
python3 agents/crewai/crew_agent_server_with_guard_rails.py
curl -X POST http://localhost:8001/iva-consulta \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuál es el IVA en España?"}'
```

## Deployment

The agent is ready for deployment on Railway and will automatically:

1. Load the RAG knowledge base with processed VAT documents
2. Initialize the Google Generative AI configuration
3. Enable EU AI Act compliance guardrails
4. Start the Flask server with the IVA Consulta endpoint
5. Handle requests from the website chatbot with full compliance monitoring

## Security Features

- **API Key Authentication**: Required for production environments
- **Rate Limiting**: Prevents abuse and ensures fair usage
- **Compliance Validation**: Automatic EU AI Act compliance checking
- **Error Sanitization**: User-friendly error messages without sensitive information
- **Audit Logging**: Complete audit trail for compliance and security

## Support

For technical support or questions about the IVA Consulta agent with guardrails, contact the development team.

---

**Note**: This version includes comprehensive EU AI Act compliance features and is recommended for production use where regulatory compliance is required.
