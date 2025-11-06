# CultureBridge AWS Infrastructure

This directory contains Terraform configuration for deploying CultureBridge to AWS.

## Architecture Overview

- **VPC**: Multi-AZ VPC with public and private subnets
- **ECS Fargate**: Container orchestration for backend and frontend
- **RDS PostgreSQL**: Multi-AZ database with automated backups
- **ElastiCache Redis**: Multi-AZ Redis cluster for caching
- **S3**: File uploads storage with encryption
- **CloudFront**: CDN for static assets and application delivery
- **ALB**: Application Load Balancer for traffic distribution
- **Route 53**: DNS management
- **Secrets Manager**: Secure storage for credentials and API keys
- **CloudWatch**: Logging and monitoring

## Prerequisites

1. AWS CLI configured with appropriate credentials
2. Terraform >= 1.0 installed
3. ACM certificate created for your domain
4. Route 53 hosted zone for your domain

## Initial Setup

### 1. Create S3 Backend for Terraform State

```bash
aws s3api create-bucket \
  --bucket culturebridge-terraform-state \
  --region us-east-1

aws s3api put-bucket-versioning \
  --bucket culturebridge-terraform-state \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
  --bucket culturebridge-terraform-state \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

aws dynamodb create-table \
  --table-name culturebridge-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 2. Create ACM Certificate

```bash
# Request certificate
aws acm request-certificate \
  --domain-name culturebridge.com \
  --subject-alternative-names www.culturebridge.com \
  --validation-method DNS \
  --region us-east-1

# Follow DNS validation instructions in ACM console
```

### 3. Configure Variables

Create a `terraform.tfvars` file:

```hcl
aws_region      = "us-east-1"
environment     = "production"
domain_name     = "culturebridge.com"
certificate_arn = "arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/CERT_ID"
```

## Deployment

### Initialize Terraform

```bash
terraform init
```

### Plan Infrastructure Changes

```bash
terraform plan -out=tfplan
```

### Apply Infrastructure

```bash
terraform apply tfplan
```

### Update Application Secrets

After initial deployment, update the secrets in AWS Secrets Manager:

```bash
# Get the secret ARN from Terraform outputs
SECRET_ARN=$(terraform output -raw app_secrets_arn)

# Update the secret with real values
aws secretsmanager update-secret \
  --secret-id $SECRET_ARN \
  --secret-string '{
    "JWT_SECRET_KEY": "your-secure-jwt-secret",
    "OPENAI_API_KEY": "sk-...",
    "STRIPE_SECRET_KEY": "sk_live_...",
    "STRIPE_WEBHOOK_SECRET": "whsec_...",
    "SMTP_USER": "your-smtp-user",
    "SMTP_PASSWORD": "your-smtp-password"
  }'
```

## Outputs

After deployment, Terraform will output important values:

- `alb_dns_name`: Load balancer DNS name
- `cloudfront_domain_name`: CloudFront distribution domain
- `ecr_backend_repository_url`: Backend Docker registry URL
- `ecr_frontend_repository_url`: Frontend Docker registry URL
- `s3_bucket_name`: Uploads bucket name

## Scaling Configuration

### Auto Scaling

ECS services are configured to auto-scale based on CPU utilization:

- **Min instances**: 2
- **Max instances**: 10
- **Scale up**: CPU > 70% for 2 minutes
- **Scale down**: CPU < 30% for 5 minutes

### Manual Scaling

To manually adjust desired count:

```bash
aws ecs update-service \
  --cluster culturebridge-cluster \
  --service culturebridge-backend \
  --desired-count 4
```

## Monitoring

### CloudWatch Logs

- Backend logs: `/ecs/culturebridge/backend`
- Frontend logs: `/ecs/culturebridge/frontend`

### CloudWatch Metrics

Key metrics to monitor:

- ECS CPU/Memory utilization
- ALB request count and latency
- RDS connections and CPU
- ElastiCache hit rate

### Alarms

Set up CloudWatch alarms for:

- High error rates (5xx responses)
- High latency (p95 > 500ms)
- Database CPU > 80%
- Low cache hit rate

## Backup and Recovery

### Database Backups

- Automated daily backups with 7-day retention
- Backup window: 03:00-04:00 UTC
- Point-in-time recovery enabled

### Disaster Recovery

To restore from backup:

```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier culturebridge-postgres \
  --target-db-instance-identifier culturebridge-postgres-restored \
  --restore-time 2025-11-05T10:00:00Z
```

## Cost Optimization

### Estimated Monthly Costs (Production)

- ECS Fargate (4 tasks): ~$100
- RDS db.t3.medium Multi-AZ: ~$150
- ElastiCache cache.t3.medium: ~$100
- ALB: ~$25
- CloudFront: ~$20 (varies with traffic)
- S3: ~$10 (varies with storage)
- **Total**: ~$405/month

### Cost Reduction Tips

1. Use Reserved Instances for predictable workloads
2. Enable S3 Intelligent-Tiering
3. Review CloudWatch log retention
4. Use Spot instances for non-critical tasks

## Security

### Best Practices Implemented

- ✅ All data encrypted at rest and in transit
- ✅ Secrets stored in AWS Secrets Manager
- ✅ Private subnets for database and cache
- ✅ Security groups with least privilege
- ✅ IAM roles with minimal permissions
- ✅ CloudWatch logging enabled
- ✅ Automated security scanning for container images

### Security Checklist

- [ ] Enable AWS GuardDuty
- [ ] Set up AWS Config rules
- [ ] Enable VPC Flow Logs
- [ ] Configure AWS WAF rules
- [ ] Set up CloudTrail for audit logging
- [ ] Enable MFA for AWS accounts

## Troubleshooting

### ECS Tasks Not Starting

Check CloudWatch logs for errors:

```bash
aws logs tail /ecs/culturebridge/backend --follow
```

### Database Connection Issues

Verify security group rules and connection string:

```bash
aws rds describe-db-instances \
  --db-instance-identifier culturebridge-postgres
```

### High Latency

Check ALB target health:

```bash
aws elbv2 describe-target-health \
  --target-group-arn <target-group-arn>
```

## Cleanup

To destroy all infrastructure:

```bash
# Disable deletion protection first
terraform apply -var="enable_deletion_protection=false"

# Destroy resources
terraform destroy
```

**Warning**: This will delete all data including databases and backups!

## Support

For issues or questions:
- Check CloudWatch logs
- Review AWS Service Health Dashboard
- Contact DevOps team
