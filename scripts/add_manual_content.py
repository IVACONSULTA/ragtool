#!/usr/bin/env python3
"""
Script to help add manually saved web content to the RAG system.

This script helps you add content that was manually saved from blocked websites
as PDF files or text files to your RAG system.
"""

import os
import sys
import json
from pathlib import Path

# Add the agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))

from rag.files_ragtool import FilesRagTool

def add_manual_content():
    """Add manually saved content to the RAG system."""
    
    print("🔧 Manual Content Addition Tool")
    print("=" * 50)
    
    # Initialize the RAG tool
    rag_config = {
        "llm": "gpt-3.5-turbo",  # You can change this to your preferred model
        "embedding_model": "text-embedding-ada-002",
        "chunk_size": 1000
    }
    
    processor = FilesRagTool(rag_config)
    
    # Check if database exists
    if not processor.check_if_database_path_exists():
        print("❌ No existing database found. Please run the main processing first.")
        return
    
    print("📁 Checking for manually saved content...")
    
    # Look for manually saved files
    data_raw_dir = Path("../data/raw")
    manual_files = []
    
    # Look for PDF files that might be manually saved web content
    for pdf_file in data_raw_dir.glob("*.pdf"):
        if "sap" in pdf_file.name.lower() or "tax" in pdf_file.name.lower() or "btp" in pdf_file.name.lower():
            manual_files.append(("pdf_file", str(pdf_file)))
    
    # Look for text files with web content
    for txt_file in data_raw_dir.glob("*.txt"):
        if "sap" in txt_file.name.lower() or "tax" in txt_file.name.lower() or "btp" in txt_file.name.lower():
            manual_files.append(("text_file", str(txt_file)))
    
    if not manual_files:
        print("📝 No manually saved content found.")
        print("\n💡 To add manual content:")
        print("   1. Save web pages as PDF files and place them in data/raw/")
        print("   2. Copy web content to text files and place them in data/raw/")
        print("   3. Use descriptive filenames like 'sap-btp-overview.pdf'")
        return
    
    print(f"📄 Found {len(manual_files)} potential manual content files:")
    for i, (data_type, file_path) in enumerate(manual_files, 1):
        print(f"   {i}. {os.path.basename(file_path)} ({data_type})")
    
    # Process each file
    successful_count = 0
    failed_count = 0
    
    for data_type, file_path in manual_files:
        print(f"\n🔄 Processing {os.path.basename(file_path)}...")
        
        try:
            if processor.add_new_file(file_path):
                successful_count += 1
                print(f"✅ Successfully added: {os.path.basename(file_path)}")
            else:
                failed_count += 1
                print(f"❌ Failed to add: {os.path.basename(file_path)}")
        except Exception as e:
            failed_count += 1
            print(f"❌ Error processing {os.path.basename(file_path)}: {e}")
    
    print(f"\n📊 Processing Summary:")
    print(f"   ✅ Successfully added: {successful_count} files")
    print(f"   ❌ Failed to add: {failed_count} files")
    
    if successful_count > 0:
        print(f"\n🎉 Manual content has been added to your RAG system!")
        print(f"   You can now search for information from these sources.")

def create_content_template():
    """Create a template for manually saving web content."""
    
    print("📝 Creating content templates...")
    
    # Create templates directory
    templates_dir = Path("../data/templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Create template files
    templates = {
        "sap-btp-overview.txt": """SAP Business Technology Platform (SAP BTP) Overview

[Copy and paste the main content from the SAP website here]

Key Features:
- [List key features from the website]

Benefits:
- [List benefits from the website]

Use Cases:
- [List use cases from the website]

[Add any other relevant information from the website]
""",
        
        "taxtech500-embedded-tax.txt": """From Banking Apps to SAP BTP: The New Era of Embedded Tax

[Copy and paste the main content from the TaxTech500 article here]

Key Points:
- [List key points from the article]

Examples:
- [List examples from the article]

Conclusion:
- [Add conclusion from the article]

[Add any other relevant information from the article]
""",
        
        "sapinsider-btp-avalara.txt": """Embracing SAP BTP and Avalara Solutions During S/4 Migration to Meet Tax Compliance Mandates

[Copy and paste the main content from the SAP Insider blog here]

Key Insights:
- [List key insights from the blog]

Migration Considerations:
- [List migration considerations from the blog]

Best Practices:
- [List best practices from the blog]

[Add any other relevant information from the blog]
""",
        
        "meridian-arco-tax-determination.txt": """Meridian Global VAT Services Limited - ARCO Tax Determination for SAP BTP

[Copy and paste the main content from the SAP partner page here]

Product Features:
- [List product features from the page]

Integration Benefits:
- [List integration benefits from the page]

Implementation:
- [List implementation details from the page]

[Add any other relevant information from the page]
"""
    }
    
    for filename, content in templates.items():
        template_path = templates_dir / filename
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   📄 Created template: {filename}")
    
    print(f"\n📁 Templates created in: {templates_dir}")
    print(f"💡 Instructions:")
    print(f"   1. Open each template file")
    print(f"   2. Copy content from the corresponding website")
    print(f"   3. Paste the content into the template")
    print(f"   4. Save the files in data/raw/ directory")
    print(f"   5. Run this script again to process the content")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Add manually saved web content to RAG system")
    parser.add_argument("--create-templates", action="store_true", 
                       help="Create content templates for manual saving")
    
    args = parser.parse_args()
    
    if args.create_templates:
        create_content_template()
    else:
        add_manual_content()
