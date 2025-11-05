"""
LangSmith Integration Module

This module provides LangSmith tracing and monitoring capabilities for the SapRagTool.
It integrates with the existing configuration system and provides decorators and
utilities for tracing AI agent operations.

Features:
- Automatic tracing of CrewAI agent operations
- RAG tool operation tracing
- HTTP request/response tracing
- Error tracking and debugging
- Performance monitoring
"""

import json
import os
import sys
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    from langsmith import Client, trace, traceable
    from langsmith.wrappers import wrap_openai

    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False

    # Create a dummy Client class for type hints when LangSmith is not available
    class Client:
        pass

    print("⚠️  LangSmith not available. Install with: pip install langsmith")

from agents.utils.config import get_langsmith_config


class CostTracker:
    """Tracks LLM costs and token usage for monitoring and budgeting."""

    def __init__(self):
        self.total_cost = 0.0
        self.total_tokens = 0
        self.calls_by_model = {}
        self.cost_by_model = {}
        self.daily_costs = {}

    def track_llm_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        input_cost: float,
        output_cost: float,
        total_cost: float,
    ):
        """Track an LLM call with cost and token information."""
        total_tokens = input_tokens + output_tokens

        # Update totals
        self.total_cost += total_cost
        self.total_tokens += total_tokens

        # Track by model
        if model not in self.calls_by_model:
            self.calls_by_model[model] = {
                "calls": 0,
                "tokens": 0,
                "cost": 0.0,
                "input_tokens": 0,
                "output_tokens": 0,
            }

        self.calls_by_model[model]["calls"] += 1
        self.calls_by_model[model]["tokens"] += total_tokens
        self.calls_by_model[model]["cost"] += total_cost
        self.calls_by_model[model]["input_tokens"] += input_tokens
        self.calls_by_model[model]["output_tokens"] += output_tokens

        # Track daily costs
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.daily_costs:
            self.daily_costs[today] = 0.0
        self.daily_costs[today] += total_cost

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get a summary of costs and usage."""
        return {
            "total_cost": self.total_cost,
            "total_tokens": self.total_tokens,
            "calls_by_model": self.calls_by_model,
            "daily_costs": self.daily_costs,
            "average_cost_per_call": (
                self.total_cost
                / sum(model["calls"] for model in self.calls_by_model.values())
                if self.calls_by_model
                else 0
            ),
        }


class LLMMetricsTracker:
    """Tracks LLM performance metrics and usage patterns."""

    def __init__(self):
        self.call_count = 0
        self.error_count = 0
        self.total_latency = 0.0
        self.response_times = []
        self.model_usage = {}
        self.error_types = {}

    def track_call(
        self, model: str, latency: float, success: bool = True, error_type: str = None
    ):
        """Track an LLM call with performance metrics."""
        self.call_count += 1
        self.total_latency += latency
        self.response_times.append(latency)

        # Track model usage
        if model not in self.model_usage:
            self.model_usage[model] = {"calls": 0, "total_latency": 0.0}
        self.model_usage[model]["calls"] += 1
        self.model_usage[model]["total_latency"] += latency

        if not success:
            self.error_count += 1
            if error_type:
                self.error_types[error_type] = self.error_types.get(error_type, 0) + 1

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of LLM performance metrics."""
        avg_latency = self.total_latency / self.call_count if self.call_count > 0 else 0
        error_rate = self.error_count / self.call_count if self.call_count > 0 else 0

        return {
            "total_calls": self.call_count,
            "error_count": self.error_count,
            "error_rate": error_rate,
            "average_latency": avg_latency,
            "model_usage": self.model_usage,
            "error_types": self.error_types,
            "response_times": {
                "min": min(self.response_times) if self.response_times else 0,
                "max": max(self.response_times) if self.response_times else 0,
                "avg": avg_latency,
            },
        }


class LangSmithManager:
    """
    Manages LangSmith integration for the SapRagTool.

    Provides centralized configuration and tracing capabilities with comprehensive
    monitoring for LLM calls, costs, and tokens.
    """

    def __init__(self):
        self.client: Optional[Client] = None
        self.config = get_langsmith_config()
        self.enabled = self.config.get("enabled", False)
        self.cost_tracker = CostTracker()
        self.llm_metrics = LLMMetricsTracker()

        if self.enabled and LANGSMITH_AVAILABLE:
            self._initialize_client()
        elif self.enabled and not LANGSMITH_AVAILABLE:
            print(
                "❌ LangSmith is enabled but not installed. Install with: pip install langsmith"
            )
            self.enabled = False

    def _initialize_client(self):
        """Initialize the LangSmith client."""
        try:
            api_key = self.config.get("api_key")
            project = self.config.get("project", "sap-rag-tool")
            endpoint = self.config.get("endpoint")

            if not api_key:
                print(
                    "❌ LangSmith API key not found. Set LANGSMITH_API_KEY environment variable."
                )
                self.enabled = False
                return

            client_kwargs = {
                "api_key": api_key,
            }

            if endpoint:
                client_kwargs["api_url"] = endpoint

            self.client = Client(**client_kwargs)
            print(f"✅ LangSmith client initialized for project: {project}")

        except Exception as e:
            print(f"❌ Failed to initialize LangSmith client: {e}")
            self.enabled = False

    def is_enabled(self) -> bool:
        """Check if LangSmith tracing is enabled."""
        return self.enabled and self.client is not None

    def get_client(self) -> Optional[Client]:
        """Get the LangSmith client instance."""
        return self.client if self.is_enabled() else None

    def trace_function(self, name: Optional[str] = None, **kwargs):
        """
        Decorator for tracing function calls.

        Args:
            name: Custom name for the trace (defaults to function name)
            **kwargs: Additional tracing parameters
        """

        def decorator(func: Callable) -> Callable:
            if not self.is_enabled():
                return func

            @wraps(func)
            def wrapper(*args, **func_kwargs):
                trace_name = name or f"{func.__module__}.{func.__name__}"
                return traceable(name=trace_name, **kwargs)(func)(*args, **func_kwargs)

            return wrapper

        return decorator

    def trace_async_function(self, name: Optional[str] = None, **kwargs):
        """
        Decorator for tracing async function calls.

        Args:
            name: Custom name for the trace (defaults to function name)
            **kwargs: Additional tracing parameters
        """

        def decorator(func: Callable) -> Callable:
            if not self.is_enabled():
                return func

            @wraps(func)
            async def wrapper(*args, **func_kwargs):
                trace_name = name or f"{func.__module__}.{func.__name__}"
                return await traceable(name=trace_name, **kwargs)(func)(
                    *args, **func_kwargs
                )

            return wrapper

        return decorator

    def create_traced_openai_client(self, openai_client):
        """
        Create a traced OpenAI client with comprehensive monitoring.

        Args:
            openai_client: The OpenAI client to wrap

        Returns:
            Traced OpenAI client or original client if LangSmith is disabled
        """
        if not self.is_enabled():
            return openai_client

        try:
            # Wrap with LangSmith tracing
            traced_client = wrap_openai(openai_client)

            # Add custom monitoring wrapper
            return self._add_monitoring_wrapper(traced_client)
        except Exception as e:
            print(f"⚠️  Failed to wrap OpenAI client with LangSmith: {e}")
            return openai_client

    def _add_monitoring_wrapper(self, client):
        """Add custom monitoring wrapper to the traced client."""
        original_chat = client.chat.completions.create

        def monitored_chat_completions_create(*args, **kwargs):
            start_time = datetime.now()
            model = kwargs.get("model", "unknown")

            try:
                # Call the original method
                response = original_chat(*args, **kwargs)

                # Calculate metrics
                end_time = datetime.now()
                latency = (end_time - start_time).total_seconds()

                # Track successful call
                self.llm_metrics.track_call(model, latency, success=True)

                # Extract token usage and costs if available
                if hasattr(response, "usage") and response.usage:
                    usage = response.usage
                    input_tokens = getattr(usage, "prompt_tokens", 0)
                    output_tokens = getattr(usage, "completion_tokens", 0)

                    # Calculate costs (approximate rates)
                    input_cost, output_cost, total_cost = self._calculate_costs(
                        model, input_tokens, output_tokens
                    )

                    # Track cost information
                    self.cost_tracker.track_llm_call(
                        model,
                        input_tokens,
                        output_tokens,
                        input_cost,
                        output_cost,
                        total_cost,
                    )

                    # Log to LangSmith with cost metadata
                    self._log_llm_call_with_costs(
                        model,
                        input_tokens,
                        output_tokens,
                        total_cost,
                        latency,
                        response,
                    )

                return response

            except Exception as e:
                # Track failed call
                end_time = datetime.now()
                latency = (end_time - start_time).total_seconds()
                self.llm_metrics.track_call(
                    model, latency, success=False, error_type=type(e).__name__
                )
                raise

        # Replace the method
        client.chat.completions.create = monitored_chat_completions_create
        return client

    def _calculate_costs(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> tuple:
        """Calculate costs based on model and token usage."""
        # OpenAI pricing (as of 2024, approximate)
        pricing = {
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        }

        # Get pricing for model (use gpt-4o-mini as default)
        model_pricing = pricing.get(model, pricing["gpt-4o-mini"])

        input_cost = (input_tokens / 1000) * model_pricing["input"]
        output_cost = (output_tokens / 1000) * model_pricing["output"]
        total_cost = input_cost + output_cost

        return input_cost, output_cost, total_cost

    def _log_llm_call_with_costs(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        total_cost: float,
        latency: float,
        response,
    ):
        """Log LLM call with cost and performance metadata to LangSmith."""
        if not self.is_enabled():
            return

        try:
            with trace(name=f"llm_call_{model}", run_type="llm") as run:
                run.inputs = {
                    "model": model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                }
                run.outputs = {
                    "response": (
                        str(response.choices[0].message.content)
                        if hasattr(response, "choices")
                        else str(response)
                    )
                }
                run.metadata = {
                    "model": model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "total_cost": total_cost,
                    "latency_seconds": latency,
                    "cost_per_token": (
                        total_cost / (input_tokens + output_tokens)
                        if (input_tokens + output_tokens) > 0
                        else 0
                    ),
                }
        except Exception as e:
            print(f"⚠️  Failed to log LLM call to LangSmith: {e}")

    def get_monitoring_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive monitoring data for dashboard display."""
        return {
            "cost_summary": self.cost_tracker.get_cost_summary(),
            "llm_metrics": self.llm_metrics.get_metrics_summary(),
            "langsmith_enabled": self.is_enabled(),
            "project": self.config.get("project", "sap-rag-tool"),
            "last_updated": datetime.now().isoformat(),
        }

    def log_monitoring_summary(self):
        """Log a summary of current monitoring data."""
        if not self.is_enabled():
            print("📊 LangSmith monitoring is disabled")
            return

        data = self.get_monitoring_dashboard_data()
        cost_summary = data["cost_summary"]
        llm_metrics = data["llm_metrics"]

        print("\n📊 LangSmith Monitoring Summary")
        print("=" * 50)
        print(f"💰 Total Cost: ${cost_summary['total_cost']:.4f}")
        print(f"🔢 Total Tokens: {cost_summary['total_tokens']:,}")
        print(f"📞 Total Calls: {llm_metrics['total_calls']}")
        print(f"⚡ Average Latency: {llm_metrics['average_latency']:.2f}s")
        print(f"❌ Error Rate: {llm_metrics['error_rate']:.2%}")

        if cost_summary["calls_by_model"]:
            print("\n📈 Usage by Model:")
            for model, stats in cost_summary["calls_by_model"].items():
                print(
                    f"  {model}: {stats['calls']} calls, ${stats['cost']:.4f}, {stats['tokens']:,} tokens"
                )

        if llm_metrics["error_types"]:
            print("\n🚨 Error Types:")
            for error_type, count in llm_metrics["error_types"].items():
                print(f"  {error_type}: {count} occurrences")

    def log_rag_operation(self, operation: str, query: str, result: Any, metadata: Optional[Dict] = None):
        """
        Log a RAG operation to LangSmith.

        Args:
            operation: Type of RAG operation (e.g., "search", "retrieve")
            query: The search query
            result: The operation result
            metadata: Optional metadata dictionary to include in the trace
        """
        if not self.is_enabled():
            return

        try:
            # Create a trace for the RAG operation using the trace context manager
            with trace(name=f"rag_{operation}", run_type="tool") as run:
                run.inputs = {"query": query}
                run.outputs = {"result": str(result)}
                if metadata:
                    run.extra = metadata
        except Exception as e:
            print(f"⚠️  Failed to log RAG operation to LangSmith: {e}")

    def log_agent_interaction(
        self,
        agent_name: str,
        user_message: str,
        agent_response: str,
        metadata: Optional[Dict] = None,
    ):
        """
        Log an agent interaction to LangSmith.

        Args:
            agent_name: Name of the agent
            user_message: User's input message
            agent_response: Agent's response
            metadata: Additional metadata
        """
        if not self.is_enabled():
            return

        try:
            # Create a trace for the agent interaction using the trace context manager
            with trace(name=f"agent_{agent_name}", run_type="chain") as run:
                run.inputs = {"user_message": user_message}
                run.outputs = {"agent_response": agent_response}
        except Exception as e:
            print(f"⚠️  Failed to log agent interaction to LangSmith: {e}")

    def log_error(
        self, error: Exception, context: str, metadata: Optional[Dict] = None
    ):
        """
        Log an error to LangSmith.

        Args:
            error: The exception that occurred
            context: Context where the error occurred
            metadata: Additional metadata
        """
        if not self.is_enabled():
            return

        try:
            # Create a trace for the error using the trace context manager
            with trace(name=f"error_{context}", run_type="chain") as run:
                run.inputs = {"context": context}
                run.outputs = {"error": str(error), "error_type": type(error).__name__}
                if metadata:
                    run.metadata = metadata
        except Exception as e:
            print(f"⚠️  Failed to log error to LangSmith: {e}")


# Global LangSmith manager instance
_langsmith_manager = None


def get_langsmith_manager() -> LangSmithManager:
    """Get the global LangSmith manager instance."""
    global _langsmith_manager
    if _langsmith_manager is None:
        _langsmith_manager = LangSmithManager()
    return _langsmith_manager


def trace_function(name: Optional[str] = None, **kwargs):
    """
    Convenience decorator for tracing function calls.

    Usage:
        @trace_function("my_operation")
        def my_function():
            pass
    """
    manager = get_langsmith_manager()
    return manager.trace_function(name, **kwargs)


def trace_async_function(name: Optional[str] = None, **kwargs):
    """
    Convenience decorator for tracing async function calls.

    Usage:
        @trace_async_function("my_async_operation")
        async def my_async_function():
            pass
    """
    manager = get_langsmith_manager()
    return manager.trace_async_function(name, **kwargs)


def log_rag_operation(
    operation: str, query: str, result: Any, metadata: Optional[Dict] = None
):
    """Convenience function for logging RAG operations."""
    manager = get_langsmith_manager()
    manager.log_rag_operation(operation, query, result, metadata)


def log_agent_interaction(
    agent_name: str,
    user_message: str,
    agent_response: str,
    metadata: Optional[Dict] = None,
):
    """Convenience function for logging agent interactions."""
    manager = get_langsmith_manager()
    manager.log_agent_interaction(agent_name, user_message, agent_response, metadata)


def log_error(error: Exception, context: str, metadata: Optional[Dict] = None):
    """Convenience function for logging errors."""
    manager = get_langsmith_manager()
    manager.log_error(error, context, metadata)


def create_traced_openai_client(openai_client):
    """Convenience function for creating traced OpenAI clients."""
    manager = get_langsmith_manager()
    return manager.create_traced_openai_client(openai_client)


def get_monitoring_dashboard_data() -> Dict[str, Any]:
    """Convenience function for getting monitoring dashboard data."""
    manager = get_langsmith_manager()
    return manager.get_monitoring_dashboard_data()


def log_monitoring_summary():
    """Convenience function for logging monitoring summary."""
    manager = get_langsmith_manager()
    manager.log_monitoring_summary()


def track_llm_call_manually(
    model: str,
    input_tokens: int,
    output_tokens: int,
    input_cost: float,
    output_cost: float,
    total_cost: float,
):
    """Manually track an LLM call for cases where automatic tracking isn't available."""
    manager = get_langsmith_manager()
    manager.cost_tracker.track_llm_call(
        model, input_tokens, output_tokens, input_cost, output_cost, total_cost
    )


def track_llm_metrics_manually(
    model: str, latency: float, success: bool = True, error_type: str = None
):
    """Manually track LLM metrics for cases where automatic tracking isn't available."""
    manager = get_langsmith_manager()
    manager.llm_metrics.track_call(model, latency, success, error_type)


# Example usage and testing
if __name__ == "__main__":
    # Test LangSmith integration
    manager = get_langsmith_manager()

    print(f"LangSmith enabled: {manager.is_enabled()}")
    print(f"LangSmith config: {manager.config}")

    if manager.is_enabled():
        print("✅ LangSmith integration is ready")
    else:
        print("❌ LangSmith integration is disabled or not available")
