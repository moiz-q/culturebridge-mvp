# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the CultureBridge platform.

## Table of Contents

1. [Application Startup Issues](#application-startup-issues)
2. [Database Issues](#database-issues)
3. [Authentication Issues](#authentication-issues)
4. [API Integration Issues](#api-integration-issues)
5. [Performance Issues](#performance-issues)
6. [Deployment Issues](#deployment-issues)
7. [Development Environment Issues](#development-environment-issues)

## Application Startup Issues

### Backend Won't Start

**Symptom**: Backend fails to start or crashes immediately

**Common Causes**:

1. **Missing environment variables**
   ```bash
   # Check if .env file exists
   ls backend/.env
   
   # Verify required variables are set
   cat backend/.env | grep -E "DATABASE_URL|REDIS_URL|JWT_SECRET_KEY"
   ```
   
   **Solution**: Copy `.env.example` and fill in all required values

2. **Database connection failure**
   ```bash
   # Test database connection
   docker-compose exec postgres pg_isready
   
   # Check if database exists
   docker-compose exec postgres psql -U culturebridge -l
   ```
   
   **Solution**: Ensure PostgreSQL is running and DATABASE_URL is correct

3. **Port already in use**
   ```bash
   # Check what's using port 8000
   lsof -i :8000  # macOS/Linux
   netstat -ano | findstr :8000  # Windows
   ```
   
   **Solution**: Kill the process or change the port in docker-compose.yml

4. **Python dependency issues**
   ```bash
   # Reinstall dependencies
   cd backend
   pip install --force-reinstall -r requirements.txt
   ```

### Frontend Won't Start

**Symptom**: Frontend fails to start or shows errors

**Common Causes**:

1. **Missing environment variables**
   ```bash
   # Check if .env.local exists
   ls frontend/.env.local
   ```
   
   **Solution**: Copy `.env.example` to `.env.local`

2. **Node modules issues**
   ```bash
   # Clear and reinstall
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Port 3000 already in use**
   ```bash
   # Use different port
   PORT=3001 npm run dev
   ```

4. **Build cache issues**
   ```bash
   # Clear Next.js cache
   rm -rf .next
   npm run dev
   ```

### Docker Compose Issues

**Symptom**: Services won't start with docker-compose

**Common Causes**:

1. **Docker daemon not running**
   ```bash
   # Check Docker status
   docker info
   ```
   
   **Solution**: Start Docker Desktop or Docker daemon

2. **Port conflicts**
   ```bash
   # Check which ports are in use
   docker-compose ps
   ```
   
   **Solution**: Stop conflicting services or change ports in docker-compose.yml

3. **Volume permission issues**
   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER .
   ```

4. **Outdated images**
   ```bash
   # Rebuild images
   docker-compose build --no-cache
   docker-compose up -d
   ```

## Database Issues

### Migration Failures

**Symptom**: Alembic migrations fail to apply

**Diagnosis**:
```bash
# Check current migration version
cd backend
alembic current

# View migration history
alembic history

# Check for pending migrations
alembic heads
```

**Solutions**:

1. **Conflicting migrations**
   ```bash
   # Downgrade to base
   alembic downgrade base
   
   # Reapply migrations
   alembic upgrade head
   ```

2. **Database schema mismatch**
   ```bash
   # Drop and recreate database
   docker-compose down -v
   docker-compose up -d postgres
   alembic upgrade head
   ```

3. **Manual schema changes**
   ```bash
   # Generate new migration to sync
   alembic revision --autogenerate -m "Sync schema"
   alembic upgrade head
   ```

### Connection Pool Exhausted

**Symptom**: "QueuePool limit exceeded" errors

**Diagnosis**:
```bash
# Check active connections
docker-compose exec postgres psql -U culturebridge -c "SELECT count(*) FROM pg_stat_activity;"
```

**Solutions**:

1. **Increase pool size** in `backend/app/database.py`:
   ```python
   engine = create_engine(
       DATABASE_URL,
       pool_size=30,  # Increase from 20
       max_overflow=10
   )
   ```

2. **Close connections properly**:
   - Ensure all database sessions are closed
   - Use context managers or try/finally blocks

3. **Restart application**:
   ```bash
   docker-compose restart backend
   ```

### Slow Queries

**Symptom**: Database queries taking too long

**Diagnosis**:
```bash
# Enable query logging in PostgreSQL
docker-compose exec postgres psql -U culturebridge -c "ALTER SYSTEM SET log_min_duration_statement = 1000;"
docker-compose restart postgres

# View slow queries
docker-compose logs postgres | grep "duration:"
```

**Solutions**:

1. **Add missing indexes**:
   ```sql
   CREATE INDEX idx_bookings_client_id ON bookings(client_id);
   CREATE INDEX idx_bookings_session_datetime ON bookings(session_datetime);
   ```

2. **Analyze query plans**:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM bookings WHERE client_id = 'uuid';
   ```

3. **Optimize queries**:
   - Use select_related/joinedload for relationships
   - Add pagination to large result sets
   - Use database-level filtering

## Authentication Issues

### JWT Token Errors

**Symptom**: "Invalid token" or "Token expired" errors

**Diagnosis**:
```bash
# Check JWT configuration
cat backend/.env | grep JWT

# Verify token expiry
python -c "
import jwt
token = 'your_token_here'
decoded = jwt.decode(token, options={'verify_signature': False})
print(decoded)
"
```

**Solutions**:

1. **Token expired**:
   - Use refresh token to get new access token
   - Implement automatic token refresh in frontend

2. **Invalid secret key**:
   - Ensure JWT_SECRET_KEY is consistent across restarts
   - Don't change JWT_SECRET_KEY in production

3. **Clock skew**:
   - Sync system time: `sudo ntpdate -s time.nist.gov`

### Login Failures

**Symptom**: Valid credentials rejected

**Diagnosis**:
```bash
# Check user in database
docker-compose exec postgres psql -U culturebridge -c "SELECT email, is_active, email_verified FROM users WHERE email='user@example.com';"
```

**Solutions**:

1. **Account inactive**:
   ```sql
   UPDATE users SET is_active = true WHERE email = 'user@example.com';
   ```

2. **Email not verified**:
   ```sql
   UPDATE users SET email_verified = true WHERE email = 'user@example.com';
   ```

3. **Password hash mismatch**:
   ```python
   # Reset password
   from app.utils.jwt_utils import hash_password
   new_hash = hash_password('NewPassword123!')
   # Update in database
   ```

### CORS Errors

**Symptom**: "CORS policy" errors in browser console

**Diagnosis**:
```bash
# Check CORS configuration
cat backend/.env | grep CORS_ORIGINS
```

**Solutions**:

1. **Add frontend origin**:
   ```bash
   # In backend/.env
   CORS_ORIGINS=http://localhost:3000,http://localhost:3001
   ```

2. **Restart backend**:
   ```bash
   docker-compose restart backend
   ```

## API Integration Issues

### OpenAI API Errors

**Symptom**: Matching engine fails or times out

**Diagnosis**:
```bash
# Test OpenAI API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Solutions**:

1. **Invalid API key**:
   - Verify key at https://platform.openai.com/api-keys
   - Ensure key has sufficient credits

2. **Rate limit exceeded**:
   - Implement exponential backoff
   - Cache match results (already implemented)
   - Upgrade OpenAI plan

3. **Timeout errors**:
   - Increase timeout in `backend/app/services/matching_service.py`
   - Use fallback to top-rated coaches

### Stripe Integration Issues

**Symptom**: Payment processing fails

**Diagnosis**:
```bash
# Test Stripe API key
curl https://api.stripe.com/v1/customers \
  -u $STRIPE_SECRET_KEY:
```

**Solutions**:

1. **Invalid API key**:
   - Verify keys at https://dashboard.stripe.com/apikeys
   - Ensure using test keys in development

2. **Webhook signature verification fails**:
   ```bash
   # Use Stripe CLI to forward webhooks
   stripe listen --forward-to localhost:8000/payment/webhook
   
   # Copy webhook secret to .env
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

3. **Test payment cards**:
   - Use Stripe test cards: https://stripe.com/docs/testing
   - Success: 4242 4242 4242 4242
   - Decline: 4000 0000 0000 0002

### AWS S3 Upload Failures

**Symptom**: File uploads fail

**Diagnosis**:
```bash
# Test AWS credentials
aws s3 ls s3://your-bucket-name --profile default
```

**Solutions**:

1. **Invalid credentials**:
   - Verify credentials in AWS Console
   - Ensure IAM user has S3 permissions

2. **Bucket doesn't exist**:
   ```bash
   # Create bucket
   aws s3 mb s3://culturebridge-dev-uploads
   ```

3. **CORS configuration**:
   ```json
   {
     "CORSRules": [{
       "AllowedOrigins": ["http://localhost:3000"],
       "AllowedMethods": ["GET", "PUT", "POST"],
       "AllowedHeaders": ["*"]
     }]
   }
   ```

### Email Sending Failures

**Symptom**: Confirmation emails not sent

**Diagnosis**:
```bash
# Check email logs
docker-compose logs backend | grep "email"
```

**Solutions**:

1. **Gmail app password**:
   - Enable 2FA on Gmail account
   - Generate app password: https://myaccount.google.com/apppasswords
   - Use app password in SMTP_PASSWORD

2. **SMTP configuration**:
   ```bash
   # Test SMTP connection
   python -c "
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your-email@gmail.com', 'your-app-password')
   print('SMTP connection successful')
   "
   ```

3. **Firewall blocking**:
   - Ensure port 587 is not blocked
   - Try alternative SMTP providers (SendGrid, Mailgun)

## Performance Issues

### Slow API Response Times

**Symptom**: API requests taking > 1 second

**Diagnosis**:
```bash
# Check API metrics
curl http://localhost:8000/health

# View response times in logs
docker-compose logs backend | grep "duration_ms"
```

**Solutions**:

1. **Enable Redis caching**:
   ```bash
   # Verify Redis is running
   docker-compose exec redis redis-cli ping
   ```

2. **Database query optimization**:
   - Add indexes on frequently queried columns
   - Use pagination for large result sets
   - Implement database query caching

3. **Increase resources**:
   ```yaml
   # In docker-compose.yml
   backend:
     deploy:
       resources:
         limits:
           cpus: '2'
           memory: 2G
   ```

### High Memory Usage

**Symptom**: Application consuming excessive memory

**Diagnosis**:
```bash
# Check memory usage
docker stats

# Check for memory leaks
docker-compose exec backend python -c "
import psutil
process = psutil.Process()
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

**Solutions**:

1. **Database connection leaks**:
   - Ensure sessions are closed properly
   - Use context managers

2. **Large file uploads**:
   - Implement streaming uploads
   - Add file size limits

3. **Restart services**:
   ```bash
   docker-compose restart backend
   ```

### Redis Cache Issues

**Symptom**: Cache not working or stale data

**Diagnosis**:
```bash
# Check Redis memory usage
docker-compose exec redis redis-cli INFO memory

# Check cache keys
docker-compose exec redis redis-cli KEYS "match:*"
```

**Solutions**:

1. **Clear cache**:
   ```bash
   docker-compose exec redis redis-cli FLUSHALL
   ```

2. **Adjust TTL**:
   - Modify cache expiration in `backend/app/utils/cache_utils.py`

3. **Increase Redis memory**:
   ```yaml
   # In docker-compose.yml
   redis:
     command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
   ```

## Deployment Issues

### ECS Task Failures

**Symptom**: ECS tasks fail to start or keep restarting

**Diagnosis**:
```bash
# Check ECS task logs
aws ecs describe-tasks --cluster culturebridge-cluster --tasks <task-id>

# View CloudWatch logs
aws logs tail /ecs/culturebridge-backend --follow
```

**Solutions**:

1. **Health check failures**:
   - Verify /health endpoint is accessible
   - Increase health check grace period

2. **Resource constraints**:
   - Increase task CPU/memory limits
   - Check for memory leaks

3. **Environment variables**:
   - Verify all secrets are in AWS Secrets Manager
   - Check IAM permissions for task role

### Database Migration in Production

**Symptom**: Migrations fail in production

**Solutions**:

1. **Run migrations before deployment**:
   ```bash
   # In CI/CD pipeline
   aws ecs run-task \
     --cluster culturebridge-cluster \
     --task-definition migration-task \
     --launch-type FARGATE
   ```

2. **Backup database first**:
   ```bash
   # Create RDS snapshot
   aws rds create-db-snapshot \
     --db-instance-identifier culturebridge-prod \
     --db-snapshot-identifier pre-migration-$(date +%Y%m%d)
   ```

3. **Test migrations in staging**:
   - Always test migrations in staging first
   - Use blue-green deployment for zero downtime

### SSL/TLS Certificate Issues

**Symptom**: HTTPS not working or certificate errors

**Solutions**:

1. **Verify ACM certificate**:
   ```bash
   aws acm list-certificates
   ```

2. **Check DNS records**:
   ```bash
   dig api.culturebridge.com
   ```

3. **Update ALB listener**:
   - Ensure ALB has HTTPS listener on port 443
   - Certificate must be attached to listener

## Development Environment Issues

### VS Code Python Extension Issues

**Symptom**: Linting or IntelliSense not working

**Solutions**:

1. **Select correct Python interpreter**:
   - Cmd/Ctrl + Shift + P
   - "Python: Select Interpreter"
   - Choose venv interpreter

2. **Install Python extension**:
   - Install "Python" extension by Microsoft
   - Install "Pylance" for better IntelliSense

3. **Configure workspace settings**:
   ```json
   {
     "python.linting.enabled": true,
     "python.linting.flake8Enabled": true,
     "python.formatting.provider": "black"
   }
   ```

### Git Issues

**Symptom**: Git operations failing

**Solutions**:

1. **Large file issues**:
   ```bash
   # Use Git LFS for large files
   git lfs install
   git lfs track "*.mp4"
   ```

2. **Merge conflicts**:
   ```bash
   # Abort merge
   git merge --abort
   
   # Or resolve conflicts manually
   git status
   # Edit conflicted files
   git add .
   git commit
   ```

3. **Reset to remote**:
   ```bash
   git fetch origin
   git reset --hard origin/main
   ```

## Getting Additional Help

If you're still experiencing issues:

1. **Check logs**:
   ```bash
   # Backend logs
   docker-compose logs backend --tail=100 --follow
   
   # Frontend logs
   docker-compose logs frontend --tail=100 --follow
   
   # All logs
   docker-compose logs --tail=100 --follow
   ```

2. **Enable debug logging**:
   ```bash
   # In backend/.env
   LOG_LEVEL=DEBUG
   ```

3. **Contact support**:
   - Email: dev-support@culturebridge.com
   - Slack: #culturebridge-dev
   - GitHub Issues: https://github.com/your-org/culturebridge-mvp/issues

4. **Useful resources**:
   - [API Documentation](../backend/API_DOCUMENTATION.md)
   - [Local Development Guide](LOCAL_DEVELOPMENT_GUIDE.md)
   - [Deployment Guide](DEPLOYMENT.md)
   - [FastAPI Documentation](https://fastapi.tiangolo.com/)
   - [Next.js Documentation](https://nextjs.org/docs)
