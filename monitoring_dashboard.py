#!/usr/bin/env python3
"""
LangSmith Monitoring Dashboard

This script demonstrates how to use the enhanced LangSmith monitoring capabilities
for tracking LLM calls, costs, and tokens in the SapRagTool.

Features:
- Real-time cost and token tracking
- Performance metrics monitoring
- Dashboard data export
- Alert configuration
- Historical data analysis
"""

import os
import sys
import json
from datetime import datetime, timedelta
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


class MonitoringDashboard:
    """Interactive monitoring dashboard for LangSmith metrics."""
    
    def __init__(self):
        self.manager = get_langsmith_manager()
        self.dashboard_config = self._load_dashboard_config()
    
    def _load_dashboard_config(self):
        """Load dashboard configuration from JSON file."""
        config_path = project_root / "langsmith_dashboard_config.json"
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️  Dashboard config not found, using defaults")
            return {"dashboard_config": {"project_name": "sap-rag-tool-dev"}}
    
    def display_dashboard(self):
        """Display the monitoring dashboard."""
        print("\n" + "="*80)
        print("📊 LANGSMITH MONITORING DASHBOARD")
        print("="*80)
        
        if not self.manager.is_enabled():
            print("❌ LangSmith monitoring is disabled")
            print("   Set LANGSMITH_API_KEY environment variable to enable")
            return
        
        # Get current monitoring data
        data = get_monitoring_dashboard_data()
        
        # Display cost overview
        self._display_cost_overview(data['cost_summary'])
        
        # Display performance metrics
        self._display_performance_metrics(data['llm_metrics'])
        
        # Display model usage
        self._display_model_usage(data['cost_summary']['calls_by_model'])
        
        # Display alerts
        self._check_alerts(data)
        
        print(f"\n📅 Last Updated: {data['last_updated']}")
        print(f"🔗 LangSmith Project: {data['project']}")
    
    def _display_cost_overview(self, cost_summary):
        """Display cost overview section."""
        print("\n💰 COST OVERVIEW")
        print("-" * 40)
        print(f"Total Cost: ${cost_summary['total_cost']:.4f}")
        print(f"Total Tokens: {cost_summary['total_tokens']:,}")
        print(f"Average Cost per Call: ${cost_summary['average_cost_per_call']:.6f}")
        
        if cost_summary['daily_costs']:
            print("\n📅 Daily Costs (Last 7 Days):")
            for date, cost in sorted(cost_summary['daily_costs'].items())[-7:]:
                print(f"  {date}: ${cost:.4f}")
    
    def _display_performance_metrics(self, llm_metrics):
        """Display performance metrics section."""
        print("\n⚡ PERFORMANCE METRICS")
        print("-" * 40)
        print(f"Total Calls: {llm_metrics['total_calls']}")
        print(f"Error Count: {llm_metrics['error_count']}")
        print(f"Error Rate: {llm_metrics['error_rate']:.2%}")
        print(f"Average Latency: {llm_metrics['average_latency']:.2f}s")
        
        if llm_metrics['response_times']:
            response_times = llm_metrics['response_times']
            print(f"Response Time Range: {response_times['min']:.2f}s - {response_times['max']:.2f}s")
    
    def _display_model_usage(self, calls_by_model):
        """Display model usage section."""
        if not calls_by_model:
            print("\n📈 MODEL USAGE")
            print("-" * 40)
            print("No model usage data available")
            return
        
        print("\n📈 MODEL USAGE")
        print("-" * 40)
        for model, stats in calls_by_model.items():
            print(f"\n{model}:")
            print(f"  Calls: {stats['calls']}")
            print(f"  Cost: ${stats['cost']:.4f}")
            print(f"  Tokens: {stats['tokens']:,}")
            print(f"  Input Tokens: {stats['input_tokens']:,}")
            print(f"  Output Tokens: {stats['output_tokens']:,}")
            if stats['calls'] > 0:
                print(f"  Avg Cost/Call: ${stats['cost']/stats['calls']:.6f}")
                print(f"  Avg Tokens/Call: {stats['tokens']/stats['calls']:.1f}")
    
    def _check_alerts(self, data):
        """Check and display alerts."""
        alerts = self.dashboard_config.get('alerts', [])
        if not alerts:
            return
        
        print("\n🚨 ALERTS")
        print("-" * 40)
        
        cost_summary = data['cost_summary']
        llm_metrics = data['llm_metrics']
        
        for alert in alerts:
            if not alert.get('enabled', True):
                continue
            
            condition = alert['condition']
            severity = alert.get('severity', 'low')
            name = alert['name']
            
            # Simple condition evaluation (in production, use a proper expression evaluator)
            triggered = False
            if "daily_costs >" in condition:
                threshold = float(condition.split('>')[1].strip())
                today = datetime.now().strftime('%Y-%m-%d')
                today_cost = cost_summary['daily_costs'].get(today, 0)
                triggered = today_cost > threshold
            elif "error_rate >" in condition:
                threshold = float(condition.split('>')[1].strip())
                triggered = llm_metrics['error_rate'] > threshold
            elif "average_latency >" in condition:
                threshold = float(condition.split('>')[1].strip())
                triggered = llm_metrics['average_latency'] > threshold
            
            if triggered:
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
                print(f"{severity_icon} {name} - {severity.upper()}")
            else:
                print(f"✅ {name} - OK")
    
    def export_data(self, format='json', filename=None):
        """Export monitoring data to file."""
        data = get_monitoring_dashboard_data()
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"langsmith_monitoring_{timestamp}.{format}"
        
        filepath = project_root / filename
        
        if format == 'json':
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        elif format == 'csv':
            self._export_csv(data, filepath)
        else:
            print(f"❌ Unsupported format: {format}")
            return
        
        print(f"✅ Data exported to: {filepath}")
    
    def _export_csv(self, data, filepath):
        """Export data as CSV."""
        import csv
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write cost summary
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Cost', data['cost_summary']['total_cost']])
            writer.writerow(['Total Tokens', data['cost_summary']['total_tokens']])
            writer.writerow(['Total Calls', data['llm_metrics']['total_calls']])
            writer.writerow(['Error Rate', data['llm_metrics']['error_rate']])
            writer.writerow(['Average Latency', data['llm_metrics']['average_latency']])
            
            # Write model usage
            writer.writerow([])
            writer.writerow(['Model', 'Calls', 'Cost', 'Tokens'])
            for model, stats in data['cost_summary']['calls_by_model'].items():
                writer.writerow([model, stats['calls'], stats['cost'], stats['tokens']])
    
    def simulate_llm_calls(self, num_calls=5):
        """Simulate LLM calls for testing purposes."""
        print(f"\n🧪 Simulating {num_calls} LLM calls...")
        
        models = ['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo']
        
        for i in range(num_calls):
            model = models[i % len(models)]
            input_tokens = 100 + (i * 50)
            output_tokens = 50 + (i * 25)
            
            # Simulate costs
            input_cost = (input_tokens / 1000) * 0.00015
            output_cost = (output_tokens / 1000) * 0.0006
            total_cost = input_cost + output_cost
            
            # Simulate latency
            latency = 1.0 + (i * 0.5)
            
            # Track the call
            track_llm_call_manually(model, input_tokens, output_tokens, 
                                  input_cost, output_cost, total_cost)
            track_llm_metrics_manually(model, latency, success=True)
            
            print(f"  Call {i+1}: {model} - {input_tokens + output_tokens} tokens, ${total_cost:.4f}")
        
        print("✅ Simulation complete")


def main():
    """Main dashboard interface."""
    dashboard = MonitoringDashboard()
    
    while True:
        print("\n" + "="*50)
        print("LANGSMITH MONITORING DASHBOARD")
        print("="*50)
        print("1. Display Dashboard")
        print("2. Export Data (JSON)")
        print("3. Export Data (CSV)")
        print("4. Simulate LLM Calls")
        print("5. Log Summary")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            dashboard.display_dashboard()
        elif choice == '2':
            dashboard.export_data('json')
        elif choice == '3':
            dashboard.export_data('csv')
        elif choice == '4':
            try:
                num_calls = int(input("Number of calls to simulate (default 5): ") or "5")
                dashboard.simulate_llm_calls(num_calls)
            except ValueError:
                print("❌ Invalid number")
        elif choice == '5':
            log_monitoring_summary()
        elif choice == '6':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")


if __name__ == "__main__":
    main()
