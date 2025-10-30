"""
EU AI Act Compliance Guardrails for CrewAI Agents

This module implements guardrail functions that validate user messages against
EU AI Act compliance requirements before they are processed by CrewAI agents.

Based on compliance rules in .cursor/rules/compliance/:
- prohibited-practices-guidelines.mdc
- risk-classification-guidelines.mdc
- ai-risk-management.mdc
"""

import logging
import re
from typing import Tuple

# Set up logging for guardrail violations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplianceViolationError(Exception):
    """Exception raised when a compliance violation is detected."""

    pass


def check_prohibited_practices(user_message: str) -> Tuple[bool, str]:
    """
    Guardrail function to check user messages against EU AI Act prohibited practices.

    Based on: .cursor/rules/compliance/prohibited-practices-guidelines.mdc

    Args:
        user_message: The user input message to validate

    Returns:
        Tuple[bool, str]: (is_compliant, message_or_error)
        - If compliant: (True, original_message)
        - If violation: (False, error_description)
    """

    # Convert to lowercase for case-insensitive matching
    message_lower = user_message.lower()

    # Prohibited biometric and identity patterns
    biometric_violations = [
        r"\b(facial recognition|face\s*recognition|biometric\s*identification)\b",
        r"\b(real.?time\s*identification|live\s*biometric)\b",
        r"\b(categorize\s*by\s*(race|ethnicity|religion|gender|sexual orientation))\b",
        r"\b(biometric\s*categorization|racial\s*profiling)\b",
    ]

    # Prohibited social scoring patterns
    social_scoring_violations = [
        r"\b(social\s*scor(e|ing)|behavior\s*scor(e|ing))\b",
        r"\b(citizen\s*scor(e|ing)|trustworthiness\s*rating)\b",
        r"\b(reputation\s*system|social\s*credit)\b",
        r"\b(rank\s*people|score\s*individuals)\b",
    ]

    # Prohibited manipulation patterns
    manipulation_violations = [
        r"\b(subliminal|subconscious\s*manipulation)\b",
        r"\b(dark\s*pattern|deceptive\s*design)\b",
        r"\b(exploit\s*(vulnerabil|children|elderly|disabled))\b",
        r"\b(deepfake|voice\s*manipulation|synthetic\s*media)\b",
    ]

    # Prohibited workplace monitoring patterns
    workplace_violations = [
        r"\b(monitor\s*emotion|emotion\s*tracking|emotional\s*profiling)\b",
        r"\b(webcam\s*monitoring|voice\s*analysis\s*emotion)\b",
        r"\b(employee\s*surveillance|workplace\s*emotion)\b",
    ]

    # Check all violation patterns
    all_violations = [
        (biometric_violations, "Biometric identification/categorization"),
        (social_scoring_violations, "Social scoring system"),
        (manipulation_violations, "Manipulation or deceptive practices"),
        (workplace_violations, "Workplace emotional monitoring"),
    ]

    for violation_patterns, violation_type in all_violations:
        for pattern in violation_patterns:
            if re.search(pattern, message_lower):
                error_msg = (
                    f"🚫 EU AI Act Violation: {violation_type} detected. "
                    f"This practice is prohibited under EU AI Act Article 5. "
                    f"Please rephrase your request without references to prohibited AI practices."
                )

                # Log the violation
                logger.warning(
                    f"Prohibited practice detected: {violation_type} in message: {user_message[:100]}..."
                )

                return (False, error_msg)

    # If no violations found, message is compliant
    logger.info("Message passed prohibited practices check")
    return (True, user_message)


def check_risk_classification(user_message: str) -> Tuple[bool, str]:
    """
    Guardrail function to assess and validate risk level of user requests.

    Based on: .cursor/rules/compliance/risk-classification-guidelines.mdc

    Args:
        user_message: The user input message to validate

    Returns:
        Tuple[bool, str]: (is_compliant, message_or_error)
        - If compliant: (True, original_message)
        - If high-risk without safeguards: (False, error_description)
    """

    message_lower = user_message.lower()

    # High-risk domain patterns
    high_risk_domains = [
        r"\b(medical\s*decision|healthcare\s*decision|diagnos[ei]s)\b",
        r"\b(hiring|employment\s*decision|job\s*interview|resume\s*screening)\b",
        r"\b(credit\s*scoring|loan\s*approval|financial\s*assessment)\b",
        r"\b(student\s*grading|admission\s*decision|educational\s*assessment)\b",
        r"\b(law\s*enforcement|criminal\s*justice|legal\s*decision)\b",
        r"\b(border\s*control|immigration|visa\s*process)\b",
    ]

    # Personal data processing patterns that increase risk
    personal_data_patterns = [
        r"\b(personal\s*data|sensitive\s*data|private\s*information)\b",
        r"\b(health\s*data|medical\s*record|genetic\s*data)\b",
        r"\b(biometric\s*data|fingerprint|voice\s*print)\b",
        r"\b(behavioral\s*analysis|personality\s*profiling)\b",
    ]

    # Decision-making patterns
    decision_making_patterns = [
        r"\b(decide|determine|evaluate|assess|judge)\s+(person|individual|candidate|applicant)\b",
        r"\b(make\s*decision\s*about|recommendation\s*for)\b",
        r"\b(approve|reject|accept|deny)\s+(application|request|person)\b",
    ]

    risk_level = "LOW"
    detected_patterns = []

    # Check for high-risk domains
    for pattern in high_risk_domains:
        if re.search(pattern, message_lower):
            risk_level = "HIGH"
            detected_patterns.append("High-risk domain usage")
            break

    # Check for personal data processing
    for pattern in personal_data_patterns:
        if re.search(pattern, message_lower):
            if risk_level == "LOW":
                risk_level = "MEDIUM"
            detected_patterns.append("Personal data processing")
            break

    # Check for decision-making about individuals
    for pattern in decision_making_patterns:
        if re.search(pattern, message_lower):
            if risk_level != "HIGH":
                risk_level = "MEDIUM"
            detected_patterns.append("Individual decision-making")
            break

    # Handle high-risk scenarios
    if risk_level == "HIGH":
        error_msg = (
            f"⚠️ HIGH-RISK AI REQUEST: This request involves high-risk AI use cases "
            f"requiring enhanced safeguards under EU AI Act. "
            f"Detected: {', '.join(detected_patterns)}. "
            f"Additional compliance measures, human oversight, and documentation required."
        )

        logger.warning(
            f"High-risk request detected: {detected_patterns} in message: {user_message[:100]}..."
        )
        return (False, error_msg)

    # Log risk assessment
    if risk_level == "MEDIUM":
        logger.info(f"Medium-risk request detected: {detected_patterns}")
    else:
        logger.info("Low-risk request - proceeding")

    return (True, user_message)


def check_ai_risk_management(user_message: str) -> Tuple[bool, str]:
    """
    Guardrail function to validate AI risk management compliance requirements.

    Based on: .cursor/rules/compliance/ai-risk-management.mdc

    Args:
        user_message: The user input message to validate

    Returns:
        Tuple[bool, str]: (is_compliant, message_or_error)
        - If compliant: (True, original_message)
        - If risk management violation: (False, error_description)
    """

    message_lower = user_message.lower()

    # Patterns requiring human oversight
    human_oversight_required = [
        r"\b(critical\s*decision|life.?affecting|safety.?critical)\b",
        r"\b(autonomous\s*decision|unsupervised\s*operation)\b",
        r"\b(permanent\s*impact|irreversible\s*effect)\b",
    ]

    # Patterns indicating insufficient transparency
    transparency_violations = [
        r"\b(hide|conceal|secret)\s+(ai|algorithm|decision)\b",
        r"\b(black\s*box|unexplained|no\s*explanation)\b",
        r"\b(automatic|without\s*explanation|silent\s*decision)\b",
    ]

    # Patterns indicating bias risks
    bias_risk_patterns = [
        r"\b(discriminat|bias|unfair|prejudice)\s+(against|toward)\b",
        r"\b(prefer|favor)\s+(certain\s*group|specific\s*demographic)\b",
        r"\b(exclude|reject)\s+(based\s*on|due\s*to)\b",
    ]

    # Patterns indicating vulnerable population targeting
    vulnerable_population_patterns = [
        r"\b(target|exploit)\s+(children|elderly|disabled|vulnerable)\b",
        r"\b(take\s*advantage|manipulate)\s+(minors|seniors)\b",
    ]

    # Check for human oversight requirements
    for pattern in human_oversight_required:
        if re.search(pattern, message_lower):
            error_msg = (
                "🤝 HUMAN OVERSIGHT REQUIRED: This request involves decisions requiring "
                "human oversight under EU AI Act Article 13. "
                "Critical or safety-affecting AI decisions must maintain meaningful human control. "
                "Please ensure human review is included in the process."
            )

            logger.warning(
                f"Human oversight required for message: {user_message[:100]}..."
            )
            return (False, error_msg)

    # Check for transparency violations
    for pattern in transparency_violations:
        if re.search(pattern, message_lower):
            error_msg = (
                "🔍 TRANSPARENCY VIOLATION: EU AI Act Article 13 requires transparency "
                "and explainability. AI systems must provide clear explanations for decisions. "
                "Please modify request to include transparency requirements."
            )

            logger.warning(
                f"Transparency violation detected in message: {user_message[:100]}..."
            )
            return (False, error_msg)

    # Check for bias risks
    for pattern in bias_risk_patterns:
        if re.search(pattern, message_lower):
            error_msg = (
                "⚖️ BIAS RISK DETECTED: This request may lead to discriminatory outcomes "
                "violating EU AI Act fairness requirements. "
                "Please ensure bias mitigation measures and fairness testing are implemented."
            )

            logger.warning(f"Bias risk detected in message: {user_message[:100]}...")
            return (False, error_msg)

    # Check for vulnerable population targeting
    for pattern in vulnerable_population_patterns:
        if re.search(pattern, message_lower):
            error_msg = (
                "🛡️ VULNERABLE POPULATION PROTECTION: EU AI Act Article 9 provides "
                "enhanced protection for vulnerable groups. "
                "Requests targeting children, elderly, or disabled individuals require "
                "additional safeguards and special protections."
            )

            logger.warning(
                f"Vulnerable population targeting detected in message: {user_message[:100]}..."
            )
            return (False, error_msg)

    # Message passed all risk management checks
    logger.info("Message passed AI risk management compliance check")
    return (True, user_message)


def validate_all_compliance_rules(user_message: str) -> Tuple[bool, str]:
    """
    Comprehensive compliance validation using all three guardrail functions.

    Args:
        user_message: The user input message to validate

    Returns:
        Tuple[bool, str]: (is_compliant, message_or_error)
    """

    # Log compliance check start
    logger.info(
        f"Starting comprehensive compliance check for message: {user_message[:50]}..."
    )

    # Run all three compliance checks
    guardrail_functions = [
        ("Prohibited Practices", check_prohibited_practices),
        ("Risk Classification", check_risk_classification),
        ("AI Risk Management", check_ai_risk_management),
    ]

    for check_name, check_function in guardrail_functions:
        is_compliant, result = check_function(user_message)

        if not is_compliant:
            logger.error(f"Compliance violation in {check_name}: {result}")
            return (False, f"[{check_name}] {result}")

    # All checks passed
    logger.info("✅ Message passed all EU AI Act compliance checks")
    return (True, user_message)


# Export the main validation function for easy import
__all__ = [
    "check_prohibited_practices",
    "check_risk_classification",
    "check_ai_risk_management",
    "validate_all_compliance_rules",
    "ComplianceViolationError",
]
