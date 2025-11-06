# Monitoring and Alerting Setup

This document describes the monitoring and alerting infrastructure for CultureBridge API.

## Health Check Endpoints

### `/health`
Comprehensive health check that verifies:
- API responsiveness
- Database connectivity and performance
- Redis connectivity
- External service configuration
- Response time

Returns:
- `200 OK` - All systems operational
- `503 Service Unavailable` - Critical system failure

Example response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-05T10:30:00Z",
  "version": "2.0.0",
  "environment": "production",
  "response_time_ms": 45.23,
  "checks": {
    "database": {
      "status": "healthy",
      "query_time_ms": 12.5,
      "pool": {
        "size": 20,
        "checked_in": 18,
        "checked_out": 2,
        "overflow": 0
      }
    },
    "redis": {
      "status": "healthy",
      "ping_time_ms": 2.1,
      "connected_clients": 5,
      "used_memory_human": "1.2M"
    },
    "external_services": {
      "openai": {"configured": true},
      "stripe": {"configured": true},
      "s3": {"configured": true}
    }
  }
}
```

### `/health/live`
Kubernetes liveness probe - checks if application is running.

### `/health/ready`
Kubernetes readiness probe - checks if application is ready to serve traffic.

## CloudWatch Metrics

The application automatically publishes the following metrics to CloudWatch:

### API Metrics

**APILatency**
- Description: Response time for API endpoints
- Unit: Milliseconds
- Dimensions: Endpoint, Method, StatusCode
- Target: p95 < 250ms

**RequestCount**
- Description: Number of API requests
- Unit: Count
- Dimensions: Endpoint, Method

**ErrorCount**
- Description: Number of errors
- Unit: Count
- Dimensions: Endpoint, ErrorType (4xx, 5xx)
- Target: < 5% error rate

### Database Metrics

**DatabaseQueryTime**
- Description: Database query execution time
- Unit: Milliseconds
- Dimensions: QueryType
- Target: p95 < 50ms

**DatabaseConnectionPoolUsage**
- Description: Connection pool utilization
- Unit: Percent
- Target: < 80%

### Cache Metrics

**CacheHit / CacheMiss**
- Description: Cache hit/miss counts
- Unit: Count
- Dimensions: CacheType

### External Service Metrics

**ExternalServiceLatency**
- Description: External API call latency
- Unit: Milliseconds
- Dimensions: Service, Operation, Success
- Targets:
  - OpenAI: < 5000ms
  - Stripe: < 2000ms

## CloudWatch Alarms

### High Error Rate
- **Metric**: ErrorCount
- **Threshold**: > 5% for 5 minutes
- **Action**: Send alert to PagerDuty
- **Severity**: Critical

### High Latency
- **Metric**: APILatency (p95)
- **Threshold**: > 500ms for 2 minutes
- **Action**: Send alert to Slack
- **Severity**: Warning

### Database Connection Pool High
- **Metric**: DatabaseConnectionPoolUsage
- **Threshold**: > 80%
- **Action**: Send alert to email
- **Severity**: Warning

### External Service Failures
- **Metric**: ExternalServiceLatency (failed calls)
- **Threshold**: > 10 failures in 5 minutes
- **Action**: Send alert to Slack
- **Severity**: Warning

## Setup Instructions

### 1. Configure AWS Credentials

Ensure the application has IAM permissions to publish CloudWatch metrics:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData",
        "cloudwatch:PutMetricAlarm",
        "cloudwatch:DescribeAlarms"
      ],
      "Resource": "*"
    }
  ]
}
```

### 2. Configure SNS Topic (Optional)

Create an SNS topic for alarm notifications:

```bash
aws sns create-topic --name culturebridge-alerts
aws sns subscribe --topic-arn arn:aws:sns:us-east-1:ACCOUNT:culturebridge-alerts \
  --protocol email --notification-endpoint alerts@culturebridge.com
```

Update `app/config.py` with the SNS topic ARN.

### 3. Enable Monitoring

Set environment variable:
```bash
ENVIRONMENT=production
```

Alarms are automatically created on application startup in production.

### 4. View Metrics

Access CloudWatch console:
1. Navigate to CloudWatch > Metrics
2. Select "CultureBridge/API" namespace
3. View metrics by dimension

### 5. Configure Dashboards

Create a CloudWatch dashboard with:
- API latency (p50, p95, p99)
- Error rate over time
- Request count by endpoint
- Database query performance
- Cache hit rate
- External service latency

## Monitoring Best Practices

1. **Set up alerts for critical metrics**
   - Error rate > 5%
   - Latency p95 > 500ms
   - Database connection pool > 80%

2. **Review metrics regularly**
   - Daily: Check error rates and latency trends
   - Weekly: Review capacity and scaling needs
   - Monthly: Analyze performance patterns

3. **Investigate anomalies**
   - Sudden latency spikes
   - Increased error rates
   - Cache hit rate drops

4. **Optimize based on data**
   - Identify slow endpoints
   - Optimize database queries
   - Adjust cache TTLs
   - Scale resources as needed

## Troubleshooting

### Metrics not appearing in CloudWatch

1. Check IAM permissions
2. Verify AWS credentials are configured
3. Check application logs for CloudWatch errors
4. Ensure `ENVIRONMENT=production`

### Alarms not triggering

1. Verify SNS topic is configured
2. Check alarm thresholds are appropriate
3. Confirm email subscription is confirmed
4. Review alarm history in CloudWatch console

### High latency alerts

1. Check database query performance
2. Review external service response times
3. Analyze endpoint-specific metrics
4. Consider scaling resources

### High error rate alerts

1. Check application logs for errors
2. Review recent deployments
3. Verify external service availability
4. Check database connectivity

## Performance Targets

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| API Latency (p95) | < 250ms | > 500ms |
| Error Rate | < 1% | > 5% |
| Database Query Time (p95) | < 50ms | > 100ms |
| Cache Hit Rate | > 80% | < 50% |
| Uptime | > 99.5% | < 99% |

## Related Documentation

- [Error Handling and Logging](ERROR_HANDLING_LOGGING.md)
- [AWS Infrastructure Setup](../docs/AWS_SETUP.md)
- [Performance Optimization](../docs/PERFORMANCE.md)
