# EU AI Act Compliance Guardrails

This package provides comprehensive EU AI Act compliance validation for CrewAI agents and other AI systems.

## 📁 Package Structure

```
guardrails/
├── __init__.py                    # Package initialization and exports
├── compliance_guardrails.py       # Core compliance validation functions
├── test_guardrails.py            # Test suite for guardrail functionality
└── README.md                     # This documentation
```

## 🛡️ Core Functions

### `check_prohibited_practices(user_message: str) -> Tuple[bool, str]`

Validates messages against EU AI Act prohibited practices:

- Biometric identification/categorization
- Social scoring systems
- Manipulation and deceptive practices
- Workplace emotional monitoring

### `check_risk_classification(user_message: str) -> Tuple[bool, str]`

Assesses and validates risk levels:

- High-risk domain detection (healthcare, employment, education, etc.)
- Personal data processing patterns
- Individual decision-making scenarios

### `check_ai_risk_management(user_message: str) -> Tuple[bool, str]`

Ensures AI risk management compliance:

- Human oversight requirements
- Transparency and explainability
- Bias risk assessment
- Vulnerable population protection

### `validate_all_compliance_rules(user_message: str) -> Tuple[bool, str]`

Comprehensive validation using all three guardrail functions.

## 📖 Usage Examples

### Basic Import and Usage

```python
from guardrails import validate_all_compliance_rules, ComplianceViolationError

# Validate a user message
is_compliant, result = validate_all_compliance_rules("What insurance do I need?")

if is_compliant:
    print("✅ Message is compliant")
    # Process the message
else:
    print(f"❌ Compliance violation: {result}")
    # Handle the violation
```

### Individual Function Usage

```python
from guardrails.compliance_guardrails import (
    check_prohibited_practices,
    check_risk_classification,
    check_ai_risk_management
)

# Test against prohibited practices only
is_compliant, result = check_prohibited_practices("Help with facial recognition")
# Returns: (False, "EU AI Act Violation: Biometric identification detected...")

# Test risk classification
is_compliant, result = check_risk_classification("Help me hire someone")
# Returns: (False, "HIGH-RISK AI REQUEST: Employment decision detected...")
```

### CrewAI Integration

The guardrails are implemented as **pre-processing compliance checks** before CrewAI agent execution:

```python
from flask import Flask, request, jsonify
from guardrails import validate_all_compliance_rules, ComplianceViolationError

@app.route("/chat", methods=["POST"])
async def chat():
    """Chat endpoint with EU AI Act compliance validation."""
    try:
        user_message = request.json.get("message", "")

        # Apply EU AI Act compliance guardrails BEFORE processing
        print("🛡️ Running EU AI Act compliance checks...")
        is_compliant, compliance_result = validate_all_compliance_rules(user_message)

        if not is_compliant:
            print(f"❌ Compliance violation detected: {compliance_result}")
            raise ComplianceViolationError(compliance_result)

        print("✅ Message passed all compliance checks")

        # Now safe to process with CrewAI
        response = await call_crewai_agent(user_message)
        return jsonify({"response": response})

    except ComplianceViolationError as e:
        return jsonify({"error": str(e), "error_type": "compliance_violation"}), 400
```

### Direct Function Integration

```python
from guardrails import validate_all_compliance_rules, ComplianceViolationError

async def call_crewai_agent(user_message: str) -> str:
    """Call CrewAI agent with compliance validation."""

    # Validate compliance before processing
    is_compliant, result = validate_all_compliance_rules(user_message)
    if not is_compliant:
        raise ComplianceViolationError(result)

    # Create and execute CrewAI task
    crew_instance = insurance_crew.create_crew_with_message(user_message)
    task_output = await crew_instance.kickoff_async()

    return str(task_output)
```

## 🧪 Testing

Run the test suite to see guardrails in action:

```bash
# From agents directory
python guardrails/test_guardrails.py

# Or from guardrails directory
cd guardrails
python test_guardrails.py
```

The test suite includes examples of:

- ✅ Compliant requests (insurance information, general assistance)
- ❌ Prohibited practices (facial recognition, social scoring)
- ⚠️ High-risk scenarios (employment decisions, medical diagnosis)

## 🚫 Common Violations Detected

### Prohibited Practices

- "implement facial recognition"
- "create social scoring system"
- "categorize by race/religion"
- "monitor employee emotions"
- "deepfake generation"

### High-Risk Use Cases

- "make hiring decisions"
- "approve loan applications"
- "medical diagnosis"
- "student grading"
- "law enforcement support"

### Risk Management Issues

- "make autonomous decisions"
- "hide AI involvement"
- "bias toward certain groups"
- "target vulnerable people"

## 🔧 Configuration

The guardrails use pattern-based detection with regular expressions. Patterns can be customized by modifying the respective arrays in `compliance_guardrails.py`:

- `biometric_violations`
- `social_scoring_violations`
- `manipulation_violations`
- `workplace_violations`
- `high_risk_domains`
- `personal_data_patterns`

## 📊 Return Format

All guardrail functions return a tuple `(bool, str)`:

- `(True, original_message)` - Message is compliant
- `(False, error_description)` - Compliance violation with detailed explanation

## 🔗 Integration with Other Systems

This package is designed for easy integration with:

- CrewAI agents and tasks
- LangChain applications
- Custom AI agents
- FastAPI endpoints
- Flask applications

### Generic Agent/Task Wrapper Patterns

#### Function Decorator Pattern

```python
from functools import wraps
from guardrails import validate_all_compliance_rules, ComplianceViolationError

def compliance_required(func):
    """Decorator to add compliance validation to any agent function."""
    @wraps(func)
    def wrapper(user_message: str, *args, **kwargs):
        is_compliant, result = validate_all_compliance_rules(user_message)
        if not is_compliant:
            raise ComplianceViolationError(result)
        return func(user_message, *args, **kwargs)
    return wrapper

# Usage
@compliance_required
def my_ai_agent(user_message: str) -> str:
    """Any AI agent function."""
    return process_with_ai(user_message)
```

#### Class-Based Agent Wrapper

```python
class ComplianceWrapper:
    """Wrapper to add compliance validation to any agent or task."""

    def __init__(self, agent_function):
        self.agent_function = agent_function

    def __call__(self, user_message: str, *args, **kwargs):
        # Validate compliance first
        is_compliant, result = validate_all_compliance_rules(user_message)
        if not is_compliant:
            raise ComplianceViolationError(result)

        # Execute original function
        return self.agent_function(user_message, *args, **kwargs)

# Usage
compliant_agent = ComplianceWrapper(original_agent_function)
result = compliant_agent("What insurance do I need?")
```

## 📋 Compliance Framework

Based on EU AI Act requirements:

- **Article 5**: Prohibited AI practices
- **Article 6**: High-risk AI system classification
- **Article 9**: Vulnerable population protection
- **Article 13**: Transparency and human oversight requirements

## 🚨 Error Handling

```python
from guardrails import ComplianceViolationError

try:
    # Process user input
    result = process_with_ai(user_message)
except ComplianceViolationError as e:
    # Handle compliance violation
    return {"error": str(e), "error_type": "compliance_violation"}
```
