#!/usr/bin/env python3
"""
Complete PDF Processing Workflow

This script performs the complete workflow:
1. Preprocess PDFs (rotate + OCR)
2. Process with RAG tool

Usage:
    python complete_workflow.py
    python complete_workflow.py --skip-preprocessing
    python complete_workflow.py --preprocessing-only
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_preprocessing():
    """Run the PDF preprocessing step."""
    print("🔄 Step 1: PDF Preprocessing")
    print("=" * 40)
    
    # Check if input directory exists
    input_dir = Path("data/raw_ocr")
    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        print("💡 Create the directory and add PDF files to process")
        return False
    
    # Check if there are PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"📄 No PDF files found in {input_dir}")
        return True  # Not an error, just nothing to process
    
    print(f"📄 Found {len(pdf_files)} PDF files to process")
    
    # Run preprocessing script
    try:
        result = subprocess.run([
            sys.executable, "scripts/batch_preprocess.py"
        ], cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ Preprocessing completed successfully")
            return True
        else:
            print("❌ Preprocessing failed")
            return False
    except Exception as e:
        print(f"❌ Error running preprocessing: {e}")
        return False


def run_rag_processing():
    """Run the RAG processing step."""
    print("\n🔄 Step 2: RAG Processing")
    print("=" * 40)
    
    # Check if processed files exist
    processed_dir = Path("data/processed")
    if not processed_dir.exists():
        print(f"❌ Processed directory not found: {processed_dir}")
        print("💡 Run preprocessing first")
        return False
    
    # Check if there are processed text files
    text_files = list(processed_dir.glob("*_processed.txt"))
    if not text_files:
        print(f"📄 No processed text files found in {processed_dir}")
        print("💡 Run preprocessing first")
        return False
    
    print(f"📄 Found {len(text_files)} processed text files")
    
    # Run files_manager_runner
    try:
        result = subprocess.run([
            sys.executable, "files_manager_runner.py"
        ], cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ RAG processing completed successfully")
            return True
        else:
            print("❌ RAG processing failed")
            return False
    except Exception as e:
        print(f"❌ Error running RAG processing: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Complete PDF processing workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python complete_workflow.py                    # Full workflow
  python complete_workflow.py --skip-preprocessing  # Skip preprocessing
  python complete_workflow.py --preprocessing-only   # Only preprocessing
        """
    )
    
    parser.add_argument(
        "--skip-preprocessing",
        action="store_true",
        help="Skip the preprocessing step"
    )
    parser.add_argument(
        "--preprocessing-only",
        action="store_true",
        help="Only run preprocessing, skip RAG processing"
    )
    
    args = parser.parse_args()
    
    print("🚀 Complete PDF Processing Workflow")
    print("=" * 50)
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    success = True
    
    # Step 1: Preprocessing (unless skipped)
    if not args.skip_preprocessing:
        if not run_preprocessing():
            success = False
            print("❌ Preprocessing failed, stopping workflow")
            return 1
    else:
        print("⏭️  Skipping preprocessing step")
    
    # Step 2: RAG Processing (unless preprocessing-only)
    if not args.preprocessing_only:
        if not run_rag_processing():
            success = False
            print("❌ RAG processing failed")
            return 1
    else:
        print("⏭️  Skipping RAG processing step")
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("✅ Complete workflow finished successfully!")
        print("💡 Your RAG agent is ready to use")
    else:
        print("❌ Workflow completed with errors")
        print("💡 Check the error messages above")
    
    return 0 if success else 1


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
