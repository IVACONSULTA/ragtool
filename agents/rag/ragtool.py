"""
Generic RagTool Class

This module provides a generic RagTool class that wraps CrewAI's RagTool
and provides common functionality for RAG operations without being specific
to any particular document type.

The generic RagTool handles:
- Basic RAG tool initialization
- Storage management
- Configuration handling
- Common RAG operations

Specific document types (like PDF) should extend this class.
"""

import os
from typing import Dict, Optional

from crewai_tools import RagTool


class BaseRagTool:
    """
    Generic RagTool class that wraps CrewAI's RagTool.
    
    This class provides common RAG functionality that can be extended
    by specific document type processors (e.g., PDFRagTool).
    """

    def __init__(self, rag_config: Dict, storage_path: str = "./db"):
        """
        Initialize the generic RagTool.

        Args:
            rag_config: Configuration for LLM and embedding models
            storage_path: Path where the vector database (ChromaDB) will be stored
        """
        self.rag_config = rag_config
        self.storage_path = storage_path
        self.rag_tool = None

    def _ensure_storage_directory(self):
        """Create storage directory if it doesn't exist."""
        os.makedirs(self.storage_path, exist_ok=True)

    def _get_core_config(self) -> Dict:
        """Get core LLM/embedding config without chunk parameters."""
        core_config = self.rag_config.copy()
        # Remove chunk parameters from core config as they're passed separately
        core_config.pop("chunk_size", None)
        core_config.pop("chunk_overlap", None)
        
        # Explicitly configure ChromaDB as the vector database
        # This prevents CrewAI from trying to use other vector databases like Qdrant
        core_config["vectordb"] = {
            "provider": "chromadb",
            "config": {
                "collection_name": "rag_documents"
            }
        }
        
        return core_config

    def _initialize_rag_tool(self) -> RagTool:
        """Initialize CrewAI RagTool with persistent storage."""
        # Ensure EMBEDDINGS_GOOGLE_API_KEY is set for Google embeddings
        self._ensure_embedding_api_key()
        
        # Get chunk parameters with defaults if not present
        chunk_size = self.rag_config.get("chunk_size", 1200)
        chunk_overlap = self.rag_config.get("chunk_overlap", 200)
        
        return RagTool(
            config=self._get_core_config(),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            storage_path=self.storage_path,
        )
    
    def _ensure_embedding_api_key(self):
        """Ensure required API keys are set for embedding providers."""
        embedding_config = self.rag_config.get("embedding_model", {})
        provider = embedding_config.get("provider", "")
        
        # For Google embeddings, CrewAI requires EMBEDDINGS_GOOGLE_API_KEY
        if provider in ["google-generativeai", "google", "gemini"]:
            if not os.getenv("EMBEDDINGS_GOOGLE_API_KEY"):
                # Try to use GOOGLE_API_KEY or GEMINI_API_KEY as fallback
                google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
                if google_key:
                    os.environ["EMBEDDINGS_GOOGLE_API_KEY"] = google_key
                    print("✅ Set EMBEDDINGS_GOOGLE_API_KEY from GOOGLE_API_KEY/GEMINI_API_KEY")
                else:
                    print("⚠️  Warning: EMBEDDINGS_GOOGLE_API_KEY not set for Google embeddings")

    def initialize_rag_tool(self) -> bool:
        """
        Initialize the RAG tool.

        Returns:
            bool: True if initialization was successful
        """
        try:
            self._ensure_storage_directory()
            self.rag_tool = self._initialize_rag_tool()
            return True
        except Exception as e:
            print(f"❌ Error initializing RAG tool: {e}")
            return False

    def check_if_database_path_exists(self) -> bool:
        """Check if vector database already exists."""
        path_exists = (
            os.path.exists(self.storage_path) and len(os.listdir(self.storage_path)) > 0
        )

        if not path_exists:
            print("\n⚠️  No existing vector database found")
            return False
        else:
            print("\n✅ Vector database found")
            return True

    def get_rag_tool(self) -> Optional[RagTool]:
        """
        Load existing vector database.

        Returns:
            RagTool instance if successful, None otherwise
        """
        print("\n🔄 Loading existing RagTool...")
        try:
            if not self.check_if_database_path_exists():
                return None

            print("🔄 Loading existing vector database...")
            self.rag_tool = self._initialize_rag_tool()

            print("✅ Vector database loaded successfully")
            return self.rag_tool

        except Exception as e:
            print(f"❌ Error loading RagTool: {e}")
            return None

    def add_document(self, document_path: str, data_type: str = "file") -> bool:
        """
        Add a document to the RAG tool.

        Args:
            document_path: Path to the document to add
            data_type: Type of data being added (e.g., "pdf_file", "text_file", "web_page")

        Returns:
            bool: True if successful
        """
        if not self.rag_tool:
            if not self.initialize_rag_tool():
                return False

        try:
            # Handle URLs (web_page) - use RagTool's built-in URL handling
            if data_type == "web_page" and document_path.startswith(('http://', 'https://')):
                # CrewAI RagTool can handle URLs directly
                # Use the add method which accepts URLs
                try:
                    self.rag_tool.add(document_path)
                    return True
                except Exception as url_error:
                    # If direct URL fails, try using a web loader
                    print(f"⚠️  Direct URL add failed, trying web loader: {url_error}")
                    try:
                        from langchain_community.document_loaders import WebBaseLoader
                        loader = WebBaseLoader(document_path)
                        documents = loader.load()
                        for doc in documents:
                            self.rag_tool.add(doc.page_content)
                        return True
                    except Exception as loader_error:
                        print(f"❌ Web loader also failed: {loader_error}")
                        return False
            
            # Create document loader based on data type
            if data_type == "text_file":
                from langchain_community.document_loaders import TextLoader
                loader = TextLoader(document_path)
            elif data_type == "pdf_file":
                from langchain_community.document_loaders import PyPDFLoader
                loader = PyPDFLoader(document_path)
            elif data_type == "csv_file":
                from langchain_community.document_loaders import CSVLoader
                loader = CSVLoader(document_path)
            elif data_type == "json_file":
                from langchain_community.document_loaders import JSONLoader
                loader = JSONLoader(document_path)
            elif data_type == "html_file":
                from langchain_community.document_loaders import BSHTMLLoader
                loader = BSHTMLLoader(document_path)
            else:
                # Default to text loader for unknown types
                from langchain_community.document_loaders import TextLoader
                loader = TextLoader(document_path)
            
            # Load documents and add to RAG tool
            documents = loader.load()
            for doc in documents:
                # Convert document to string content
                self.rag_tool.add(doc.page_content)
            return True
        except Exception as e:
            print(f"❌ Error adding document {document_path}: {e}")
            return False

    def search(self, query: str) -> str:
        """
        Search the knowledge base.

        Args:
            query: Search query

        Returns:
            Search results as string
        """
        if not self.rag_tool:
            return "RAG tool not initialized"

        try:
            return self.rag_tool._run(query)
        except Exception as e:
            print(f"❌ Error searching: {e}")
            return f"Error searching: {e}"

    def reset_database(self) -> bool:
        """
        Reset the vector database by removing all data.

        Returns:
            bool: True if successful
        """
        try:
            import shutil

            # Reset vector database storage
            if os.path.exists(self.storage_path):
                shutil.rmtree(self.storage_path)
                print("✅ Vector database reset successfully")
            else:
                print("ℹ️  No vector database to reset")

            return True
        except Exception as e:
            print(f"❌ Error resetting database: {e}")
            return False

    def is_available(self) -> bool:
        """Check if RAG tool is available and functional."""
        return self.rag_tool is not None

    def get_config(self) -> Dict:
        """Get the current RAG configuration."""
        return self.rag_config

    def get_storage_path(self) -> str:
        """Get the storage path."""
        return self.storage_path

    def get_status_info(self) -> str:
        """Get formatted status information."""
        status = "ENABLED" if self.is_available() else "DISABLED"
        return f"RAG Tool: {status}"
