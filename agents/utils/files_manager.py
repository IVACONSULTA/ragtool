#!/usr/bin/env python3
"""
Files Management Script for RagTool

Simple CLI script to manage various file types in your ChromaDB.
This script provides an easy interface to the FilesRagTool utility.

Supported file types: PDF, DOCX, TXT, MD, CSV, JSON, HTML, images, and more.

Usage:
    python files_manager.py                    # Process all supported files in ./data/raw
    python files_manager.py --add new.pdf     # Add a new file
    python files_manager.py --list            # List processed files
    python files_manager.py --force           # Force reprocess all files
    python files_manager.py --reset           # Reset database (careful!)
    python files_manager.py --supported       # Show supported file types
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(
    __file__
).parent.parent.parent  # Go up two levels from agents/utils/
sys.path.append(str(project_root))

# Import FilesRagTool from the correct location (conditional import)
try:
    from agents.rag.files_ragtool import FilesRagTool
except ImportError:
    # FilesRagTool requires external dependencies that may not be installed
    FilesRagTool = None

###################################################################################################
############################       Utility Functions      #########################################
###################################################################################################


def is_running_on_railway() -> bool:
    """Detect if running locally vs on Railway."""
    # Railway sets specific environment variables
    railway_project_name = os.getenv("RAILWAY_PROJECT_NAME")
    railway_env = os.getenv("RAILWAY_ENVIRONMENT_NAME")
    railway_service = os.getenv("RAILWAY_SERVICE_NAME")

    # Check if both environment variables are present and not empty
    if not railway_project_name or not railway_env or not railway_service:
        print("🏠 Local development detected - Railway env vars not set")
        return False

    # Check if the environment variables are not just empty strings
    if (
        railway_project_name.strip() == ""
        or railway_env.strip() == ""
        or railway_service.strip() == ""
    ):
        print("🏠 Local development detected - Railway env vars are empty")
        return False

    # If Railway-specific vars are present and not empty, we're on Railway
    print("🛤️Railway environment detected:")
    print(f"🛤️  - Project: '{railway_project_name}'")
    print(f"🛤️  - Environment: '{railway_env}'")
    print(f"🛤️  - Service: '{railway_service}'")
    return True


def get_config():
    """Get configuration for LLM and embedding models."""
    try:
        # Try different import approaches for config
        try:
            from agents.config import get_rag_config
        except ImportError:
            from config import get_rag_config

        return get_rag_config()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("🔄 Using fallback configuration...")
        # Fallback configuration
        return {
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


def init_db_and_process_files(data_path: str, processor):
    data_dir = data_path

    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        print(
            "💡 Create the directory and add supported files, or use --data-dir to specify a different path"
        )
        print(f"💡 Expected location: {os.path.abspath(data_dir)}")
        return 1
    
    # Find all supported files
    supported_files = []
    unsupported_files = []

    for filename in os.listdir(data_dir):
        file_path = os.path.join(data_dir, filename)
        if os.path.isfile(file_path) and processor._is_supported_file(file_path):
            supported_files.append(file_path)
        else:
            unsupported_files.append(file_path)


    if len(unsupported_files) > 0:

        print(f"📄 Found {len(unsupported_files)} unsupported files:")

        for file_path in unsupported_files:
            filename = os.path.basename(file_path)
            data_type = processor._get_data_type_from_path(file_path)
            print(f"   - {filename} ({data_type})")
        print()
        print("These files will not be processed.")


    if not supported_files:
        print(f"\n📄 No supported files found in {data_dir}")
        print("💡 Add some supported files to the directory and try again")
        print("💡 Use --supported to see what file types are supported")
        return 0

    print(f"\n📄 Found {len(supported_files)} supported files:")
    for file_path in supported_files:
        filename = os.path.basename(file_path)
        data_type = processor._get_data_type_from_path(file_path)
        print(f"   - {filename} ({data_type})")
    print()

    # Process the files
    force_reprocess = True
    success = processor.initialize_ragtool_and_process_files(
        supported_files, force_reprocess
    )

    if success:
        return 0
    else:
        print("❌ Some files failed to process")
        return 1


###################################################################################################
############################       MAIN FUNCTION      #############################################
###################################################################################################


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Manage various file types in ChromaDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python files_manager.py                     # Process all supported files in data/raw/
  python files_manager.py --add policy2.pdf  # Add new file
  python files_manager.py --add data.csv     # Add CSV file
  python files_manager.py --list             # Show processed files
  python files_manager.py --force            # Force reprocess all files
  python files_manager.py --reset            # Reset database
  python files_manager.py --supported        # Show supported file types
        """,
    )

    parser.add_argument(
        "--add", metavar="FILE", help="Add a new file to the database"
    )
    parser.add_argument("--list", action="store_true", help="List all processed files")
    parser.add_argument(
        "--force", action="store_true", help="Force reprocess all files"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset the entire ChromaDB (USE WITH CAUTION)",
    )
    parser.add_argument(
        "--supported",
        action="store_true",
        help="Show supported file types and exit",
    )
    parser.add_argument(
        "--storage", default="./db", help="ChromaDB storage path (default: ./db)"
    )
    parser.add_argument(
        "--data-dir",
        default="./data/raw",
        help="Directory containing files (default: ./data/raw)",
    )

    args = parser.parse_args()

    print(f"🚀 RagTool Files Manager args: {args}")

    # Initialize processor
    if FilesRagTool is None:
        print("❌ FilesRagTool is not available. Please install required dependencies:")
        print("   pip install crewai crewai-tools")
        return
    
    config = get_config()
    processor = FilesRagTool(config, args.storage)

    print("🚀 RagTool Files Manager")
    print(f"📂 Storage path: {args.storage}")
    print(f"📁 Data directory: {args.data_dir}")
    print()

    # Handle different actions
    if args.supported:
        processor.print_supported_types()
        return 0

    elif args.reset:
        print("⚠️  WARNING: This will delete all processed file data!")

        running_on_railway = is_running_on_railway()
        reset_confirmed = False

        # If running locally, confirm reset needed before resetting whole DataBase
        if not running_on_railway:
            confirm = input(
                "Are you sure you want to reset the ChromaDB? (type 'yes' to confirm): "
            )
            reset_confirmed = confirm.lower() == "yes"

        if running_on_railway or reset_confirmed:
            success = processor.reset_database()
            if success:
                print("✅ Database reset successfully")
                print("Starting to re-process all files...")
                # Find all supported files in data directory
                init_db_and_process_files(args.data_dir, processor)
                print("\n\n✅ Database files re-processed successfully...")
                print("🚀 Your RAG agent is ready to use!\n")
                return 0
            else:
                print("❌ Failed to reset database")
                return 1
        else:
            print("❌ Reset cancelled")
            return 0

    elif args.list:
        metadata = processor.list_processed_files()
        processed_files = metadata.get("processed_files", {})

        if not processed_files:
            print("📄 No files have been processed yet")
        else:
            print(f"📄 Processed Files ({len(processed_files)}):")
            print("-" * 60)
            for filename, info in processed_files.items():
                processed_at = info.get("processed_at", "Unknown")
                file_path = info.get("path", "Unknown")
                print(f"📄 {filename}")
                print(f"   Path: {file_path}")
                print(f"   Processed: {processed_at}")
                print()

        last_updated = metadata.get("last_updated")
        if last_updated:
            print(f"🕒 Database last updated: {last_updated}")

        return 0

    elif args.add:
        file_path = args.add

        # Check if file exists
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return 1

        # Check if it's a supported file type
        if not processor._is_supported_file(file_path):
            print(f"❌ File type not supported: {file_path}")
            print("💡 Use --supported to see what file types are supported")
            return 1

        data_type = processor._get_data_type_from_path(file_path)
        print(f"📄 Adding file: {file_path} (type: {data_type})")
        success = processor.add_new_file(file_path)

        if success:
            print("✅ File added successfully")
            return 0
        else:
            print("❌ Failed to add file")
            return 1

    else:
        # Default action: process all supported files in data directory
        init_db_and_process_files(args.data_dir, processor)
        print("\n\n✅ Database files processed successfully...")
        print("🚀 Your RAG agent is ready to use!\n\n")


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
