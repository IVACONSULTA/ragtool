"""
Basic tests for RagTool components that can run in CI environment.

These tests check basic functionality without requiring real API keys
or external services.
"""

import os
from unittest.mock import MagicMock, patch

import pytest


def test_environment_setup():
    """Test that basic environment is set up correctly."""
    assert os.getenv("OPENAI_API_KEY") is not None, "OPENAI_API_KEY should be set"


def test_config_import():
    """Test that config module can be imported."""
    try:
        from agents.utils.config import get_rag_config

        assert callable(get_rag_config)
    except ImportError as e:
        pytest.fail(f"Could not import config module: {e}")


def test_files_ragtool_import():
    """Test that PDF processor can be imported."""
    try:
        from agents.rag.files_ragtool import FilesRagTool

        assert FilesRagTool is not None
    except ImportError as e:
        pytest.fail(f"Could not import FilesRagTool: {e}")


def test_rag_wrapper_import():
    """Test that RAG wrapper can be imported."""
    try:
        from agents.rag.rag_wrapper import RagToolWrapper, create_rag_wrapper

        assert RagToolWrapper is not None
        assert callable(create_rag_wrapper)
    except ImportError as e:
        pytest.fail(f"Could not import RAG wrapper: {e}")


@patch("agents.config.os.getenv")
def test_config_with_env_vars(mock_getenv):
    """Test config creation with environment variables."""
    # Mock environment variables
    mock_getenv.side_effect = lambda key, default=None: {
        "OPENAI_API_KEY": "test-key",
        "LLM_MODEL": "gpt-4o-mini",
        "EMBEDDING_MODEL": "text-embedding-3-small",
        "LLM_PROVIDER": "openai",
        "EMBEDDING_PROVIDER": "openai",
        "LLM_MAX_TOKENS": "1024",
    }.get(key, default)

    from agents.utils.config import get_rag_config

    config = get_rag_config()

    assert config is not None
    assert "llm" in config
    assert "embedding_model" in config
    assert config["llm"]["provider"] == "openai"
    assert config["llm"]["config"]["model"] == "gpt-4o-mini"


def test_files_ragtool_initialization():
    """Test that FilesRagTool can be initialized with basic config."""
    from agents.rag.files_ragtool import FilesRagTool

    config = {
        "llm": {
            "provider": "openai",
            "config": {"model": "gpt-4o-mini", "max_tokens": 1024},
        },
        "embedding_model": {
            "provider": "openai",
            "config": {"model": "text-embedding-3-small"},
        },
    }

    processor = FilesRagTool(config, "./test_db")
    assert processor is not None
    assert processor.config == config
    assert processor.storage_path == "./test_db"


def test_rag_wrapper_creation():
    """Test that RAG wrapper can be created with mock tool."""
    from agents.rag.rag_wrapper import create_rag_wrapper

    # Create a mock RAG tool
    mock_rag_tool = MagicMock()
    mock_rag_tool._run.return_value = "Test response"

    wrapper = create_rag_wrapper(mock_rag_tool)

    assert wrapper is not None
    assert wrapper.name == "knowledge_base"
    assert "search" in wrapper.description.lower()


def test_files_manager_import():
    """Test that PDF management module can be imported."""
    try:
        from agents.utils.files_manager import (
            init_db_and_process_pdfs,
            is_running_on_railway,
        )

        assert callable(is_running_on_railway)
        assert callable(init_db_and_process_pdfs)
    except ImportError as e:
        pytest.fail(f"Could not import files_manager module: {e}")


def test_railway_environment_detection():
    """Test Railway environment detection in CI (should be local)."""
    from agents.utils.files_manager import is_running_on_railway

    # In CI, should detect local environment (not Railway)
    assert (
        not is_running_on_railway()
    ), "CI should detect local environment, not Railway"


def test_config_module_cli():
    """Test that config module can be used as CLI."""
    import subprocess
    import sys

    # Test config module help
    result = subprocess.run(
        [sys.executable, "-m", "agents.config", "--help"],
        capture_output=True,
        text=True,
    )

    # Should not fail (exit code 0 or 2 for help)
    assert result.returncode in [0, 2], f"Config CLI failed: {result.stderr}"


def test_files_manager_cli():
    """Test that files_manager can be used as CLI."""
    import subprocess
    import sys

    # Test files_manager help
    result = subprocess.run(
        [sys.executable, "utils/files_manager.py", "--help"],
        capture_output=True,
        text=True,
    )

    # Should not fail
    assert result.returncode == 0, f"files_manager CLI failed: {result.stderr}"
    assert "PDF Management" in result.stdout or "manage" in result.stdout.lower()


if __name__ == "__main__":
    pytest.main([__file__])
