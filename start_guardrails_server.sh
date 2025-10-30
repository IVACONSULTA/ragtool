#!/bin/bash

# Start the CrewAI RAG Agent Server with Guardrails
# This script starts the server with IVA Consulta as the default agent

echo "🚀 Starting CrewAI RAG Agent Server with Guardrails..."
echo "🎯 Default Agent: IVA Consulta VAT Specialist"
echo "🛡️  EU AI Act Compliance: Enabled"
echo ""

# Change to the project directory
cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Start the server
python3 agents/crewai/crew_agent_server_with_guard_rails.py
