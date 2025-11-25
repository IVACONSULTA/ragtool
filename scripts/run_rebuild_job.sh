#!/bin/bash

# Run Database Rebuild Job on Cloud Run
# This script builds a Cloud Run Job image, deploys it, and executes it
# Includes all environment variables and secrets from the main service

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-ivaconsulta}"
REGION="${GCP_REGION:-europe-west1}"
REPOSITORY="${GAR_REPOSITORY:-ragtool}"
JOB_NAME="ragtool-rebuild-db"
IMAGE_NAME="${JOB_NAME}"

# Image reference
FULL_IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}"
LATEST_TAG="${FULL_IMAGE_PATH}:latest"

echo -e "${GREEN}🔄 Database Rebuild Job for Cloud Run${NC}"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Job Name: $JOB_NAME"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI is not installed${NC}"
    exit 1
fi

# Set project
gcloud config set project $PROJECT_ID

# Configure Docker auth
echo -e "${BLUE}🔐 Configuring Docker authentication...${NC}"
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# Build the rebuild job image
echo -e "${BLUE}🔨 Building rebuild job Docker image...${NC}"
docker build -f Dockerfile.rebuild -t $LATEST_TAG .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful${NC}"

# Push image
echo -e "${BLUE}📤 Pushing image to Artifact Registry...${NC}"
docker push $LATEST_TAG

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to push image${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Image pushed successfully${NC}"

# Check if job exists
JOB_EXISTS=$(gcloud run jobs list --region=$REGION --format="value(name)" | grep -w "$JOB_NAME" || echo "")

if [ -z "$JOB_EXISTS" ]; then
    # Create new job with all environment variables and secrets
    echo -e "${BLUE}📝 Creating Cloud Run Job with full configuration...${NC}"
    
    gcloud run jobs create $JOB_NAME \
        --image=$LATEST_TAG \
        --region=$REGION \
        --memory=2Gi \
        --cpu=2 \
        --max-retries=1 \
        --task-timeout=30m \
        --set-env-vars="\
GEMINI_2.0_FLASH=GEMINI_2.0FLASH,\
GEMINI_2.5_FLASH=GEMINI_2.5FLASH,\
GROQ_LLAMA__LIGHT_MODEL=GROQ_LLAMA__LIGHT_MODEL,\
GROQ_LLAMA_MODEL=GROQ_LLAMA_MODEL,\
GROQ_MIXTRAL_MODEL=GROQ_MIXTRAL_MODEL,\
OPENAI_4o_MINI=OPENAI_4o_MINI,\
CONFIG_SET=GEMINI_2.5_FLASH,\
LANGSMITH_PROJECT=rag-ivaconsulta-dev,\
AGENT_ROLE=VAT_AGENT,\
RAG_DATA_PATH=./data/raw,\
CHROMA_DB_PATH=./db,\
VAT_AGENT=VAT_AGENT,\
SAP_AGENT=SAP_AGENT,\
CREWAI_TRACING_ENABLED=true,\
LANGCHAIN_TRACING_V2=true" \
        --set-secrets="\
OPENAI_API_KEY=OPENAI_API_KEY:latest,\
EMBEDDINGS_GOOGLE_API_KEY=EMBEDDINGS_GOOGLE_API_KEY:latest,\
GOOGLE_API_KEY=GOOGLE_API_KEY:latest,\
GEMINI_API_KEY=GEMINI_API_KEY:latest,\
GROQ_API_KEY=GROQ_API_KEY:latest,\
LANGSMITH_API_KEY=LANGSMITH_API_KEY:latest,\
API_KEY=API_KEY:latest"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Job created successfully${NC}"
    else
        echo -e "${RED}❌ Failed to create job${NC}"
        exit 1
    fi
else
    # Update existing job
    echo -e "${BLUE}🔄 Updating existing Cloud Run Job...${NC}"
    
    gcloud run jobs update $JOB_NAME \
        --image=$LATEST_TAG \
        --region=$REGION \
        --memory=2Gi \
        --cpu=2 \
        --max-retries=1 \
        --task-timeout=30m \
        --set-env-vars="\
GEMINI_2.0_FLASH=GEMINI_2.0FLASH,\
GEMINI_2.5_FLASH=GEMINI_2.5FLASH,\
GROQ_LLAMA__LIGHT_MODEL=GROQ_LLAMA__LIGHT_MODEL,\
GROQ_LLAMA_MODEL=GROQ_LLAMA_MODEL,\
GROQ_MIXTRAL_MODEL=GROQ_MIXTRAL_MODEL,\
OPENAI_4o_MINI=OPENAI_4o_MINI,\
CONFIG_SET=GEMINI_2.5_FLASH,\
LANGSMITH_PROJECT=rag-ivaconsulta-dev,\
AGENT_ROLE=VAT_AGENT,\
RAG_DATA_PATH=./data/raw,\
CHROMA_DB_PATH=./db,\
VAT_AGENT=VAT_AGENT,\
SAP_AGENT=SAP_AGENT,\
CREWAI_TRACING_ENABLED=true,\
LANGCHAIN_TRACING_V2=true" \
        --set-secrets="\
OPENAI_API_KEY=OPENAI_API_KEY:latest,\
EMBEDDINGS_GOOGLE_API_KEY=EMBEDDINGS_GOOGLE_API_KEY:latest,\
GOOGLE_API_KEY=GOOGLE_API_KEY:latest,\
GEMINI_API_KEY=GEMINI_API_KEY:latest,\
GROQ_API_KEY=GROQ_API_KEY:latest,\
LANGSMITH_API_KEY=LANGSMITH_API_KEY:latest,\
API_KEY=API_KEY:latest"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Job updated successfully${NC}"
    else
        echo -e "${RED}❌ Failed to update job${NC}"
        exit 1
    fi
fi

# Display job configuration
echo ""
echo -e "${BLUE}📋 Job Configuration:${NC}"
echo "  Memory: 2Gi"
echo "  CPU: 2"
echo "  Timeout: 30 minutes"
echo "  Max Retries: 1"
echo ""
echo -e "${BLUE}🔧 Environment Variables:${NC}"
echo "  CONFIG_SET: GEMINI_2.5_FLASH"
echo "  AGENT_ROLE: VAT_AGENT"
echo "  RAG_DATA_PATH: ./data/raw"
echo "  CHROMA_DB_PATH: ./db"
echo "  LANGSMITH_PROJECT: rag-ivaconsulta-dev"
echo "  CREWAI_TRACING_ENABLED: true"
echo "  LANGCHAIN_TRACING_V2: true"
echo ""
echo -e "${BLUE}🔐 Secrets Configured:${NC}"
echo "  ✅ OPENAI_API_KEY"
echo "  ✅ EMBEDDINGS_GOOGLE_API_KEY"
echo "  ✅ GOOGLE_API_KEY"
echo "  ✅ GEMINI_API_KEY"
echo "  ✅ GROQ_API_KEY"
echo "  ✅ LANGSMITH_API_KEY"
echo "  ✅ API_KEY"
echo ""

# Ask if user wants to execute now
read -p "Execute rebuild job now? (y/n): " EXECUTE_NOW

if [[ $EXECUTE_NOW =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🚀 Executing rebuild job...${NC}"
    echo ""
    
    # Execute the job
    EXECUTION=$(gcloud run jobs execute $JOB_NAME --region=$REGION --format="value(metadata.name)" 2>&1)
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to execute job${NC}"
        echo "$EXECUTION"
        exit 1
    fi
    
    echo -e "${YELLOW}⏳ Job execution started: $EXECUTION${NC}"
    echo ""
    echo -e "${BLUE}📊 Monitor execution:${NC}"
    echo "  gcloud run jobs executions describe $EXECUTION --region=$REGION"
    echo ""
    echo -e "${BLUE}📋 View logs:${NC}"
    echo "  gcloud run jobs executions logs read $EXECUTION --region=$REGION"
    echo ""
    
    # Wait for completion with progress indicator
    echo -e "${BLUE}⏳ Waiting for job to complete...${NC}"
    echo -e "${YELLOW}   This may take 5-10 minutes depending on database size${NC}"
    echo ""
    
    # Poll for completion
    MAX_WAIT=1800  # 30 minutes
    ELAPSED=0
    POLL_INTERVAL=10
    
    while [ $ELAPSED -lt $MAX_WAIT ]; do
        # Get execution status
        STATUS=$(gcloud run jobs executions describe $EXECUTION \
            --region=$REGION \
            --format="value(status.conditions[0].type)" 2>/dev/null || echo "")
        
        if [ "$STATUS" == "Completed" ]; then
            # Check if successful
            SUCCESS=$(gcloud run jobs executions describe $EXECUTION \
                --region=$REGION \
                --format="value(status.conditions[0].status)" 2>/dev/null)
            
            if [ "$SUCCESS" == "True" ]; then
                echo ""
                echo -e "${GREEN}✅ Job completed successfully!${NC}"
                
                # Show summary logs
                echo ""
                echo -e "${BLUE}📋 Job logs (last 30 lines):${NC}"
                gcloud run jobs executions logs read $EXECUTION --region=$REGION --limit=30
                
                echo ""
                echo -e "${GREEN}✅ Database rebuild complete!${NC}"
                exit 0
            else
                echo ""
                echo -e "${RED}❌ Job failed${NC}"
                
                # Show error logs
                echo ""
                echo -e "${BLUE}📋 Error logs:${NC}"
                gcloud run jobs executions logs read $EXECUTION --region=$REGION --limit=50
                exit 1
            fi
        fi
        
        # Show progress
        echo -ne "\r⏳ Waiting... ${ELAPSED}s elapsed"
        
        sleep $POLL_INTERVAL
        ELAPSED=$((ELAPSED + POLL_INTERVAL))
    done
    
    echo ""
    echo -e "${YELLOW}⚠️  Timeout waiting for job completion${NC}"
    echo "Check status manually:"
    echo "  gcloud run jobs executions describe $EXECUTION --region=$REGION"
    exit 1
else
    echo -e "${YELLOW}⏭️  Skipping execution${NC}"
    echo ""
    echo -e "${BLUE}📝 To execute later:${NC}"
    echo "  gcloud run jobs execute $JOB_NAME --region=$REGION"
    echo ""
    echo -e "${BLUE}📊 To list executions:${NC}"
    echo "  gcloud run jobs executions list --job=$JOB_NAME --region=$REGION"
    echo ""
    echo -e "${BLUE}📋 To view logs:${NC}"
    echo "  EXECUTION=\$(gcloud run jobs executions list --job=$JOB_NAME --region=$REGION --limit=1 --format='value(metadata.name)')"
    echo "  gcloud run jobs executions logs read \$EXECUTION --region=$REGION"
fi

echo ""
echo -e "${GREEN}✅ Done!${NC}"

