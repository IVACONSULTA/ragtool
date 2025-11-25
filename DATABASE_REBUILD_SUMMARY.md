# Database Rebuild Options - Quick Summary

## 🎯 Three Ways to Rebuild Database on Cloud Run

### Option 1: Cloud Run Job ⭐ RECOMMENDED

**One command to set up and run**:

```bash
./scripts/run_rebuild_job.sh
```

**What it does**:

- Creates a separate Cloud Run Job
- Rebuilds database without affecting running service
- **Automatically configures ALL environment variables** (CONFIG_SET, AGENT_ROLE, paths, etc.)
- **Automatically adds ALL secrets** (API keys from Secret Manager)
- Can be executed on-demand or scheduled
- No downtime for your service

**Configured automatically**:

- ✅ All LLM model configurations (Gemini, OpenAI, Groq)
- ✅ RAG data path and database path
- ✅ LangSmith tracing settings
- ✅ All API keys from Secret Manager

**When to use**: Production, scheduled maintenance, CI/CD

---

### Option 2: Environment Variable Flag

**Deploy with rebuild**:

```bash
# Enable rebuild
gcloud run services update ragtool-agent \
  --region=europe-west1 \
  --set-env-vars=REBUILD_DATABASE=true

# After rebuild, disable it
gcloud run services update ragtool-agent \
  --region=europe-west1 \
  --set-env-vars=REBUILD_DATABASE=false
```

**What it does**:

- Rebuilds database on container startup
- Service unavailable during rebuild (5-10 minutes)
- Simple but causes downtime

**When to use**: Quick updates, development

---

### Option 3: Local Rebuild

**Rebuild locally then deploy**:

```bash
# 1. Rebuild locally
python scripts/rebuild_database.py

# 2. Build and deploy
./scripts/build_and_push.sh
./scripts/deploy_cloud_run.sh
```

**What it does**:

- Rebuilds database on your machine
- Includes database in Docker image
- No rebuild time on Cloud Run

**When to use**: Development, testing

---

## 📊 Quick Comparison

| Method        | Downtime    | Setup  | Best For    |
| ------------- | ----------- | ------ | ----------- |
| Cloud Run Job | ✅ None     | Medium | Production  |
| Env Variable  | ❌ 5-10 min | Easy   | Quick fixes |
| Local Rebuild | ✅ None     | Easy   | Development |

---

## 🚀 Files Created

1. **`scripts/rebuild_database.py`** - Python script to rebuild database
2. **`scripts/run_rebuild_job.sh`** - Deploy and run Cloud Run Job
3. **`scripts/entrypoint.sh`** - Startup script with rebuild check
4. **`Dockerfile.rebuild`** - Dockerfile for rebuild job
5. **`Dockerfile.flexible`** - Dockerfile with rebuild support
6. **`DATABASE_REBUILD_GUIDE.md`** - Complete documentation

---

## 💡 Recommended Workflow

### For Production:

1. **Initial setup** (once):

   ```bash
   ./scripts/run_rebuild_job.sh
   ```

2. **When you add new documents**:

   ```bash
   # Just execute the existing job
   gcloud run jobs execute ragtool-rebuild-db --region=europe-west1
   ```

3. **Schedule weekly rebuilds** (optional):
   ```bash
   gcloud scheduler jobs create http ragtool-weekly-rebuild \
     --location=europe-west1 \
     --schedule="0 2 * * 0" \
     --uri="https://europe-west1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/ivaconsulta/jobs/ragtool-rebuild-db:run" \
     --http-method=POST \
     --oauth-service-account-email=237915647765-compute@developer.gserviceaccount.com
   ```

---

## ✅ Next Steps

1. Review `DATABASE_REBUILD_GUIDE.md` for detailed instructions
2. Choose the method that fits your workflow
3. Test locally first: `python scripts/rebuild_database.py`
4. Deploy to Cloud Run using your chosen method

---

**Questions?** Check `DATABASE_REBUILD_GUIDE.md` for troubleshooting and best practices.
