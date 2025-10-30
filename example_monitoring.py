#!/usr/bin/env python3
"""
Example LangSmith Monitoring Usage

This script demonstrates how to use the enhanced LangSmith monitoring
capabilities for tracking LLM calls, costs, and tokens.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from agents.langsmith_integration import (
    get_langsmith_manager,
    get_monitoring_dashboard_data,
    log_monitoring_summary,
    track_llm_call_manually,
    track_llm_metrics_manually
)


def main():
    """Demonstrate LangSmith monitoring capabilities."""
    print("🚀 LangSmith Monitoring Example")
    print("=" * 50)
    
    # Initialize LangSmith manager
    manager = get_langsmith_manager()
    
    if not manager.is_enabled():
        print("❌ LangSmith monitoring is disabled")
        print("   Set LANGSMITH_API_KEY environment variable to enable")
        print("\n💡 Example setup:")
        print("   export LANGSMITH_API_KEY='your_api_key_here'")
        print("   export LANGCHAIN_TRACING_V2='true'")
        return
    
    print("✅ LangSmith monitoring is enabled")
    
    # Simulate some LLM calls for demonstration
    print("\n🧪 Simulating LLM calls...")
    
    # Simulate calls to different models
    test_calls = [
        {
            "model": "gpt-4o-mini",
            "input_tokens": 150,
            "output_tokens": 75,
            "latency": 1.2
        },
        {
            "model": "gpt-4o",
            "input_tokens": 200,
            "output_tokens": 100,
            "latency": 2.5
        },
        {
            "model": "gpt-3.5-turbo",
            "input_tokens": 100,
            "output_tokens": 50,
            "latency": 0.8
        }
    ]
    
    for i, call in enumerate(test_calls, 1):
        print(f"  Call {i}: {call['model']} - {call['input_tokens'] + call['output_tokens']} tokens")
        
        # Calculate costs (approximate)
        input_cost = (call['input_tokens'] / 1000) * 0.00015
        output_cost = (call['output_tokens'] / 1000) * 0.0006
        total_cost = input_cost + output_cost
        
        # Track the call
        track_llm_call_manually(
            call['model'],
            call['input_tokens'],
            call['output_tokens'],
            input_cost,
            output_cost,
            total_cost
        )
        
        # Track metrics
        track_llm_metrics_manually(
            call['model'],
            call['latency'],
            success=True
        )
    
    print("✅ Simulation complete")
    
    # Display monitoring summary
    print("\n📊 Monitoring Summary:")
    log_monitoring_summary()
    
    # Get detailed dashboard data
    print("\n📈 Detailed Dashboard Data:")
    data = get_monitoring_dashboard_data()
    
    print(f"Total Cost: ${data['cost_summary']['total_cost']:.4f}")
    print(f"Total Tokens: {data['cost_summary']['total_tokens']:,}")
    print(f"Total Calls: {data['llm_metrics']['total_calls']}")
    print(f"Average Latency: {data['llm_metrics']['average_latency']:.2f}s")
    
    # Show model breakdown
    if data['cost_summary']['calls_by_model']:
        print("\n📊 Model Breakdown:")
        for model, stats in data['cost_summary']['calls_by_model'].items():
            print(f"  {model}:")
            print(f"    Calls: {stats['calls']}")
            print(f"    Cost: ${stats['cost']:.4f}")
            print(f"    Tokens: {stats['tokens']:,}")
    
    print("\n🎉 Example completed!")
    print("\n💡 Next steps:")
    print("   1. Run 'python monitoring_dashboard.py' for interactive dashboard")
    print("   2. Check your LangSmith project dashboard at https://smith.langchain.com/")
    print("   3. Configure alerts in langsmith_dashboard_config.json")


if __name__ == "__main__":
    main()
