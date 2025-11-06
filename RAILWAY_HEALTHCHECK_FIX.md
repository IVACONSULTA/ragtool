# Railway Healthcheck Fix

## Problem Identified

The Railway healthcheck was failing with "service unavailable" because the application was doing heavy initialization (loading documents, creating embeddings, initializing ChromaDB) **before** the Flask server started listening on the PORT.

### Root Cause

In the original implementation (lines 60-298), the following heavy operations occurred at module import time:

1. **CustomLlm initialization** - Connects to OpenAI/Gemini APIs
2. **CustomRagTool initialization** - Loads documents, creates embeddings, initializes ChromaDB
3. **Crew initialization** - Initializes IVAConsultaCrew or SapCrew with all dependencies

This initialization could take 5-10+ minutes for large document sets. Railway's healthcheck started immediately after the build, but the Flask app didn't start listening on the PORT until AFTER all initialization completed. This caused Railway to timeout after 8m20s (configured timeout).

## Solution Implemented

Refactored the application to use **background initialization**:

1. **Server starts immediately** - Flask begins listening on PORT right away
2. **Initialization runs in background thread** - Heavy operations moved to `initialize_agents_background()` function
3. **Health endpoint reports status** - Returns initialization progress
4. **Chat endpoint checks readiness** - Returns 503 if not ready yet

### Key Changes

#### 1. Added Initialization State Management

```python
# Global initialization state
initialization_complete = False
initialization_error = None
initialization_status = "starting"

# Global variables for initialized components
custom_llm = None
custom_rag_tool = None
iva_consulta_crew = None
sap_crew = None
active_crew = None
langsmith_manager = None
```

#### 2. Created Background Initialization Function

Moved all heavy initialization logic into `initialize_agents_background()` function that:

- Runs in a separate thread
- Updates `initialization_status` at each stage
- Sets `initialization_complete = True` when done
- Captures errors in `initialization_error` if something fails

#### 3. Updated `/health` Endpoint

Now returns different statuses based on initialization state:

- **"initializing"** - Server is starting, agents not ready yet
- **"healthy"** - Initialization complete, ready to serve requests
- **"unhealthy"** - Initialization failed with error

Response includes:

```json
{
  "status": "initializing",
  "initialization_status": "initializing_rag",
  "initialization_complete": false,
  "timestamp": "2024-01-01T12:00:00",
  ...
}
```

#### 4. Updated `/chat` Endpoint

Added check at the beginning:

```python
if not initialization_complete:
    if initialization_error:
        return jsonify({
            "error": "Server initialization failed",
            "details": initialization_error,
            "status": "unhealthy"
        }), 503
    else:
        return jsonify({
            "error": "Server is still initializing. Please try again in a moment.",
            "initialization_status": initialization_status,
            "status": "initializing"
        }), 503
```

#### 5. Modified Main Block

```python
if __name__ == "__main__":
    # ... setup code ...

    # Start background initialization thread
    init_thread = threading.Thread(target=initialize_agents_background, daemon=True)
    init_thread.start()

    # Start Flask server immediately
    app.run(host="0.0.0.0", port=port, ...)
```

## Benefits

1. **Passes Railway Healthcheck** - Server responds to `/health` immediately
2. **Zero Downtime** - Server is available during initialization
3. **Better Monitoring** - Can track initialization progress via health endpoint
4. **Graceful Degradation** - Returns helpful error messages if not ready
5. **Production Ready** - Follows best practices for long-running initialization

## Testing

### Local Testing

```bash
# Start the server
python agents/crewai/crew_agent_server_with_guard_rails.py

# In another terminal, check health immediately
curl http://localhost:8001/health

# Should return:
# {"status": "initializing", "initialization_status": "initializing_rag", ...}

# Wait a few minutes, check again
curl http://localhost:8001/health

# Should return:
# {"status": "healthy", "initialization_complete": true, ...}
```

### Railway Deployment

After deploying to Railway:

1. Build completes successfully
2. Healthcheck starts immediately
3. `/health` endpoint responds with `"status": "initializing"`
4. Railway considers deployment healthy (200 status code)
5. Background initialization continues
6. After initialization completes, `/health` returns `"status": "healthy"`
7. `/chat` endpoint becomes available

## Railway Configuration

The `railway.json` configuration remains the same:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 500,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

The 500-second timeout is now more than sufficient since the server starts immediately.

## Initialization Stages

The `initialization_status` field tracks progress through these stages:

1. `"starting"` - Initial state
2. `"initializing_langsmith"` - Setting up LangSmith integration
3. `"initializing_llm"` - Initializing language model
4. `"initializing_rag"` - Loading documents and creating embeddings (slowest part)
5. `"initializing_crews"` - Setting up CrewAI agents
6. `"ready"` - Initialization complete
7. `"failed"` - Initialization encountered an error

## Rollback Plan

If issues arise, you can revert to the previous synchronous initialization by:

1. Moving the `initialize_agents_background()` function body back to module level
2. Removing the threading code from the main block
3. Reverting the health endpoint changes

However, this will bring back the original healthcheck timeout issue.

## Future Improvements

1. **Progress Percentage** - Add percentage completion to initialization status
2. **Estimated Time** - Provide estimated time remaining for initialization
3. **Caching** - Cache embeddings to speed up subsequent startups
4. **Lazy Loading** - Only initialize components when first requested
5. **Health Monitoring** - Continue monitoring health after initialization

## References

- [Railway Healthcheck Documentation](https://docs.railway.com/guides/healthchecks)
- Flask Threading: https://flask.palletsprojects.com/en/2.3.x/deploying/
- Background Tasks in Python: https://docs.python.org/3/library/threading.html
