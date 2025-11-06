# Deployment Checklist

Use this checklist to ensure all steps are completed before and after deployment.

## Pre-Deployment Checklist

### Infrastructure Setup

- [ ] AWS account created and configured
- [ ] Terraform state S3 bucket created
- [ ] DynamoDB table for Terraform locks created
- [ ] ACM certificate requested and validated
- [ ] Route 53 hosted zone configured
- [ ] Terraform infrastructure deployed
- [ ] ECR repositories created

### Secrets Configuration

- [ ] Database credentials stored in Secrets Manager
- [ ] JWT secret key generated and stored
- [ ] OpenAI API key added to Secrets Manager
- [ ] Stripe API keys (secret and webhook) added
- [ ] SMTP credentials configured
- [ ] AWS access keys for S3 configured

### CI/CD Setup

- [ ] GitHub Actions secrets configured
- [ ] IAM user for GitHub Actions created
- [ ] GitHub environments (staging, production) created
- [ ] Branch protection rules configured
- [ ] Required reviewers assigned for production

### Database Setup

- [ ] RDS instance running and accessible
- [ ] Database migrations tested locally
- [ ] Initial admin user created
- [ ] Database backups configured
- [ ] Connection pooling configured

### Application Configuration

- [ ] Environment variables reviewed
- [ ] CORS origins configured
- [ ] Rate limiting settings verified
- [ ] Email templates prepared
- [ ] S3 bucket permissions verified

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing locally
- [ ] Code reviewed and approved
- [ ] Database migrations reviewed
- [ ] Rollback plan prepared
- [ ] Stakeholders notified of deployment window
- [ ] Monitoring dashboards ready

### During Deployment

- [ ] Create backup of production database
- [ ] Run database migrations
- [ ] Deploy backend service
- [ ] Deploy frontend service
- [ ] Wait for services to stabilize
- [ ] Run smoke tests

### Post-Deployment

- [ ] Verify health endpoints responding
- [ ] Check application logs for errors
- [ ] Test critical user flows:
  - [ ] User registration
  - [ ] User login
  - [ ] Profile creation
  - [ ] Coach search
  - [ ] Booking creation
  - [ ] Payment processing
  - [ ] Community features
- [ ] Monitor error rates in CloudWatch
- [ ] Monitor API latency
- [ ] Verify database connections
- [ ] Check Redis cache hit rate

## Smoke Tests

Run these tests after deployment:

```bash
# Health checks
curl https://culturebridge.com/health
curl https://culturebridge.com/api/health

# Authentication
curl -X POST https://culturebridge.com/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","role":"client"}'

# Coach listing
curl https://culturebridge.com/api/coaches

# Admin dashboard (requires auth)
curl https://culturebridge.com/api/admin/metrics \
  -H "Authorization: Bearer <token>"
```

## Rollback Checklist

If issues are detected:

- [ ] Identify the issue and severity
- [ ] Decide if rollback is necessary
- [ ] Notify stakeholders
- [ ] Execute rollback script or workflow
- [ ] Verify rollback successful
- [ ] Monitor application stability
- [ ] Document the issue
- [ ] Schedule post-mortem

## Monitoring Checklist

### First Hour After Deployment

- [ ] Monitor error rates (should be < 1%)
- [ ] Monitor API latency (p95 < 500ms)
- [ ] Check ECS task health
- [ ] Monitor database CPU and connections
- [ ] Check Redis memory usage
- [ ] Review application logs

### First 24 Hours

- [ ] Monitor user activity
- [ ] Check payment processing
- [ ] Monitor email delivery
- [ ] Review security logs
- [ ] Check S3 upload functionality
- [ ] Monitor costs

### First Week

- [ ] Review CloudWatch alarms
- [ ] Analyze performance metrics
- [ ] Check for memory leaks
- [ ] Review user feedback
- [ ] Monitor database growth
- [ ] Optimize as needed

## Security Checklist

### Pre-Production

- [ ] Security scan completed
- [ ] Dependency vulnerabilities addressed
- [ ] Secrets not exposed in logs
- [ ] HTTPS enforced
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] SQL injection prevention verified
- [ ] XSS protection enabled

### Post-Production

- [ ] Enable AWS GuardDuty
- [ ] Configure AWS WAF rules
- [ ] Enable VPC Flow Logs
- [ ] Set up CloudTrail
- [ ] Configure security alarms
- [ ] Review IAM policies
- [ ] Enable MFA for admin accounts

## Performance Checklist

- [ ] Database indexes created
- [ ] Redis caching enabled
- [ ] CloudFront CDN configured
- [ ] Image optimization enabled
- [ ] Gzip compression enabled
- [ ] Connection pooling configured
- [ ] Auto-scaling configured
- [ ] Load testing completed

## Compliance Checklist

- [ ] GDPR data export implemented
- [ ] GDPR data deletion implemented
- [ ] Privacy policy updated
- [ ] Terms of service updated
- [ ] Cookie consent implemented
- [ ] Data retention policies configured
- [ ] Audit logging enabled

## Documentation Checklist

- [ ] API documentation updated
- [ ] README updated
- [ ] Deployment guide updated
- [ ] Architecture diagrams updated
- [ ] Runbook created
- [ ] Troubleshooting guide updated
- [ ] Change log updated

## Communication Checklist

### Before Deployment

- [ ] Notify team of deployment schedule
- [ ] Inform stakeholders of expected downtime
- [ ] Prepare status page update
- [ ] Schedule team availability

### After Deployment

- [ ] Announce successful deployment
- [ ] Update status page
- [ ] Send release notes to users
- [ ] Update internal documentation
- [ ] Schedule retrospective meeting

## Emergency Contacts

Keep this information readily available:

- **DevOps Lead:** [Name] - [Contact]
- **Backend Lead:** [Name] - [Contact]
- **Frontend Lead:** [Name] - [Contact]
- **Database Admin:** [Name] - [Contact]
- **AWS Support:** [Account Number]
- **On-Call Engineer:** [Contact]

## Rollback Triggers

Initiate rollback if:

- Error rate > 5% for 5 minutes
- API latency p95 > 2 seconds
- Database connection failures
- Critical functionality broken
- Security vulnerability detected
- Data corruption detected

## Success Criteria

Deployment is successful when:

- ✅ All health checks passing
- ✅ Error rate < 1%
- ✅ API latency p95 < 500ms
- ✅ All critical user flows working
- ✅ No database errors
- ✅ Monitoring dashboards green
- ✅ No security alerts
- ✅ User feedback positive

## Post-Deployment Tasks

Within 24 hours:

- [ ] Review deployment metrics
- [ ] Document any issues encountered
- [ ] Update runbook with lessons learned
- [ ] Schedule retrospective
- [ ] Thank the team

Within 1 week:

- [ ] Conduct retrospective meeting
- [ ] Update deployment process based on feedback
- [ ] Archive deployment artifacts
- [ ] Update cost projections
- [ ] Plan next deployment

## Notes

Use this section to document deployment-specific notes:

**Deployment Date:** _______________
**Deployed By:** _______________
**Git Commit:** _______________
**Issues Encountered:** _______________
**Resolution:** _______________
**Lessons Learned:** _______________
