#!/bin/bash
# Script to push repository to Bitbucket
# Usage: ./scripts/push_to_bitbucket.sh <workspace-name> <repository-name>

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if arguments are provided
if [ $# -lt 2 ]; then
    echo -e "${RED}Error: Missing arguments${NC}"
    echo "Usage: $0 <workspace-name> <repository-name>"
    echo ""
    echo "Example: $0 myworkspace orchestrator-iva"
    exit 1
fi

WORKSPACE=$1
REPO_NAME=$2
BITBUCKET_URL="git@bitbucket.org:${WORKSPACE}/${REPO_NAME}.git"

echo -e "${YELLOW}🚀 Setting up Bitbucket remote...${NC}"
echo ""
echo "Workspace: ${WORKSPACE}"
echo "Repository: ${REPO_NAME}"
echo "Bitbucket URL: ${BITBUCKET_URL}"
echo ""

# Check if bitbucket remote already exists
if git remote get-url bitbucket >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Bitbucket remote already exists${NC}"
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote set-url bitbucket "$BITBUCKET_URL"
        echo -e "${GREEN}✅ Updated bitbucket remote${NC}"
    else
        echo -e "${YELLOW}Skipping remote update${NC}"
    fi
else
    echo -e "${GREEN}➕ Adding bitbucket remote...${NC}"
    git remote add bitbucket "$BITBUCKET_URL"
    echo -e "${GREEN}✅ Bitbucket remote added${NC}"
fi

echo ""
echo -e "${YELLOW}📋 Current remotes:${NC}"
git remote -v

echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Make sure the repository exists on Bitbucket!${NC}"
echo ""
echo "If you haven't created it yet:"
echo "1. Go to https://bitbucket.org/${WORKSPACE}/workspace/repositories"
echo "2. Click 'Create repository'"
echo "3. Name it: ${REPO_NAME}"
echo "4. Choose 'Private' or 'Public'"
echo "5. DO NOT initialize with README, .gitignore, or license"
echo "6. Click 'Create repository'"
echo ""
read -p "Has the repository been created on Bitbucket? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Please create the repository on Bitbucket first, then run this script again.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}📤 Pushing to Bitbucket...${NC}"

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: ${CURRENT_BRANCH}"

# Push to Bitbucket
echo ""
echo -e "${GREEN}Pushing ${CURRENT_BRANCH} branch to Bitbucket...${NC}"
git push -u bitbucket "${CURRENT_BRANCH}"

# Check if there are other branches to push
OTHER_BRANCHES=$(git branch -r | grep -v HEAD | grep -v "origin/${CURRENT_BRANCH}" | sed 's/origin\///' | xargs)
if [ -n "$OTHER_BRANCHES" ]; then
    echo ""
    echo -e "${YELLOW}Found other branches: ${OTHER_BRANCHES}${NC}"
    read -p "Do you want to push all branches? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Pushing all branches...${NC}"
        git push bitbucket --all
    fi
fi

# Check if there are tags to push
TAGS=$(git tag -l)
if [ -n "$TAGS" ]; then
    echo ""
    echo -e "${YELLOW}Found tags: ${TAGS}${NC}"
    read -p "Do you want to push all tags? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Pushing all tags...${NC}"
        git push bitbucket --tags
    fi
fi

echo ""
echo -e "${GREEN}✅ Successfully pushed to Bitbucket!${NC}"
echo ""
echo "Repository URL: https://bitbucket.org/${WORKSPACE}/${REPO_NAME}"
echo ""
echo -e "${YELLOW}Note: Your GitHub remote (origin) is still configured.${NC}"
echo "You can push to both remotes:"
echo "  - GitHub:   git push origin main"
echo "  - Bitbucket: git push bitbucket main"

