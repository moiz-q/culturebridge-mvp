#!/bin/bash

# Setup script for CI/CD pipeline
# This script configures GitHub Actions secrets and AWS resources

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔧 Setting up CI/CD pipeline${NC}"

# Check prerequisites
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install it first.${NC}"
    exit 1
fi

if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI not found. Please install it first.${NC}"
    exit 1
fi

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_REGION:-us-east-1}

echo -e "${YELLOW}AWS Account ID: $AWS_ACCOUNT_ID${NC}"
echo -e "${YELLOW}AWS Region: $AWS_REGION${NC}"

# Create IAM user for GitHub Actions
echo -e "${YELLOW}👤 Creating IAM user for GitHub Actions...${NC}"
aws iam create-user --user-name github-actions-culturebridge || echo "User already exists"

# Create and attach policy
cat > /tmp/github-actions-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecs:UpdateService",
        "ecs:DescribeServices",
        "ecs:DescribeTaskDefinition",
        "ecs:RegisterTaskDefinition"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:PassRole"
      ],
      "Resource": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/culturebridge-ecs-*"
    }
  ]
}
EOF

aws iam put-user-policy \
    --user-name github-actions-culturebridge \
    --policy-name GitHubActionsPolicy \
    --policy-document file:///tmp/github-actions-policy.json

# Create access keys
echo -e "${YELLOW}🔑 Creating access keys...${NC}"
ACCESS_KEYS=$(aws iam create-access-key --user-name github-actions-culturebridge --output json)
ACCESS_KEY_ID=$(echo $ACCESS_KEYS | jq -r '.AccessKey.AccessKeyId')
SECRET_ACCESS_KEY=$(echo $ACCESS_KEYS | jq -r '.AccessKey.SecretAccessKey')

# Set GitHub secrets
echo -e "${YELLOW}🔐 Setting GitHub secrets...${NC}"
gh secret set AWS_ACCESS_KEY_ID --body "$ACCESS_KEY_ID"
gh secret set AWS_SECRET_ACCESS_KEY --body "$SECRET_ACCESS_KEY"
gh secret set AWS_REGION --body "$AWS_REGION"

# Get database URLs from Secrets Manager
echo -e "${YELLOW}🗄️  Retrieving database URLs...${NC}"
STAGING_DB_URL=$(aws secretsmanager get-secret-value \
    --secret-id staging-culturebridge-db-url \
    --query SecretString \
    --output text | jq -r '.DATABASE_URL' 2>/dev/null || echo "")

PRODUCTION_DB_URL=$(aws secretsmanager get-secret-value \
    --secret-id culturebridge-db-url \
    --query SecretString \
    --output text | jq -r '.DATABASE_URL' 2>/dev/null || echo "")

if [ -n "$STAGING_DB_URL" ]; then
    gh secret set STAGING_DATABASE_URL --body "$STAGING_DB_URL"
fi

if [ -n "$PRODUCTION_DB_URL" ]; then
    gh secret set PRODUCTION_DATABASE_URL --body "$PRODUCTION_DB_URL"
fi

# Set up GitHub environments
echo -e "${YELLOW}🌍 Setting up GitHub environments...${NC}"
echo "Please manually configure the following in GitHub:"
echo "1. Go to Settings > Environments"
echo "2. Create 'staging' environment"
echo "3. Create 'production' environment with required reviewers"
echo "4. Add environment-specific secrets if needed"

echo -e "${GREEN}✅ CI/CD setup completed!${NC}"
echo -e "${YELLOW}⚠️  Remember to:${NC}"
echo "  - Configure GitHub environment protection rules"
echo "  - Add Snyk token if using security scanning"
echo "  - Set up notification webhooks (Slack, email, etc.)"
echo "  - Review and test the pipeline with a test deployment"

# Cleanup
rm /tmp/github-actions-policy.json
