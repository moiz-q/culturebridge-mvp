# Secrets Manager for Application Secrets

# Application Secrets (JWT, OpenAI, Stripe, etc.)
resource "aws_secretsmanager_secret" "app_secrets" {
  name_prefix             = "${var.project_name}-app-secrets-"
  recovery_window_in_days = 7
  
  tags = {
    Name = "${var.project_name}-app-secrets"
  }
}

# Placeholder secret version (to be updated manually or via CI/CD)
resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    JWT_SECRET_KEY         = "CHANGE_ME_IN_PRODUCTION"
    OPENAI_API_KEY         = "CHANGE_ME_IN_PRODUCTION"
    STRIPE_SECRET_KEY      = "CHANGE_ME_IN_PRODUCTION"
    STRIPE_WEBHOOK_SECRET  = "CHANGE_ME_IN_PRODUCTION"
    SMTP_USER              = "CHANGE_ME_IN_PRODUCTION"
    SMTP_PASSWORD          = "CHANGE_ME_IN_PRODUCTION"
  })
  
  lifecycle {
    ignore_changes = [secret_string]
  }
}
