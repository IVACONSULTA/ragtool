#!/bin/bash
# Simple test runner script for SapRagTool

echo "🧪 SapRagTool Test Runner"
echo "========================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "   Consider activating your virtual environment first"
fi

# Parse command line arguments
CATEGORY=""
VERBOSE=""
STOP_ON_FAILURE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            CATEGORY="unit_tests"
            shift
            ;;
        --integration)
            CATEGORY="integration_tests"
            shift
            ;;
        --security)
            CATEGORY="security_tests"
            shift
            ;;
        --compliance)
            CATEGORY="compliance_tests"
            shift
            ;;
        --verbose|-v)
            VERBOSE="--verbose"
            shift
            ;;
        --stop-on-failure)
            STOP_ON_FAILURE="--stop-on-failure"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --unit              Run unit tests only"
            echo "  --integration       Run integration tests only"
            echo "  --security          Run security tests only"
            echo "  --compliance        Run compliance tests only"
            echo "  --verbose, -v       Verbose output"
            echo "  --stop-on-failure   Stop on first failure"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                  # Run all tests"
            echo "  $0 --unit           # Run unit tests only"
            echo "  $0 --security -v    # Run security tests with verbose output"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run tests
if [ -n "$CATEGORY" ]; then
    echo "Running $CATEGORY..."
    python tests/test_runner.py --category "$CATEGORY" $VERBOSE $STOP_ON_FAILURE
else
    echo "Running all tests..."
    python tests/test_runner.py $VERBOSE $STOP_ON_FAILURE
fi

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 All tests completed successfully!"
else
    echo ""
    echo "❌ Some tests failed. Please check the output above."
    exit 1
fi
