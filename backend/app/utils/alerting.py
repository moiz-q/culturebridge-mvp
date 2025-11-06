"""
Alerting configuration and utilities for CloudWatch Alarms.

Requirements: 8.5
"""
from typing import Dict, List, Any
import logging

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from app.config import settings


logger = logging.getLogger(__name__)


class AlertManager:
    """
    Manages CloudWatch alarms for monitoring critical metrics.
    """
    
    def __init__(self):
        self.cloudwatch = None
        self.namespace = "CultureBridge/API"
        self.sns_topic_arn = None  # Should be configured in settings
        
        if BOTO3_AVAILABLE and settings.ENVIRONMENT == "production":
            try:
                self.cloudwatch = boto3.client(
                    'cloudwatch',
                    region_name=settings.AWS_REGION
                )
            except Exception as e:
                logger.warning(f"Could not initialize CloudWatch client: {e}")
    
    def create_high_error_rate_alarm(self):
        """
        Create alarm for high error rate (>5% for 5 minutes).
        
        Requirements: 8.5
        """
        if not self.cloudwatch:
            return
        
        try:
            self.cloudwatch.put_metric_alarm(
                AlarmName='CultureBridge-HighErrorRate',
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=1,
                MetricName='ErrorCount',
                Namespace=self.namespace,
                Period=300,  # 5 minutes
                Statistic='Sum',
                Threshold=5.0,
                ActionsEnabled=True,
                AlarmActions=[self.sns_topic_arn] if self.sns_topic_arn else [],
                AlarmDescription='Alert when error rate exceeds 5% for 5 minutes',
                TreatMissingData='notBreaching'
            )
            logger.info("Created high error rate alarm")
        except ClientError as e:
            logger.error(f"Failed to create error rate alarm: {e}")
    
    def create_high_latency_alarm(self):
        """
        Create alarm for high API latency (p95 > 500ms).
        
        Requirements: 8.5
        """
        if not self.cloudwatch:
            return
        
        try:
            self.cloudwatch.put_metric_alarm(
                AlarmName='CultureBridge-HighLatency',
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=2,
                MetricName='APILatency',
                Namespace=self.namespace,
                Period=60,  # 1 minute
                ExtendedStatistic='p95',
                Threshold=500.0,  # 500ms
                ActionsEnabled=True,
                AlarmActions=[self.sns_topic_arn] if self.sns_topic_arn else [],
                AlarmDescription='Alert when p95 latency exceeds 500ms for 2 minutes',
                TreatMissingData='notBreaching'
            )
            logger.info("Created high latency alarm")
        except ClientError as e:
            logger.error(f"Failed to create latency alarm: {e}")
    
    def create_database_connection_alarm(self):
        """
        Create alarm for database connection pool exhaustion.
        
        Requirements: 8.5
        """
        if not self.cloudwatch:
            return
        
        try:
            self.cloudwatch.put_metric_alarm(
                AlarmName='CultureBridge-DatabaseConnectionPoolHigh',
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=1,
                MetricName='DatabaseConnectionPoolUsage',
                Namespace=self.namespace,
                Period=60,
                Statistic='Average',
                Threshold=80.0,  # 80% of pool
                ActionsEnabled=True,
                AlarmActions=[self.sns_topic_arn] if self.sns_topic_arn else [],
                AlarmDescription='Alert when database connection pool usage exceeds 80%',
                TreatMissingData='notBreaching'
            )
            logger.info("Created database connection alarm")
        except ClientError as e:
            logger.error(f"Failed to create database alarm: {e}")
    
    def create_external_service_failure_alarm(self):
        """
        Create alarm for external service failures (OpenAI, Stripe).
        
        Requirements: 8.5
        """
        if not self.cloudwatch:
            return
        
        try:
            self.cloudwatch.put_metric_alarm(
                AlarmName='CultureBridge-ExternalServiceFailures',
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=1,
                MetricName='ExternalServiceLatency',
                Namespace=self.namespace,
                Period=300,  # 5 minutes
                Statistic='SampleCount',
                Threshold=10.0,  # More than 10 failures
                ActionsEnabled=True,
                AlarmActions=[self.sns_topic_arn] if self.sns_topic_arn else [],
                AlarmDescription='Alert when external service failures exceed threshold',
                TreatMissingData='notBreaching',
                Dimensions=[
                    {'Name': 'Success', 'Value': 'False'}
                ]
            )
            logger.info("Created external service failure alarm")
        except ClientError as e:
            logger.error(f"Failed to create external service alarm: {e}")
    
    def setup_all_alarms(self):
        """
        Set up all monitoring alarms.
        Should be called during application startup in production.
        
        Requirements: 8.5
        """
        if settings.ENVIRONMENT != "production":
            logger.info("Skipping alarm setup in non-production environment")
            return
        
        logger.info("Setting up CloudWatch alarms...")
        self.create_high_error_rate_alarm()
        self.create_high_latency_alarm()
        self.create_database_connection_alarm()
        self.create_external_service_failure_alarm()
        logger.info("CloudWatch alarms setup complete")


# Global alert manager instance
alert_manager = AlertManager()


# Alarm configuration as code (for reference/documentation)
ALARM_CONFIGURATIONS = {
    "high_error_rate": {
        "metric": "ErrorCount",
        "threshold": 5.0,
        "period": 300,
        "evaluation_periods": 1,
        "comparison": "GreaterThanThreshold",
        "description": "Error rate exceeds 5% for 5 minutes"
    },
    "high_latency": {
        "metric": "APILatency",
        "threshold": 500.0,
        "period": 60,
        "evaluation_periods": 2,
        "statistic": "p95",
        "comparison": "GreaterThanThreshold",
        "description": "P95 latency exceeds 500ms for 2 minutes"
    },
    "database_connections": {
        "metric": "DatabaseConnectionPoolUsage",
        "threshold": 80.0,
        "period": 60,
        "evaluation_periods": 1,
        "comparison": "GreaterThanThreshold",
        "description": "Database connection pool usage exceeds 80%"
    },
    "external_service_failures": {
        "metric": "ExternalServiceLatency",
        "threshold": 10.0,
        "period": 300,
        "evaluation_periods": 1,
        "comparison": "GreaterThanThreshold",
        "description": "External service failures exceed 10 in 5 minutes"
    }
}
