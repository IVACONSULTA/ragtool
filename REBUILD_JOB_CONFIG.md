# Rebuild Job Configuration Reference

## 🔧 Complete Configuration

The `run_rebuild_job.sh` script automatically configures the Cloud Run Job with **all** environment variables and secrets from your main service.

## 📋 Environment Variables

### LLM Model Configurations

```bash
GEMINI_2.0_FLASH=GEMINI_2.0FLASH
GEMINI_2.5_FLASH=GEMINI_2.5FLASH
GROQ_LLAMA__LIGHT_MODEL=GROQ_LLAMA__LIGHT_MODEL
GROQ_LLAMA_MODEL=GROQ_LLAMA_MODEL
GROQ_MIXTRAL_MODEL=GROQ_MIXTRAL_MODEL
OPENAI_4o_MINI=OPENAI_4o_MINI
```

### Active Configuration

```bash
CONFIG_SET=GEMINI_2.5_FLASH  # Which model to use
```

### Agent Configuration

```bash
AGENT_ROLE=VAT_AGENT          # Agent type
VAT_AGENT=VAT_AGENT           # VAT agent flag
SAP_AGENT=SAP_AGENT           # SAP agent flag
```

### Data Paths

```bash
RAG_DATA_PATH=./data/raw      # Source documents
CHROMA_DB_PATH=./db           # Vector database location
```

### Monitoring & Tracing

```bash
LANGSMITH_PROJECT=rag-ivaconsulta-dev
CREWAI_TRACING_ENABLED=true
LANGCHAIN_TRACING_V2=true
```

## 🔐 Secrets (from Secret Manager)

All secrets are automatically pulled from Google Cloud Secret Manager:

```bash
OPENAI_API_KEY=OPENAI_API_KEY:latest
EMBEDDINGS_GOOGLE_API_KEY=EMBEDDINGS_GOOGLE_API_KEY:latest
GOOGLE_API_KEY=GOOGLE_API_KEY:latest
GEMINI_API_KEY=GEMINI_API_KEY:latest
GROQ_API_KEY=GROQ_API_KEY:latest
LANGSMITH_API_KEY=LANGSMITH_API_KEY:latest
API_KEY=API_KEY:latest
```

**Note**: The `:latest` suffix means the job always uses the latest version of each secret.

## 💻 Resource Allocation

```yaml
Memory: 2Gi
CPU: 2 cores
Timeout: 30 minutes
Max Retries: 1
```

## 🎯 What This Means

When you run `./scripts/run_rebuild_job.sh`, the job will:

1. ✅ Use the **same LLM configuration** as your main service (Gemini 2.5 Flash)
2. ✅ Process files from the **same data directory** (`./data/raw`)
3. ✅ Save to the **same database location** (`./db`)
4. ✅ Use the **same API keys** (from Secret Manager)
5. ✅ Enable **same monitoring** (LangSmith tracing)

**Result**: The rebuild job runs in **exactly the same environment** as your main service, ensuring consistency.

## 🔄 Updating Configuration

### To Change Model Configuration

Edit `scripts/run_rebuild_job.sh` and modify the `CONFIG_SET` variable:

```bash
CONFIG_SET=OPENAI_4o_MINI  # Change to OpenAI
# or
CONFIG_SET=GROQ_LLAMA_MODEL  # Change to Groq
```

### To Change Data Paths

Edit the environment variables in the script:

```bash
RAG_DATA_PATH=./data/raw_sap  # Use SAP data
CHROMA_DB_PATH=./db_sap       # Use separate database
```

### To Add New Environment Variables

Add to the `--set-env-vars` section in the script:

```bash
--set-env-vars="\
EXISTING_VARS...,\
NEW_VAR=NEW_VALUE"
```

### To Add New Secrets

1. Create the secret in Secret Manager:

   ```bash
   echo -n "SECRET_VALUE" | gcloud secrets create NEW_SECRET \
     --project=ivaconsulta \
     --data-file=-
   ```

2. Add to the `--set-secrets` section:
   ```bash
   --set-secrets="\
   EXISTING_SECRETS...,\
   NEW_SECRET=NEW_SECRET:latest"
   ```

## 🔍 Verifying Configuration

After running the script, verify the job configuration:

```bash
# View all environment variables
gcloud run jobs describe ragtool-rebuild-db \
  --region=europe-west1 \
  --format="yaml(spec.template.spec.template.spec.containers[0].env)"

# View all secrets
gcloud run jobs describe ragtool-rebuild-db \
  --region=europe-west1 \
  --format="yaml(spec.template.spec.template.spec.containers[0].env)" | grep -A 2 "secretKeyRef"

# View resource limits
gcloud run jobs describe ragtool-rebuild-db \
  --region=europe-west1 \
  --format="yaml(spec.template.spec.template.spec.containers[0].resources)"
```

## 📊 Configuration Sync

The configuration is kept in sync with your main service (`google-cloud-service.yml`).

**Important**: If you update environment variables in your main service, remember to update them in `run_rebuild_job.sh` as well, or the rebuild job may use outdated configuration.

### Quick Sync Check

Compare configurations:

```bash
# Main service env vars
gcloud run services describe ragtool-agent \
  --region=europe-west1 \
  --format="value(spec.template.spec.containers[0].env[].name)" | sort

# Rebuild job env vars
gcloud run jobs describe ragtool-rebuild-db \
  --region=europe-west1 \
  --format="value(spec.template.spec.template.spec.containers[0].env[].name)" | sort
```

They should match!

## 🎉 Summary

Running `./scripts/run_rebuild_job.sh` creates a Cloud Run Job that:

- ✅ Has **identical configuration** to your main service
- ✅ Uses **same API keys** (automatically from Secret Manager)
- ✅ Processes **same data** (from `./data/raw`)
- ✅ Outputs to **same database** (to `./db`)
- ✅ Enables **same monitoring** (LangSmith tracing)

**No manual configuration needed!** Just run the script and it handles everything automatically. 🚀

---

**Last Updated**: 2025-11-24  
**Script**: `scripts/run_rebuild_job.sh`
