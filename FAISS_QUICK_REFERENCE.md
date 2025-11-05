# FAISS Vector Database - Quick Reference

## 🎯 What Changed?

The RagTool now uses **FAISS** (Facebook AI Similarity Search) instead of ChromaDB as the vector database. This provides:
- ✅ Better stability (no version upgrade issues)
- ✅ Free & local storage
- ✅ Railway-compatible deployment
- ✅ Same API - no code changes needed!

## 🚀 Quick Start

### 1. Update Dependencies
```bash
pip install -r requirements.txt
```

### 2. Reset & Rebuild Database (Recommended)
```bash
# Reset old database
python3 -m agents.rag.files_ragtool --action reset

# Rebuild with FAISS
python3 -m agents.rag.files_ragtool --action process --force
```

### 3. Verify It Works
```bash
python3 -c "from agents.rag.files_ragtool import FilesRagTool; from agents.utils.config import get_rag_config; print('✅ FAISS ready!')"
```

## 📋 Common Commands

```bash
# Process all files in data/raw
python3 -m agents.rag.files_ragtool --action process

# Force reprocess everything
python3 -m agents.rag.files_ragtool --action process --force

# Add a new file
python3 -m agents.rag.files_ragtool --action add --file path/to/file.pdf

# List processed files
python3 -m agents.rag.files_ragtool --action list

# Reset database
python3 -m agents.rag.files_ragtool --action reset
```

## 🔧 Railway Deployment

FAISS works out-of-the-box on Railway! For persistent storage, add a volume:

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

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| `No module named 'faiss'` | Run: `pip install faiss-cpu>=1.7.4` |
| Old database conflicts | Run: `rm -rf ./db && python3 -m agents.rag.files_ragtool --action process` |
| Database not found after restart | Ensure `./db` has write permissions or use Railway volumes |

## 💡 Key Points

- **No API Changes**: All existing code works as-is
- **Free**: No cost, no external services
- **Scalable**: Perfect for 4-100+ documents
- **Local**: Database stored in `./db` directory
- **Fast**: Optimized similarity search

## 📚 More Information

See [FAISS_MIGRATION_GUIDE.md](docs/FAISS_MIGRATION_GUIDE.md) for detailed documentation.

---

**Quick Help**: If something doesn't work, try:
1. `pip install --upgrade crewai-tools faiss-cpu`
2. `python3 -m agents.rag.files_ragtool --action reset`
3. `python3 -m agents.rag.files_ragtool --action process --force`

