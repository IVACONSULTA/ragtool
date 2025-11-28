# RAG Tool LangSmith Integration Setup

This guide explains how to set up LangSmith tracing for your RAG tool's LLM calls in the "sap-rag-tool-dev" project.

## 🎯 Overview

The RAG tool now automatically traces all its internal LLM calls to LangSmith, providing comprehensive monitoring of:

- RAG search operations
- LLM calls made during document retrieval
- Cost and token usage
- Performance metrics
- Error tracking

## 🚀 Quick Setup

### 1. Set Environment Variables

```bash
# Required
export LANGSMITH_API_KEY="your_langsmith_api_key_here"
export LANGCHAIN_TRACING_V2="true"

# Optional (defaults to sap-rag-tool-dev)
export LANGCHAIN_PROJECT="sap-rag-tool-dev"
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
```

Or add to your `.env` file:

```env
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=sap-rag-tool-dev
```

### 2. Test the Integration

```bash
python test_rag_langsmith_tracing.py
```

### 3. View Traces in LangSmith

1. Visit https://smith.langchain.com/
2. Navigate to the "sap-rag-tool-dev" project
3. View traces of RAG operations and LLM calls

## 🔧 How It Works

### Automatic Tracing Setup

When the RAG tool is initialized, it automatically:

1. **Sets up LangSmith environment variables** for automatic tracing
2. **Configures the project** to use "sap-rag-tool-dev"
3. **Enables tracing** for all internal LLM calls
4. **Logs RAG operations** with detailed metadata

### RAG Operation Tracing

Each RAG search operation creates traces for:

- **RAG Search Start**: When a search begins
- **LLM Calls**: All internal LLM calls made by the RAG tool
- **RAG Search Results**: The final search results
- **Errors**: Any errors that occur during the process

### Trace Structure

```
sap-rag-tool-dev/
├── rag_search/
│   ├── Input: {"query": "SAP consulting"}
│   ├── Output: {"result": "Search results..."}
│   └── Metadata: {"operation": "search", "timestamp": "..."}
└── llm_call_*/
    ├── Input: {"model": "gpt-4o-mini", "prompt": "..."}
    ├── Output: {"response": "..."}
    └── Metadata: {"cost": 0.001, "tokens": 150, "latency": 1.2}
```

## 📊 Monitoring Features

### Cost Tracking

- **RAG operation costs** from internal LLM calls
- **Token usage** for each search operation
- **Cost per search** analysis
- **Daily cost breakdown** for RAG operations

### Performance Metrics

- **Search latency** for each RAG operation
- **LLM call performance** within RAG operations
- **Error rates** for RAG searches
- **Success/failure tracking**

### Usage Analytics

- **Search frequency** and patterns
- **Query types** and complexity
- **Result quality** metrics
- **User interaction** patterns

## 🛠️ Configuration

### Project Settings

The RAG tool is configured to use the "sap-rag-tool-dev" project by default. This can be changed by setting the `LANGCHAIN_PROJECT` environment variable.

### Tracing Levels

The RAG tool traces at multiple levels:

1. **RAG Operation Level**: High-level search operations
2. **LLM Call Level**: Individual LLM calls within RAG
3. **Error Level**: Error tracking and debugging

### Custom Metadata

Each trace includes custom metadata:

```json
{
  "operation": "rag_search",
  "query_type": "semantic_search",
  "result_length": 1500,
  "processing_time": 2.5,
  "model_used": "gpt-4o-mini",
  "tokens_used": 300,
  "cost": 0.002
}
```

## 🔍 Troubleshooting

### Common Issues

1. **No traces appearing in LangSmith**

   - Check `LANGSMITH_API_KEY` is set correctly
   - Verify `LANGCHAIN_TRACING_V2=true`
   - Ensure the project name is correct

2. **RAG tool not tracing**

   - Check if RAG tool is properly initialized
   - Verify LangSmith integration is enabled
   - Check application logs for errors

3. **Missing LLM call traces**
   - Ensure the RAG tool's internal LLM calls are being made
   - Check if the LLM configuration is correct
   - Verify CrewAI RagTool is working properly

### Debug Mode

Enable debug logging to see tracing details:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Verification Steps

1. **Check Environment Variables**:

   ```bash
   echo $LANGSMITH_API_KEY
   echo $LANGCHAIN_TRACING_V2
   echo $LANGCHAIN_PROJECT
   ```

2. **Test RAG Tool**:

   ```bash
   python test_rag_langsmith_tracing.py
   ```

3. **Check LangSmith Dashboard**:
   - Visit https://smith.langchain.com/
   - Look for traces in "sap-rag-tool-dev" project

## 📈 Dashboard Views

### RAG Operations View

- **Search frequency** over time
- **Query success rates**
- **Average response times**
- **Cost per search**

### LLM Calls View

- **Model usage** within RAG operations
- **Token consumption** patterns
- **Cost breakdown** by model
- **Performance metrics**

### Error Analysis

- **Error types** in RAG operations
- **Failure patterns** and causes
- **Debugging information**
- **Resolution tracking**

## 🎯 Best Practices

### 1. Monitor RAG Performance

- Set up alerts for high latency
- Track cost per search operation
- Monitor error rates

### 2. Optimize Queries

- Analyze query patterns
- Identify common failure cases
- Optimize for better results

### 3. Cost Management

- Set daily budgets for RAG operations
- Monitor token usage patterns
- Optimize model selection

### 4. Error Handling

- Set up error alerts
- Track error patterns
- Implement retry logic

## 🔄 Updates and Maintenance

### Regular Monitoring

- Check traces daily for issues
- Monitor cost trends
- Review error patterns

### Configuration Updates

- Update project settings as needed
- Adjust tracing levels
- Modify metadata collection

### Performance Optimization

- Analyze slow queries
- Optimize LLM model selection
- Improve search algorithms

## 📞 Support

For issues with RAG tool LangSmith integration:

1. Check the troubleshooting section above
2. Review application logs
3. Test with the provided test script
4. Verify LangSmith configuration

## 🎉 Success Indicators

You'll know the integration is working when you see:

1. **Traces in LangSmith**: RAG operations appear in the "sap-rag-tool-dev" project
2. **LLM Call Traces**: Individual LLM calls are traced with cost and performance data
3. **Monitoring Dashboard**: Data appears in the monitoring dashboard
4. **No Errors**: RAG tool operates without LangSmith-related errors

This integration provides comprehensive visibility into your RAG tool's LLM usage, helping you optimize performance and manage costs effectively.
