"""
Agents Utils Module

This module provides utility functions and tools for the SapRagTool agents.
It includes file management, configuration, and other helper functions.
"""

# Import files_manager functions that don't require external dependencies
from .files_manager import get_config, is_running_on_railway
from .files_manager import main as files_manager_main

# FilesRagTool is imported directly from agents.rag.files_ragtool when needed
# to avoid circular import issues
FilesRagTool = None

from .config import (
    ConfigurationManager,
    ConfigurationSet,
    create_custom_configuration_set,
    get_configuration_set,
    get_data_path,
    get_llm_config,
    get_rag_config,
    set_configuration_set,
)

# Version information
__version__ = "1.0.0"
__author__ = "SapRagTool Team"

# Module exports
__all__ = [
    # Files manager exports
    "is_running_on_railway",
    "get_config",
    "FilesRagTool",
    "files_manager_main",
    # Config exports
    "get_rag_config",
    "get_llm_config",
    "get_data_path",
    "get_configuration_set",
    "set_configuration_set",
    "create_custom_configuration_set",
    "ConfigurationSet",
    "ConfigurationManager",
]

# Module metadata
__description__ = "Utility functions and tools for SapRagTool agents"
__license__ = "MIT"
