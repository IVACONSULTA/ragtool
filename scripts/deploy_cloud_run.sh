#!/bin/bash

# Deployment script for Google Cloud Run
# This script deploys the RagTool CrewAI RAG Agent to Cloud Run with proper configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-ivaconsulta}"
REGION="${GCP_REGION:-europe-west1}"
REPOSITORY="${GAR_REPOSITORY:-ragtool}"
IMAGE_NAME="${IMAGE_NAME:-ragtool-agent}"
SERVICE_NAME="${SERVICE_NAME:-ragtool-agent}"

# Image reference
IMAGE_REF="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:latest"

echo -e "${GREEN}🚀 Deploying RagTool CrewAI RAG Agent to Cloud Run${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo "Image: $IMAGE_REF"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI is not installed${NC}"
    exit 1
fi

# Set the project
gcloud config set project $PROJECT_ID

# Enable Cloud Run API if not already enabled
echo -e "${GREEN}📦 Enabling Cloud Run API...${NC}"
gcloud services enable run.googleapis.com --project=$PROJECT_ID

# Check if image exists
echo -e "${GREEN}🔍 Checking if Docker image exists...${NC}"
if ! gcloud artifacts docker images describe $IMAGE_REF &> /dev/null; then
    echo -e "${RED}❌ Error: Docker image not found: $IMAGE_REF${NC}"
    echo "Please build and push the image first using the GitHub Actions workflow"
    exit 1
fi

# Prompt for non-sensitive environment variables
echo -e "${YELLOW}📝 Configuration${NC}"
read -p "LangSmith Project (default: ivaconsulta-rag-tool): " LANGSMITH_PROJECT
LANGSMITH_PROJECT=${LANGSMITH_PROJECT:-ivaconsulta-rag-tool}

read -p "Agent Role (default: VAT_AGENT): " AGENT_ROLE
AGENT_ROLE=${AGENT_ROLE:-VAT_AGENT}

read -p "Container Port (default: 8080): " CONTAINER_PORT
CONTAINER_PORT=${CONTAINER_PORT:-8080}

read -p "Flask Environment (default: PROD): " FLASK_ENV
FLASK_ENV=${FLASK_ENV:-PROD}

read -p "Allow unauthenticated access? (y/n, default: y): " ALLOW_UNAUTH
ALLOW_UNAUTH=${ALLOW_UNAUTH:-y}

# Check if secrets exist
echo -e "${GREEN}🔐 Checking secrets...${NC}"
MISSING_SECRETS=()

# Required secrets
REQUIRED_SECRETS=("OPENAI_API_KEY" "LANGSMITH_API_KEY" "API_KEY")

# Optional secrets (for Gemini models)
OPTIONAL_SECRETS=("GEMINI_API_KEY")

for secret in "${REQUIRED_SECRETS[@]}"; do
    if ! gcloud secrets describe $secret --project=$PROJECT_ID &> /dev/null; then
        MISSING_SECRETS+=($secret)
    fi
done

# Build secrets flag
SECRETS_LIST=()
for secret in "${REQUIRED_SECRETS[@]}"; do
    if gcloud secrets describe $secret --project=$PROJECT_ID &> /dev/null; then
        SECRETS_LIST+=("$secret=$secret:latest")
    fi
done

# Add optional secrets if they exist
for secret in "${OPTIONAL_SECRETS[@]}"; do
    if gcloud secrets describe $secret --project=$PROJECT_ID &> /dev/null; then
        SECRETS_LIST+=("$secret=$secret:latest")
    fi
done

if [ ${#MISSING_SECRETS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Missing required secrets: ${MISSING_SECRETS[*]}${NC}"
    echo "Run ./scripts/setup_gcp_secrets.sh first to create them"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    SECRETS_FLAG=""
elif [ ${#SECRETS_LIST[@]} -gt 0 ]; then
    SECRETS_FLAG="--set-secrets=$(IFS=,; echo "${SECRETS_LIST[*]}")"
else
    SECRETS_FLAG=""
fi

# Build deployment command
DEPLOY_CMD="gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_REF \
    --region=$REGION \
    --platform=managed \
    --port=$CONTAINER_PORT \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300 \
    --max-instances=10 \
    --set-env-vars=\"FLASK_ENV=$FLASK_ENV,LANGSMITH_PROJECT=$LANGSMITH_PROJECT,AGENT_ROLE=$AGENT_ROLE\""

if [ -n "$SECRETS_FLAG" ]; then
    DEPLOY_CMD="$DEPLOY_CMD $SECRETS_FLAG"
fi

if [[ $ALLOW_UNAUTH =~ ^[Yy]$ ]]; then
    DEPLOY_CMD="$DEPLOY_CMD --allow-unauthenticated"
else
    DEPLOY_CMD="$DEPLOY_CMD --no-allow-unauthenticated"
fi

# Deploy
echo ""
echo -e "${GREEN}🚀 Deploying to Cloud Run...${NC}"
echo "Command: $DEPLOY_CMD"
echo ""

eval $DEPLOY_CMD

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo -e "${YELLOW}Service URL:${NC} $SERVICE_URL"
echo ""
echo -e "${YELLOW}Test the deployment:${NC}"
echo "  Health check: curl $SERVICE_URL/health"
echo "  Chat endpoint: curl -X POST $SERVICE_URL/chat \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -H 'X-API-Key: your-api-key' \\"
echo "    -d '{\"message\": \"Hello\", \"agent_type\": \"IVA_CONSULTA\"}'"
echo ""
echo -e "${YELLOW}View logs:${NC}"
echo "  gcloud run services logs read $SERVICE_NAME --region=$REGION"
echo ""

