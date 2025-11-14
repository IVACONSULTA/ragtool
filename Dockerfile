# Dockerfile.ragtool
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    APP_HOME=/

WORKDIR ${APP_HOME}

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# copy dependency manifests early to leverage Docker cache
COPY requirements.txt requirements-dev.txt ./

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-dev.txt

# Include any additional packages needed solely by RagTool here if they
# are not part of requirements.txt (e.g. fastapi/uvicorn).

COPY . .

EXPOSE 8080

# Replace "agents.dspy_assistant.ragtool_service:app" with the actual module
# and application object that serves RagTool's HTTP API.
CMD ["python", "agents/crewai/crew_agent_server_with_guard_rails.py"]
