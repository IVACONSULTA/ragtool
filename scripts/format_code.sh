#!/bin/bash
# Auto-format Python code with Black and isort

set -e  # Exit on any error

# Check if we're in virtual environment, if not activate it
if [ -z "$VIRTUAL_ENV" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

echo "🔧 Formatting Python code with Black..."
python -m black agents/ tests/ files_manager_runner.py

echo "📋 Organizing imports with isort..."
python -m isort agents/ tests/ files_manager_runner.py

echo "🔍 Running flake8 checks..."
python -m flake8 agents/ tests/ files_manager_runner.py

echo "✅ Code formatting complete!"
