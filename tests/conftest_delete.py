"""
Pytest configuration and fixtures for SapRagTool tests
"""

import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def project_root_path():
    """Provide project root path for tests"""
    return project_root


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide test data directory path"""
    return project_root / "tests" / "data"


@pytest.fixture(scope="session")
def sample_pdf_path(test_data_dir):
    """Provide path to sample PDF for testing"""
    return test_data_dir / "sample.pdf"


@pytest.fixture
def mock_openai_api():
    """Mock OpenAI API for testing"""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Mock chat completions
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response

        # Mock embeddings
        mock_embedding = Mock()
        mock_embedding.data = [Mock()]
        mock_embedding.data[0].embedding = [0.1] * 1536  # Typical embedding size
        mock_client.embeddings.create.return_value = mock_embedding

        yield mock_client


@pytest.fixture
def mock_langsmith():
    """Mock LangSmith for testing"""
    with patch("langsmith.Client") as mock_client:
        mock_client.return_value = Mock()
        yield mock_client


@pytest.fixture
def mock_chromadb():
    """Mock ChromaDB for testing"""
    with patch("chromadb.Client") as mock_client:
        mock_collection = Mock()
        mock_client.return_value.get_collection.return_value = mock_collection
        mock_collection.query.return_value = {
            "documents": [["Test document"]],
            "metadatas": [[{"source": "test.pdf"}]],
            "distances": [[0.1]],
        }
        yield mock_client


@pytest.fixture
def mock_requests():
    """Mock requests for HTTP testing"""
    with patch("requests.Session") as mock_session:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_session.return_value.get.return_value = mock_response
        mock_session.return_value.post.return_value = mock_response
        yield mock_session


@pytest.fixture
def test_environment():
    """Set up test environment variables"""
    test_env = {
        "OPENAI_API_KEY": "test-key-123",
        "LANGSMITH_API_KEY": "test-langsmith-key",
        "LANGSMITH_PROJECT": "test-project",
        "LANGCHAIN_TRACING_V2": "true",
        "FLASK_ENV": "testing",
    }

    with patch.dict(os.environ, test_env):
        yield test_env


@pytest.fixture
def mock_flask_app():
    """Mock Flask app for testing"""
    from flask import Flask

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    return app


# Pytest markers for test categorization
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "compliance: Compliance tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line(
        "markers", "requires_server: Tests that require a running server"
    )


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file names"""
    for item in items:
        # Add markers based on test file names
        if "test_security" in item.nodeid:
            item.add_marker(pytest.mark.security)
        elif "test_guardrails" in item.nodeid:
            item.add_marker(pytest.mark.compliance)
        elif "test_rag_langsmith" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)

        # Mark slow tests
        if "slow" in item.nodeid or "integration" in item.nodeid:
            item.add_marker(pytest.mark.slow)

        # Mark tests that require server
        if "security" in item.nodeid and "test_health_endpoint" in item.nodeid:
            item.add_marker(pytest.mark.requires_server)
