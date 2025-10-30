"""
EU AI Act Compliance Guardrails Package

This package provides compliance validation functions for CrewAI agents
to ensure adherence to EU AI Act requirements.

Main Components:
- compliance_guardrails: Core compliance validation functions
- test_guardrails: Test suite for guardrail functionality
"""

from .compliance_guardrails import (
    ComplianceViolationError,
    check_ai_risk_management,
    check_prohibited_practices,
    check_risk_classification,
    validate_all_compliance_rules,
)

__version__ = "1.0.0"
__author__ = "EU AI Act Compliance Team"

__all__ = [
    "check_prohibited_practices",
    "check_risk_classification",
    "check_ai_risk_management",
    "validate_all_compliance_rules",
    "ComplianceViolationError",
]
