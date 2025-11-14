# FAISS Vector Database Migration Guide

## Overview

This project has been migrated from ChromaDB to **FAISS** (Facebook AI Similarity Search) as the vector database for the RagTool. This change resolves compatibility issues with ChromaDB version upgrades while providing a robust, free, and Railway-compatible solution.

## Why FAISS?

### Advantages
- ✅ **Local & File-Based**: No external database service required
- ✅ **Free & Open Source**: No cost, no limitations
- ✅ **Railway Compatible**: Works perfectly in Railway's deployment environment
- ✅ **High Performance**: Optimized for similarity search by Facebook AI Research
- ✅ **Persistent Storage**: Saves index to disk for reuse across restarts
- ✅ **Scalable**: Handles small to medium datasets efficiently (perfect for 4+ documents)
- ✅ **No Server Required**: Embedded library, not a separate service
- ✅ **Version Stable**: Less prone to breaking changes between versions

### Why Not ChromaDB?
- ❌ Version upgrade issues causing database corruption
- ❌ More complex dependency management
- ❌ Requires more resources for server mode

## What Changed?

### 1. Vector Database Configuration

The RagTool now automatically configures FAISS as the vector database provider. The configuration is set in `agents/rag/ragtool.py`:

```python
def _get_core_config(self) -> Dict:
    """Get core LLM/embedding config without chunk parameters."""
    core_config = self.rag_config.copy()
    
    # Configure FAISS as the vector database
    core_config["vectordb"] = {
        "provider": "faiss",
        "config": {
            "collection_name": "rag_documents"
        }
    }
    
    return core_config
```

### 2. Updated Dependencies

Added to `requirements.txt`:
```
faiss-cpu>=1.7.4
```

### 3. Updated Terminology

Documentation and code comments updated:
- "ChromaDB" → "Vector Database" or "FAISS"
- Database references now generic or FAISS-specific

## Migration Steps

### Option 1: Start Fresh (Recommended)

If you want a clean start with FAISS:

1. **Backup your existing database** (optional):
   ```bash
   cp -r ./db ./db_backup_chromadb
   ```

2. **Reset the database**:
   ```bash
   python3 -m agents.rag.files_ragtool --action reset
   ```

3. **Install/Update dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Reprocess your documents**:
   ```bash
   python3 -m agents.rag.files_ragtool --action process --force
   ```

### Option 2: Parallel Setup

Keep your old ChromaDB and create a new FAISS database:

1. **Use a different storage path**:
   ```bash
   python3 -m agents.rag.files_ragtool --action process --storage ./db_faiss
   ```

2. **Update your configuration** to point to the new path if needed.

## Usage

### No Code Changes Required

The RagTool API remains **exactly the same**. All existing code will work without modifications:

```python
from agents.rag.files_ragtool import FilesRagTool
from agents.utils.config import get_rag_config

# Initialize (now uses FAISS internally)
rag_config = get_rag_config()
processor = FilesRagTool(rag_config, storage_path="./db")

# Process files (same as before)
success = processor.initialize_ragtool_and_process_files(
    ["data/raw/VATBOOK1.txt"],
    force_reprocess=False
)

# Load existing database (same as before)
rag_tool = processor.get_rag_tool()

# Search (same as before)
results = processor.search("What is VAT?")
```

### CLI Commands

All CLI commands remain the same:

```bash
# Process all files in data/raw
python3 -m agents.rag.files_ragtool --action process

# Force reprocess all files
python3 -m agents.rag.files_ragtool --action process --force

# Add a new file
python3 -m agents.rag.files_ragtool --action add --file path/to/document.pdf

# Add a URL
python3 -m agents.rag.files_ragtool --action add-url --url https://example.com

# List processed files
python3 -m agents.rag.files_ragtool --action list

# Reset database
python3 -m agents.rag.files_ragtool --action reset
```

## Railway Deployment

FAISS works perfectly on Railway with **no additional configuration**:

1. **Storage**: FAISS uses the local `./db` directory
2. **No External Service**: No database service to configure
3. **Persistent Volume**: Add a volume mount to `/db` for persistence across deployments

### Railway Configuration

Add to your `railway.json` or Railway dashboard:

```json
{
  "volumes": [
    {
      "mount": "/app/db",
      "name": "faiss-vector-db"
    }
  ]
}
```

## Performance Comparison

### FAISS vs ChromaDB

| Feature | FAISS | ChromaDB |
|---------|-------|----------|
| Setup Complexity | Simple (library) | Moderate (server/embedded) |
| Memory Usage | Low | Moderate |
| Disk Space | Efficient | Moderate |
| Search Speed | Very Fast | Fast |
| Deployment | Easy | Moderate |
| Cost | Free | Free |
| Railway Compatible | ✅ Excellent | ⚠️ Requires configuration |

### Expected Performance

For your use case (4 documents + future growth):
- **Indexing Time**: ~1-5 seconds per document
- **Search Time**: < 100ms per query
- **Disk Usage**: ~1-10 MB for 4 documents
- **Memory**: ~50-200 MB

## Troubleshooting

### Issue: "No module named 'faiss'"

**Solution**: Install the FAISS package
```bash
pip install faiss-cpu>=1.7.4
# or for GPU support (if available)
pip install faiss-gpu>=1.7.4
```

### Issue: Database not found after restart

**Solution**: Ensure the `./db` directory is:
1. Not in `.gitignore` (or use Railway volumes)
2. Has write permissions
3. Mounted as a volume on Railway

### Issue: Old ChromaDB causing conflicts

**Solution**: Reset or remove old database
```bash
rm -rf ./db
python3 -m agents.rag.files_ragtool --action process
```

### Issue: Import errors from crewai_tools

**Solution**: Update crewai-tools to latest version
```bash
pip install --upgrade crewai-tools
```

## Verification

Test that FAISS is working correctly:

```python
from agents.rag.files_ragtool import FilesRagTool
from agents.utils.config import get_rag_config

# Initialize
rag_config = get_rag_config()
processor = FilesRagTool(rag_config)

# Test
print("✅ FAISS configuration loaded successfully!")
print(f"Storage path: {processor.get_storage_path()}")
```

## Additional Resources

- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [CrewAI RagTool Docs](https://docs.crewai.com/en/tools/ai-ml/ragtool)
- [Railway Documentation](https://docs.railway.app/)

## Support

If you encounter issues:
1. Check this migration guide
2. Review the troubleshooting section
3. Verify dependencies are correctly installed
4. Check Railway logs for deployment issues

## Future Considerations

### Scaling Beyond FAISS

If your dataset grows significantly (10,000+ documents), consider:
- **Qdrant**: Open-source, self-hosted, more features
- **Pinecone**: Managed service, scales automatically (paid)
- **Weaviate**: Open-source, advanced features

However, for small-to-medium datasets (< 10,000 documents), **FAISS is the optimal choice**.

---

**Last Updated**: November 2024
**Version**: 1.0

