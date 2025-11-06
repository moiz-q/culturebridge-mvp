# CI/CD Pipeline Documentation

## Overview

CultureBridge uses GitHub Actions for continuous integration and deployment. The pipeline automates testing, building, and deploying the application to AWS ECS.

## Pipeline Architecture

```
┌─────────────┐
│   Git Push  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│     Backend Tests & Linting         │
│  - pytest with coverage             │
│  - flake8, black, mypy              │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│    Frontend Tests & Linting         │
│  - ESLint, TypeScript check         │
│  - Build verification               │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│      Build Docker Images            │
│  - Backend image → ECR              │
│  - Frontend image → ECR             │
└──────┬──────────────────────────────┘
       │
       ├─────────────────┬─────────────┐
       ▼                 ▼             ▼
┌──────────────┐  ┌──────────┐  ┌──────────┐
│   Staging    │  │Production│  │ Rollback │
│  (develop)   │  │  (main)  │  │ (manual) │
└──────────────┘  └──────────┘  └──────────┘
```

## Workflows

### 1. Main CI/CD Pipeline (`ci-cd.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs:**

#### Backend Tests
- Runs pytest with PostgreSQL and Redis services
- Executes linting (flake8, black, mypy)
- Generates coverage report
- Uploads coverage to Codecov

#### Frontend Tests
- Runs ESLint and TypeScript checks
- Builds the Next.js application
- Verifies build succeeds

#### Build Images
- Builds Docker images for backend and frontend
- Pushes images to Amazon ECR
- Tags with commit SHA and `latest`

#### Deploy to Staging
- **Trigger**: Push to `develop` branch
- Runs database migrations
- Updates ECS services
- Waits for services to stabilize
- Runs smoke tests

#### Deploy to Production
- **Trigger**: Push to `main` branch
- **Requires**: Manual approval via GitHub environment
- Runs database migrations
- Updates ECS services
- Waits for services to stabilize
- Runs smoke tests
- Sends deployment notifications

#### Rollback Production
- **Trigger**: Manual workflow dispatch
- Reverts to previous task definitions
- Waits for services to stabilize
- Verifies health checks

### 2. Security Scanning (`security-scan.yml`)

**Triggers:**
- Push to `main` or `develop`
- Pull requests
- Weekly schedule (Mondays at 9 AM UTC)

**Scans:**
- Dependency vulnerabilities (Snyk)
- Container image vulnerabilities (Trivy)
- Static code analysis (Bandit)

### 3. Pull Request Checks (`pr-checks.yml`)

**Triggers:**
- Pull requests to `main` or `develop`

**Checks:**
- PR title format (conventional commits)
- Merge conflicts
- File size limits (5MB max)
- Secret detection (TruffleHog)
- Code quality (Pylint, Radon)
- Bundle size analysis

## Setup Instructions

### Prerequisites

1. AWS account with appropriate permissions
2. GitHub repository with Actions enabled
3. GitHub CLI (`gh`) installed
4. AWS CLI configured

### Initial Setup

Run the setup script:

```bash
chmod +x scripts/setup-ci.sh
./scripts/setup-ci.sh
```

This script will:
- Create IAM user for GitHub Actions
- Generate access keys
- Set GitHub secrets
- Configure AWS permissions

### Manual Configuration

#### 1. GitHub Environments

Create two environments in GitHub Settings > Environments:

**Staging Environment:**
- No protection rules
- Deployment branch: `develop`

**Production Environment:**
- Required reviewers: Add team members
- Deployment branch: `main`
- Wait timer: 5 minutes (optional)

#### 2. GitHub Secrets

Required secrets (set automatically by setup script):
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `STAGING_DATABASE_URL`
- `PRODUCTION_DATABASE_URL`

Optional secrets:
- `SNYK_TOKEN` - For security scanning
- `SLACK_WEBHOOK_URL` - For notifications
- `CODECOV_TOKEN` - For coverage reports

#### 3. Branch Protection Rules

Configure branch protection for `main` and `develop`:

- Require pull request reviews (1 reviewer)
- Require status checks to pass:
  - `Backend Tests`
  - `Frontend Tests`
  - `Security Scanning`
- Require branches to be up to date
- Include administrators

## Deployment Process

### Automatic Deployment

**To Staging:**
1. Create feature branch from `develop`
2. Make changes and commit
3. Create PR to `develop`
4. After approval and merge, automatic deployment to staging

**To Production:**
1. Create PR from `develop` to `main`
2. After approval and merge, deployment requires manual approval
3. Approve deployment in GitHub Actions UI
4. Automatic deployment to production

### Manual Deployment

Use deployment scripts for manual deployments:

```bash
# Deploy to staging
chmod +x scripts/deploy.sh
./scripts/deploy.sh staging

# Deploy to production
./scripts/deploy.sh production
```

### Rollback

If issues are detected after deployment:

**Via GitHub Actions:**
1. Go to Actions > Rollback Production
2. Click "Run workflow"
3. Confirm rollback

**Via Script:**
```bash
chmod +x scripts/rollback.sh
./scripts/rollback.sh production
```

## Monitoring Deployments

### GitHub Actions UI

Monitor deployments in real-time:
1. Go to repository > Actions
2. Select the workflow run
3. View logs for each job

### AWS Console

Monitor ECS deployments:
1. Go to ECS > Clusters > culturebridge-cluster
2. Select service (backend or frontend)
3. View "Deployments" tab
4. Check "Events" for deployment status

### CloudWatch Logs

View application logs:
```bash
# Backend logs
aws logs tail /ecs/culturebridge/backend --follow

# Frontend logs
aws logs tail /ecs/culturebridge/frontend --follow
```

## Troubleshooting

### Build Failures

**Backend tests failing:**
```bash
# Run tests locally
cd backend
pytest tests/ -v
```

**Frontend build failing:**
```bash
# Run build locally
cd frontend
npm run build
```

### Deployment Failures

**ECS service not updating:**
1. Check CloudWatch logs for errors
2. Verify task definition is valid
3. Check security group rules
4. Verify secrets are accessible

**Health checks failing:**
1. Check application logs
2. Verify database connectivity
3. Check Redis connectivity
4. Verify environment variables

### Rollback Issues

If rollback fails:
1. Check previous task definitions exist
2. Manually update service in AWS console
3. Verify health endpoints are responding

## Performance Optimization

### Build Time Optimization

- Use Docker layer caching
- Cache npm/pip dependencies
- Parallelize independent jobs
- Use GitHub Actions cache

### Deployment Time Optimization

- Use blue-green deployments
- Optimize health check intervals
- Pre-warm containers
- Use faster instance types

## Security Best Practices

1. **Secrets Management:**
   - Never commit secrets to repository
   - Use GitHub Secrets for sensitive data
   - Rotate access keys regularly
   - Use AWS Secrets Manager for application secrets

2. **Access Control:**
   - Limit IAM permissions to minimum required
   - Use separate AWS accounts for staging/production
   - Enable MFA for production deployments
   - Audit access logs regularly

3. **Image Security:**
   - Scan images for vulnerabilities
   - Use minimal base images
   - Keep dependencies updated
   - Sign container images

4. **Network Security:**
   - Use private subnets for ECS tasks
   - Enable VPC Flow Logs
   - Use security groups with least privilege
   - Enable AWS WAF for ALB

## Maintenance

### Regular Tasks

**Weekly:**
- Review security scan results
- Check for dependency updates
- Monitor deployment success rate

**Monthly:**
- Rotate access keys
- Review and update IAM policies
- Audit CloudWatch logs retention
- Review and optimize costs

**Quarterly:**
- Update base Docker images
- Review and update CI/CD pipeline
- Conduct disaster recovery drill
- Update documentation

## Cost Monitoring

Monitor CI/CD costs:
- GitHub Actions minutes usage
- ECR storage costs
- CloudWatch logs storage
- Data transfer costs

Optimize costs:
- Clean up old Docker images
- Reduce log retention period
- Use GitHub Actions cache
- Optimize build parallelization

## Support

For issues or questions:
- Check GitHub Actions logs
- Review CloudWatch logs
- Consult AWS documentation
- Contact DevOps team
