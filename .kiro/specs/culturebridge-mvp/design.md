# Design Document

## Overview

CultureBridge Phase 2 is a full-stack web application built with modern technologies to deliver a scalable, secure, and intelligent coach-matching platform. The architecture follows a three-tier model with a React/Next.js frontend, FastAPI backend, and PostgreSQL database, enhanced by OpenAI integration for AI-driven matching.

**Technology Stack:**
- Frontend: Next.js 14 (React 18, TypeScript, TailwindCSS)
- Backend: FastAPI (Python 3.11+)
- Database: PostgreSQL 15
- AI: OpenAI API (GPT-4 for embeddings and scoring)
- Auth: JWT with bcrypt password hashing
- Payments: Stripe API
- Storage: AWS S3 for file uploads
- Hosting: AWS (ECS with Docker, RDS, CloudFront)
- CI/CD: GitHub Actions

## Architecture

### High-Level Architecture Diagram

```mermaid
graph TB
    Client[Web Browser] --> CDN[CloudFront CDN]
    CDN --> FE[Next.js Frontend]
    FE --> ALB[Application Load Balancer]
    ALB --> API1[FastAPI Instance 1]
    ALB --> API2[FastAPI Instance 2]
    API1 --> DB[(PostgreSQL RDS)]
    API2 --> DB
    API1 --> Redis[(Redis Cache)]
    API2 --> Redis
    API1 --> S3[S3 Bucket]
    API2 --> S3
    API1 --> OpenAI[OpenAI API]
    API2 --> OpenAI
    API1 --> Stripe[Stripe API]
    API2 --> Stripe
    API1 --> Email[Email Service]
    API2 --> Email
```

### System Layers

1. **Presentation Layer**: Next.js SSR/SSG with React components
2. **API Layer**: FastAPI RESTful endpoints with Pydantic validation
3. **Business Logic Layer**: Service classes for matching, booking, payments
4. **Data Access Layer**: SQLAlchemy ORM with repository pattern
5. **External Services Layer**: OpenAI, Stripe, AWS S3, Email providers


## Components and Interfaces

### Frontend Components

**Page Structure:**
- `/` - Landing page with hero, features, testimonials
- `/auth/signup` - Registration with role selection
- `/auth/login` - Login form
- `/dashboard` - Role-specific dashboard (Client/Coach/Admin)
- `/profile` - User profile management
- `/coaches` - Browse and search coaches
- `/booking` - Session booking flow
- `/community` - Forum and discussions
- `/resources` - Resource library
- `/admin` - Admin console (role-restricted)

**Key React Components:**
- `AuthProvider` - Context for authentication state and JWT management
- `ProtectedRoute` - HOC for role-based route protection
- `CoachCard` - Display coach profile with match score
- `BookingCalendar` - Interactive calendar for session scheduling
- `PaymentForm` - Stripe Elements integration
- `ForumPost` - Forum post display with upvote/comment
- `AdminTable` - Reusable data table with CRUD actions
- `MatchResults` - AI match results with confidence visualization

### Backend API Structure

**Directory Layout:**
```
backend/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Environment configuration
│   ├── database.py             # Database connection
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── booking.py
│   │   ├── payment.py
│   │   └── community.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py
│   │   ├── profile.py
│   │   ├── booking.py
│   │   └── community.py
│   ├── routers/                # API route handlers
│   │   ├── auth.py
│   │   ├── coaches.py
│   │   ├── matching.py
│   │   ├── booking.py
│   │   ├── payment.py
│   │   ├── community.py
│   │   └── admin.py
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   ├── matching_service.py
│   │   ├── booking_service.py
│   │   ├── payment_service.py
│   │   └── email_service.py
│   ├── repositories/           # Data access layer
│   │   ├── user_repository.py
│   │   ├── coach_repository.py
│   │   └── booking_repository.py
│   ├── middleware/             # Custom middleware
│   │   ├── auth_middleware.py
│   │   └── logging_middleware.py
│   └── utils/                  # Utilities
│       ├── jwt_utils.py
│       ├── validators.py
│       └── s3_utils.py
├── tests/                      # Test suite
├── alembic/                    # Database migrations
└── requirements.txt
```

### API Endpoints

**Authentication (`/auth`)**
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Authenticate and get JWT
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/reset-password` - Request password reset
- `POST /auth/reset-password/confirm` - Confirm password reset

**Coaches (`/coaches`)**
- `GET /coaches` - List coaches with filters (language, country, expertise)
- `GET /coaches/{id}` - Get coach details
- `PUT /coaches/{id}` - Update coach profile (coach only)
- `GET /coaches/{id}/availability` - Get coach availability

**Matching (`/match`)**
- `POST /match` - Get AI-generated coach matches
- `GET /match/cache/{client_id}` - Get cached match results

**Booking (`/booking`)**
- `POST /booking` - Create new booking
- `GET /booking/{id}` - Get booking details
- `GET /booking/client/{client_id}` - Get client bookings
- `GET /booking/coach/{coach_id}` - Get coach bookings
- `PATCH /booking/{id}/status` - Update booking status
- `DELETE /booking/{id}` - Cancel booking

**Payment (`/payment`)**
- `POST /payment/checkout` - Create Stripe checkout session
- `POST /payment/webhook` - Stripe webhook handler
- `GET /payment/{id}` - Get payment details

**Community (`/community`)**
- `GET /community/posts` - List forum posts with pagination
- `POST /community/posts` - Create new post
- `GET /community/posts/{id}` - Get post details
- `POST /community/posts/{id}/comment` - Add comment
- `POST /community/posts/{id}/upvote` - Upvote post
- `GET /community/resources` - List resources with filters
- `POST /community/resources/{id}/bookmark` - Bookmark resource

**Admin (`/admin`)**
- `GET /admin/metrics` - Get platform analytics
- `GET /admin/users` - List all users with filters
- `PATCH /admin/users/{id}` - Update user (role, status)
- `DELETE /admin/users/{id}` - Delete user
- `GET /admin/bookings` - List all bookings
- `DELETE /admin/posts/{id}` - Delete forum post
- `GET /admin/revenue` - Revenue reports


## Data Models

### Database Schema

**Users Table**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('client', 'coach', 'admin')),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Client Profiles Table**
```sql
CREATE TABLE client_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    photo_url VARCHAR(500),
    phone VARCHAR(20),
    timezone VARCHAR(50),
    quiz_data JSONB NOT NULL,
    preferences JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);
```

**Coach Profiles Table**
```sql
CREATE TABLE coach_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    photo_url VARCHAR(500),
    bio TEXT,
    intro_video_url VARCHAR(500),
    expertise TEXT[],
    languages TEXT[],
    countries TEXT[],
    hourly_rate DECIMAL(10,2) CHECK (hourly_rate >= 25 AND hourly_rate <= 500),
    currency VARCHAR(3) DEFAULT 'USD',
    availability JSONB,
    rating DECIMAL(3,2) DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);
```

**Bookings Table**
```sql
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES users(id),
    coach_id UUID REFERENCES users(id),
    session_datetime TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    status VARCHAR(20) CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
    payment_id UUID,
    meeting_link VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Payments Table**
```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID REFERENCES bookings(id),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) CHECK (status IN ('pending', 'succeeded', 'failed', 'refunded')),
    stripe_session_id VARCHAR(255),
    stripe_payment_intent_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Posts Table**
```sql
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    post_type VARCHAR(20) CHECK (post_type IN ('discussion', 'question', 'announcement')),
    is_private BOOLEAN DEFAULT false,
    upvotes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Comments Table**
```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    author_id UUID REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Resources Table**
```sql
CREATE TABLE resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    resource_type VARCHAR(20) CHECK (resource_type IN ('article', 'video', 'document')),
    url VARCHAR(500) NOT NULL,
    tags TEXT[],
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Bookmarks Table**
```sql
CREATE TABLE bookmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    resource_id UUID REFERENCES resources(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, resource_id)
);
```

**Match Cache Table**
```sql
CREATE TABLE match_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES users(id),
    match_results JSONB NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### SQLAlchemy Models

Models will use SQLAlchemy ORM with relationships:
- `User` has one `ClientProfile` or `CoachProfile`
- `Booking` belongs to `User` (client) and `User` (coach)
- `Payment` belongs to `Booking`
- `Post` belongs to `User` and has many `Comments`
- `Resource` can be bookmarked by many `Users`


## AI Matching Engine Design

### Matching Algorithm Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Cache
    participant MatchService
    participant OpenAI
    participant DB

    Client->>API: POST /match
    API->>Cache: Check cached results
    alt Cache Hit
        Cache-->>API: Return cached matches
        API-->>Client: Return matches
    else Cache Miss
        API->>MatchService: Generate matches
        MatchService->>DB: Fetch client quiz_data
        MatchService->>DB: Fetch all active coaches
        MatchService->>MatchService: Normalize data
        MatchService->>OpenAI: Generate embeddings
        OpenAI-->>MatchService: Return embeddings
        MatchService->>MatchService: Calculate scores
        MatchService->>MatchService: Rank coaches
        MatchService->>Cache: Store results (24h TTL)
        MatchService-->>API: Return top 10 matches
        API-->>Client: Return matches
    end
```

### Matching Factors (20+)

**Client Quiz Data:**
1. Target countries (array)
2. Cultural adaptation goals (array)
3. Preferred languages (array)
4. Industry/profession
5. Family status
6. Previous expat experience (boolean)
7. Timeline urgency (1-5 scale)
8. Budget range
9. Preferred coaching style (directive/collaborative/supportive)
10. Specific challenges (array)

**Coach Profile Data:**
11. Expertise areas (array)
12. Languages spoken (array)
13. Countries of experience (array)
14. Coaching specializations (array)
15. Years of experience
16. Hourly rate
17. Availability windows
18. Rating score
19. Total completed sessions
20. Verification status

**Derived Factors:**
21. Language overlap score
22. Country experience match
23. Goal-expertise alignment
24. Budget compatibility
25. Availability match

### Scoring Algorithm

**Step 1: Data Normalization**
- Convert categorical data to embeddings using OpenAI
- Normalize numerical values (0-1 scale)
- Create feature vectors for clients and coaches

**Step 2: Similarity Calculation**
```python
def calculate_match_score(client_vector, coach_vector, weights):
    # Weighted cosine similarity
    language_score = cosine_similarity(client.languages, coach.languages) * weights['language']
    country_score = cosine_similarity(client.countries, coach.countries) * weights['country']
    goal_score = cosine_similarity(client.goals, coach.expertise) * weights['goals']
    
    # Budget compatibility
    budget_score = 1.0 if coach.rate <= client.budget_max else 0.5
    
    # Availability match
    availability_score = check_availability_overlap(client.timezone, coach.availability)
    
    # Weighted sum
    total_score = (
        language_score * 0.25 +
        country_score * 0.20 +
        goal_score * 0.30 +
        budget_score * 0.15 +
        availability_score * 0.10
    ) * 100
    
    return min(total_score, 100)
```

**Step 3: Ranking**
- Sort coaches by match score (descending)
- Apply secondary sort by rating for ties
- Return top 10 with confidence scores

### Caching Strategy

- Cache key: `match:{client_id}:{hash(quiz_data)}`
- TTL: 24 hours
- Invalidation: On client profile update or coach profile changes
- Storage: Redis for fast retrieval


## Authentication & Authorization

### JWT Token Structure

**Access Token (24h expiry):**
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "client|coach|admin",
  "exp": 1234567890,
  "iat": 1234567890
}
```

**Refresh Token (7 days expiry):**
- Stored in httpOnly cookie
- Used to obtain new access token
- Rotated on each refresh

### Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant DB

    User->>Frontend: Enter credentials
    Frontend->>API: POST /auth/login
    API->>DB: Verify credentials
    DB-->>API: User data
    API->>API: Generate JWT
    API-->>Frontend: Access token + Refresh token
    Frontend->>Frontend: Store access token
    Frontend->>API: API request + Bearer token
    API->>API: Verify JWT
    API-->>Frontend: Protected resource
```

### Role-Based Access Control (RBAC)

**Permission Matrix:**

| Endpoint | Client | Coach | Admin |
|----------|--------|-------|-------|
| GET /coaches | ✓ | ✓ | ✓ |
| POST /match | ✓ | ✗ | ✓ |
| POST /booking | ✓ | ✗ | ✓ |
| GET /booking/coach/:id | ✗ | ✓ (own) | ✓ |
| PUT /coaches/:id | ✗ | ✓ (own) | ✓ |
| GET /admin/* | ✗ | ✗ | ✓ |
| POST /community/posts | ✓ | ✓ | ✓ |
| DELETE /community/posts/:id | ✗ | ✗ | ✓ |

**Middleware Implementation:**
- `@require_auth` - Validates JWT token
- `@require_role(['admin'])` - Checks user role
- `@require_ownership` - Validates resource ownership


## Payment Integration

### Stripe Checkout Flow

```mermaid
sequenceDiagram
    participant Client
    participant Frontend
    participant API
    participant Stripe
    participant DB

    Client->>Frontend: Select time slot
    Frontend->>API: POST /booking
    API->>DB: Create pending booking
    API-->>Frontend: Booking ID
    Frontend->>API: POST /payment/checkout
    API->>Stripe: Create checkout session
    Stripe-->>API: Session URL
    API-->>Frontend: Redirect URL
    Frontend->>Stripe: Redirect to checkout
    Client->>Stripe: Complete payment
    Stripe->>API: Webhook: payment.succeeded
    API->>DB: Update booking status
    API->>DB: Create payment record
    API->>API: Send confirmation emails
    Stripe-->>Client: Redirect to success page
```

### Webhook Handling

**Events to Handle:**
- `checkout.session.completed` - Payment successful
- `payment_intent.succeeded` - Payment confirmed
- `payment_intent.payment_failed` - Payment failed
- `charge.refunded` - Refund processed

**Webhook Security:**
- Verify Stripe signature using webhook secret
- Idempotency: Check if event already processed
- Retry logic: Handle webhook failures gracefully

### Payment Data Model

```python
class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(UUID, primary_key=True)
    booking_id = Column(UUID, ForeignKey("bookings.id"))
    amount = Column(Numeric(10, 2))
    currency = Column(String(3), default="USD")
    status = Column(Enum(PaymentStatus))
    stripe_session_id = Column(String(255))
    stripe_payment_intent_id = Column(String(255))
    metadata = Column(JSONB)  # Store additional Stripe data
```


## Error Handling

### Error Response Format

All API errors return consistent JSON structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "value": "invalid-email"
    },
    "timestamp": "2025-11-05T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

### Error Codes

**Client Errors (4xx):**
- `VALIDATION_ERROR` (400) - Invalid input data
- `UNAUTHORIZED` (401) - Missing or invalid token
- `FORBIDDEN` (403) - Insufficient permissions
- `NOT_FOUND` (404) - Resource not found
- `CONFLICT` (409) - Resource already exists
- `RATE_LIMIT_EXCEEDED` (429) - Too many requests

**Server Errors (5xx):**
- `INTERNAL_ERROR` (500) - Unexpected server error
- `SERVICE_UNAVAILABLE` (503) - External service down
- `GATEWAY_TIMEOUT` (504) - External service timeout

### Exception Handling Strategy

**FastAPI Exception Handlers:**
```python
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request.state.request_id
            }
        }
    )
```

**Retry Logic:**
- OpenAI API: 3 retries with exponential backoff
- Stripe API: 2 retries with 1s delay
- Database: Connection pool with automatic reconnection
- Email: Queue failed emails for retry (max 5 attempts)

**Fallback Mechanisms:**
- AI Matching: Return top-rated coaches if OpenAI fails
- Payment: Show manual payment instructions if Stripe down
- Email: Log to database if email service fails

### Logging Strategy

**Log Levels:**
- `DEBUG` - Development only
- `INFO` - Request/response, business events
- `WARNING` - Recoverable errors, fallbacks triggered
- `ERROR` - Unhandled exceptions, service failures
- `CRITICAL` - System-wide failures

**Structured Logging Format:**
```json
{
  "timestamp": "2025-11-05T10:30:00Z",
  "level": "ERROR",
  "service": "matching-service",
  "request_id": "req_abc123",
  "user_id": "user_xyz",
  "message": "OpenAI API timeout",
  "error": {
    "type": "TimeoutError",
    "stack_trace": "..."
  },
  "context": {
    "endpoint": "/match",
    "duration_ms": 10500
  }
}
```

**Log Destinations:**
- Development: Console (pretty-printed)
- Production: AWS CloudWatch Logs
- Errors: Separate error log stream + alerts


## Testing Strategy

### Test Pyramid

```
        /\
       /  \
      / E2E \         10% - End-to-end tests
     /______\
    /        \
   /Integration\      30% - Integration tests
  /____________\
 /              \
/   Unit Tests   \    60% - Unit tests
/__________________\
```

### Unit Tests

**Coverage Target: 80%+**

**Backend (PyTest):**
- Models: Validation, relationships, methods
- Services: Business logic, edge cases
- Repositories: CRUD operations (mocked DB)
- Utils: JWT generation, validators, formatters

**Frontend (Jest + React Testing Library):**
- Components: Rendering, user interactions
- Hooks: Custom hooks behavior
- Utils: Formatters, validators
- Context: State management

**Example Test:**
```python
def test_calculate_match_score():
    client = ClientFactory(
        languages=["English", "Spanish"],
        countries=["Spain"],
        goals=["career_transition"]
    )
    coach = CoachFactory(
        languages=["English", "Spanish", "French"],
        countries=["Spain", "France"],
        expertise=["career_coaching"]
    )
    
    score = matching_service.calculate_match_score(client, coach)
    
    assert score >= 80  # High match expected
    assert score <= 100
```

### Integration Tests

**API Integration Tests:**
- Full request/response cycle
- Database transactions
- Authentication flow
- External service mocks (Stripe, OpenAI)

**Example:**
```python
def test_booking_flow(client, db_session):
    # Create test user and coach
    user = create_test_user(role="client")
    coach = create_test_coach()
    
    # Authenticate
    token = get_auth_token(user)
    
    # Create booking
    response = client.post(
        "/booking",
        json={
            "coach_id": coach.id,
            "session_datetime": "2025-11-10T14:00:00Z"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["status"] == "pending"
    
    # Verify database
    booking = db_session.query(Booking).first()
    assert booking.client_id == user.id
```

### End-to-End Tests

**Playwright/Cypress Tests:**
- User registration and login
- Complete booking flow with Stripe test mode
- Forum post creation and interaction
- Admin dashboard operations

**Critical User Journeys:**
1. Client signs up → completes quiz → views matches → books session → pays
2. Coach signs up → completes profile → receives booking → confirms session
3. Admin logs in → views analytics → manages users → moderates content

### Test Data Management

**Factories (Factory Boy):**
- `UserFactory` - Generate test users
- `CoachFactory` - Generate coach profiles
- `BookingFactory` - Generate bookings
- `PaymentFactory` - Generate payment records

**Database Fixtures:**
- Use transactions for test isolation
- Reset database between tests
- Seed data for E2E tests

### CI/CD Testing Pipeline

**GitHub Actions Workflow:**
```yaml
name: Test & Deploy

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: pytest tests/unit --cov=app --cov-report=xml
      - name: Run integration tests
        run: pytest tests/integration
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  lint:
    runs-on: ubuntu-latest
    steps:
      - name: Run linters
        run: |
          flake8 app/
          black --check app/
          mypy app/
  
  deploy-staging:
    needs: [test, lint]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: ./deploy.sh staging
```


## Deployment & Infrastructure

### AWS Architecture

**Services Used:**
- **ECS (Elastic Container Service)**: Run FastAPI containers
- **RDS (PostgreSQL)**: Managed database with Multi-AZ
- **ElastiCache (Redis)**: Caching layer
- **S3**: File storage for uploads
- **CloudFront**: CDN for frontend and static assets
- **ALB (Application Load Balancer)**: Traffic distribution
- **Route 53**: DNS management
- **CloudWatch**: Logging and monitoring
- **Secrets Manager**: Store API keys and credentials
- **ACM**: SSL/TLS certificates

### Container Configuration

**Dockerfile (Backend):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Dockerfile (Frontend):**
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
RUN npm ci --production

EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Configuration

**Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/culturebridge
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://elasticache-endpoint:6379

# JWT
JWT_SECRET_KEY=<from-secrets-manager>
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# OpenAI
OPENAI_API_KEY=<from-secrets-manager>
OPENAI_MODEL=gpt-4

# Stripe
STRIPE_SECRET_KEY=<from-secrets-manager>
STRIPE_WEBHOOK_SECRET=<from-secrets-manager>

# AWS
AWS_REGION=us-east-1
S3_BUCKET_NAME=culturebridge-uploads

# Email
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=<from-secrets-manager>
SMTP_PASSWORD=<from-secrets-manager>

# App
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://culturebridge.com
```

### Scaling Configuration

**Auto Scaling:**
- Min instances: 2
- Max instances: 10
- Scale up: CPU > 70% for 2 minutes
- Scale down: CPU < 30% for 5 minutes

**Database:**
- Instance: db.t3.medium (2 vCPU, 4GB RAM)
- Storage: 100GB SSD with auto-scaling
- Backups: Daily automated backups, 7-day retention
- Read replicas: 1 for analytics queries

**Redis:**
- Instance: cache.t3.medium
- Max memory: 3.09 GB
- Eviction policy: allkeys-lru

### Monitoring & Alerts

**CloudWatch Metrics:**
- API latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Request count
- Database connections
- Cache hit rate
- OpenAI API latency

**Alerts:**
- Error rate > 5% for 5 minutes → PagerDuty
- API latency p95 > 500ms → Slack
- Database CPU > 80% → Email
- Failed deployments → Slack

**Health Checks:**
- Endpoint: `GET /health`
- Interval: 30 seconds
- Timeout: 5 seconds
- Unhealthy threshold: 3 consecutive failures

### CI/CD Pipeline

**Deployment Flow:**
```mermaid
graph LR
    A[Git Push] --> B[GitHub Actions]
    B --> C{Tests Pass?}
    C -->|No| D[Notify Developer]
    C -->|Yes| E[Build Docker Images]
    E --> F[Push to ECR]
    F --> G[Deploy to Staging]
    G --> H{Manual Approval}
    H -->|Approved| I[Deploy to Production]
    H -->|Rejected| J[Rollback]
    I --> K[Run Smoke Tests]
    K -->|Pass| L[Complete]
    K -->|Fail| M[Auto Rollback]
```

**Deployment Strategy:**
- Blue-Green deployment for zero downtime
- Database migrations run before deployment
- Rollback capability within 5 minutes

### Security Measures

**Network Security:**
- VPC with private subnets for database and cache
- Security groups: Allow only necessary ports
- WAF rules: Rate limiting, SQL injection protection

**Application Security:**
- HTTPS only (TLS 1.3)
- CORS configured for specific origins
- Input validation and sanitization
- SQL injection prevention via ORM
- XSS protection via Content Security Policy
- CSRF tokens for state-changing operations

**Data Security:**
- Encryption at rest (RDS, S3)
- Encryption in transit (TLS)
- Password hashing with bcrypt (12 rounds)
- Secrets stored in AWS Secrets Manager
- Regular security audits and dependency updates

### Backup & Disaster Recovery

**Backup Strategy:**
- Database: Automated daily backups, 7-day retention
- S3: Versioning enabled, cross-region replication
- Configuration: Infrastructure as Code (Terraform)

**Recovery Objectives:**
- RTO (Recovery Time Objective): 1 hour
- RPO (Recovery Point Objective): 24 hours

**Disaster Recovery Plan:**
1. Detect failure via monitoring
2. Assess impact and root cause
3. Restore from latest backup
4. Verify data integrity
5. Resume operations
6. Post-mortem analysis


## Migration Strategy

### Phase 1 to Phase 2 Migration

**Pre-Migration Steps:**
1. Audit Phase 1 data structure and quality
2. Create mapping document (Phase 1 fields → Phase 2 schema)
3. Set up Phase 2 staging environment
4. Develop and test migration scripts

**Data Export:**
```python
# Export from Bubble via API
def export_bubble_data():
    endpoints = [
        '/api/1.1/obj/user',
        '/api/1.1/obj/coach_profile',
        '/api/1.1/obj/booking',
        '/api/1.1/obj/payment'
    ]
    
    for endpoint in endpoints:
        data = requests.get(
            f"{BUBBLE_URL}{endpoint}",
            headers={"Authorization": f"Bearer {BUBBLE_API_KEY}"}
        )
        save_to_csv(endpoint, data.json())
```

**Field Mapping:**

| Phase 1 (Bubble) | Phase 2 (PostgreSQL) | Transformation |
|------------------|----------------------|----------------|
| User.email | users.email | Direct copy |
| User.password | users.password_hash | Re-hash with bcrypt |
| User.type | users.role | Map: "seeker" → "client" |
| CoachProfile.bio | coach_profiles.bio | Direct copy |
| CoachProfile.rate | coach_profiles.hourly_rate | Convert to decimal |
| Booking.date | bookings.session_datetime | Parse ISO format |
| Payment.amount | payments.amount | Convert to decimal |

**Migration Script:**
```python
def migrate_users(csv_file):
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                user = User(
                    id=uuid.uuid4(),
                    email=row['email'],
                    password_hash=bcrypt.hashpw(
                        row['password'].encode(), 
                        bcrypt.gensalt(12)
                    ),
                    role=map_role(row['type']),
                    created_at=parse_datetime(row['created_date'])
                )
                db.session.add(user)
                db.session.commit()
                log_success(user.id)
            except Exception as e:
                log_error(row['email'], str(e))
                db.session.rollback()
```

**Validation Steps:**
1. Row count verification (Phase 1 vs Phase 2)
2. Sample data comparison (10% random sample)
3. Referential integrity checks
4. Business logic validation (e.g., booking totals match)

**Cutover Plan:**
1. Announce maintenance window (2 hours)
2. Set Phase 1 to read-only mode
3. Run final incremental migration
4. Validate data integrity
5. Update DNS to point to Phase 2
6. Monitor for issues
7. Keep Phase 1 available for 30 days (read-only)

**Rollback Plan:**
- If critical issues detected within 1 hour
- Revert DNS to Phase 1
- Investigate and fix issues
- Schedule new cutover


## Performance Optimization

### Frontend Optimization

**Next.js Optimizations:**
- Static Site Generation (SSG) for landing pages
- Incremental Static Regeneration (ISR) for coach listings
- Server-Side Rendering (SSR) for personalized dashboards
- Image optimization with next/image
- Code splitting and lazy loading
- Bundle size monitoring (< 200KB initial load)

**Caching Strategy:**
- Browser cache: Static assets (1 year)
- CDN cache: Pages and API responses (5 minutes)
- Service worker: Offline support for key pages

**Performance Targets:**
- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.5s
- Cumulative Layout Shift (CLS): < 0.1

### Backend Optimization

**Database Optimization:**
- Indexes on frequently queried columns:
  - `users.email` (unique)
  - `bookings.client_id`, `bookings.coach_id`
  - `bookings.session_datetime`
  - `posts.created_at`
  - `coach_profiles.languages` (GIN index for arrays)
- Connection pooling (20 connections)
- Query optimization with EXPLAIN ANALYZE
- Materialized views for analytics

**API Optimization:**
- Response compression (gzip)
- Pagination for list endpoints (20 items per page)
- Field selection (sparse fieldsets)
- Rate limiting: 100 requests/minute per user
- Request deduplication for idempotent operations

**Caching Layers:**
1. **Application Cache (Redis):**
   - Match results: 24 hours
   - Coach listings: 5 minutes
   - User sessions: 24 hours
   
2. **Database Query Cache:**
   - Frequently accessed coach profiles
   - Static reference data

3. **CDN Cache:**
   - Static assets: 1 year
   - API responses (GET only): 1 minute

### Load Testing

**Test Scenarios:**
- 100 concurrent users browsing coaches
- 50 concurrent match requests
- 20 concurrent bookings with payments
- Sustained load: 1000 requests/minute for 1 hour

**Performance Benchmarks:**
- API latency p95: < 250ms
- Database query time p95: < 50ms
- OpenAI API call: < 5s (with timeout at 10s)
- Page load time: < 3s

**Tools:**
- Load testing: Apache JMeter or k6
- Profiling: Python cProfile, FastAPI profiler
- Monitoring: New Relic or DataDog APM


## Design Decisions & Rationale

### Technology Choices

**1. FastAPI vs Node.js/Express**
- **Decision**: FastAPI (Python)
- **Rationale**: 
  - Better integration with OpenAI Python SDK
  - Strong typing with Pydantic for data validation
  - Automatic API documentation (OpenAPI/Swagger)
  - Excellent async support for I/O-bound operations
  - Python ecosystem for data processing and ML

**2. PostgreSQL vs MongoDB**
- **Decision**: PostgreSQL
- **Rationale**:
  - Structured data with clear relationships
  - ACID compliance for payment transactions
  - Strong support for JSONB for flexible fields (quiz_data)
  - Mature ecosystem and tooling
  - Better for complex queries and analytics

**3. Next.js vs Create React App**
- **Decision**: Next.js
- **Rationale**:
  - SEO optimization with SSR/SSG
  - Built-in routing and API routes
  - Image optimization out of the box
  - Better performance with automatic code splitting
  - Production-ready with minimal configuration

**4. JWT vs Session-based Auth**
- **Decision**: JWT
- **Rationale**:
  - Stateless authentication (easier to scale)
  - Works well with microservices architecture
  - Mobile app support (future consideration)
  - Reduced database queries for auth checks

**5. Stripe vs PayPal**
- **Decision**: Stripe
- **Rationale**:
  - Better developer experience and documentation
  - More flexible API for custom flows
  - Strong webhook support
  - Better international support
  - Lower fees for platform model

### Architecture Patterns

**1. Repository Pattern**
- Separates data access logic from business logic
- Makes testing easier with mock repositories
- Allows switching data sources without changing business logic

**2. Service Layer**
- Encapsulates business logic
- Promotes code reuse across endpoints
- Easier to test complex workflows

**3. Dependency Injection**
- FastAPI's built-in DI for database sessions
- Improves testability and modularity
- Reduces coupling between components

### Scalability Considerations

**Horizontal Scaling:**
- Stateless API design allows multiple instances
- Load balancer distributes traffic
- Database connection pooling prevents bottlenecks

**Vertical Scaling:**
- Database can be upgraded to larger instances
- Redis cache reduces database load
- CDN offloads static content delivery

**Future Considerations:**
- Microservices: Split matching engine into separate service
- Message queue: Add RabbitMQ/SQS for async tasks
- Read replicas: Separate analytics queries from transactional load

### Security Considerations

**Defense in Depth:**
- Multiple layers: WAF, application validation, database constraints
- Principle of least privilege for database users
- Regular security audits and dependency updates

**Data Privacy:**
- GDPR compliance with data export/deletion
- Minimal data collection
- Encrypted storage for sensitive data
- Audit logs for data access

### Trade-offs

**1. Caching Match Results**
- **Pro**: Faster response, reduced OpenAI costs
- **Con**: Stale results if coach profiles change
- **Mitigation**: 24-hour TTL, cache invalidation on profile updates

**2. Monolithic vs Microservices**
- **Decision**: Start monolithic
- **Rationale**: Simpler to develop and deploy initially
- **Future**: Can extract services as needed (matching, payments)

**3. Real-time vs Polling**
- **Decision**: Polling for notifications initially
- **Rationale**: Simpler implementation, sufficient for MVP
- **Future**: WebSocket for real-time chat/notifications

