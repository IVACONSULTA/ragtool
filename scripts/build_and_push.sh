#!/bin/bash

# Build and Push script for Google Artifact Registry
# This script builds the Docker image locally and pushes it to Artifact Registry

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-ivaconsulta}"
REGION="${GCP_REGION:-europe-west1}"
REPOSITORY="${GAR_REPOSITORY:-ragtool}"
IMAGE_NAME="${IMAGE_NAME:-ragtool-agent}"

# Image references
LOCAL_TAG="${IMAGE_NAME}:local"
FULL_IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}"
LATEST_TAG="${FULL_IMAGE_PATH}:latest"

echo -e "${GREEN}🐳 Docker Build and Push to Artifact Registry${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Repository: $REPOSITORY"
echo "Image Name: $IMAGE_NAME"
echo "Full Path: $LATEST_TAG"
echo ""
echo -e "${YELLOW}Note: This builds the RagTool CrewAI RAG Agent${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: Docker is not installed${NC}"
    echo "Install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

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

# Configure Docker to use gcloud as credential helper
echo -e "${BLUE}🔐 Configuring Docker authentication...${NC}"
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# Prompt for version tag
echo -e "${YELLOW}📝 Image Tagging${NC}"
read -p "Enter version tag (e.g., v1.0.0, or press Enter to generate a unique tag): " VERSION_TAG
if [ -z "$VERSION_TAG" ]; then
  VERSION_TAG=$(date +%Y%m%d%H%M%S)
  echo "No version tag provided. Using generated tag: $VERSION_TAG"
fi

VERSIONED_TAG="${FULL_IMAGE_PATH}:${VERSION_TAG}"
TAGS=("$VERSIONED_TAG")
echo -e "${GREEN}Using tag: $VERSION_TAG${NC}"
echo -e "${YELLOW}Note: Tag immutability is enabled - only using version tag${NC}"

# Build the Docker image with no cache to ensure fresh build
echo ""
echo -e "${BLUE}🔨 Building Docker image (no cache - fresh build)...${NC}"
docker build --no-cache --pull -t $LOCAL_TAG .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful${NC}"

# Tag the image
echo ""
echo -e "${BLUE}🏷️  Tagging image for Artifact Registry...${NC}"
for tag in "${TAGS[@]}"; do
    docker tag $LOCAL_TAG $tag
    echo -e "${GREEN}  Tagged: $tag${NC}"
done

# Push the image
echo ""
echo -e "${BLUE}📤 Pushing image to Artifact Registry...${NC}"
for tag in "${TAGS[@]}"; do
    echo -e "${YELLOW}  Pushing $tag...${NC}"
    docker push $tag
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✅ Successfully pushed: $tag${NC}"
    else
        echo -e "${RED}  ❌ Failed to push: $tag${NC}"
        exit 1
    fi
done

# Verify the image exists
echo ""
echo -e "${BLUE}🔍 Verifying image in Artifact Registry...${NC}"
if gcloud artifacts docker images describe $VERSIONED_TAG &> /dev/null; then
    echo -e "${GREEN}✅ Image verified in Artifact Registry${NC}"
    
    # Show image details
    echo ""
    echo -e "${BLUE}📋 Image Details:${NC}"
    gcloud artifacts docker images describe $VERSIONED_TAG \
        --format="table(tags,createTime,updateTime,imageSizeBytes)"
else
    echo -e "${YELLOW}⚠️  Could not verify image (may take a moment to appear)${NC}"
fi

echo ""
echo -e "${GREEN}✅ Build and push complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Deploy to Cloud Run:"
echo "   ./scripts/deploy_cloud_run.sh"
echo ""
echo "2. Or deploy manually:"
echo "   gcloud run deploy ragtool-agent \\"
echo "     --image=$VERSIONED_TAG \\"
echo "     --region=$REGION"
echo ""
echo "3. Test locally:"
echo "   docker pull $VERSIONED_TAG"
echo "   docker run -p 8080:8080 --env-file .env $VERSIONED_TAG"
echo ""
echo -e "${BLUE}📌 Image tag: $VERSION_TAG${NC}"
echo ""

