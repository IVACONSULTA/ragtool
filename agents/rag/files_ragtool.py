"""
Files RagTool for ChromaDB

This module handles processing various file types and managing the ChromaDB vector database
separately from the main agent server. This allows for:
- One-time processing of various file types
- Efficient loading of existing ChromaDB
- Easy addition of new documents

FilesRagTool extends the generic BaseRagTool class with file processing functionality.

Supported Data Sources:
- 📰 PDF files
- 📊 CSV files
- 📃 JSON files
- 📝 Text files
- 📁 Directories/Folders
- 📝 MDX files
- 📄 DOCX files
- 🧾 XML files
- 📬 Gmail
- 📝 GitHub repositories
- 🐘 PostgreSQL databases
- 🐬 MySQL databases
- 🤖 Slack conversations
- 💬 Discord messages
- 🗨️ Discourse forums
- 📝 Substack newsletters
- 🐝 Beehiiv content
- 💾 Dropbox files
- 🖼️ Images
- ⚙️ Custom data sources
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from crewai_tools import RagTool

from .ragtool import BaseRagTool

# OCR functionality removed - files should be preprocessed manually


class FilesRagTool(BaseRagTool):
    """Handles various file types processing and ChromaDB management."""

    def __init__(self, rag_config: Dict, storage_path: str = "./db"):
        """
        Initialize Files processor.

        Args:
            rag_config: Configuration for LLM and embedding models
            storage_path: Path where ChromaDB will be stored
        """
        super().__init__(rag_config, storage_path)
        # Store processed_files.json in data/processed directory for better organization
        self.metadata_file = "data/processed/processed_files.json"

    def _ensure_metadata_directory(self):
        """Create metadata directory if it doesn't exist."""
        metadata_dir = os.path.dirname(self.metadata_file)
        if metadata_dir:
            os.makedirs(metadata_dir, exist_ok=True)

    def _load_processed_files_metadata(self) -> Dict:
        """Load metadata about processed files."""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Warning: Could not load metadata file: {e}")
        return {"processed_files": {}, "last_updated": None}

    def _save_processed_files_metadata(self, metadata: Dict):
        """Save metadata about processed files."""
        try:
            self._ensure_metadata_directory()
            with open(self.metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"⚠️  Warning: Could not save metadata file: {e}")

    def _get_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of a file to detect changes."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"⚠️  Warning: Could not calculate hash for {file_path}: {e}")
            return ""

    @staticmethod
    def _get_supported_extensions_dict() -> Dict[str, str]:
        """
        Get dictionary of supported file extensions and their corresponding data types.

        Returns:
            Dict[str, str]: Dictionary mapping file extensions to data types
        """
        return {
            # Document files
            ".pdf": "pdf_file",
            ".docx": "docx",
            ".doc": "docx_file",
            ".txt": "text_file",
            ".md": "text_file",
            ".mdx": "mdx_file",
            ".xml": "xml_file",
            ".csv": "csv_file",
            ".json": "json_file",
            ".html": "html_file",
            ".htm": "html_file",
            # Image files
            ".jpg": "image_file",
            ".jpeg": "image_file",
            ".png": "image_file",
            ".gif": "image_file",
            ".bmp": "image_file",
            ".tiff": "image_file",
            ".webp": "image_file",
        }

    def _get_data_type_from_path(self, file_path: str) -> str:
        """
        Determine data type from file path or extension.

        Args:
            file_path: Path to the file or URL

        Returns:
            str: Data type for CrewAI RagTool
        """
        # Handle URLs
        if file_path.startswith(("http://", "https://")):
            if "youtube.com" in file_path or "youtu.be" in file_path:
                return "youtube_video"
            elif "github.com" in file_path:
                return "github"
            else:
                return "web_page"

        # Handle directories
        if os.path.isdir(file_path):
            return "directory"

        # Handle files by extension
        _, ext = os.path.splitext(file_path.lower())
        return FilesRagTool._get_supported_extensions_dict().get(ext, "file")

    def _is_supported_file(self, file_path: str) -> bool:
        """
        Check if file is supported for processing.

        Args:
            file_path: Path to the file

        Returns:
            bool: True if file is supported
        """
        # URLs are always supported
        if file_path.startswith(("http://", "https://")):
            return True

        # Directories are supported
        if os.path.isdir(file_path):
            return True

        # Check file extension
        _, ext = os.path.splitext(file_path.lower())
        return ext in FilesRagTool._get_supported_extensions_dict()

    def initialize_ragtool_and_process_files(
        self, file_paths: List[str], force_reprocess: bool = False
    ) -> bool:
        """
        Process various file types and add them to ChromaDB.

        Args:
            file_paths: List of file paths to process
            force_reprocess: If True, reprocess all files even if they haven't changed

        Returns:
            bool: True if processing was successful
        """
        try:
            self._ensure_metadata_directory()
            metadata = self._load_processed_files_metadata()

            # Initialize RagTool using base class method
            if not self.rag_tool:
                if not self.initialize_rag_tool():
                    return False

            files_to_process = []

            # Check which files need processing
            for file_path in file_paths:
                if not self._is_supported_file(file_path):
                    print(f"⚠️  Warning: Unsupported file type: {file_path}")
                    continue

                # For URLs and directories, don't check file existence
                if file_path.startswith(("http://", "https://")) or os.path.isdir(
                    file_path
                ):
                    file_key = file_path
                    file_hash = "url_or_directory"  # Special hash for non-files
                else:
                    if not os.path.exists(file_path):
                        print(f"⚠️  Warning: File not found: {file_path}")
                        continue
                    file_key = os.path.basename(file_path)
                    file_hash = self._get_file_hash(file_path)

                # Check if file needs processing
                if (
                    force_reprocess
                    or file_key not in metadata["processed_files"]
                    or metadata["processed_files"][file_key]["hash"] != file_hash
                ):
                    data_type = self._get_data_type_from_path(file_path)
                    files_to_process.append(
                        {
                            "path": file_path,
                            "key": file_key,
                            "hash": file_hash,
                            "data_type": data_type,
                        }
                    )
                    print(f"📄 Will process: {file_path} (type: {data_type})")
                else:
                    print(f"✅ Already processed: {file_path}")

            # Process files that need processing
            if files_to_process:
                print(f"🔄 Processing {len(files_to_process)} files...")
                failed_to_process = []
                successful_count = 0

                for file_to_process in files_to_process:
                    try:
                        print(f"📄 Processing {file_to_process['path']}...")

                        # Check if it's a JSON file and validate for web page links
                        if file_to_process["data_type"] == "json_file":
                            with open(file_to_process["path"], "r") as f:
                                json_data = json.load(f)

                            validation_result = self.validate_web_page_links(json_data)

                            if validation_result["valid_links"]:
                                (
                                    success,
                                    successful_count,
                                    failed_to_process,
                                    metadata,
                                ) = self.process_json_file(
                                    metadata, failed_to_process, validation_result
                                )
                                if not success:
                                    failed_to_process.append(file_to_process["path"])
                            else:
                                # No valid links found, process as regular file
                                if not self.add_document(
                                    file_to_process["path"],
                                    data_type=file_to_process["data_type"],
                                ):
                                    failed_to_process.append(file_to_process["path"])
                                else:
                                    # Update metadata
                                    metadata["processed_files"][
                                        file_to_process["key"]
                                    ] = {
                                        "hash": file_to_process["hash"],
                                        "processed_at": datetime.now().isoformat(),
                                        "path": file_to_process["path"],
                                        "data_type": file_to_process["data_type"],
                                    }
                                    successful_count += 1
                                    print(
                                        f"✅ Successfully processed: {file_to_process['path']}"
                                    )
                        else:
                            # Regular processing for non-JSON files
                            success = self.add_document(
                                file_to_process["path"],
                                data_type=file_to_process["data_type"],
                            )

                            if not success:
                                failed_to_process.append(file_to_process["path"])
                            else:
                                # Update metadata
                                metadata["processed_files"][file_to_process["key"]] = {
                                    "hash": file_to_process["hash"],
                                    "processed_at": datetime.now().isoformat(),
                                    "path": file_to_process["path"],
                                    "data_type": file_to_process["data_type"],
                                }
                                successful_count += 1
                                print(
                                    f"✅ Successfully processed: {file_to_process['path']}"
                                )

                    except Exception as e:
                        failed_to_process.append(file_to_process["path"])
                        print(f"❌ Error processing {file_to_process['path']}: {e}")
                        # Continue processing other files instead of stopping

                # Update metadata
                metadata["last_updated"] = datetime.now().isoformat()
                self._save_processed_files_metadata(metadata)

                # Print processing summary
                print(f"📊 Processing Summary:")
                print(f"   ✅ Successfully processed: {successful_count} files")
                if failed_to_process:
                    print(f"   ❌ Failed to process: {len(failed_to_process)} files")
                    print(f"   📝 Failed files: {', '.join(failed_to_process)}")

                    # Check if any failed files are URLs and provide tips
                    failed_urls = [f for f in failed_to_process if f.startswith("http")]
                    if failed_urls:
                        self.print_web_scraping_tips(failed_urls)
                else:
                    print(f"   🎉 All files processed successfully!")
            else:
                print("✅ All files are already processed and up to date")

            return True

        except Exception as e:
            print(f"❌ Error in file processing: {e}")
            return False

    def get_rag_tool(self) -> Optional[RagTool]:
        """
        Load existing ChromaDB without reprocessing files.

        Returns:
            RagTool instance if successful, None otherwise
        """
        print("\n🔄 Loading existing RagTool...")
        try:
            # Use base class method to get RAG tool
            rag_tool = super().get_rag_tool()
            if rag_tool is None:
                return None

            # Load metadata for info
            metadata = self._load_processed_files_metadata()
            processed_count = len(metadata.get("processed_files", {}))
            last_updated = metadata.get("last_updated", "Unknown")

            print(f"📄 Contains {processed_count} processed files")
            print(f"🕒 Last updated: {last_updated}")

            return rag_tool

        except Exception as e:
            print(f"❌ Error loading RagTool: {e}")
            return None

    def add_new_file(self, file_path: str) -> bool:
        """
        Add a new file to the existing ChromaDB.

        Args:
            file_path: Path to the new file

        Returns:
            bool: True if successful
        """
        return self.initialize_ragtool_and_process_files([file_path])

    def add_new_url(self, url: str, data_type: str = None) -> bool:
        """
        Add a new URL to the existing ChromaDB.

        Args:
            url: URL to add
            data_type: Optional data type override

        Returns:
            bool: True if successful
        """
        if data_type is None:
            data_type = self._get_data_type_from_path(url)
        return self.initialize_ragtool_and_process_files([url])

    def list_processed_files(self) -> Dict:
        """Get information about processed files."""
        return self._load_processed_files_metadata()

    def reset_database(self) -> bool:
        """
        Reset the ChromaDB by removing all data and clearing processed files metadata.
        Use with caution!

        Returns:
            bool: True if successful
        """
        # Use base class method to reset ChromaDB
        if not super().reset_database():
            return False

        # Reset processed files metadata
        try:
            empty_metadata = {"processed_files": {}, "last_updated": None}
            self._save_processed_files_metadata(empty_metadata)
            print("✅ Processed files metadata reset successfully")
            return True
        except Exception as e:
            print(f"❌ Error resetting processed files metadata: {e}")
            return False

    def get_supported_file_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return list(FilesRagTool._get_supported_extensions_dict().keys())

    def print_supported_types(self):
        """Print information about supported file types."""
        print("\n📋 Supported File Types:")
        print("=" * 50)

        # Group by category
        categories = {
            "Documents": [".pdf", ".docx", ".doc", ".txt", ".md", ".mdx", ".xml"],
            "Data": [".csv", ".json"],
            "Web": [".html", ".htm"],
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
        }

        for category, extensions in categories.items():
            print(f"\n{category}:")
            for ext in extensions:
                data_type = FilesRagTool._get_supported_extensions_dict()[ext]
                print(f"  {ext} → {data_type}")

        print(f"\n🌐 URLs: web_page, youtube_video, github")
        print(f"📁 Directories: directory")
        print(f"📚 Other sources: Gmail, Slack, Discord, etc.")

    def validate_web_page_links(self, json_data: Union[str, List[Dict]]) -> Dict:
        """
        Validate JSON data containing web page links.

        Args:
            json_data: JSON string or list of dictionaries containing link data

        Returns:
            Dict with validation results:
            - 'valid': bool indicating if all elements are valid
            - 'valid_links': list of valid link dictionaries
            - 'invalid_links': list of invalid link dictionaries with error details
            - 'errors': list of general validation errors
        """
        result = {"valid": True, "valid_links": [], "invalid_links": [], "errors": []}

        try:
            # Convert JSON string to dictionary if needed
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data

            # Ensure data is a list
            if not isinstance(data, list):
                result["valid"] = False
                result["errors"].append("JSON data must be a list of link objects")
                return result

            # Validate each element
            for i, element in enumerate(data):
                if not isinstance(element, dict):
                    result["invalid_links"].append(
                        {
                            "index": i,
                            "element": element,
                            "error": "Element must be a dictionary",
                        }
                    )
                    result["valid"] = False
                    continue

                # Check for required properties
                if "data_type" not in element:
                    result["invalid_links"].append(
                        {
                            "index": i,
                            "element": element,
                            "error": "Missing required property: data_type",
                        }
                    )
                    result["valid"] = False
                elif element["data_type"] != "web_page":
                    result["invalid_links"].append(
                        {
                            "index": i,
                            "element": element,
                            "error": f"data_type must be 'web_page', got: {element['data_type']}",
                        }
                    )
                    result["valid"] = False

                if "url" not in element:
                    result["invalid_links"].append(
                        {
                            "index": i,
                            "element": element,
                            "error": "Missing required property: url",
                        }
                    )
                    result["valid"] = False
                elif not isinstance(element["url"], str) or not element["url"].strip():
                    result["invalid_links"].append(
                        {
                            "index": i,
                            "element": element,
                            "error": "url must be a non-empty string",
                        }
                    )
                    result["valid"] = False

                # If element passed all validations, add to valid_links
                if (
                    element.get("data_type") == "web_page"
                    and "url" in element
                    and isinstance(element["url"], str)
                    and element["url"].strip()
                ):
                    result["valid_links"].append(element)

        except json.JSONDecodeError as e:
            result["valid"] = False
            result["errors"].append(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Unexpected error during validation: {str(e)}")

        return result

    def process_json_file(
        self, metadata: Dict, failed_to_process: List, validation_result: Dict
    ) -> Tuple[bool, int, List, Dict]:
        """
        Process a JSON file, extracting and processing web page links if found.

        Args:
            metadata: Dictionary containing processed files metadata
            failed_to_process: List to track failed files
            validation_result: Dictionary containing validation results with valid_links

        Returns:
            Tuple of (success, successful_count, failed_to_process, metadata)
        """
        successful_count = 0
        retry_count = 0  # Number of retries for failed URLs

        try:
            print(
                f"🔗 Found {len(validation_result['valid_links'])} valid web page links in JSON file"
            )

            # Process each valid link
            for link in validation_result["valid_links"]:
                print(f"🌐 Processing web page: {link['url']}")

                # Try to add document to DataBase with retry logic
                success = self._add_document_with_retry(
                    link["url"], data_type="web_page", max_retries=retry_count
                )

                if not success:
                    failed_to_process.append(link["url"])
                    print(
                        f"❌ Failed to process after {retry_count} retries: {link['url']}"
                    )
                else:
                    # Update metadata for the URL
                    url_key = f"url_{hashlib.md5(link['url'].encode()).hexdigest()}"
                    metadata["processed_files"][url_key] = {
                        "hash": hashlib.md5(link["url"].encode()).hexdigest(),
                        "processed_at": datetime.now().isoformat(),
                        "path": link["url"],
                        "data_type": "web_page",
                    }
                    successful_count += 1
                    print(f"✅ Successfully processed: {link['url']}")

        except Exception as json_error:
            print(f"⚠️  Error processing JSON file: {json_error}")
            return False, successful_count, failed_to_process, metadata

        if successful_count > 0:
            return True, successful_count, failed_to_process, metadata
        else:
            return False, successful_count, failed_to_process, metadata

    def _add_document_with_retry(
        self, document_path: str, data_type: str = "file", max_retries: int = 2
    ) -> bool:
        """
        Add a document to the RAG tool with retry logic for web pages.

        Args:
            document_path: Path to the document to add
            data_type: Type of data being added
            max_retries: Maximum number of retry attempts

        Returns:
            bool: True if successful
        """
        if not self.rag_tool:
            if not self.initialize_rag_tool():
                return False

        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    print(
                        f"🔄 Retry attempt {attempt}/{max_retries} for {document_path}"
                    )
                    # Add delay between retries
                    import time

                    time.sleep(2 * attempt)  # Exponential backoff

                # Use the base class method which handles document loaders properly
                return self.add_document(document_path, data_type)

            except Exception as e:
                error_msg = str(e)
                print(
                    f"❌ Error adding document {document_path} (attempt {attempt + 1}): {e}"
                )

                # Check if it's a 403 Forbidden error
                if "403" in error_msg or "Forbidden" in error_msg:
                    print(f"🚫 Website blocked access (403 Forbidden): {document_path}")
                    if attempt < max_retries:
                        print(
                            f"💡 This website may have anti-bot protection. Retrying with delay..."
                        )
                    else:
                        print(
                            f"⚠️  Website consistently blocks access. Consider manual processing."
                        )
                        break

                # Check if it's a connection error
                elif (
                    "Connection aborted" in error_msg
                    or "RemoteDisconnected" in error_msg
                ):
                    print(f"🌐 Connection issue: {document_path}")
                    if attempt < max_retries:
                        print(f"💡 Retrying due to connection issue...")
                    else:
                        print(
                            f"⚠️  Persistent connection issues. Website may be temporarily unavailable."
                        )
                        break

                # For other errors, don't retry
                else:
                    print(f"❌ Non-retryable error: {error_msg}")
                    break

        return False

    def print_web_scraping_tips(self, failed_urls: List[str]):
        """
        Print helpful tips for handling failed web scraping attempts.

        Args:
            failed_urls: List of URLs that failed to process
        """
        if not failed_urls:
            return

        print(f"\n💡 Web Scraping Tips for {len(failed_urls)} failed URLs:")
        print("=" * 60)

        for url in failed_urls:
            print(f"\n🔗 {url}")

            if "sap.com" in url:
                print("   💡 SAP websites often have strict anti-bot protection")
                print("   📋 Consider using SAP's official APIs or documentation")
                print("   🔍 Try accessing the content manually and saving as PDF")

            elif "taxtech500.com" in url:
                print("   💡 This site may require user authentication")
                print("   📋 Consider creating an account and accessing manually")
                print("   🔍 Try using browser developer tools to extract content")

            elif "sapinsider.org" in url:
                print("   💡 This site may have subscription requirements")
                print("   📋 Check if you need a SAP Insider account")
                print("   🔍 Try accessing through a different browser or VPN")

            else:
                print("   💡 General tips for blocked websites:")
                print("   📋 Try accessing manually and saving content locally")
                print("   🔍 Use browser developer tools to extract text content")
                print("   🌐 Consider using a different network or VPN")
                print("   ⏰ Try again later as the site may be temporarily blocking")

        print(f"\n📝 Alternative approaches:")
        print("   1. Save web pages as PDF files and add them to the data/raw folder")
        print("   2. Copy and paste content into text files")
        print("   3. Use browser extensions to save web pages")
        print("   4. Contact website administrators for API access")
        print("   5. Use alternative data sources with similar information")


def main():
    """CLI interface for file processing."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Process various file types for ChromaDB"
    )
    parser.add_argument(
        "--action",
        choices=["process", "add", "add-url", "list", "reset", "supported"],
        default="process",
        help="Action to perform",
    )
    parser.add_argument("--file", help="File path (for 'add' action)")
    parser.add_argument("--url", help="URL (for 'add-url' action)")
    parser.add_argument("--data-type", help="Data type override (for 'add-url' action)")
    parser.add_argument(
        "--force", action="store_true", help="Force reprocess all files"
    )
    parser.add_argument(
        "--storage", default="./chroma_db", help="ChromaDB storage path"
    )

    args = parser.parse_args()

    # Load configuration from centralized config utility
    from agents.utils.config import get_rag_config

    print("\n" + "=" * 40)
    print("RagTool Configuration Loader starting ...")
    print("=" * 60)

    try:
        rag_config = get_rag_config()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("🔄 Using fallback configuration...")
        # Fallback configuration
        rag_config = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-4o-mini",
                },
            },
            "embedding_model": {
                "provider": "openai",
                "config": {"model": "text-embedding-3-small"},
            },
            "chunk_size": 1200,
            "chunk_overlap": 200,
        }

    print("\n" + "=" * 40)
    print("... RagTool Configuration Loader ended.")
    print("=" * 60)

    processor = FilesRagTool(rag_config, args.storage)

    if args.action == "process":
        # Process all supported files in data/raw directory
        data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "raw"
        )
        if os.path.exists(data_dir):
            all_files = []
            for f in os.listdir(data_dir):
                file_path = os.path.join(data_dir, f)
                if processor._is_supported_file(file_path):
                    all_files.append(file_path)

            if all_files:
                success = processor.initialize_ragtool_and_process_files(
                    all_files, args.force
                )
                exit(0 if success else 1)
            else:
                print("No supported files found in data/raw directory")
                exit(1)
        else:
            print("Data/raw directory not found")
            exit(1)

    elif args.action == "add":
        if not args.file:
            print("--file argument required for 'add' action")
            exit(1)
        success = processor.add_new_file(args.file)
        exit(0 if success else 1)

    elif args.action == "add-url":
        if not args.url:
            print("--url argument required for 'add-url' action")
            exit(1)
        success = processor.add_new_url(args.url, args.data_type)
        exit(0 if success else 1)

    elif args.action == "list":
        metadata = processor.list_processed_files()
        print(json.dumps(metadata, indent=2))

    elif args.action == "supported":
        processor.print_supported_types()

    elif args.action == "reset":
        confirm = input("Are you sure you want to reset the ChromaDB? (y/N): ")
        if confirm.lower() == "y":
            success = processor.reset_database()
            exit(0 if success else 1)
        else:
            print("Reset cancelled")
            exit(0)


if __name__ == "__main__":
    main()
