#!/bin/bash

# Script to process manually added content
# This script helps you add manually saved web content to your RAG system

echo "🔧 Manual Content Processing Script"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "files_manager_runner.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if data/raw directory exists
if [ ! -d "data/raw" ]; then
    echo "❌ Error: data/raw directory not found"
    exit 1
fi

echo "📁 Checking for manual content files..."

# Count files in data/raw
file_count=$(find data/raw -name "*.txt" -o -name "*.pdf" | wc -l)
echo "📄 Found $file_count files in data/raw directory"

if [ $file_count -eq 0 ]; then
    echo "📝 No files found in data/raw directory"
    echo ""
    echo "💡 To add manual content:"
    echo "   1. Copy content from blocked websites"
    echo "   2. Save as .txt or .pdf files in data/raw/"
    echo "   3. Use descriptive filenames like 'sap-btp-overview.txt'"
    echo "   4. Run this script again"
    exit 0
fi

echo ""
echo "🔄 Processing files..."

# Process all files
python3 files_manager_runner.py process

echo ""
echo "✅ Processing complete!"
echo ""
echo "📊 Check the output above for processing results"
echo "🔍 You can now search for content from the manually added sources"
