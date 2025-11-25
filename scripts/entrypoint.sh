#!/bin/bash

# Entrypoint script for Cloud Run container
# Checks if database rebuild is requested before starting the server

set -e

echo "🚀 Starting RagTool Agent..."

# Check if rebuild is requested via environment variable
if [ "$REBUILD_DATABASE" = "true" ]; then
    echo "🔄 REBUILD_DATABASE=true detected"
    echo "🔨 Rebuilding vector database..."
    
    # Run rebuild script
    python scripts/rebuild_database.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Database rebuild complete"
    else
        echo "❌ Database rebuild failed"
        exit 1
    fi
fi

# Start the main application
echo "🚀 Starting Flask server..."
exec python agents/crewai/crew_agent_server_with_guard_rails.py

