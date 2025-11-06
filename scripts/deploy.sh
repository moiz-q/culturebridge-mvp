#!/bin/bash

# Deployment script for CultureBridge
# Usage: ./scripts/deploy.sh [staging|production]

set -e

ENVIRONMENT=${1:-staging}
AWS_REGION=${AWS_REGION:-us-east-1}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting deployment to ${ENVIRONMENT}${NC}"

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo -e "${RED}❌ Invalid environment. Use 'staging' or 'production'${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured${NC}"
    exit 1
fi

# Set environment-specific variables
if [ "$ENVIRONMENT" == "production" ]; then
    ECS_CLUSTER="culturebridge-cluster"
    ECS_BACKEND_SERVICE="culturebridge-backend"
    ECS_FRONTEND_SERVICE="culturebridge-frontend"
else
    ECS_CLUSTER="staging-culturebridge-cluster"
    ECS_BACKEND_SERVICE="staging-culturebridge-backend"
    ECS_FRONTEND_SERVICE="staging-culturebridge-frontend"
fi

# Get ECR repository URLs
echo -e "${YELLOW}📦 Getting ECR repository URLs...${NC}"
BACKEND_REPO=$(aws ecr describe-repositories --repository-names culturebridge/backend --query 'repositories[0].repositoryUri' --output text --region $AWS_REGION)
FRONTEND_REPO=$(aws ecr describe-repositories --repository-names culturebridge/frontend --query 'repositories[0].repositoryUri' --output text --region $AWS_REGION)

# Login to ECR
echo -e "${YELLOW}🔐 Logging in to ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $BACKEND_REPO

# Build and push backend
echo -e "${YELLOW}🏗️  Building backend image...${NC}"
cd backend
docker build -t $BACKEND_REPO:latest -t $BACKEND_REPO:$(git rev-parse --short HEAD) .
echo -e "${YELLOW}📤 Pushing backend image...${NC}"
docker push $BACKEND_REPO:latest
docker push $BACKEND_REPO:$(git rev-parse --short HEAD)
cd ..

# Build and push frontend
echo -e "${YELLOW}🏗️  Building frontend image...${NC}"
cd frontend
docker build -t $FRONTEND_REPO:latest -t $FRONTEND_REPO:$(git rev-parse --short HEAD) .
echo -e "${YELLOW}📤 Pushing frontend image...${NC}"
docker push $FRONTEND_REPO:latest
docker push $FRONTEND_REPO:$(git rev-parse --short HEAD)
cd ..

# Run database migrations
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
cd backend
pip install alembic psycopg2-binary > /dev/null 2>&1
alembic upgrade head
cd ..

# Update ECS services
echo -e "${YELLOW}🔄 Updating ECS services...${NC}"
aws ecs update-service \
    --cluster $ECS_CLUSTER \
    --service $ECS_BACKEND_SERVICE \
    --force-new-deployment \
    --region $AWS_REGION \
    > /dev/null

aws ecs update-service \
    --cluster $ECS_CLUSTER \
    --service $ECS_FRONTEND_SERVICE \
    --force-new-deployment \
    --region $AWS_REGION \
    > /dev/null

# Wait for services to stabilize
echo -e "${YELLOW}⏳ Waiting for services to stabilize (this may take a few minutes)...${NC}"
aws ecs wait services-stable \
    --cluster $ECS_CLUSTER \
    --services $ECS_BACKEND_SERVICE $ECS_FRONTEND_SERVICE \
    --region $AWS_REGION

# Run smoke tests
echo -e "${YELLOW}🧪 Running smoke tests...${NC}"
if [ "$ENVIRONMENT" == "production" ]; then
    HEALTH_URL="https://culturebridge.com/health"
else
    HEALTH_URL="https://staging.culturebridge.com/health"
fi

sleep 10
if curl -f -s $HEALTH_URL > /dev/null; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Deployment to ${ENVIRONMENT} completed successfully!${NC}"
echo -e "${GREEN}🌐 Application URL: ${HEALTH_URL%/health}${NC}"
