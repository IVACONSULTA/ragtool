# Database Rebuild Guide for Cloud Run

This guide explains how to rebuild the RAG vector database when deploying to Google Cloud Run.

## 🎯 When to Rebuild the Database

Rebuild the database when:

- ✅ Adding new documents to `data/raw/`
- ✅ Updating existing documents
- ✅ Changing embedding models
- ✅ Changing chunk size or overlap settings
- ✅ Fixing database corruption

## 🔧 Three Methods to Rebuild

### Method 1: Cloud Run Job (Recommended) ⭐

**Best for**: One-time rebuilds, scheduled maintenance, CI/CD pipelines

**Advantages**:

- ✅ Doesn't affect running service
- ✅ Can run on-demand or scheduled
- ✅ Separate resource allocation
- ✅ Easy to monitor and debug

#### Setup and Run

```bash
# 1. Build and deploy the rebuild job
./scripts/run_rebuild_job.sh

# This will:
# - Build Docker image for rebuild
# - Push to Artifact Registry
# - Create/update Cloud Run Job with ALL environment variables and secrets
# - Configure: CONFIG_SET, AGENT_ROLE, RAG_DATA_PATH, CHROMA_DB_PATH
# - Add secrets: OPENAI_API_KEY, GEMINI_API_KEY, LANGSMITH_API_KEY, etc.
# - Optionally execute immediately
```

**Environment Variables Configured**:

- `CONFIG_SET=GEMINI_2.5_FLASH`
- `AGENT_ROLE=VAT_AGENT`
- `RAG_DATA_PATH=./data/raw`
- `CHROMA_DB_PATH=./db`
- `LANGSMITH_PROJECT=rag-ivaconsulta-dev`
- `CREWAI_TRACING_ENABLED=true`
- `LANGCHAIN_TRACING_V2=true`
- All model configuration variables (GEMINI, GROQ, OPENAI)

**Secrets Configured**:

- `OPENAI_API_KEY` (from Secret Manager)
- `EMBEDDINGS_GOOGLE_API_KEY` (from Secret Manager)
- `GOOGLE_API_KEY` (from Secret Manager)
- `GEMINI_API_KEY` (from Secret Manager)
- `GROQ_API_KEY` (from Secret Manager)
- `LANGSMITH_API_KEY` (from Secret Manager)
- `API_KEY` (from Secret Manager)

#### Manual Execution

```bash
# Execute the rebuild job
gcloud run jobs execute ragtool-rebuild-db --region=europe-west1

# Monitor execution
gcloud run jobs executions list \
  --job=ragtool-rebuild-db \
  --region=europe-west1 \
  --limit=1

# View logs
EXECUTION=$(gcloud run jobs executions list \
  --job=ragtool-rebuild-db \
  --region=europe-west1 \
  --limit=1 \
  --format="value(metadata.name)")

gcloud run jobs executions logs read $EXECUTION --region=europe-west1
```

#### Schedule Regular Rebuilds

```bash
# Create Cloud Scheduler job to rebuild weekly
gcloud scheduler jobs create http ragtool-weekly-rebuild \
  --location=europe-west1 \
  --schedule="0 2 * * 0" \
  --uri="https://europe-west1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/ivaconsulta/jobs/ragtool-rebuild-db:run" \
  --http-method=POST \
  --oauth-service-account-email=237915647765-compute@developer.gserviceaccount.com
```

---

### Method 2: Environment Variable Flag

**Best for**: Deploying with rebuild as part of deployment

**Advantages**:

- ✅ Simple - just set an environment variable
- ✅ Integrated with deployment
- ✅ No separate job needed

**Disadvantages**:

- ❌ Increases startup time significantly (5-10 minutes)
- ❌ Service unavailable during rebuild
- ❌ Uses service resources

#### Setup

Use `Dockerfile.flexible` instead of regular `Dockerfile`:

```bash
# Build with flexible Dockerfile
docker build -f Dockerfile.flexible \
  -t europe-west1-docker.pkg.dev/ivaconsulta/ragtool/ragtool-agent:latest .

# Push
docker push europe-west1-docker.pkg.dev/ivaconsulta/ragtool/ragtool-agent:latest
```

#### Deploy with Rebuild

```bash
# Deploy new revision with rebuild flag
gcloud run services update ragtool-agent \
  --region=europe-west1 \
  --set-env-vars=REBUILD_DATABASE=true \
  --image=europe-west1-docker.pkg.dev/ivaconsulta/ragtool/ragtool-agent:latest

# After rebuild completes, deploy again without flag
gcloud run services update ragtool-agent \
  --region=europe-west1 \
  --set-env-vars=REBUILD_DATABASE=false
```

---

### Method 3: Local Rebuild + Deploy

**Best for**: Development, testing, small databases

**Advantages**:

- ✅ Full control over rebuild process
- ✅ Can test locally before deploying
- ✅ Fastest deployment (database pre-built)

**Disadvantages**:

- ❌ Requires local environment setup
- ❌ Larger Docker image size
- ❌ Must rebuild image after database changes

#### Steps

```bash
# 1. Rebuild database locally
python scripts/rebuild_database.py

# 2. Verify database was created
ls -lh db/

# 3. Build Docker image (includes new database)
./scripts/build_and_push.sh

# 4. Deploy to Cloud Run
./scripts/deploy_cloud_run.sh
```

---

## 📊 Comparison Matrix

| Method            | Downtime | Setup Complexity | Best For      | Cost   |
| ----------------- | -------- | ---------------- | ------------- | ------ |
| **Cloud Run Job** | None     | Medium           | Production    | Low    |
| **Env Variable**  | 5-10 min | Low              | Quick updates | Medium |
| **Local Rebuild** | None     | Low              | Development   | Low    |

## 🔍 Monitoring Rebuild Progress

### Check Job Status

```bash
# List recent executions
gcloud run jobs executions list \
  --job=ragtool-rebuild-db \
  --region=europe-west1 \
  --limit=5

# Get execution details
gcloud run jobs executions describe EXECUTION_NAME \
  --region=europe-west1
```

### View Logs

```bash
# Stream logs in real-time
gcloud run jobs executions logs tail EXECUTION_NAME \
  --region=europe-west1

# Read all logs
gcloud run jobs executions logs read EXECUTION_NAME \
  --region=europe-west1
```

### Check Service Logs (Method 2)

```bash
# Watch for rebuild messages
gcloud run services logs tail ragtool-agent \
  --region=europe-west1 | grep -i "rebuild\|database"
```

## 🚨 Troubleshooting

### Job Fails with Timeout

Increase timeout in job configuration:

```bash
gcloud run jobs update ragtool-rebuild-db \
  --region=europe-west1 \
  --task-timeout=60m
```

### Out of Memory

Increase memory allocation:

```bash
gcloud run jobs update ragtool-rebuild-db \
  --region=europe-west1 \
  --memory=4Gi
```

### Database Not Found After Rebuild

Check that paths match:

```bash
# Job environment variables should match service
gcloud run jobs describe ragtool-rebuild-db \
  --region=europe-west1 \
  --format="value(spec.template.spec.template.spec.containers[0].env)"
```

### Rebuild Takes Too Long

Optimize by:

1. Reducing chunk size
2. Processing fewer files
3. Using faster embedding model
4. Increasing CPU/memory

## 📝 Best Practices

### 1. Test Locally First

```bash
# Always test rebuild locally before running in Cloud
python scripts/rebuild_database.py
```

### 2. Backup Before Rebuild

```bash
# Export current database (if needed)
gcloud storage cp -r gs://your-bucket/db ./db-backup
```

### 3. Monitor Costs

```bash
# Check job execution costs
gcloud billing accounts list
```

### 4. Use Appropriate Method

- **Production**: Use Cloud Run Job
- **Development**: Use local rebuild
- **Emergency**: Use env variable method

### 5. Schedule Regular Rebuilds

```bash
# Weekly rebuild on Sundays at 2 AM
gcloud scheduler jobs create http ragtool-weekly-rebuild \
  --location=europe-west1 \
  --schedule="0 2 * * 0" \
  --uri="https://europe-west1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/ivaconsulta/jobs/ragtool-rebuild-db:run" \
  --http-method=POST \
  --oauth-service-account-email=237915647765-compute@developer.gserviceaccount.com
```

## 🎯 Quick Reference

### Rebuild with Job (Recommended)

```bash
./scripts/run_rebuild_job.sh
```

### Rebuild with Env Variable

```bash
gcloud run services update ragtool-agent \
  --region=europe-west1 \
  --set-env-vars=REBUILD_DATABASE=true
```

### Rebuild Locally

```bash
python scripts/rebuild_database.py
./scripts/build_and_push.sh
./scripts/deploy_cloud_run.sh
```

---

**Last Updated**: 2025-11-24  
**Version**: 1.0.0
