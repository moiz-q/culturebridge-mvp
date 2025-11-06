#!/bin/bash

# Rollback script for CultureBridge
# Usage: ./scripts/rollback.sh [staging|production]

set -e

ENVIRONMENT=${1:-staging}
AWS_REGION=${AWS_REGION:-us-east-1}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${RED}⚠️  Starting rollback for ${ENVIRONMENT}${NC}"

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo -e "${RED}❌ Invalid environment. Use 'staging' or 'production'${NC}"
    exit 1
fi

# Confirmation prompt for production
if [ "$ENVIRONMENT" == "production" ]; then
    read -p "Are you sure you want to rollback PRODUCTION? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo -e "${YELLOW}Rollback cancelled${NC}"
        exit 0
    fi
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

# Get previous task definitions
echo -e "${YELLOW}🔍 Finding previous task definitions...${NC}"

BACKEND_TASK_DEF=$(aws ecs describe-services \
    --cluster $ECS_CLUSTER \
    --services $ECS_BACKEND_SERVICE \
    --query 'services[0].deployments[1].taskDefinition' \
    --output text \
    --region $AWS_REGION)

FRONTEND_TASK_DEF=$(aws ecs describe-services \
    --cluster $ECS_CLUSTER \
    --services $ECS_FRONTEND_SERVICE \
    --query 'services[0].deployments[1].taskDefinition' \
    --output text \
    --region $AWS_REGION)

if [ "$BACKEND_TASK_DEF" == "None" ] || [ "$FRONTEND_TASK_DEF" == "None" ]; then
    echo -e "${RED}❌ No previous deployment found to rollback to${NC}"
    exit 1
fi

echo -e "${YELLOW}Backend task definition: $BACKEND_TASK_DEF${NC}"
echo -e "${YELLOW}Frontend task definition: $FRONTEND_TASK_DEF${NC}"

# Rollback backend service
echo -e "${YELLOW}🔄 Rolling back backend service...${NC}"
aws ecs update-service \
    --cluster $ECS_CLUSTER \
    --service $ECS_BACKEND_SERVICE \
    --task-definition $BACKEND_TASK_DEF \
    --force-new-deployment \
    --region $AWS_REGION \
    > /dev/null

# Rollback frontend service
echo -e "${YELLOW}🔄 Rolling back frontend service...${NC}"
aws ecs update-service \
    --cluster $ECS_CLUSTER \
    --service $ECS_FRONTEND_SERVICE \
    --task-definition $FRONTEND_TASK_DEF \
    --force-new-deployment \
    --region $AWS_REGION \
    > /dev/null

# Wait for rollback to complete
echo -e "${YELLOW}⏳ Waiting for rollback to complete...${NC}"
aws ecs wait services-stable \
    --cluster $ECS_CLUSTER \
    --services $ECS_BACKEND_SERVICE $ECS_FRONTEND_SERVICE \
    --region $AWS_REGION

# Verify rollback
echo -e "${YELLOW}🧪 Verifying rollback...${NC}"
if [ "$ENVIRONMENT" == "production" ]; then
    HEALTH_URL="https://culturebridge.com/health"
else
    HEALTH_URL="https://staging.culturebridge.com/health"
fi

sleep 10
if curl -f -s $HEALTH_URL > /dev/null; then
    echo -e "${GREEN}✅ Rollback completed successfully${NC}"
    echo -e "${GREEN}🌐 Application URL: ${HEALTH_URL%/health}${NC}"
else
    echo -e "${RED}❌ Health check failed after rollback${NC}"
    exit 1
fi
