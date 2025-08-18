#!/bin/bash

# PlotTwist Cloud Run Deployment Script
# Usage: ./deploy.sh [PROJECT_ID]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏗️  PlotTwist Cloud Run Deployment${NC}"
echo "=================================="

# Get project ID
if [ -z "$1" ]; then
    PROJECT_ID=$(gcloud config get-value project)
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}❌ No project ID provided and no default project set${NC}"
        echo "Usage: ./deploy.sh [PROJECT_ID]"
        exit 1
    fi
else
    PROJECT_ID=$1
fi

echo -e "${YELLOW}📋 Using project: ${PROJECT_ID}${NC}"

# Set variables
SERVICE_NAME="plottwist"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo -e "${YELLOW}🔧 Building and pushing Docker image...${NC}"

# Build and push the image (target AMD64 for Cloud Run compatibility)
docker build --platform linux/amd64 -t ${IMAGE_NAME}:latest .
docker push ${IMAGE_NAME}:latest

echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"

# Deploy to Cloud Run
gcloud run deploy ${SERVICE_NAME} \
    --image=${IMAGE_NAME}:latest \
    --project=${PROJECT_ID} \
    --region=${REGION} \
    --platform=managed \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --max-instances=10 \
    --port=8080 \
    --set-env-vars="ENVIRONMENT=production" \
    --timeout=300

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --project=${PROJECT_ID} --format="value(status.url)")

echo ""
echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${GREEN}🌐 Service URL: ${SERVICE_URL}${NC}"
echo -e "${GREEN}🏥 Health check: ${SERVICE_URL}/health${NC}"
echo -e "${GREEN}📊 API endpoint: ${SERVICE_URL}/create-report${NC}"

echo ""
echo -e "${BLUE}🧪 Test your deployment:${NC}"
echo "curl -X POST \"${SERVICE_URL}/create-report\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"property_info\": \"263 N Harvard St, Boston, MA\"}'"

echo ""
echo -e "${YELLOW}💡 For the hackathon demo, visit: ${SERVICE_URL}${NC}" 