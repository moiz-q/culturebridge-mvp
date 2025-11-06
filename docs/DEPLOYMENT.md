# CultureBridge Deployment Guide

This guide covers the complete deployment process for CultureBridge from infrastructure setup to production deployment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Infrastructure Setup](#infrastructure-setup)
3. [Application Deployment](#application-deployment)
4. [Post-Deployment](#post-deployment)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

- **AWS CLI** (v2.x): `aws --version`
- **Terraform** (v1.0+): `terraform --version`
- **Docker** (v20.x+): `docker --version`
- **GitHub CLI** (optional): `gh --version`
- **Node.js** (v18.x): `node --version`
- **Python** (v3.11+): `python --version`

### AWS Account Setup

1. Create AWS account or use existing
2. Configure AWS CLI:
   ```bash
   aws configure
   ```
3. Verify access:
   ```bash
   aws sts get-caller-identity
   ```

### Domain Setup

1. Register domain (e.g., culturebridge.com)
2. Create Route 53 hosted zone
3. Update domain nameservers to Route 53

## Infrastructure Setup

### Step 1: Create Terraform Backend

```bash
# Create S3 bucket for Terraform state
aws s3api create-bucket \
  --bucket culturebridge-terraform-state \
  --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket culturebridge-terraform-state \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket culturebridge-terraform-state \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name culturebridge-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### Step 2: Request SSL Certificate

```bash
# Request certificate
aws acm request-certificate \
  --domain-name culturebridge.com \
  --subject-alternative-names www.culturebridge.com \
  --validation-method DNS \
  --region us-east-1

# Note the certificate ARN from output
```

Validate the certificate:
1. Go to AWS Console > ACM
2. Click on the certificate
3. Add the CNAME records to Route 53
4. Wait for validation (usually 5-30 minutes)

### Step 3: Configure Terraform Variables

```bash
cd infrastructure/terraform

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

Update these values:
- `certificate_arn`: From Step 2
- `domain_name`: Your domain
- `aws_region`: Your preferred region

### Step 4: Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Review planned changes
terraform plan -out=tfplan

# Apply infrastructure
terraform apply tfplan
```

This will create:
- VPC with public/private subnets
- RDS PostgreSQL database
- ElastiCache Redis cluster
- S3 bucket for uploads
- ECS cluster
- Application Load Balancer
- CloudFront distribution
- ECR repositories
- Security groups
- IAM roles

**Note:** This takes approximately 15-20 minutes.

### Step 5: Update Application Secrets

```bash
# Get secret ARN
SECRET_ARN=$(terraform output -raw app_secrets_arn)

# Update secrets
aws secretsmanager update-secret \
  --secret-id $SECRET_ARN \
  --secret-string '{
    "JWT_SECRET_KEY": "your-secure-random-string-min-32-chars",
    "OPENAI_API_KEY": "sk-...",
    "STRIPE_SECRET_KEY": "sk_live_...",
    "STRIPE_WEBHOOK_SECRET": "whsec_...",
    "SMTP_USER": "your-smtp-username",
    "SMTP_PASSWORD": "your-smtp-password"
  }'
```

Generate secure JWT secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Application Deployment

### Option 1: Automated Deployment (Recommended)

#### Setup CI/CD

```bash
# Run setup script
chmod +x scripts/setup-ci.sh
./scripts/setup-ci.sh
```

#### Configure GitHub

1. Go to repository Settings > Environments
2. Create `staging` environment
3. Create `production` environment:
   - Add required reviewers
   - Set deployment branch to `main`

#### Deploy

```bash
# Deploy to staging
git checkout develop
git push origin develop

# Deploy to production
git checkout main
git merge develop
git push origin main
# Approve deployment in GitHub Actions UI
```

### Option 2: Manual Deployment

#### Build and Push Images

```bash
# Get ECR URLs
BACKEND_REPO=$(terraform output -raw ecr_backend_repository_url)
FRONTEND_REPO=$(terraform output -raw ecr_frontend_repository_url)

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $BACKEND_REPO

# Build and push backend
cd backend
docker build -t $BACKEND_REPO:latest .
docker push $BACKEND_REPO:latest
cd ..

# Build and push frontend
cd frontend
docker build -t $FRONTEND_REPO:latest .
docker push $FRONTEND_REPO:latest
cd ..
```

#### Run Database Migrations

```bash
# Get database URL
DB_URL=$(aws secretsmanager get-secret-value \
  --secret-id culturebridge-db-url \
  --query SecretString \
  --output text | jq -r '.DATABASE_URL')

# Run migrations
cd backend
export DATABASE_URL=$DB_URL
alembic upgrade head
cd ..
```

#### Update ECS Services

```bash
# Update backend
aws ecs update-service \
  --cluster culturebridge-cluster \
  --service culturebridge-backend \
  --force-new-deployment

# Update frontend
aws ecs update-service \
  --cluster culturebridge-cluster \
  --service culturebridge-frontend \
  --force-new-deployment

# Wait for deployment
aws ecs wait services-stable \
  --cluster culturebridge-cluster \
  --services culturebridge-backend culturebridge-frontend
```

### Using Deployment Script

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh production
```

## Post-Deployment

### Verify Deployment

```bash
# Check health endpoints
curl https://culturebridge.com/health
curl https://culturebridge.com/api/health

# Check ECS services
aws ecs describe-services \
  --cluster culturebridge-cluster \
  --services culturebridge-backend culturebridge-frontend
```

### Create Admin User

```bash
# Connect to backend container
TASK_ARN=$(aws ecs list-tasks \
  --cluster culturebridge-cluster \
  --service-name culturebridge-backend \
  --query 'taskArns[0]' \
  --output text)

# Execute command in container
aws ecs execute-command \
  --cluster culturebridge-cluster \
  --task $TASK_ARN \
  --container backend \
  --interactive \
  --command "/bin/bash"

# Inside container, create admin user
python -c "
from app.database import SessionLocal
from app.models.user import User
from app.utils.jwt_utils import hash_password

db = SessionLocal()
admin = User(
    email='admin@culturebridge.com',
    password_hash=hash_password('ChangeMe123!'),
    role='admin',
    is_active=True,
    email_verified=True
)
db.add(admin)
db.commit()
print('Admin user created')
"
```

### Configure Stripe Webhook

1. Go to Stripe Dashboard > Developers > Webhooks
2. Add endpoint: `https://culturebridge.com/api/payment/webhook`
3. Select events:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.refunded`
4. Copy webhook signing secret
5. Update in Secrets Manager

### Test Critical Flows

Run through these user journeys:

1. **User Registration:**
   - Sign up as client
   - Sign up as coach
   - Verify email functionality

2. **Profile Creation:**
   - Complete client profile with quiz
   - Complete coach profile
   - Upload profile photo

3. **Coach Discovery:**
   - Search for coaches
   - View coach profiles
   - Test AI matching

4. **Booking Flow:**
   - Select time slot
   - Complete payment (use Stripe test card)
   - Verify confirmation emails

5. **Community Features:**
   - Create forum post
   - Add comment
   - Bookmark resource

6. **Admin Dashboard:**
   - View analytics
   - Manage users
   - Moderate content

## Monitoring

### CloudWatch Dashboards

Create custom dashboard:

```bash
aws cloudwatch put-dashboard \
  --dashboard-name CultureBridge \
  --dashboard-body file://monitoring/dashboard.json
```

### Key Metrics to Monitor

- **Application:**
  - API latency (p50, p95, p99)
  - Error rate (4xx, 5xx)
  - Request count
  - Active users

- **Infrastructure:**
  - ECS CPU/Memory utilization
  - ALB target health
  - RDS connections and CPU
  - Redis memory and hit rate

- **Business:**
  - User registrations
  - Bookings created
  - Payments processed
  - Active sessions

### Set Up Alarms

```bash
# High error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name culturebridge-high-error-rate \
  --alarm-description "Alert when error rate exceeds 5%" \
  --metric-name 5XXError \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 50 \
  --comparison-operator GreaterThanThreshold

# High latency alarm
aws cloudwatch put-metric-alarm \
  --alarm-name culturebridge-high-latency \
  --alarm-description "Alert when p95 latency exceeds 500ms" \
  --metric-name TargetResponseTime \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 0.5 \
  --comparison-operator GreaterThanThreshold
```

### Log Analysis

```bash
# View recent backend logs
aws logs tail /ecs/culturebridge/backend --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/culturebridge/backend \
  --filter-pattern "ERROR"

# View specific time range
aws logs filter-log-events \
  --log-group-name /ecs/culturebridge/backend \
  --start-time $(date -d '1 hour ago' +%s)000
```

## Troubleshooting

### Common Issues

#### 1. ECS Tasks Not Starting

**Symptoms:** Tasks fail to start or immediately stop

**Diagnosis:**
```bash
# Check task status
aws ecs describe-tasks \
  --cluster culturebridge-cluster \
  --tasks <task-arn>

# Check logs
aws logs tail /ecs/culturebridge/backend --since 10m
```

**Common Causes:**
- Invalid environment variables
- Cannot pull Docker image from ECR
- Insufficient memory/CPU
- Database connection failure

**Solutions:**
- Verify secrets in Secrets Manager
- Check ECR permissions
- Increase task resources
- Verify security group rules

#### 2. Database Connection Errors

**Symptoms:** Application cannot connect to database

**Diagnosis:**
```bash
# Test database connectivity
aws rds describe-db-instances \
  --db-instance-identifier culturebridge-postgres

# Check security groups
aws ec2 describe-security-groups \
  --group-ids <security-group-id>
```

**Solutions:**
- Verify security group allows traffic from ECS tasks
- Check database credentials in Secrets Manager
- Verify database is in same VPC
- Check RDS instance status

#### 3. High Latency

**Symptoms:** API responses are slow

**Diagnosis:**
```bash
# Check ALB metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --dimensions Name=LoadBalancer,Value=<alb-name> \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

**Solutions:**
- Scale up ECS tasks
- Optimize database queries
- Increase Redis cache usage
- Enable CloudFront caching

#### 4. Deployment Failures

**Symptoms:** Deployment stuck or fails

**Diagnosis:**
```bash
# Check deployment status
aws ecs describe-services \
  --cluster culturebridge-cluster \
  --services culturebridge-backend

# Check events
aws ecs describe-services \
  --cluster culturebridge-cluster \
  --services culturebridge-backend \
  --query 'services[0].events[0:10]'
```

**Solutions:**
- Check health check configuration
- Verify new task definition is valid
- Increase deployment timeout
- Rollback to previous version

### Emergency Procedures

#### Immediate Rollback

```bash
chmod +x scripts/rollback.sh
./scripts/rollback.sh production
```

#### Scale Down (Reduce Costs)

```bash
# Reduce to minimum instances
aws ecs update-service \
  --cluster culturebridge-cluster \
  --service culturebridge-backend \
  --desired-count 1

aws ecs update-service \
  --cluster culturebridge-cluster \
  --service culturebridge-frontend \
  --desired-count 1
```

#### Database Backup

```bash
# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier culturebridge-postgres \
  --db-snapshot-identifier culturebridge-manual-$(date +%Y%m%d-%H%M%S)
```

## Maintenance

### Regular Tasks

**Daily:**
- Review CloudWatch alarms
- Check error logs
- Monitor costs

**Weekly:**
- Review security scan results
- Update dependencies
- Check backup status
- Review performance metrics

**Monthly:**
- Rotate access keys
- Review IAM policies
- Update documentation
- Conduct security audit

### Updates and Patches

```bash
# Update backend dependencies
cd backend
pip list --outdated
pip install -U <package>

# Update frontend dependencies
cd frontend
npm outdated
npm update

# Rebuild and redeploy
./scripts/deploy.sh production
```

## Cost Optimization

### Monitor Costs

```bash
# Get cost and usage
aws ce get-cost-and-usage \
  --time-period Start=2025-11-01,End=2025-11-30 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```

### Optimization Tips

1. **Use Reserved Instances** for predictable workloads
2. **Enable S3 Intelligent-Tiering** for uploads
3. **Reduce CloudWatch log retention** to 30 days
4. **Use Spot instances** for non-critical tasks
5. **Clean up old ECR images** regularly
6. **Optimize database instance size** based on usage

## Support

For assistance:
- **Documentation:** Check docs/ directory
- **Logs:** CloudWatch Logs
- **Monitoring:** CloudWatch Dashboards
- **AWS Support:** Open support case
- **Team:** Contact DevOps team

## Additional Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
