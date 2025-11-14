# Manual File Processing Workflow

This directory contains documentation for the simplified file processing workflow.

## Overview

The RAG tool now uses a simplified workflow where you manually copy processed files to the `data/raw` folder.

## Workflow

### Step 1: Prepare Your Files

1. Process your files externally (using your preferred OCR/rotation tools)
2. Convert them to supported text formats (`.txt`, `.md`, etc.)
3. Copy the processed files to `data/raw/` folder

### Step 2: Use the RAG Tool

Once you have your processed files in `data/raw/`, use the files manager:

```bash
python3 files_manager_runner.py
```

## Supported File Types

The RAG tool supports various file types including:

- Text files (`.txt`, `.md`)
- PDF files (`.pdf`)
- Word documents (`.docx`)
- CSV files (`.csv`)
- JSON files (`.json`)
- HTML files (`.html`)
- And more...

## Manual Processing

Since OCR and rotation are now handled manually, you can:

1. Use any external tools for PDF processing
2. Convert files to your preferred format
3. Place them directly in `data/raw/`
4. Run the files manager to process them

## Benefits

- No complex dependencies for OCR/rotation
- Use your preferred external tools
- Simpler workflow
- More control over the preprocessing step
