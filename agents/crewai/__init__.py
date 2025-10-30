"""
CrewAI Agent Package

This package contains CrewAI-based agents and related functionality for the insurance coverage assistant.

Modules:
    crew_entities: Custom agent classes and crew management
    crew_agent_server: Basic agent server implementation
    crew_agent_server_with_guard_rails: Agent server with EU AI Act compliance guardrails
"""

# Import main classes for easy access
# Handle missing dependencies gracefully
try:
    from .crew_entities import (
        CustomLlm,
        CustomRagTool,
        InsuranceCrew,
        is_running_locally,
    )

    __all__ = ["CustomLlm", "CustomRagTool", "InsuranceCrew", "is_running_locally"]
except ImportError:
    # If dependencies are missing, define empty __all__
    __all__ = []
