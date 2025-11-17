#!/bin/bash

# Setup script for Google Cloud Secret Manager
# This script helps you create secrets in Google Secret Manager for your Orchestrator Agent

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-ivaconsulta}"
REGION="${GCP_REGION:-europe-west1}"
SERVICE_NAME="${SERVICE_NAME:-ragtool-agent}"

echo -e "${GREEN}🔐 Google Cloud Secret Manager Setup${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI is not installed${NC}"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  Not authenticated with gcloud. Please run: gcloud auth login${NC}"
    exit 1
fi

# Set the project
gcloud config set project $PROJECT_ID

# Enable Secret Manager API if not already enabled
echo -e "${GREEN}📦 Enabling Secret Manager API...${NC}"
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID

# Function to create or update a secret
create_secret() {
    local secret_name=$1
    local description=$2
    local is_sensitive=$3
    
    if gcloud secrets describe $secret_name --project=$PROJECT_ID &> /dev/null; then
        echo -e "${YELLOW}⚠️  Secret '$secret_name' already exists${NC}"
        read -p "Do you want to add a new version? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
    else
        echo -e "${GREEN}Creating secret: $secret_name${NC}"
        echo "$description" | gcloud secrets create $secret_name \
            --data-file=- \
            --project=$PROJECT_ID \
            --replication-policy="automatic" || true
    fi
    
    # Prompt for secret value
    if [ "$is_sensitive" = "true" ]; then
        echo -e "${YELLOW}Enter value for $secret_name (input will be hidden):${NC}"
        read -s secret_value
    else
        echo -e "${YELLOW}Enter value for $secret_name:${NC}"
        read secret_value
    fi
    
    if [ -z "$secret_value" ]; then
        echo -e "${YELLOW}⚠️  Skipping $secret_name (empty value)${NC}"
        return
    fi
    
    # Add secret version
    echo "$secret_value" | gcloud secrets versions add $secret_name \
        --data-file=- \
        --project=$PROJECT_ID
    
    echo -e "${GREEN}✅ Secret '$secret_name' created/updated${NC}"
    echo ""
}

# Function to grant Cloud Run service account access
grant_secret_access() {
    local secret_name=$1
    local service_account="${PROJECT_ID}@appspot.gserviceaccount.com"
    
    echo -e "${GREEN}Granting Cloud Run service account access to $secret_name...${NC}"
    gcloud secrets add-iam-policy-binding $secret_name \
        --member="serviceAccount:${service_account}" \
        --role="roles/secretmanager.secretAccessor" \
        --project=$PROJECT_ID || echo -e "${YELLOW}⚠️  Could not grant access (may already be granted)${NC}"
}

# Main setup
echo -e "${GREEN}Starting secret creation...${NC}"
echo ""

# Required secrets
create_secret "OPENAI_API_KEY" "OpenAI API key for the RagTool CrewAI RAG agent" "true"
create_secret "LANGSMITH_API_KEY" "LangSmith API key for tracing and monitoring" "true"
create_secret "API_KEY" "API authentication key for the RagTool service" "true"

# Optional secrets (for Gemini models)
echo ""
read -p "Do you want to set up GEMINI_API_KEY for Google Gemini models? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    create_secret "GEMINI_API_KEY" "Google Gemini API key for Gemini model support" "true"
fi

# Grant access to Cloud Run service account
echo -e "${GREEN}🔑 Granting Cloud Run service account access to secrets...${NC}"
SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"

for secret in OPENAI_API_KEY LANGSMITH_API_KEY API_KEY GEMINI_API_KEY; do
    if gcloud secrets describe $secret --project=$PROJECT_ID &> /dev/null; then
        grant_secret_access $secret
    fi
done

echo ""
echo -e "${GREEN}✅ Secret setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Deploy your Cloud Run service with secrets:"
echo "   gcloud run deploy $SERVICE_NAME \\"
echo "     --image=$REGION-docker.pkg.dev/$PROJECT_ID/ragtool/ragtool-agent:latest \\"
echo "     --region=$REGION \\"
echo "     --set-secrets=\"OPENAI_API_KEY=OPENAI_API_KEY:latest,LANGSMITH_API_KEY=LANGSMITH_API_KEY:latest,API_KEY=API_KEY:latest\" \\"
echo "     --set-env-vars=\"FLASK_ENV=PROD,LANGSMITH_PROJECT=ivaconsulta-rag-tool,AGENT_ROLE=VAT_AGENT,PORT=8080\""
echo ""
echo "2. Or use the deployment script: ./scripts/deploy_cloud_run.sh"
echo ""

