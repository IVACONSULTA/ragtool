#!/bin/bash
# Run the CrewAI agent server with guard rails

echo "🚀 Starting crew_agent_server_with_guard_rails.py..."

# Activate virtual environment if not already active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

# Run the agent server
python agents/crewai/crew_agent_server_with_guard_rails.py
#python agents/crewai/crew_agent_server.py


echo "☁️ CrewAI agent server stopped."