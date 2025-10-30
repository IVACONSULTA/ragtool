"""
RAG (Retrieval Augmented Generation) Package

This package contains RAG-related functionality for document processing and knowledge base management.

Modules:
    ragtool: Generic RAG tool base class
    files_ragtool: Multi-format file processing and ChromaDB management
    rag_wrapper: CrewAI-compatible wrapper for RAG tools
"""

# Import main classes for easy access
# Handle missing dependencies gracefully
try:
    from .ragtool import BaseRagTool
    from .files_ragtool import FilesRagTool
    from .rag_wrapper import RagToolWrapper, create_rag_wrapper

    __all__ = ["BaseRagTool", "FilesRagTool", "RagToolWrapper", "create_rag_wrapper"]
except ImportError:
    # If dependencies are missing, define empty __all__
    __all__ = []
