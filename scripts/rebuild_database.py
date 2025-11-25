#!/usr/bin/env python3
"""
Database Rebuild Script for Cloud Run

This script rebuilds the RAG vector database by processing all files
in the data directory. Can be run as a Cloud Run Job or locally.

Usage:
    python scripts/rebuild_database.py
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from agents.rag.ragtool import RagTool
from agents.utils.config import get_data_path

def rebuild_database():
    """Rebuild the RAG vector database from scratch."""
    
    print("🔄 Starting database rebuild...")
    print(f"📂 Data path: {get_data_path()}")
    
    # Get data path from environment or use default
    data_path = os.getenv("RAG_DATA_PATH", "./data/raw")
    db_path = os.getenv("CHROMA_DB_PATH", "./db")
    
    print(f"📁 Processing files from: {data_path}")
    print(f"💾 Database will be saved to: {db_path}")
    
    try:
        # Initialize RagTool with rebuild=True
        print("\n🤖 Initializing RagTool...")
        rag_tool = RagTool(
            data_path=data_path,
            rebuild=True  # Force rebuild
        )
        
        print("\n✅ Database rebuild complete!")
        print(f"📊 Database location: {db_path}")
        
        # Get status
        status = rag_tool.get_status()
        print(f"\n📈 Status: {status}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error rebuilding database: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(rebuild_database())

