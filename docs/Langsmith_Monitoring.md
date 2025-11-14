# LangSmith Monitoring Setup Guide

This guide explains how to set up comprehensive monitoring for LLM calls, costs, and tokens using LangSmith in the SapRagTool.

## 🚀 Quick Start

### 1. Enable LangSmith Monitoring

Set the required environment variables:

```bash
# Required
export LANGSMITH_API_KEY="your_langsmith_api_key_here"
export LANGCHAIN_TRACING_V2="true"

# Optional
export LANGCHAIN_PROJECT="sap-rag-tool"
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
```

Or add to your `.env` file:

```env
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=sap-rag-tool
```

### 2. Run the Monitoring Dashboard

```bash
python monitoring_dashboard.py
```

## 📊 Monitoring Features

### Cost Tracking

- **Total costs** across all LLM calls
- **Daily cost breakdown** for budget monitoring
- **Cost per model** to identify expensive models
- **Cost per call** for efficiency analysis
- **Input/output token costs** for detailed breakdown

### Performance Metrics

- **Total call count** and success rate
- **Average latency** and response times
- **Error tracking** with error type classification
- **Model usage patterns** and performance by model
- **Response time distribution** (min, max, average)

### Token Usage

- **Total tokens** consumed across all calls
- **Input vs output tokens** breakdown
- **Token usage by model** for optimization
- **Average tokens per call** for efficiency

## 🎯 Dashboard Configuration

The monitoring system uses `langsmith_dashboard_config.json` for configuration:

```json
{
  "monitoring_metrics": {
    "cost_tracking": {
      "enabled": true,
      "alerts": {
        "daily_budget_exceeded": {
          "threshold": 10.0,
          "enabled": true
        }
      }
    }
  }
}
```

### Available Alerts

- **Daily Budget Exceeded**: Triggers when daily costs exceed threshold
- **High Error Rate**: Triggers when error rate exceeds 5%
- **Slow Response Time**: Triggers when average latency exceeds 30s

## 🔧 Integration with CrewAI

The monitoring is automatically integrated with CrewAI agents:

```python
from agents.langsmith_integration import get_langsmith_manager

# Get monitoring data
manager = get_langsmith_manager()
data = manager.get_monitoring_dashboard_data()

# Log monitoring summary
manager.log_monitoring_summary()
```

## 📈 LangSmith Dashboard Views

### 1. Cost Overview

- Total cost trends over time
- Daily cost breakdown
- Cost by model comparison
- Budget alerts and thresholds

### 2. Token Usage

- Token consumption trends
- Input vs output token ratios
- Token efficiency by model
- Usage patterns over time

### 3. Performance Metrics

- Call success rates
- Response time trends
- Error analysis
- Model performance comparison

### 4. Model Usage

- Call distribution by model
- Cost distribution by model
- Performance metrics by model
- Usage recommendations

## 🛠️ Advanced Configuration

### Custom Cost Calculation

Update pricing in `agents/langsmith_integration.py`:

```python
def _calculate_costs(self, model: str, input_tokens: int, output_tokens: int) -> tuple:
    pricing = {
        'gpt-4o': {'input': 0.005, 'output': 0.015},
        'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
        # Add your custom models here
    }
```

### Custom Alerts

Add alerts in `langsmith_dashboard_config.json`:

```json
{
  "alerts": [
    {
      "name": "Custom Alert",
      "condition": "total_cost > 50.0",
      "severity": "high",
      "enabled": true
    }
  ]
}
```

### Export Data

Export monitoring data in various formats:

```python
from agents.langsmith_integration import get_monitoring_dashboard_data
import json

# Get data
data = get_monitoring_dashboard_data()

# Export as JSON
with open('monitoring_data.json', 'w') as f:
    json.dump(data, f, indent=2)

# Export as CSV (using dashboard script)
python monitoring_dashboard.py
# Select option 3 for CSV export
```

## 📊 Dashboard Widgets

The monitoring dashboard includes several widgets:

1. **Cost Overview**: Line chart showing cost trends
2. **Token Usage**: Bar chart showing token consumption
3. **Model Usage**: Pie chart showing model distribution
4. **Performance Metrics**: Line chart showing latency and error rates
5. **Error Analysis**: Table showing error types and frequencies

## 🔍 Troubleshooting

### Common Issues

1. **LangSmith not enabled**

   - Check `LANGSMITH_API_KEY` is set
   - Verify API key is valid
   - Check network connectivity

2. **No cost data**

   - Ensure LLM calls are being made
   - Check if token usage is being tracked
   - Verify model pricing is configured

3. **Missing performance data**
   - Check if latency tracking is enabled
   - Verify error tracking is working
   - Ensure calls are being monitored

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 API Reference

### LangSmithManager Methods

```python
# Get monitoring data
data = manager.get_monitoring_dashboard_data()

# Log summary
manager.log_monitoring_summary()

# Track manual calls
manager.cost_tracker.track_llm_call(model, input_tokens, output_tokens, input_cost, output_cost, total_cost)
manager.llm_metrics.track_call(model, latency, success, error_type)
```

### Convenience Functions

```python
from agents.langsmith_integration import (
    get_monitoring_dashboard_data,
    log_monitoring_summary,
    track_llm_call_manually,
    track_llm_metrics_manually
)
```

## 🎯 Best Practices

1. **Set Budget Alerts**: Configure daily budget limits to avoid unexpected costs
2. **Monitor Error Rates**: Set up alerts for high error rates to catch issues early
3. **Regular Exports**: Export data regularly for historical analysis
4. **Model Optimization**: Use cost and performance data to optimize model selection
5. **Token Efficiency**: Monitor token usage to optimize prompts and responses

## 📞 Support

For issues with LangSmith monitoring:

1. Check the [LangSmith documentation](https://docs.smith.langchain.com/)
2. Verify your API key and project settings
3. Check the application logs for error messages
4. Use the monitoring dashboard to debug issues

## 🔄 Updates

The monitoring system is designed to be extensible. To add new metrics:

1. Update the `CostTracker` or `LLMMetricsTracker` classes
2. Add new dashboard widgets in the configuration
3. Update the dashboard display methods
4. Add new alerts as needed

This monitoring setup provides comprehensive visibility into your LLM usage, costs, and performance, helping you optimize your AI applications effectively.
