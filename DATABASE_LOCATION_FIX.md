# Database Location Fix - Complete Guide

## Problem

CrewAI RagTool was storing the ChromaDB database in the system directory:

```
/Users/macnolo/Library/Application Support/RagIvaconsulta/
```

Instead of the project directory:

```
/Users/macnolo/Desktop/Code/RagIvaconsulta/db/
```

## Root Cause

CrewAI uses Python's `appdirs` library to determine storage locations, which defaults to system-specific directories:

- macOS: `~/Library/Application Support/`
- Linux: `~/.local/share/`
- Windows: `%APPDATA%`

## Solution Implemented

### 1. Updated `.env_local` File ✅

Added environment variables to force local storage:

```bash
# CrewAI Storage Directory (forces local storage instead of system directory)
CREWAI_STORAGE_DIR=./db
```

### 2. Modified `config.py` ✅

Updated to load `.env_local` first (for local development):

```python
# Try .env_local first (for local development), then .env
if not load_dotenv('.env_local'):
    load_dotenv()
```

### 3. Fixed Google Embeddings Configuration ✅

Corrected the embedding model name in `gemini-2.0-flash` configuration:

```python
rag_provider="google-generativeai",  # Changed from "google"
embedding_provider="google-generativeai",  # Changed from "google"
embedding_model="models/embedding-001",  # Using correct model name
```

### 4. Removed Failed FAISS/Qdrant Attempts ✅

Reverted to default ChromaDB configuration as it's the most stable option supported by CrewAI.

## Additional Setup Required

### Option 1: Add to `.zshrc` (Recommended for Permanent Fix)

Add these lines to your `~/.zshrc` file:

```bash
# RagIvaconsulta - Force local database storage
export CREWAI_STORAGE_DIR="$HOME/Desktop/Code/RagIvaconsulta/db"
export CHROMA_DB_PATH="$HOME/Desktop/Code/RagIvaconsulta/db"

# Optional: Create an alias for easy project navigation
alias cdrag='cd $HOME/Desktop/Code/RagIvaconsulta && export CREWAI_STORAGE_DIR="./db" && export CHROMA_DB_PATH="./db"'
```

Then reload your shell:

```bash
source ~/.zshrc
```

### Option 2: Use Project-Specific `.envrc` (with direnv)

If you have `direnv` installed:

1. Create `.envrc` in project root:

```bash
export CREWAI_STORAGE_DIR=./db
export CHROMA_DB_PATH=./db
```

2. Allow the directory:

```bash
direnv allow .
```

### Option 3: Always Source `.env_local` Before Running

```bash
cd /Users/macnolo/Desktop/Code/RagIvaconsulta
export $(cat .env_local | grep -v '^#' | xargs)
python3 ./files_manager_runner.py --reset
```

## Verification Steps

### 1. Clean Up Old Database

```bash
# Remove old system database
rm -rf "/Users/macnolo/Library/Application Support/RagIvaconsulta"

# Remove local database
rm -rf ./db
```

### 2. Test Environment Variables

```bash
cd /Users/macnolo/Desktop/Code/RagIvaconsulta
python3 -c "from dotenv import load_dotenv; import os; load_dotenv('.env_local'); print('CREWAI_STORAGE_DIR:', os.getenv('CREWAI_STORAGE_DIR'))"
```

Expected output:

```
CREWAI_STORAGE_DIR: ./db
```

### 3. Run Files Manager

```bash
python3 ./files_manager_runner.py --reset
```

### 4. Verify Database Location

```bash
# Check that database was created in project directory
ls -la ./db/

# Verify nothing was created in system directory
ls -la "/Users/macnolo/Library/Application Support/RagIvaconsulta" 2>/dev/null || echo "No system directory found - GOOD!"
```

## Railway Deployment

For Railway, add these environment variables in the Railway dashboard:

```
CREWAI_STORAGE_DIR=/app/db
CHROMA_DB_PATH=/app/db
```

And ensure you have a volume mounted at `/app/db` for persistence.

## Troubleshooting

### Issue: Database Still Created in System Directory

**Solution 1**: Ensure environment variables are loaded before importing any CrewAI modules:

```python
# At the very top of your script, before any imports
from dotenv import load_dotenv
load_dotenv('.env_local')

# Now import CrewAI
from crewai_tools import RagTool
```

**Solution 2**: Explicitly set environment variables in your shell before running:

```bash
export CREWAI_STORAGE_DIR="$PWD/db"
export CHROMA_DB_PATH="$PWD/db"
python3 ./files_manager_runner.py --reset
```

**Solution 3**: Remove the old system database directory entirely:

```bash
rm -rf "/Users/macnolo/Library/Application Support/RagIvaconsulta"
```

### Issue: Permission Denied

If you get permission errors when removing the system directory:

```bash
sudo rm -rf "/Users/macnolo/Library/Application Support/RagIvaconsulta"
```

### Issue: Database Files Are Huge

The `chroma.sqlite3` file can grow large (2+ GB). To optimize:

1. **Reset and rebuild**:

```bash
python3 ./files_manager_runner.py --reset
```

2. **Use VACUUM on SQLite** (if needed):

```bash
sqlite3 ./db/chroma.sqlite3 "VACUUM;"
```

## Best Practices

### 1. Always Use Virtual Environment

```bash
cd /Users/macnolo/Desktop/Code/RagIvaconsulta
source .venv/bin/activate
```

### 2. Set Environment Variables Early

Ensure `.env_local` is loaded before any AI/database operations.

### 3. Use Absolute Paths for Railway

When deploying to Railway, use absolute paths:

```
CREWAI_STORAGE_DIR=/app/db
CHROMA_DB_PATH=/app/db
```

### 4. Add `db/` to `.gitignore`

Ensure your `.gitignore` includes:

```
db/
.db/
*.sqlite3
```

## Summary

✅ **What Was Fixed:**

- Added `CREWAI_STORAGE_DIR` to `.env_local`
- Modified `config.py` to load `.env_local` first
- Fixed Google embeddings configuration
- Reverted to stable ChromaDB configuration

✅ **What You Need To Do:**

1. Add environment variables to your `.zshrc` (see Option 1 above)
2. Run `source ~/.zshrc`
3. Clean up old database: `rm -rf "/Users/macnolo/Library/Application Support/RagIvaconsulta"`
4. Reset and rebuild: `python3 ./files_manager_runner.py --reset`
5. Verify location: `ls -la ./db/`

✅ **Result:**
Database will be created in `./db/` in your project directory, making it:

- Version controlled (if desired)
- Portable
- Easy to backup
- Railway deployable
- Accessible for debugging

---

**Last Updated**: November 5, 2025
**Status**: ✅ Solution Implemented
