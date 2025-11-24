# Cloud Run Port Configuration Fix

## Problem Identified

The deployment was failing with the error:

```
The user-provided container failed to start and listen on the port defined provided by the PORT=8001 environment variable
```

## Root Cause

There was a **port mismatch** between different configuration files:

1. **Dockerfile**: Was set to `PORT=8080` and `EXPOSE 8080`
2. **google-cloud-service.yml**: Expected container to listen on `containerPort: 8001`
3. **Python server**: Correctly reads from `PORT` environment variable (defaults to 8001)

Cloud Run was setting `PORT=8001` in the environment, but the Dockerfile was overriding it with `PORT=8080`, causing the container to listen on the wrong port.

## Changes Made

### 1. Dockerfile

**File**: `/Users/macnolo/Desktop/Code/RagIvaconsulta/Dockerfile`

**Changed**:

- Line 6: `PORT=8080` → `PORT=8001`
- Line 29: `EXPOSE 8080` → `EXPOSE 8001`

### 2. Deploy Script

**File**: `/Users/macnolo/Desktop/Code/RagIvaconsulta/scripts/deploy_cloud_run.sh`

**Changed**:

- Line 60-61: Default container port from `8080` to `8001`

### 3. Setup Script

**File**: `/Users/macnolo/Desktop/Code/RagIvaconsulta/scripts/setup_gcp_secrets.sh`

**Changed**:

- Line 137: Documentation updated to show `--port=8001`

## Verification

All configuration files are now optimized for Cloud Run:

- ✅ Dockerfile: `PORT=8001`, `EXPOSE 8001`
- ✅ google-cloud-service.yml:
  - `containerPort: 8001`
  - `minScale: 1` (always-warm instance)
  - `cpu: 2000m` (increased for faster init)
  - `memory: 1Gi` (increased for RAG database)
- ✅ Python server: Reads `PORT` env var (defaults to 8001)
- ✅ Startup probe: Checks `tcpSocket.port: 8001`

## Next Steps

### 1. Rebuild the Docker Image

You need to rebuild and push the Docker image with the corrected port configuration:

```bash
./scripts/build_and_push.sh
```

This will:

- Build a fresh Docker image with `PORT=8001`
- Tag it with a new version
- Push it to Google Artifact Registry

### 2. Redeploy to Cloud Run

After the new image is pushed, deploy it:

```bash
./scripts/deploy_cloud_run.sh
```

Or use the YAML configuration directly:

```bash
gcloud run services replace google-cloud-service.yml --region=europe-west1
```

### 3. Monitor the Deployment

Check the logs to verify the container starts successfully:

```bash
gcloud run services logs read ragtool-agent --region=europe-west1 --limit=50
```

You should see:

```
🚀 Starting CrewAI RAG Agent Server with Guardrails...
📍 Server will be available on port: 8001
✅ Starting Flask app on host=0.0.0.0, port=8001, debug=False
✅ Server is now listening and ready for healthchecks!
```

### 4. Test the Health Endpoint

Once deployed, test the health endpoint:

```bash
SERVICE_URL=$(gcloud run services describe ragtool-agent --region=europe-west1 --format='value(status.url)')
curl $SERVICE_URL/health
```

Expected response:

```json
{
  "status": "healthy" or "initializing",
  "initialization_status": "...",
  "server": "CrewAI RAG Agent Server",
  "version": "1.0.0"
}
```

## Technical Details

### Why This Matters

Cloud Run:

1. Sets the `PORT` environment variable (in your case, to `8001`)
2. Expects the container to listen on that port
3. Routes traffic to that port
4. Uses startup/liveness probes on that port

When the Dockerfile hardcoded `PORT=8080`, it created a conflict:

- Cloud Run was checking port 8001 (as configured in YAML)
- Container was actually listening on port 8080 (from Dockerfile ENV)
- Health checks failed → deployment failed

### Startup Probe Configuration

Your `google-cloud-service.yml` includes a generous startup probe:

```yaml
startupProbe:
  timeoutSeconds: 10
  periodSeconds: 10
  failureThreshold: 60 # 60 * 10s = 10 minutes total
  tcpSocket:
    port: 8001
```

This allows up to 10 minutes for:

- RAG file processing
- Vector database initialization
- Agent setup
- LangSmith integration

### Keep-Warm Configuration

To eliminate cold starts and ensure instant responses:

```yaml
annotations:
  autoscaling.knative.dev/minScale: "1" # Always keep 1 instance running
  autoscaling.knative.dev/maxScale: "10" # Scale up to 10 under load

resources:
  limits:
    cpu: 2000m # Increased from 1000m
    memory: 1Gi # Increased from 512Mi
```

**Benefits**:

- ✅ No cold start delays (instant responses)
- ✅ RAG database stays loaded in memory
- ✅ Consistent sub-second response times
- ✅ Better user experience
- ✅ Faster initialization with increased resources

**Cost**: ~$15-30/month for always-on instance

## Troubleshooting

If deployment still fails after rebuilding:

### 1. Check Container Logs

```bash
gcloud run services logs read ragtool-agent --region=europe-west1 --limit=100
```

Look for:

- Port binding errors
- Python application startup errors
- RAG initialization issues

### 2. Verify Image

```bash
gcloud artifacts docker images describe \
  europe-west1-docker.pkg.dev/ivaconsulta/ragtool/ragtool-agent:latest
```

### 3. Test Locally

```bash
# Pull the image
docker pull europe-west1-docker.pkg.dev/ivaconsulta/ragtool/ragtool-agent:latest

# Run locally with port 8001
docker run -p 8001:8001 \
  --env-file .env \
  europe-west1-docker.pkg.dev/ivaconsulta/ragtool/ragtool-agent:latest

# Test in another terminal
curl http://localhost:8001/health
```

### 4. Check Memory/CPU

If the container starts but crashes:

- Increase memory in `google-cloud-service.yml` (currently 512Mi)
- Increase CPU (currently 1000m)

### 5. Increase Startup Timeout

If initialization takes longer than 10 minutes:

- Increase `failureThreshold` in startup probe (currently 60)
- Or decrease `periodSeconds` (currently 10)

## Additional Notes

### Environment Variables

The `PORT` environment variable is now consistently set to `8001`:

- In Dockerfile (default)
- In google-cloud-service.yml (via Cloud Run)
- Read by Python server in `crew_agent_server_with_guard_rails.py`

### Background Initialization

Your server implements background initialization:

- Server starts immediately and responds to health checks
- Agent initialization happens in a background thread
- Health endpoint reports initialization status

This is excellent for Cloud Run startup probes!

### Port Consistency Across Environments

- **Local Development**: Port 8001 (from Dockerfile or .env)
- **Cloud Run**: Port 8001 (from google-cloud-service.yml)
- **Railway**: Port set by Railway (via PORT env var)

## Summary

✅ **Fixed**: Port mismatch between Dockerfile and Cloud Run configuration  
✅ **Action Required**: Rebuild and redeploy with corrected port configuration  
✅ **Expected Result**: Container will start successfully and pass health checks

The fix ensures that:

1. Docker container listens on port 8001
2. Cloud Run routes traffic to port 8001
3. Startup probe checks port 8001
4. All configurations are aligned

---

**Date**: 2025-11-21  
**Issue**: Container failed to start - port mismatch  
**Resolution**: Aligned all port configurations to 8001
