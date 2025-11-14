# SapRagTool Makefile
# Provides easy commands for testing, development, and deployment

.PHONY: help test test-unit test-integration test-security test-compliance test-all test-quick clean install dev-install lint format

# Default target
help:
	@echo "SapRagTool Development Commands"
	@echo "==============================="
	@echo ""
	@echo "Testing:"
	@echo "  test              Run all tests with pytest"
	@echo "  test-unit         Run unit tests only"
	@echo "  test-integration  Run integration tests only"
	@echo "  test-security     Run security tests only"
	@echo "  test-compliance   Run compliance tests only"
	@echo "  test-all          Run comprehensive test suite"
	@echo "  test-quick        Run quick tests (no slow tests)"
	@echo ""
	@echo "Development:"
	@echo "  install           Install production dependencies"
	@echo "  dev-install       Install development dependencies"
	@echo "  lint              Run code linting"
	@echo "  format            Format code with black and isort"
	@echo "  clean             Clean up temporary files"
	@echo ""
	@echo "Security:"
	@echo "  security-test     Run security tests against running server"
	@echo "  security-scan     Run security vulnerability scan"
	@echo ""

# Testing commands
test:
	pytest tests/ -v --tb=short

test-unit:
	pytest tests/ -v -m unit --tb=short

test-integration:
	pytest tests/ -v -m integration --tb=short

test-security:
	pytest tests/ -v -m security --tb=short

test-compliance:
	pytest tests/ -v -m compliance --tb=short

test-all:
	python tests/test_runner.py --verbose

test-quick:
	pytest tests/ -v -m "not slow" --tb=short

# Development commands
install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements-dev.txt

lint:
	flake8 agents/ utils/ tests/ --max-line-length=100 --ignore=E203,W503
	pylint agents/ utils/ tests/ --disable=C0114,C0116

format:
	black agents/ utils/ tests/ --line-length=100
	isort agents/ utils/ tests/ --profile=black

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf reports/

# Security commands
security-test:
	@echo "Running security tests..."
	@echo "Note: This requires a running server"
	python tests/test_security.py

security-scan:
	@echo "Running security vulnerability scan..."
	safety check
	bandit -r agents/ utils/ tests/ -f json -o security_report.json

# Development server
dev-server:
	@echo "Starting development server..."
	python agents/crew_agent_server.py

# PDF processing
process-pdfs:
	@echo "Processing PDF files..."
	python utils/files_manager.py

# Railway deployment
railway-deploy:
	@echo "Deploying to Railway..."
	railway up

# Docker commands (if using Docker)
docker-build:
	docker build -t sapragtool .

docker-run:
	docker run -p 8001:8001 sapragtool

# Test coverage
coverage:
	pytest tests/ --cov=agents --cov=utils --cov-report=html --cov-report=term

# Full test suite with coverage
test-full:
	pytest tests/ --cov=agents --cov=utils --cov-report=html --cov-report=term -v

# Quick development setup
setup-dev: dev-install
	@echo "Setting up development environment..."
	cp env.example .env
	@echo "Please edit .env with your API keys"
	@echo "Then run: make process-pdfs"

# Production setup
setup-prod: install
	@echo "Setting up production environment..."
	cp env.example .env
	@echo "Please edit .env with your production API keys"
	@echo "Then run: make process-pdfs"

# Help for specific commands
test-help:
	@echo "Test Commands Help"
	@echo "=================="
	@echo ""
	@echo "Available test categories:"
	@echo "  unit         - Fast unit tests"
	@echo "  integration  - Integration tests (may be slower)"
	@echo "  security     - Security tests"
	@echo "  compliance   - Compliance tests"
	@echo "  slow         - Slow running tests"
	@echo ""
	@echo "Examples:"
	@echo "  make test-unit        # Run only unit tests"
	@echo "  make test-security    # Run only security tests"
	@echo "  make test-quick       # Run all tests except slow ones"
	@echo "  make test-all         # Run comprehensive test suite"
