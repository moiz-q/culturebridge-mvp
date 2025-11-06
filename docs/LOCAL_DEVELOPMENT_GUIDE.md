# Local Development Setup Guide

This guide provides detailed instructions for setting up the CultureBridge development environment on your local machine.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Running the Application](#running-the-application)
4. [Development Tools](#development-tools)
5. [Testing](#testing)
6. [Debugging](#debugging)
7. [Common Tasks](#common-tasks)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

#### 1. Docker and Docker Compose

**macOS**:
```bash
# Install Docker Desktop
brew install --cask docker
```

**Windows**:
- Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)

**Linux**:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

Verify installation:
```bash
docker --version
docker-compose --version
```

#### 2. Git

**macOS**:
```bash
brew install git
```

**Windows**:
- Download from [git-scm.com](https://git-scm.com/download/win)

**Linux**:
```bash
sudo apt-get install git  # Debian/Ubuntu
sudo yum install git      # CentOS/RHEL
```

### Optional (For Local Development Without Docker)

#### Python 3.11+

**macOS**:
```bash
brew install python@3.11
```

**Windows**:
- Download from [python.org](https://www.python.org/downloads/)

**Linux**:
```bash
sudo apt-get install python3.11 python3.11-venv  # Debian/Ubuntu
```

#### Node.js 18+

**macOS**:
```bash
brew install node@18
```

**Windows**:
- Download from [nodejs.org](https://nodejs.org/)

**Linux**:
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### PostgreSQL 15+

**macOS**:
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Windows**:
- Download from [postgresql.org](https://www.postgresql.org/download/windows/)

**Linux**:
```bash
sudo apt-get install postgresql-15
```

#### Redis 7+

**macOS**:
```bash
brew install redis
brew services start redis
```

**Windows**:
- Download from [redis.io](https://redis.io/download) or use WSL

**Linux**:
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/moiz-q/culturebridge-mvp.git
cd culturebridge-mvp
```

### 2. Set Up Environment Variables

#### Backend Environment

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` with your configuration:

```bash
# Database (use localhost if running locally, postgres if using Docker)
DATABASE_URL=postgresql://culturebridge:password@localhost:5432/culturebridge

# Redis
REDIS_URL=redis://localhost:6379

# JWT Secret (generate a secure random string)
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# OpenAI API Key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your-key-here

# Stripe Keys (get from https://dashboard.stripe.com/test/apikeys)
STRIPE_SECRET_KEY=sk_test_your-key-here
STRIPE_WEBHOOK_SECRET=whsec_your-secret-here

# AWS Credentials (for S3 file uploads)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=culturebridge-dev-uploads

# Email Configuration (use Gmail for development)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000
```

#### Frontend Environment

```bash
cd ../frontend
cp .env.example .env.local
```

Edit `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your-key-here
```

### 3. Obtain Required API Keys

#### OpenAI API Key

1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new secret key
5. Copy the key to `OPENAI_API_KEY` in `backend/.env`

#### Stripe API Keys

1. Go to https://dashboard.stripe.com/
2. Sign up or log in
3. Switch to Test Mode (toggle in top right)
4. Navigate to Developers > API Keys
5. Copy "Secret key" to `STRIPE_SECRET_KEY`
6. Copy "Publishable key" to frontend `.env.local`
7. For webhook secret:
   ```bash
   # Install Stripe CLI
   brew install stripe/stripe-cli/stripe  # macOS
   
   # Login
   stripe login
   
   # Forward webhooks to local server
   stripe listen --forward-to localhost:8000/payment/webhook
   
   # Copy the webhook signing secret to STRIPE_WEBHOOK_SECRET
   ```

#### AWS Credentials (for S3)

1. Go to AWS Console > IAM
2. Create a new user with S3 access
3. Generate access keys
4. Create an S3 bucket for development
5. Copy credentials to `backend/.env`

## Running the Application

### Option A: Using Docker Compose (Recommended)

This is the easiest way to get everything running:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Run database migrations
docker-compose exec backend alembic upgrade head

# Create admin user
docker-compose exec backend python -c "
from app.database import SessionLocal
from app.models.user import User
from app.utils.jwt_utils import hash_password
import uuid

db = SessionLocal()
admin = User(
    id=uuid.uuid4(),
    email='admin@test.com',
    password_hash=hash_password('Admin123!'),
    role='admin',
    is_active=True,
    email_verified=True
)
db.add(admin)
db.commit()
print('Admin created: admin@test.com / Admin123!')
"

# Stop all services
docker-compose down

# Stop and remove volumes (reset database)
docker-compose down -v
```

Access the applications:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option B: Running Locally (Without Docker)

#### Start Backend

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies (first time only)
pip install -r requirements.txt

# Run migrations (first time only)
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Frontend

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

## Development Tools

### Backend Development

#### Database Management

**View database with psql**:
```bash
# Using Docker
docker-compose exec postgres psql -U culturebridge -d culturebridge

# Local PostgreSQL
psql -U culturebridge -d culturebridge
```

**Common psql commands**:
```sql
\dt              -- List tables
\d users         -- Describe users table
\q               -- Quit
```

**Create migration**:
```bash
cd backend
alembic revision --autogenerate -m "Add new column to users"
alembic upgrade head
```

**Rollback migration**:
```bash
alembic downgrade -1
```

#### Redis Management

**Connect to Redis**:
```bash
# Using Docker
docker-compose exec redis redis-cli

# Local Redis
redis-cli
```

**Common Redis commands**:
```
KEYS *           # List all keys
GET key          # Get value
DEL key          # Delete key
FLUSHALL         # Clear all data
```

#### API Testing

**Using curl**:
```bash
# Health check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"Admin123!"}'

# Authenticated request
curl http://localhost:8000/profile \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Using HTTPie** (more user-friendly):
```bash
# Install
pip install httpie

# Login
http POST localhost:8000/auth/login email=admin@test.com password=Admin123!

# Authenticated request
http GET localhost:8000/profile Authorization:"Bearer YOUR_TOKEN"
```

### Frontend Development

#### React DevTools

Install browser extension:
- [Chrome](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi)
- [Firefox](https://addons.mozilla.org/en-US/firefox/addon/react-devtools/)

#### Next.js DevTools

Built into Next.js 14. Access at http://localhost:3000 (look for Next.js icon in bottom right)

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
open htmlcov/index.html  # View coverage report

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_signup

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch

# Run specific test file
npm test -- src/components/CoachCard.test.tsx
```

## Debugging

### Backend Debugging

#### Using VS Code

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": false,
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

#### Using pdb

Add breakpoint in code:
```python
import pdb; pdb.set_trace()
```

### Frontend Debugging

#### Using VS Code

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js: debug server-side",
      "type": "node-terminal",
      "request": "launch",
      "command": "npm run dev",
      "cwd": "${workspaceFolder}/frontend"
    }
  ]
}
```

#### Using Browser DevTools

1. Open browser DevTools (F12)
2. Go to Sources tab
3. Set breakpoints in source code
4. Refresh page to hit breakpoints

## Common Tasks

### Reset Database

```bash
# Using Docker
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head

# Local PostgreSQL
dropdb culturebridge
createdb culturebridge
cd backend
alembic upgrade head
```

### Seed Test Data

```bash
cd backend
python scripts/seed_data.py
```

### Clear Redis Cache

```bash
# Using Docker
docker-compose exec redis redis-cli FLUSHALL

# Local Redis
redis-cli FLUSHALL
```

### Update Dependencies

**Backend**:
```bash
cd backend
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

**Frontend**:
```bash
cd frontend
npm update
npm audit fix
```

### Run Linters

**Backend**:
```bash
cd backend
black app/              # Format code
flake8 app/            # Check style
mypy app/              # Type checking
```

**Frontend**:
```bash
cd frontend
npm run lint           # Check linting
npm run lint -- --fix  # Fix issues
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 PID  # macOS/Linux
taskkill /PID PID /F  # Windows
```

### Database Connection Errors

```bash
# Check if PostgreSQL is running
docker-compose ps
# or
pg_isready

# Check connection string in .env
# Ensure DATABASE_URL matches your setup
```

### Redis Connection Errors

```bash
# Check if Redis is running
docker-compose ps
# or
redis-cli ping

# Should return PONG
```

### Module Not Found Errors

**Backend**:
```bash
cd backend
pip install -r requirements.txt
```

**Frontend**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Permission Errors (Docker)

```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Or run Docker commands with sudo
sudo docker-compose up
```

### Alembic Migration Errors

```bash
# Check current migration version
alembic current

# View migration history
alembic history

# Downgrade to specific version
alembic downgrade <revision>

# Upgrade to latest
alembic upgrade head
```

## Next Steps

- Read the [API Documentation](../backend/API_DOCUMENTATION.md)
- Review [Deployment Guide](DEPLOYMENT.md)
- Check [CI/CD Setup](CI-CD.md)
- Explore feature-specific guides in `backend/` directory

## Getting Help

- Check existing documentation in `docs/` and `backend/`
- Review GitHub issues
- Contact the development team
- Email: dev-support@culturebridge.com
