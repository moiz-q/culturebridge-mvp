# CultureBridge MVP

CultureBridge is an AI-powered platform that connects intercultural coaches with expats, diplomats, and global nomads seeking cultural adaptation support. The platform features intelligent AI-driven coach matching, secure payment processing, community engagement tools, and comprehensive admin analytics.

## Features

- **AI-Powered Matching**: OpenAI-based matching engine analyzing 20+ factors to connect clients with ideal coaches
- **Secure Authentication**: JWT-based authentication with role-based access control (Client, Coach, Admin)
- **Booking & Payments**: Complete session booking system with Stripe integration
- **Calendar Integration**: Sync bookings with Google Calendar and Outlook
- **Community Features**: Forums, discussions, and resource library for user engagement
- **Admin Dashboard**: Analytics, user management, and content moderation tools
- **GDPR Compliant**: Data export and deletion capabilities

## Project Structure

```
culturebridge-mvp/
├── backend/              # FastAPI backend application
│   ├── app/             # Application code
│   │   ├── models/      # SQLAlchemy database models
│   │   ├── schemas/     # Pydantic validation schemas
│   │   ├── routers/     # API endpoint handlers
│   │   ├── services/    # Business logic layer
│   │   ├── repositories/# Data access layer
│   │   ├── middleware/  # Custom middleware
│   │   └── utils/       # Utility functions
│   ├── tests/           # Backend tests
│   ├── alembic/         # Database migrations
│   ├── migration/       # Phase 1 to Phase 2 data migration
│   ├── Dockerfile       # Backend container
│   └── requirements.txt # Python dependencies
├── frontend/            # Next.js frontend application
│   ├── src/            # Source code
│   │   ├── app/        # Next.js pages (App Router)
│   │   ├── components/ # React components
│   │   ├── contexts/   # React contexts
│   │   └── lib/        # Utilities and API client
│   ├── public/         # Static assets
│   ├── Dockerfile      # Frontend container
│   └── package.json    # Node dependencies
├── infrastructure/      # Infrastructure as Code
│   └── terraform/      # AWS infrastructure definitions
├── docs/               # Additional documentation
├── scripts/            # Deployment and utility scripts
└── docker-compose.yml  # Local development setup
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Relational database
- **SQLAlchemy**: ORM
- **Redis**: Caching layer
- **OpenAI**: AI matching engine
- **Stripe**: Payment processing
- **AWS S3**: File storage

### Frontend
- **Next.js 14**: React framework
- **TypeScript**: Type-safe JavaScript
- **TailwindCSS**: Utility-first CSS
- **Axios**: HTTP client

## Quick Start

### Prerequisites

**Required:**
- Docker 20.10+ and Docker Compose 2.0+
- Git

**For Local Development (Optional):**
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Option 1: Docker Compose (Recommended for Development)

This is the fastest way to get the entire stack running locally.

1. **Clone the repository**:
```bash
git clone https://github.com/moiz-q/culturebridge-mvp.git
cd culturebridge-mvp
```

2. **Set up environment variables**:
```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env.local
```

3. **Configure required API keys** in `backend/.env`:
```bash
# Required for core functionality
OPENAI_API_KEY=your_openai_api_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

4. **Start all services**:
```bash
docker-compose up -d
```

This starts:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- Backend API (port 8000)
- Frontend app (port 3000)

5. **Run database migrations**:
```bash
docker-compose exec backend alembic upgrade head
```

6. **Access the applications**:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Alternative API Docs**: http://localhost:8000/redoc

7. **Create an admin user** (optional):
```bash
docker-compose exec backend python -c "
from app.database import SessionLocal
from app.models.user import User
from app.utils.jwt_utils import hash_password
import uuid

db = SessionLocal()
admin = User(
    id=uuid.uuid4(),
    email='admin@culturebridge.com',
    password_hash=hash_password('Admin123!'),
    role='admin',
    is_active=True,
    email_verified=True
)
db.add(admin)
db.commit()
print('Admin user created: admin@culturebridge.com / Admin123!')
"
```

### Option 2: Local Development (Without Docker)

For development with hot-reloading and debugging.

#### Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Set up database**:
```bash
# Create database (if using local PostgreSQL)
createdb culturebridge

# Run migrations
alembic upgrade head
```

6. **Start development server**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Set up environment**:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

4. **Start development server**:
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## Development Workflow

### Making Code Changes

1. **Create a feature branch**:
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes** following the project structure:
   - Backend API routes: `backend/app/routers/`
   - Business logic: `backend/app/services/`
   - Database models: `backend/app/models/`
   - Frontend pages: `frontend/src/app/`
   - React components: `frontend/src/components/`

3. **Database schema changes**:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

4. **Run tests**:
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

5. **Commit and push**:
```bash
git add .
git commit -m "Description of changes"
git push origin feature/your-feature-name
```

### Testing

**Backend Testing**:
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_signup
```

**Frontend Testing**:
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

### Code Quality

**Backend Linting**:
```bash
cd backend

# Format code
black app/

# Check linting
flake8 app/

# Type checking
mypy app/
```

**Frontend Linting**:
```bash
cd frontend

# Lint code
npm run lint

# Fix linting issues
npm run lint -- --fix
```

## Environment Variables

### Backend Environment Variables

See `backend/.env.example` for all available options. Key variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/culturebridge
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# External Services
OPENAI_API_KEY=sk-...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
S3_BUCKET_NAME=culturebridge-uploads

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

### Frontend Environment Variables

See `frontend/.env.example` for all available options:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

## Documentation

### API Documentation
- **Interactive API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **Comprehensive Guide**: `backend/API_DOCUMENTATION.md`

### Project Documentation
- **Design Document**: `.kiro/specs/culturebridge-mvp/design.md`
- **Requirements**: `.kiro/specs/culturebridge-mvp/requirements.md`
- **Implementation Tasks**: `.kiro/specs/culturebridge-mvp/tasks.md`
- **Deployment Guide**: `docs/DEPLOYMENT.md`
- **CI/CD Guide**: `docs/CI-CD.md`

### Feature-Specific Guides
- **Authentication**: `backend/AUTH_QUICK_START.md`
- **Matching Engine**: `backend/MATCHING_QUICK_START.md`
- **Booking System**: `backend/BOOKING_QUICK_START.md`
- **Payment Processing**: `backend/PAYMENT_QUICK_START.md`
- **Community Features**: `backend/COMMUNITY_QUICK_START.md`
- **Admin Dashboard**: `backend/ADMIN_QUICK_START.md`
- **Data Migration**: `backend/MIGRATION_QUICK_START.md`

## Deployment

For production deployment instructions, see:
- **AWS Deployment**: `docs/DEPLOYMENT.md`
- **CI/CD Setup**: `docs/CI-CD.md`
- **Deployment Checklist**: `docs/DEPLOYMENT_CHECKLIST.md`

Quick deployment commands:
```bash
# Deploy to staging
./scripts/deploy.sh staging

# Deploy to production (requires approval)
./scripts/deploy.sh production

# Rollback deployment
./scripts/rollback.sh production
```

## Troubleshooting

### Common Issues

**Database connection errors**:
```bash
# Check if PostgreSQL is running
docker-compose ps

# View database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head
```

**Redis connection errors**:
```bash
# Check if Redis is running
docker-compose ps

# View Redis logs
docker-compose logs redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

**Port already in use**:
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in docker-compose.yml
```

**Module not found errors**:
```bash
# Backend: Reinstall dependencies
cd backend
pip install -r requirements.txt

# Frontend: Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

For more troubleshooting help, see `docs/DEPLOYMENT.md#troubleshooting`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Support

- **Email**: support@culturebridge.com
- **Documentation**: https://docs.culturebridge.com
- **Issue Tracker**: https://github.com/moiz-q/culturebridge-mvp/issues

## License

Proprietary - All rights reserved. Copyright © 2025 CultureBridge Inc.
