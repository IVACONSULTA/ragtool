# 📄 Files Management Guide for RagTool

This guide explains how to efficiently manage various file types in your ChromaDB-powered RAG system.

## 🎯 Overview

The files management system separates document processing from the main agent server, providing:

- **Multi-format support**: Process PDF, DOCX, TXT, MD, CSV, JSON, HTML, images, and URLs
- **Efficient startup**: Load existing ChromaDB vector database instead of reprocessing files every time
- **Persistent storage**: Files are processed once and stored in ChromaDB vector database
- **Easy document management**: Simple CLI tools to add/remove documents
- **Change detection**: Only reprocess files when they've been modified
- **Railway optimization**: Faster deployments with pre-processed databases
- **JSON-based web scraping**: Process multiple URLs from JSON configuration files

## 📁 File Structure

```
RagIvaconsulta/
├── data/
│   ├── raw/                       # Your source files (PDFs, DOCX, TXT, JSON, etc.)
│   │   ├── policy-document.pdf
│   │   ├── data.csv
│   │   ├── dossier_fuentes.json  # JSON with web page links
│   │   └── document.docx
│   └── processed/                 # Processed file metadata
│       └── processed_files.json   # Metadata about processed files
├── db/                            # ChromaDB vector database storage
│   └── [chromadb files]           # Vector database files
├── agents/
│   ├── utils/
│   │   ├── files_manager.py       # CLI for file management
│   │   └── config.py              # Configuration management
│   └── rag/
│       ├── ragtool.py             # Base RAG tool class
│       └── files_ragtool.py       # Files processing implementation
```

## 🚀 Quick Start

### 1. Initial Setup (First Time)

```bash
# Add your files to the data/raw directory
cp your-policy.pdf data/raw/
cp your-data.csv data/raw/
cp your-document.docx data/raw/

# Process all supported files (first time only)
python agents/utils/files_manager.py

# Start your agent server
python agents/crewai/crew_agent_server_with_guard_rails.py
```

### 2. Regular Usage

After initial setup, your agent server will automatically load the existing ChromaDB vector database:

```bash
# Just start your server - no file processing needed!
python agents/crewai/crew_agent_server_with_guard_rails.py
```

Output will show:

```
✅ Successfully loaded existing ChromaDB vector database - no reprocessing needed
📄 Contains 5 processed files
🕒 Last updated: 2026-02-17T10:30:00
```

## 🛠️ Files Management Commands

### Show Supported File Types

```bash
# Display all supported file types
python agents/utils/files_manager.py --supported
```

Output:

```
📋 Supported File Types:
==================================================

Documents:
  .pdf → pdf_file
  .docx → docx
  .doc → docx_file
  .txt → text_file
  .md → text_file
  .mdx → mdx_file
  .xml → xml_file

Data:
  .csv → csv_file
  .json → json_file

Web:
  .html → html_file
  .htm → html_file

Images:
  .jpg → image_file
  .jpeg → image_file
  .png → image_file
  .gif → image_file
  .bmp → image_file
  .tiff → image_file
  .webp → image_file

🌐 URLs: web_page, youtube_video, github
📁 Directories: directory
📚 Other sources: Gmail, Slack, Discord, etc.
```

### Process All Files

```bash
# Process all supported files in data/raw/ directory
python agents/utils/files_manager.py

# Force reprocess all files (even if unchanged)
python agents/utils/files_manager.py --force

# Process files from a custom directory
python agents/utils/files_manager.py --data-dir /path/to/files
```

### Add New Files

```bash
# Add a single new file
python agents/utils/files_manager.py --add data/raw/new-policy.pdf

# Add a CSV file
python agents/utils/files_manager.py --add data/raw/data.csv

# Add a DOCX file
python agents/utils/files_manager.py --add data/raw/document.docx

# Or add to data/raw/ directory and process all
cp new-policy.pdf data/raw/
python agents/utils/files_manager.py
```

### List Processed Files

```bash
# See what files have been processed
python agents/utils/files_manager.py --list
```

Output:

```
📄 Processed Files (5):
────────────────────────────────────────────────────────
📄 policy-document.pdf
   Path: ./data/raw/policy-document.pdf
   Processed: 2026-02-17T10:30:00.123456

📄 data.csv
   Path: ./data/raw/data.csv
   Processed: 2026-02-17T10:31:15.789012

📄 document.docx
   Path: ./data/raw/document.docx
   Processed: 2026-02-17T10:32:45.456789

📄 url_abc123def456
   Path: https://example.com/article
   Processed: 2026-02-17T10:33:20.123456

📄 notes.md
   Path: ./data/raw/notes.md
   Processed: 2026-02-17T10:34:00.987654

🕒 Database last updated: 2026-02-17T10:34:00.987654
```

### Reset Database

```bash
# Reset entire ChromaDB vector database (use with caution!)
python agents/utils/files_manager.py --reset
```

**Smart Reset Behavior**:

- **Local Development**: Prompts for confirmation before reset
- **Railway Environment**: Automatically resets without confirmation (for automated deployments)
- **Auto-Reprocessing**: After reset, automatically reprocesses all supported files in the data directory
- **Force Processing**: Uses force reprocessing to ensure all files are processed again

**Example Output (Local)**:

```
⚠️  WARNING: This will delete all processed file data!
Are you sure you want to reset the ChromaDB? (type 'yes' to confirm): yes
✅ Database reset successfully
Starting to re-process all files...
📄 Found 5 supported files:
   - policy-document.pdf (pdf_file)
   - data.csv (csv_file)
   - document.docx (docx)
   - notes.md (text_file)
   - config.json (json_file)
✅ All files processed successfully
✅ Database files re-processed successfully...
🚀 Your RAG agent is ready to use!
```

**Example Output (Railway)**:

```
🛤️ Railway environment detected:
🛤️  - Project: 'my-rag-tool'
🛤️  - Environment: 'production'
🛤️  - Service: 'web'
⚠️  WARNING: This will delete all processed file data!
✅ Database reset successfully
Starting to re-process all files...
📄 Found 5 supported files:
   - policy-document.pdf (pdf_file)
   - data.csv (csv_file)
   - document.docx (docx)
   - notes.md (text_file)
   - config.json (json_file)
✅ All files processed successfully
✅ Database files re-processed successfully...
🚀 Your RAG agent is ready to use!
```

## 🔄 How It Works

### Architecture

The system is built with a modular architecture:

#### `BaseRagTool` (agents/rag/ragtool.py)

Base class providing core RAG functionality:
- **Storage Management**: ChromaDB initialization and management
- **Configuration Handling**: LLM and embedding model configuration
- **Document Loading**: Support for various document loaders (PDF, text, CSV, JSON, HTML)
- **Search Operations**: Query the vector database
- **Database Reset**: Clean database operations

#### `FilesRagTool` (agents/rag/files_ragtool.py)

Extends `BaseRagTool` with file-specific features:
- **Multi-format Support**: Handles 15+ file types
- **Metadata Tracking**: Tracks processed files with hashes and timestamps
- **Change Detection**: Only reprocess modified files
- **URL Processing**: Download and process PDFs from URLs
- **JSON Web Scraping**: Process multiple URLs from JSON configuration
- **Retry Logic**: Automatic retry for failed web scraping attempts

#### `files_manager.py` (agents/utils/files_manager.py)

CLI interface for file management:
- **Command-line Interface**: Easy-to-use CLI for all operations
- **Environment Detection**: Automatic Railway vs local detection
- **Configuration Integration**: Uses centralized config system

### Utility Functions

#### `is_running_on_railway()`

- **Purpose**: Detects Railway cloud environment automatically
- **Detection Method**: Checks for Railway-specific environment variables (`RAILWAY_PROJECT_NAME`, `RAILWAY_ENVIRONMENT_NAME`, `RAILWAY_SERVICE_NAME`)
- **Returns**: `True` if running on Railway, `False` for local development
- **Usage**: Enables environment-specific behavior (confirmations, logging, etc.)

#### `get_config()`

- **Purpose**: Load RAG configuration from centralized config system
- **Features**:
  - Attempts to import from `agents.config`
  - Falls back to default configuration if import fails
  - Supports multiple LLM providers (OpenAI, Google, Groq)
- **Returns**: Configuration dictionary with LLM, embedding, and chunking settings

#### `init_db_and_process_files(data_path, processor)`

- **Purpose**: Centralized file discovery and processing logic
- **Features**:
  - Finds all supported files in specified directory
  - Validates file types before processing
  - Provides detailed progress feedback
  - Uses force reprocessing for reliable results
  - Handles empty directories gracefully
  - Reports unsupported files
- **Usage**: Shared by both reset and default processing workflows

### Smart Processing Logic

1. **First Run**: No ChromaDB vector database exists

   - Scan `data/raw/` directory for supported files
   - Validate file types using extension mapping
   - Process each file with appropriate loader
   - Create ChromaDB vector database with embeddings
   - Save metadata about processed files to `data/processed/processed_files.json`

2. **Subsequent Runs**: ChromaDB vector database exists

   - Load existing ChromaDB vector database directly (fast!)
   - Check if any files have changed (using MD5 file hashes)
   - Only reprocess changed or new files
   - Skip unchanged files with confirmation message

3. **Adding New Files**:
   - Validate file type is supported
   - Calculate MD5 hash of new file
   - Determine data type from file extension
   - Add to existing ChromaDB vector database
   - Update metadata with hash, timestamp, and path

4. **JSON File Processing**:
   - Detect JSON files with web page links
   - Support two JSON structures:
     - Legacy: Array of objects with `data_type` and `url`
     - Dossier: Object with `normativa` array containing `enlaces_oficiales`
   - Validate and extract URLs
   - Detect URL type (PDF vs web page)
   - Download PDFs to temporary files
   - Process with retry logic (2 retries by default)
   - Automatic PDF fallback for failed web pages
   - Clean up temporary files after processing

### Metadata Tracking

The system tracks (in `data/processed/processed_files.json`):

- **File hashes**: MD5 hash to detect when files are modified
- **Processing timestamps**: ISO format timestamp when each file was last processed
- **File paths**: Full path to each processed file
- **Data types**: Type of each file (pdf_file, csv_file, etc.)
- **URL metadata**: For URLs from JSON files, includes `normativa_id` and `normativa_titulo`
- **Last updated**: Global timestamp for the entire database

## 🚄 Railway Deployment Strategy

### Environment Detection

The system automatically detects Railway environments by checking for:

- `RAILWAY_PROJECT_NAME`
- `RAILWAY_ENVIRONMENT_NAME`
- `RAILWAY_SERVICE_NAME`

When running on Railway, certain behaviors change:

- Reset operations don't require confirmation (automated deployment safe)
- Enhanced logging for deployment tracking
- Optimized processing flow for cloud environments

### Option 1: Pre-built ChromaDB Vector Database (Recommended)

1. **Local Development**:

   ```bash
   # Process files locally
   python agents/utils/files_manager.py

   # Commit the db/ directory
   git add db/
   git add data/processed/processed_files.json
   git commit -m "Add processed ChromaDB vector database"
   git push
   ```

2. **Railway Deployment**:
   - Platform builds and deploys
   - Agent server loads existing ChromaDB vector database instantly
   - No file processing during deployment = faster startup

### Option 2: Process on Deployment Platform

1. **Include files in deployment**:

   ```bash
   git add data/raw/
   git commit -m "Add source files"
   ```

2. **First deployment**:

   - Agent processes files on first startup
   - ChromaDB vector database is created and persisted
   - Subsequent deployments load existing ChromaDB vector database

3. **Automatic Reset & Reprocessing**:
   - Use `--reset` flag for clean deployments
   - On Railway: Automatically resets and reprocesses all files
   - No manual confirmation required in production environment

### Environment Variables

```bash
# Configuration Set Selection
CONFIG_SET=GEMINI_2.0_FLASH  # or OPENAI_4o_MINI, GROQ_LLAMA__MODEL, etc.

# API Keys (flexible handling)
API_KEY=your_api_key                    # Generic key for all providers
# OR provider-specific keys:
OPENAI_API_KEY=your_openai_key         # For OpenAI
GEMINI_API_KEY=your_gemini_key         # For Google/Gemini
EMBEDDINGS_GOOGLE_API_KEY=your_key     # For Google embeddings (auto-set from GEMINI_API_KEY)

# Optional: Custom paths
RAG_DATA_PATH=./data/raw               # Override default data path
CHROMA_DB_PATH=./db                    # Override default ChromaDB path

# Optional: LangSmith tracing
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=your_project_name
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

## 📊 Performance Benefits

### Before (Original Approach)

```
Agent Startup → Process Files → Create Embeddings → Ready
                    ↑ ~30-60 seconds every startup
```

### After (Optimized Approach)

```
Agent Startup → Load ChromaDB Vector DB → Ready
                    ↑ ~2-5 seconds
```

**Improvement**: ~10x faster startup times!

### Supported File Types Performance

| File Type | Extension | Processing Speed | Notes |
|-----------|-----------|------------------|-------|
| PDF | .pdf | Medium | Depends on size and complexity |
| Text | .txt, .md | Fast | Direct text extraction |
| DOCX | .docx, .doc | Medium | Requires document parsing |
| CSV | .csv | Fast | Structured data |
| JSON | .json | Fast | Structured data, supports web scraping |
| HTML | .html, .htm | Fast | Web content |
| Images | .jpg, .png, etc. | Slow | Requires OCR (manual preprocessing recommended) |
| URLs | http(s):// | Variable | Depends on website and network |

## 🔧 Advanced Usage

### Code Structure

The system features a clean, modular architecture:

- **Base Class Pattern**: `BaseRagTool` provides core functionality, `FilesRagTool` extends it
- **Modular utility functions**: Railway detection and file processing logic separated
- **Environment-aware behavior**: Different behavior for local vs Railway environments
- **Improved error handling**: Retry logic, fallback mechanisms, detailed error messages
- **Reusable components**: Common file processing logic centralized
- **Configuration System**: Centralized configuration with multiple provider support

### Custom Storage Path

```bash
# Use custom ChromaDB location via command line
python agents/utils/files_manager.py --storage /custom/path/to/db

# Or set via environment variable
export CHROMA_DB_PATH=/custom/path/to/db
```

### Custom Data Directory

```bash
# Process files from different directory
python agents/utils/files_manager.py --data-dir /path/to/files

# Or set via environment variable
export RAG_DATA_PATH=/path/to/files
```

### Programmatic Usage

```python
from agents.rag.files_ragtool import FilesRagTool
from agents.utils.config import get_rag_config

# Initialize processor
config = get_rag_config()  # Get configuration from centralized system
processor = FilesRagTool(config, "./db")

# Process multiple files
files_to_process = [
    "data/raw/document.pdf",
    "data/raw/data.csv",
    "data/raw/notes.md"
]
success = processor.initialize_ragtool_and_process_files(files_to_process)

# Add a single file
processor.add_new_file("data/raw/new-document.pdf")

# Add a URL
processor.add_new_url("https://example.com/article", data_type="web_page")

# List processed files
metadata = processor.list_processed_files()
print(f"Processed {len(metadata['processed_files'])} files")

# Load existing database
rag_tool = processor.get_rag_tool()

# Search the database
results = rag_tool._run("What is the policy on data retention?")
```

### JSON Web Scraping Configuration

Create a JSON file with web page links to process multiple URLs:

**Legacy Format** (`data/raw/links.json`):
```json
[
  {
    "data_type": "web_page",
    "url": "https://example.com/article1"
  },
  {
    "data_type": "pdf_file",
    "url": "https://example.com/document.pdf"
  }
]
```

**Dossier Format** (`data/raw/dossier_fuentes.json`):
```json
{
  "normativa": [
    {
      "id": "ley_001",
      "titulo": "Ley General de Protección de Datos",
      "enlaces_oficiales": [
        "https://boe.es/buscar/doc.php?id=BOE-A-2018-16673",
        "https://example.com/ley-proteccion-datos.pdf"
      ]
    },
    {
      "id": "real_decreto_002",
      "titulo": "Real Decreto de Seguridad",
      "enlaces_oficiales": [
        "https://boe.es/buscar/doc.php?id=BOE-A-2021-12345"
      ]
    }
  ]
}
```

Then process:
```bash
python agents/utils/files_manager.py --add data/raw/dossier_fuentes.json
```

The system will:
1. Detect JSON structure (legacy or dossier)
2. Extract all URLs from `enlaces_oficiales` arrays
3. Automatically detect if URLs are PDFs or web pages
4. Download PDFs to temporary files
5. Process each URL with retry logic
6. Fall back to PDF download if web scraping fails
7. Clean up temporary files
8. Track metadata including `normativa_id` and `normativa_titulo`

## 🔍 Troubleshooting

### "No existing ChromaDB vector database found"

- **Cause**: First run or database was deleted
- **Solution**: Run `python agents/utils/files_manager.py` to process files

### "File not found" or "File type not supported"

- **Cause**: File path is incorrect or file type is not supported
- **Solution**: 
  - Check file exists: `ls data/raw/`
  - Verify file type is supported: `python agents/utils/files_manager.py --supported`
  - Check `RAG_DATA_PATH` environment variable if using custom path

### "Error loading existing ChromaDB vector database"

- **Cause**: Database corruption or version mismatch
- **Solution**: Reset and reprocess: `python agents/utils/files_manager.py --reset`
  - The reset command automatically reprocesses all files after resetting
  - On Railway: Runs without confirmation
  - Locally: Prompts for confirmation before reset

### "Configuration error" or "API key missing"

- **Cause**: Missing or incorrect configuration
- **Solution**:
  - Check configuration: `python -m agents.utils.config --info`
  - Set API keys in `.env` file or environment variables
  - Verify `CONFIG_SET` is valid: `python -m agents.utils.config --list-sets`

### Slow startup on Railway

- **Cause**: Files being processed on every deployment
- **Solution**: Pre-process locally and commit ChromaDB to git:
  ```bash
  python agents/utils/files_manager.py
  git add db/ data/processed/
  git commit -m "Add pre-processed database"
  git push
  ```

### Out of memory on Railway

- **Cause**: Large files or many documents
- **Solution**: 
  - Use Railway's memory scaling
  - Process files locally and commit database
  - Reduce chunk size in configuration
  - Split large files into smaller ones

### Web scraping fails with 403 Forbidden

- **Cause**: Website has anti-bot protection
- **Solution**:
  - System automatically retries with delays
  - If persistent, manually save page as PDF
  - Check web scraping tips in output for specific sites
  - Consider using alternative data sources

### JSON file not processing URLs

- **Cause**: Incorrect JSON structure or invalid URLs
- **Solution**:
  - Validate JSON structure (legacy or dossier format)
  - Check URLs are valid and accessible
  - Review processing output for validation errors
  - Ensure `enlaces_oficiales` arrays contain valid URL strings

### "FilesRagTool is not available"

- **Cause**: Missing dependencies
- **Solution**: Install required packages:
  ```bash
  pip install crewai crewai-tools langchain-community
  ```

## 📋 Best Practices

### Development Workflow

1. **Add files locally**: Copy to `data/raw/` directory
   ```bash
   cp document.pdf data/raw/
   cp data.csv data/raw/
   ```

2. **Verify file types**: Check files are supported
   ```bash
   python agents/utils/files_manager.py --supported
   ```

3. **Process locally**: Run file manager
   ```bash
   python agents/utils/files_manager.py
   ```

4. **Test locally**: Start agent and test queries
   ```bash
   python agents/crewai/crew_agent_server_with_guard_rails.py
   ```

5. **Commit everything**: Include files and database
   ```bash
   git add data/raw/ db/ data/processed/
   git commit -m "Add documents and processed database"
   git push
   ```

6. **Deploy**: Platform uses pre-processed ChromaDB

### Railway-Specific Workflow

1. **Automated Reset**: Use `--reset` in deployment scripts for clean starts
2. **Environment Detection**: Scripts automatically detect Railway environment
3. **No Manual Intervention**: Reset operations run without confirmation on Railway
4. **Automated Reprocessing**: All files automatically reprocessed after reset
5. **Environment Variables**: Set `CONFIG_SET` and API keys in Railway dashboard

### Production Workflow

1. **Separate processing**: Use dedicated script for file processing
2. **Monitor storage**: Check ChromaDB size periodically
   ```bash
   du -sh db/
   ```

3. **Backup ChromaDB**: Include in backup strategy
   ```bash
   tar -czf db-backup-$(date +%Y%m%d).tar.gz db/ data/processed/
   ```

4. **Update management**: Plan for document updates
   - Use `--force` to reprocess modified files
   - Track changes in `processed_files.json`

5. **Configuration management**: Use configuration sets for different environments
   ```bash
   # Development
   CONFIG_SET=GEMINI_2.0_FLASH
   
   # Production
   CONFIG_SET=OPENAI_4o_MINI
   ```

### Security Considerations

- **File validation**: Ensure files are from trusted sources
- **Access control**: Restrict who can add/modify files
- **Content review**: Review file content before processing
- **Storage security**: Secure ChromaDB storage location
- **API key management**: Use environment variables, never commit keys
- **URL validation**: Verify URLs before processing from JSON files
- **Temporary file cleanup**: System automatically cleans up temp files

### Performance Optimization

1. **Pre-process files**: Process files locally before deployment
2. **Chunk size tuning**: Adjust `chunk_size` and `chunk_overlap` in config
3. **Selective processing**: Only process changed files (automatic)
4. **Batch processing**: Process multiple files in one operation
5. **Memory management**: Monitor memory usage for large files
6. **Database optimization**: Reset and reprocess periodically for optimal performance

## 🔄 Migration from Old Approach

If you're migrating from the old approach where files were processed every time:

1. **Backup existing data**:
   ```bash
   cp -r db/ db_backup/
   cp data/processed/processed_files.json data/processed/processed_files.json.backup
   ```

2. **Run the new processor**:
   ```bash
   python agents/utils/files_manager.py
   ```

3. **Update your agent server**: The new code automatically handles this

4. **Test the migration**:
   ```bash
   python agents/crewai/crew_agent_server_with_guard_rails.py
   # Should show: "Successfully loaded existing ChromaDB"
   ```

5. **Verify processed files**:
   ```bash
   python agents/utils/files_manager.py --list
   ```

6. **Clean up**: Remove old processing code if any

### Migration Checklist

- [ ] Backup existing database and metadata
- [ ] Update file paths to new structure (`data/raw/`, `data/processed/`)
- [ ] Install new dependencies: `pip install crewai crewai-tools langchain-community`
- [ ] Set up configuration: Check `CONFIG_SET` and API keys
- [ ] Process files with new system
- [ ] Test agent with existing queries
- [ ] Verify all files are processed correctly
- [ ] Update deployment scripts if needed
- [ ] Remove old processing code

## 📈 Monitoring and Maintenance

### Regular Tasks

- **Check processed files**: 
  ```bash
  python agents/utils/files_manager.py --list
  ```

- **Monitor ChromaDB size**: 
  ```bash
  du -sh db/
  ls -lh data/processed/processed_files.json
  ```

- **Update documents**: 
  ```bash
  # Add new files
  cp new-document.pdf data/raw/
  python agents/utils/files_manager.py
  ```

- **Refresh content**: 
  ```bash
  # Force reprocess when files are updated
  python agents/utils/files_manager.py --force
  ```

- **Check configuration**:
  ```bash
  python -m agents.utils.config --info
  ```

### Health Checks

```bash
# Quick health check
python -c "
from agents.rag.files_ragtool import FilesRagTool
from agents.utils.files_manager import is_running_on_railway
from agents.utils.config import get_rag_config

config = get_rag_config()
processor = FilesRagTool(config, './db')

print('Environment:', 'Railway' if is_running_on_railway() else 'Local')
print('Database exists:', processor.check_if_database_path_exists())
metadata = processor.list_processed_files()
print(f'Processed files: {len(metadata[\"processed_files\"])}')
print(f'Last updated: {metadata.get(\"last_updated\", \"Never\")}')
"
```

### Automated Monitoring Script

Create a monitoring script (`scripts/monitor_rag.py`):

```python
#!/usr/bin/env python3
"""Monitor RAG system health"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.rag.files_ragtool import FilesRagTool
from agents.utils.config import get_rag_config
from agents.utils.files_manager import is_running_on_railway

def main():
    print("🔍 RAG System Health Check")
    print("=" * 60)
    
    # Configuration check
    try:
        config = get_rag_config()
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return 1
    
    # Database check
    processor = FilesRagTool(config, './db')
    db_exists = processor.check_if_database_path_exists()
    print(f"{'✅' if db_exists else '❌'} Database exists: {db_exists}")
    
    # Metadata check
    metadata = processor.list_processed_files()
    file_count = len(metadata.get('processed_files', {}))
    print(f"📄 Processed files: {file_count}")
    print(f"🕒 Last updated: {metadata.get('last_updated', 'Never')}")
    
    # Storage size
    if os.path.exists('./db'):
        db_size = sum(f.stat().st_size for f in Path('./db').rglob('*') if f.is_file())
        print(f"💾 Database size: {db_size / (1024*1024):.2f} MB")
    
    # Environment
    env = 'Railway' if is_running_on_railway() else 'Local'
    print(f"🌍 Environment: {env}")
    
    print("=" * 60)
    print("✅ Health check complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

Run it:
```bash
python scripts/monitor_rag.py
```

This comprehensive system makes your RAG tool efficient, maintainable, and production-ready! 🚀

## 🆕 New Features

### Multi-Format Support
- **15+ file types**: PDF, DOCX, TXT, MD, CSV, JSON, HTML, images, and more
- **URL processing**: Direct web page and PDF URL support
- **JSON web scraping**: Batch process URLs from JSON configuration

### Advanced Processing
- **Automatic retry logic**: 2 retries for failed web scraping
- **PDF fallback**: Automatically try PDF download if web scraping fails
- **Smart URL detection**: Automatically detect PDF vs web page URLs
- **Temporary file cleanup**: Automatic cleanup of downloaded files

### Configuration System
- **Multiple providers**: OpenAI, Google/Gemini, Groq support
- **Configuration sets**: Easy switching between different configurations
- **Flexible API keys**: Generic or provider-specific key support
- **LangSmith integration**: Optional tracing and monitoring

### Metadata Tracking
- **Comprehensive metadata**: Hash, timestamp, path, type for each file
- **URL metadata**: Track normativa ID and title for JSON sources
- **Change detection**: MD5 hash-based change detection
- **Processing history**: Complete audit trail of processed files

## 🐛 Common Issues & Quick Fixes

### Database is Locked

If ChromaDB is locked by another process:

```bash
# Kill any running processes
pkill -9 -f "files_manager.py"
pkill -9 -f "crew_agent_server"

# Reset database
rm -rf db && mkdir db

# Reprocess files
python agents/utils/files_manager.py
```

### Check Virtual Environment

Verify you're using the correct Python environment:

```bash
# Check current Python
which python
python --version

# Check virtual environment
python -c "import sys; print(sys.prefix)"

# If using pyenv
pyenv version
pyenv which python
```

### Python Version Issues

If you need to use a specific Python version:

```bash
# With pyenv
/Users/macnolo/.pyenv/versions/3.11.14/bin/python agents/utils/files_manager.py

# Install dependencies with specific Python
/Users/macnolo/.pyenv/versions/3.11.14/bin/python -m pip install "crewai>=0.11.2"
```

### Missing Dependencies

Install all required dependencies:

```bash
pip install crewai crewai-tools langchain-community
pip install chromadb pypdf python-docx beautifulsoup4
pip install requests python-dotenv
```

### ChromaDB Version Conflicts

If you encounter ChromaDB version issues:

```bash
# Uninstall and reinstall
pip uninstall chromadb -y
pip install chromadb

# Or specify version
pip install chromadb==0.4.22
```

### Import Errors

If you get import errors:

```bash
# Ensure project root is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run from project root
cd /Users/macnolo/Desktop/Code/RagIvaconsulta
python agents/utils/files_manager.py
```

### Configuration Not Found

If configuration fails to load:

```bash
# Check .env file exists
ls -la .env

# Verify API keys are set
python -m agents.utils.config --info

# List available configuration sets
python -m agents.utils.config --list-sets
```

### Metadata File Corruption

If `processed_files.json` is corrupted:

```bash
# Backup corrupted file
cp data/processed/processed_files.json data/processed/processed_files.json.corrupted

# Reset and reprocess
python agents/utils/files_manager.py --reset
```

### Web Scraping Timeouts

If web scraping consistently times out:

```bash
# Increase timeout in code or
# Process URLs manually and save as files
wget https://example.com/page -O data/raw/page.html
python agents/utils/files_manager.py --add data/raw/page.html
```
