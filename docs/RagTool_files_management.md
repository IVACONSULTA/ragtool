# 📄 PDF Management Guide for RagTool

This guide explains how to efficiently manage PDF documents in your FAISS-powered RAG system.

## 🎯 Overview

The new PDF management system separates document processing from the main agent server, providing:

- **Efficient startup**: Load existing FAISS vector database instead of reprocessing PDFs every time
- **Persistent storage**: PDFs are processed once and stored in FAISS vector database
- **Easy document management**: Simple CLI tools to add/remove documents
- **Change detection**: Only reprocess PDFs when they've been modified
- **Railway optimization**: Faster deployments with pre-processed databases

## 📁 File Structure

```
RagTool/
├── data/
│   ├── raw/                       # Your PDF files and metadata
│   │   ├── policy-document.pdf
│   │   └── processed_files.json  # Metadata about processed files
│   └── processed/                # Processed file metadata
├── db/                            # FAISS vector database storage
│   └── [faiss index files]       # Vector database files
├── files_manager_runner.py        # PDF processing utilities
└── agents/
    └── crew_agent_server_with_guard_rails.py  # Main server (loads existing DB)
```

## 🚀 Quick Start

### 1. Initial Setup (First Time)

```bash
# Add your PDF files to the utils/data directory
cp your-policy.pdf utils/data/

# Process all PDFs (first time only)
python utils/files_manager.py

# Start your agent server
python agents/crew_agent_server.py
```

### 2. Regular Usage

After initial setup, your agent server will automatically load the existing FAISS vector database:

```bash
# Just start your server - no PDF processing needed!
python agents/crewai/crew_agent_server_with_guard_rails.py
```

Output will show:

```
✅ Successfully loaded existing FAISS vector database - no reprocessing needed
📄 Contains 1 processed files
🕒 Last updated: 2024-01-15T10:30:00
```

## 🛠️ PDF Management Commands

### Process All PDFs

```bash
# Process all PDFs in utils/data/ directory
python utils/files_manager.py

# Force reprocess all PDFs (even if unchanged)
python utils/files_manager.py --force
```

### Add New PDFs

```bash
# Add a single new PDF
python utils/files_manager.py --add utils/data/new-policy.pdf

# Or add to utils/data/ directory and process all
cp new-policy.pdf utils/data/
python utils/files_manager.py
```

### List Processed Files

```bash
# See what files have been processed
python utils/files_manager.py --list
```

Output:

```
📄 Processed Files (2):
────────────────────────────────────────────────────────
📄 policy-document.pdf
   Path: ./utils/data/policy-document.pdf
   Processed: 2024-01-15T10:30:00.123456

📄 new-policy.pdf
   Path: ./utils/data/new-policy.pdf
   Processed: 2024-01-15T14:15:30.789012

🕒 Database last updated: 2024-01-15T14:15:30.789012
```

### Reset Database

```bash
# Reset entire FAISS vector database (use with caution!)
python3 files_manager_runner.py --reset
```

**Smart Reset Behavior**:

- **Local Development**: Prompts for confirmation before reset
- **Railway Environment**: Automatically resets without confirmation (for automated deployments)
- **Auto-Reprocessing**: After reset, automatically reprocesses all PDFs in the data directory
- **Force Processing**: Uses force reprocessing to ensure all files are processed again

**Example Output (Local)**:

```
⚠️  WARNING: This will delete all processed PDF data!
Are you sure you want to reset the FAISS vector database? (type 'yes' to confirm): yes
✅ Database reset successfully
Starting to re-process all PDFs...
📄 Found 2 PDF files:
   - policy-document.pdf
   - user-manual.pdf
✅ All PDF files processed successfully
✅ Database PDFS re-processed successfully...
🚀 Your RAG agent is ready to use!
```

**Example Output (Railway)**:

```
🛤️ Railway environment detected:
🛤️  - Project: 'my-rag-tool'
🛤️  - Environment: 'production'
🛤️  - Service: 'web'
⚠️  WARNING: This will delete all processed PDF data!
✅ Database reset successfully
Starting to re-process all PDFs...
📄 Found 2 PDF files:
   - policy-document.pdf
   - user-manual.pdf
✅ All PDF files processed successfully
✅ Database PDFS re-processed successfully...
🚀 Your RAG agent is ready to use!
```

## 🔄 How It Works

### New Utility Functions

The management script now includes several utility functions for better organization:

#### `is_running_on_railway()`

- **Purpose**: Detects Railway cloud environment automatically
- **Detection Method**: Checks for Railway-specific environment variables
- **Returns**: `True` if running on Railway, `False` for local development
- **Usage**: Enables environment-specific behavior (confirmations, logging, etc.)

#### `init_db_and_process_pdfs(data_path, processor)`

- **Purpose**: Centralized PDF discovery and processing logic
- **Features**:
  - Finds all PDF files in specified directory
  - Provides detailed progress feedback
  - Uses force reprocessing for reliable results
  - Handles empty directories gracefully
- **Usage**: Shared by both reset and default processing workflows

### Smart Processing Logic

1. **First Run**: No FAISS vector database exists

   - Process all PDFs in `data/raw/` directory (or role-specific path)
   - Create FAISS vector database with embeddings
   - Save metadata about processed files

2. **Subsequent Runs**: FAISS vector database exists

   - Load existing FAISS vector database directly (fast!)
   - Check if any PDFs have changed (using file hashes)
   - Only reprocess changed files

3. **Adding New PDFs**:
   - Calculate hash of new file
   - Add to existing FAISS vector database
   - Update metadata

### Metadata Tracking

The system tracks:

- **File hashes**: Detect when PDFs are modified
- **Processing timestamps**: When each file was last processed
- **File paths**: Where each PDF is located

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

### Option 1: Pre-built FAISS Vector Database (Recommended)

1. **Local Development**:

   ```bash
   # Process PDFs locally
   python3 files_manager_runner.py process

   # Commit the db/ directory
   git add db/
   git commit -m "Add processed FAISS vector database"
   git push
   ```

2. **Railway/Cloud Run Deployment**:
   - Platform builds and deploys
   - Agent server loads existing FAISS vector database instantly
   - No PDF processing during deployment = faster startup

### Option 2: Process on Deployment Platform

1. **Include PDFs in deployment**:

   ```bash
   git add data/raw/
   git commit -m "Add PDF files"
   ```

2. **First deployment**:

   - Agent processes PDFs on first startup
   - FAISS vector database is created and persisted
   - Subsequent deployments load existing FAISS vector database

3. **Automatic Reset & Reprocessing**:
   - Use `--reset` flag for clean deployments
   - On Railway/Cloud Run: Automatically resets and reprocesses all PDFs
   - No manual confirmation required in production environment

### Environment Variables

```bash
# Optional: Custom paths
RAG_DATA_PATH=./data/raw  # Default depends on AGENT_ROLE
# For VAT agent: ./data/raw
# For SAP agent: ./data/raw_sap
```

## 📊 Performance Benefits

### Before (Original Approach)

```
Agent Startup → Process PDF → Create Embeddings → Ready
                    ↑ ~30-60 seconds every startup
```

### After (Optimized Approach)

```
Agent Startup → Load FAISS Vector DB → Ready
                    ↑ ~2-5 seconds
```

**Improvement**: ~10x faster startup times!

## 🔧 Advanced Usage

### Code Structure Improvements

The management script now features:

- **Modular utility functions**: Railway detection and PDF processing logic extracted
- **Environment-aware behavior**: Different behavior for local vs Railway environments
- **Improved error handling**: Better feedback for different environments
- **Reusable components**: Common PDF processing logic centralized

### Custom Storage Path

```bash
# Use custom FAISS vector database location
# Set via environment variable or config
RAG_DATA_PATH=/custom/path/to/data
```

### Custom Data Directory

```bash
# Process PDFs from different directory
python utils/files_manager.py --data-dir /path/to/pdfs
```

### Programmatic Usage

```python
from agents.rag.files_ragtool import FilesRagTool
from agents.utils.config import get_rag_config

# Initialize processor
config = get_rag_config()  # Get configuration
processor = FilesRagTool(config, "./db")

# Process files
python3 files_manager_runner.py process

# Load existing database
rag_tool = processor.get_rag_tool()
```

## 🔍 Troubleshooting

### "No existing FAISS vector database found"

- **Cause**: First run or database was deleted
- **Solution**: Run `python3 files_manager_runner.py process` to process PDFs

### "PDF file not found"

- **Cause**: PDF file path is incorrect
- **Solution**: Check file exists and path is correct (check `RAG_DATA_PATH` or role-specific path)

### "Error loading existing FAISS vector database"

- **Cause**: Database corruption or version mismatch
- **Solution**: Reset and reprocess: `python3 files_manager_runner.py --reset`
  - The reset command now automatically reprocesses all PDFs after resetting
  - On Railway/Cloud Run: Runs without confirmation
  - Locally: Prompts for confirmation before reset

### Slow startup on Railway/Cloud Run

- **Cause**: PDFs being processed on every deployment
- **Solution**: Pre-process locally and commit FAISS vector database to git

### Out of memory on Railway

- **Cause**: Large PDFs or many documents
- **Solution**: Use Railway's memory scaling or process PDFs locally

## 📋 Best Practices

### Development Workflow

1. **Add PDFs locally**: Copy to `data/raw/` directory (or role-specific path)
2. **Process locally**: Run `python3 files_manager_runner.py process`
3. **Test locally**: Start agent and test
4. **Commit everything**: Include both PDFs and FAISS vector database
5. **Deploy**: Platform uses pre-processed FAISS vector database

### Railway-Specific Workflow

1. **Automated Reset**: Use `--reset` in deployment scripts for clean starts
2. **Environment Detection**: Scripts automatically detect Railway environment
3. **No Manual Intervention**: Reset operations run without confirmation on Railway
4. **Automated Reprocessing**: All PDFs automatically reprocessed after reset

### Production Workflow

1. **Separate processing**: Use dedicated script for PDF processing
2. **Monitor storage**: Check ChromaDB size periodically
3. **Backup ChromaDB**: Include in backup strategy
4. **Update management**: Plan for document updates

### Security Considerations

- **PDF validation**: Ensure PDFs are from trusted sources
- **Access control**: Restrict who can add/modify PDFs
- **Content review**: Review PDF content before processing
- **Storage security**: Secure ChromaDB storage location

## 🔄 Migration from Old Approach

If you're migrating from the old approach where PDFs were processed every time:

1. **Run the new processor**:

   ```bash
   python utils/files_manager.py
   ```

2. **Update your agent server**: The new code automatically handles this

3. **Test the migration**:

   ```bash
   python agents/crew_agent_server.py
   # Should show: "Successfully loaded existing ChromaDB"
   ```

4. **Clean up**: Remove old PDF processing code if any

## 📈 Monitoring and Maintenance

### Regular Tasks

- **Check processed files**: `python3 files_manager_runner.py list`
- **Monitor FAISS vector database size**: Check `db/` directory size
- **Update documents**: Add new PDFs to `data/raw/` and process
- **Refresh content**: Use `--force` when PDFs are updated

### Health Checks

```bash
# Quick health check
python -c "
from utils.files_ragtool import PDFRagTool
from utils.files_manager import is_running_on_railway
processor = PDFRagTool({}, './db')
print('Environment:', 'Railway' if is_running_on_railway() else 'Local')
print('Database exists:', processor.database_path_exists())
print('Metadata:', processor.list_processed_files())
"
```

This new system makes your RAG tool much more efficient and production-ready! 🚀

# Bugs & Fixes

## Database is Locked:

pkill -9 -f "files_manager.py"
pkill -9 -f "crew_agent_server"
rm -rf db && mkdir db

## Check Virtual environment in Use:

python3

import sys
print(sys.prefix)

##If Python local is not sat

# with pyenv

/Users/macnolo/.pyenv/versions/3.11.14/bin/python <command>
/Users/macnolo/.pyenv/versions/3.11.14/bin/python -m pip install "crewai>=0.11.2"
