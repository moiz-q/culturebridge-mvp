# Implementation Plan

- [x] 1. Set up project structure and development environment





  - Initialize backend FastAPI project with directory structure (app/, tests/, alembic/)
  - Initialize frontend Next.js project with TypeScript and TailwindCSS
  - Create Docker configuration files (Dockerfile for backend and frontend)
  - Set up requirements.txt with core dependencies (FastAPI, SQLAlchemy, Pydantic, bcrypt, PyJWT, stripe, openai, boto3, redis)
  - Set up package.json with frontend dependencies (React, Next.js, TailwindCSS, Axios)
  - Create .env.example files for both backend and frontend with required environment variables
  - _Requirements: 8.2, 9.5_

- [x] 2. Implement database models and migrations




- [x] 2.1 Create SQLAlchemy base configuration and database connection


  - Write database.py with SQLAlchemy engine, session factory, and Base class
  - Implement connection pooling configuration (20 connections)
  - Create Alembic configuration for database migrations
  - _Requirements: 8.2_

- [x] 2.2 Implement User and Profile models


  - Create User model with fields (id, email, password_hash, role, is_active, email_verified, timestamps)
  - Create ClientProfile model with fields (user_id, personal info, quiz_data JSONB, preferences JSONB)
  - Create CoachProfile model with fields (user_id, bio, expertise array, languages array, countries array, pricing, availability JSONB, rating)
  - Define relationships between User and Profile models
  - Add model validation methods and constraints
  - _Requirements: 1.1, 2.1, 2.2, 3.1, 3.2, 3.4, 3.5_

- [x] 2.3 Implement Booking and Payment models


  - Create Booking model with fields (client_id, coach_id, session_datetime, duration, status, payment_id, meeting_link)
  - Create Payment model with fields (booking_id, amount, currency, status, stripe_session_id, stripe_payment_intent_id)
  - Define relationships between Booking, Payment, and User models
  - Add status enums and validation
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 2.4 Implement Community models


  - Create Post model with fields (author_id, title, content, post_type, is_private, upvotes, timestamps)
  - Create Comment model with fields (post_id, author_id, content, timestamp)
  - Create Resource model with fields (title, description, resource_type, url, tags array, created_by)
  - Create Bookmark model for user-resource relationships
  - Create MatchCache model for storing AI match results
  - _Requirements: 6.1, 6.2, 6.3_

- [x] 2.5 Create initial database migration


  - Generate Alembic migration for all models
  - Add database indexes (users.email, bookings.client_id, bookings.coach_id, posts.created_at, coach_profiles.languages GIN index)
  - Test migration up and down
  - _Requirements: 8.2_


- [x] 3. Implement authentication and authorization system



- [x] 3.1 Create JWT utilities and authentication service


  - Write jwt_utils.py with token generation, validation, and refresh logic
  - Implement password hashing with bcrypt (12 salt rounds)
  - Create auth_service.py with signup, login, and password reset methods
  - _Requirements: 1.1, 1.2, 1.4_

- [x] 3.2 Implement authentication middleware and dependencies


  - Create auth_middleware.py with JWT validation decorator
  - Implement role-based access control decorators (@require_role, @require_ownership)
  - Create FastAPI dependencies for current user extraction
  - _Requirements: 1.2, 7.3_

- [x] 3.3 Create authentication API endpoints


  - Implement POST /auth/signup endpoint with role assignment
  - Implement POST /auth/login endpoint returning JWT tokens
  - Implement POST /auth/refresh endpoint for token refresh
  - Implement POST /auth/reset-password and confirm endpoints
  - Create Pydantic schemas for request/response validation
  - _Requirements: 1.1, 1.2, 1.3, 1.5_
- [x] 4. Implement user profile management




- [ ] 4. Implement user profile management

- [x] 4.1 Create profile repositories


  - Write user_repository.py with CRUD operations for users
  - Write profile repositories for ClientProfile and CoachProfile
  - Implement query methods with filters and pagination
  - _Requirements: 2.1, 3.1_

- [x] 4.2 Implement profile API endpoints


  - Create GET /profile endpoint to fetch current user profile
  - Create PUT /profile endpoint to update profile data
  - Implement profile photo upload to S3 with size and format validation (5MB max, JPEG/PNG/WebP)
  - Create GET /coaches and GET /coaches/{id} endpoints with filtering
  - Create PUT /coaches/{id} endpoint for coach profile updates
  - Validate quiz data contains all 20 required factors
  - _Requirements: 2.1, 2.2, 2.3, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4.3 Implement GDPR compliance features


  - Create GET /profile/export endpoint to export user data as JSON
  - Create DELETE /profile endpoint to delete user account and associated data
  - Implement cascade deletion for related records
  - _Requirements: 2.4_

- [x] 5. Implement AI matching engine


- [x] 5.1 Create matching service with OpenAI integration


  - Write matching_service.py with data normalization methods
  - Implement OpenAI API integration for text embeddings
  - Create calculate_match_score function with weighted similarity calculation (language 25%, country 20%, goals 30%, budget 15%, availability 10%)
  - Implement ranking algorithm to return top 10 coaches with confidence scores
  - Add timeout handling (10 seconds) with fallback to top-rated coaches
  - _Requirements: 4.1, 4.2, 4.3, 4.5_

- [x] 5.2 Implement Redis caching for match results


  - Create cache utilities for Redis connection
  - Implement cache key generation (match:{client_id}:{hash(quiz_data)})
  - Add cache storage with 24-hour TTL
  - Implement cache invalidation on profile updates
  - _Requirements: 4.4_

- [x] 5.3 Create matching API endpoint


  - Implement POST /match endpoint with authentication
  - Integrate matching service with caching layer
  - Create Pydantic schemas for match request/response
  - Add error handling and fallback logic
  - _Requirements: 4.1, 4.3, 4.4, 4.5_

- [x] 6. Implement booking and calendar management



- [x] 6.1 Create booking service and repository


  - Write booking_repository.py with CRUD operations
  - Create booking_service.py with availability checking logic
  - Implement booking creation with status management (pending, confirmed, completed, cancelled)
  - Add validation for time slot availability
  - _Requirements: 5.1_

- [x] 6.2 Implement booking API endpoints


  - Create POST /booking endpoint to create pending bookings
  - Implement GET /booking/{id} endpoint for booking details
  - Create GET /booking/client/{client_id} and GET /booking/coach/{coach_id} endpoints
  - Implement PATCH /booking/{id}/status endpoint for status updates
  - Create DELETE /booking/{id} endpoint for cancellations
  - Add role-based access control for booking operations
  - _Requirements: 5.1_

- [x] 6.3 Implement calendar integration


  - Create calendar service for Google Calendar and Outlook integration
  - Implement OAuth flow for calendar connection
  - Add booking sync functionality to create calendar events
  - _Requirements: 5.5_

- [x] 7. Implement payment processing with Stripe




- [x] 7.1 Create payment service


  - Write payment_service.py with Stripe API integration
  - Implement Stripe checkout session creation
  - Add payment record creation in database
  - Implement idempotency handling for webhook events
  - _Requirements: 5.2, 5.3_

- [x] 7.2 Implement payment API endpoints


  - Create POST /payment/checkout endpoint to initiate Stripe checkout
  - Implement POST /payment/webhook endpoint for Stripe webhooks
  - Add webhook signature verification
  - Create GET /payment/{id} endpoint for payment details
  - Handle webhook events (checkout.session.completed, payment_intent.succeeded, payment_intent.payment_failed, charge.refunded)
  - Update booking status on successful payment
  - _Requirements: 5.2, 5.3_

- [x] 7.3 Implement email notifications


  - Create email_service.py with SMTP configuration
  - Implement confirmation email templates for clients and coaches
  - Add email sending on booking confirmation (within 2 minutes)
  - Implement retry logic for failed emails (max 5 attempts)
  - _Requirements: 5.4_
-

- [x] 8. Implement community features



- [x] 8.1 Create community repositories


  - Write repositories for Post, Comment, Resource, and Bookmark models
  - Implement query methods with pagination (20 items per page)
  - Add filtering by tags, content type, and visibility
  - _Requirements: 6.1, 6.3, 6.5_

- [x] 8.2 Implement forum API endpoints


  - Create POST /community/posts endpoint to create posts
  - Implement GET /community/posts endpoint with pagination and filters
  - Create GET /community/posts/{id} endpoint for post details
  - Implement POST /community/posts/{id}/comment endpoint
  - Create POST /community/posts/{id}/upvote endpoint
  - Add support for public and private forums
  - _Requirements: 6.1, 6.2, 6.4, 6.5_

- [x] 8.3 Implement resource library endpoints

  - Create GET /community/resources endpoint with filtering
  - Implement POST /community/resources/{id}/bookmark endpoint
  - Add search functionality by tags and content type
  - _Requirements: 6.2, 6.3_


- [x] 9. Implement admin dashboard and analytics





- [x] 9.1 Create admin service with analytics


  - Write admin_service.py with analytics calculation methods
  - Implement metrics aggregation (total users, active sessions, session volume, revenue)
  - Create report generation methods for CSV export
  - Add audit logging for admin actions
  - _Requirements: 7.1, 7.2, 7.5_

- [x] 9.2 Implement admin API endpoints



  - Create GET /admin/metrics endpoint with 30-day analytics
  - Implement GET /admin/users endpoint with filters and pagination
  - Create PATCH /admin/users/{id} endpoint for user management
  - Implement DELETE /admin/users/{id} endpoint
  - Create GET /admin/bookings endpoint
  - Implement DELETE /admin/posts/{id} endpoint for content moderation
  - Create GET /admin/revenue endpoint for revenue reports
  - Add role-based access control (admin only)
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 10. Implement error handling and logging




- [x] 10.1 Create error handling infrastructure


  - Write custom exception classes for different error types
  - Implement FastAPI exception handlers with consistent JSON error format
  - Add request ID generation middleware
  - Create retry logic for external services (OpenAI 3 retries, Stripe 2 retries)
  - _Requirements: 8.3, 8.4_

- [x] 10.2 Implement structured logging


  - Create logging middleware with structured JSON format
  - Add CloudWatch logging configuration
  - Implement log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Add context logging (request_id, user_id, endpoint, duration)
  - _Requirements: 8.4_

- [x] 11. Build frontend application





- [x] 11.1 Create authentication UI components


  - Build signup page with role selection
  - Create login page with form validation
  - Implement AuthProvider context for JWT management
  - Create ProtectedRoute HOC for route protection
  - Build password reset flow UI
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 11.2 Build profile management pages


  - Create client profile page with quiz form (20 factors)
  - Build coach profile page with expertise, languages, pricing, and availability inputs
  - Implement photo upload component with validation
  - Create profile view and edit modes
  - _Requirements: 2.1, 2.2, 2.3, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 11.3 Build coach discovery and matching UI


  - Create coaches listing page with filters (language, country, expertise)
  - Build CoachCard component displaying match scores
  - Implement MatchResults component with confidence visualization
  - Create coach detail page with full profile
  - _Requirements: 4.1, 4.3_

- [x] 11.4 Build booking and payment flow


  - Create BookingCalendar component for time slot selection
  - Build booking confirmation page
  - Implement Stripe Elements integration with PaymentForm component
  - Create booking success and failure pages
  - Build booking history pages for clients and coaches
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 11.5 Build community features UI


  - Create forum listing page with pagination
  - Build ForumPost component with upvote and comment functionality
  - Implement post creation form
  - Create resource library page with filtering
  - Build bookmark functionality
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 11.6 Build admin dashboard


  - Create admin analytics dashboard with metrics visualization
  - Build AdminTable component for user management
  - Implement user detail view with activity history
  - Create content moderation interface
  - Build report export functionality
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 11.7 Build landing page and common components


  - Create landing page with hero, features, and testimonials sections
  - Build navigation header with role-based menu
  - Create footer component
  - Implement loading states and error boundaries
  - Add responsive design for mobile devices
  - _Requirements: 8.1_


- [x] 12. Implement security and performance optimizations




- [x] 12.1 Add security measures


  - Implement CORS configuration for specific origins
  - Add rate limiting middleware (100 requests/minute per user)
  - Create input validation and sanitization utilities
  - Implement CSRF protection for state-changing operations
  - Add Content Security Policy headers
  - _Requirements: 8.3_

- [x] 12.2 Implement caching and performance optimizations


  - Add response compression (gzip) middleware
  - Implement API response caching with Redis
  - Create database query optimization with proper indexes
  - Add pagination to all list endpoints (20 items per page)
  - Implement Next.js SSG for landing page and ISR for coach listings
  - _Requirements: 8.1_

- [x] 12.3 Add health checks and monitoring


  - Create GET /health endpoint with database connectivity check
  - Implement CloudWatch metrics integration
  - Add performance monitoring for API latency
  - Create alerting configuration for error rates and latency
  - _Requirements: 8.5_
-

- [x] 13. Create Docker containers and deployment configuration




- [x] 13.1 Create Docker configurations


  - Write production Dockerfile for FastAPI backend
  - Create production Dockerfile for Next.js frontend
  - Write docker-compose.yml for local development
  - Add .dockerignore files
  - _Requirements: 8.2, 9.5_

- [x] 13.2 Set up AWS infrastructure configuration


  - Create ECS task definitions for backend and frontend
  - Write ALB configuration for load balancing
  - Configure RDS PostgreSQL instance with Multi-AZ
  - Set up ElastiCache Redis cluster
  - Create S3 bucket for file uploads with proper permissions
  - Configure CloudFront CDN for frontend
  - Set up Route 53 DNS configuration
  - Create Secrets Manager entries for API keys
  - _Requirements: 8.2, 8.5_

- [x] 13.3 Implement CI/CD pipeline


  - Create GitHub Actions workflow for testing (unit and integration tests)
  - Add linting and type checking steps (flake8, black, mypy for backend; ESLint for frontend)
  - Implement Docker image building and pushing to ECR
  - Create staging deployment automation
  - Add manual approval step for production deployment
  - Implement rollback capability
  - _Requirements: 9.2, 9.3, 9.4_
-

- [x] 14. Implement data migration from Phase 1



- [x] 14.1 Create migration scripts


  - Write export script to fetch data from Bubble API
  - Create field mapping utilities (Phase 1 to Phase 2 schema)
  - Implement user migration script with password re-hashing
  - Create profile migration scripts for clients and coaches
  - Write booking and payment migration scripts
  - _Requirements: 10.1, 10.2_

- [x] 14.2 Add migration validation and reporting


  - Implement data validation checks (row counts, referential integrity)
  - Create migration report generation
  - Add error logging for failed records
  - Implement rollback capability for migration
  - _Requirements: 10.3, 10.4, 10.5_

- [x] 15. Write comprehensive tests





- [ ]* 15.1 Create unit tests for backend
  - Write tests for models (validation, relationships)
  - Create tests for services (auth, matching, booking, payment)
  - Write tests for repositories (CRUD operations)
  - Create tests for utilities (JWT, validators, formatters)
  - Achieve 80%+ code coverage
  - _Requirements: 9.1_

- [ ]* 15.2 Create integration tests for API
  - Write tests for authentication flow
  - Create tests for booking and payment flow with mocked Stripe
  - Write tests for matching engine with mocked OpenAI
  - Create tests for community features
  - Test role-based access control
  - _Requirements: 9.1_

- [ ]* 15.3 Create frontend tests
  - Write component tests with React Testing Library
  - Create tests for custom hooks
  - Write tests for context providers
  - Test form validation and submission
  - _Requirements: 9.1_

- [ ]* 15.4 Create end-to-end tests
  - Write E2E test for client signup to booking flow
  - Create E2E test for coach profile setup
  - Write E2E test for admin dashboard operations
  - Test critical user journeys with Playwright or Cypress
  - _Requirements: 9.1_
-

- [x] 16. Create documentation and final setup




- [x] 16.1 Write API documentation


  - Generate OpenAPI/Swagger documentation from FastAPI
  - Add endpoint descriptions and examples
  - Document authentication requirements
  - Create error response documentation
  - _Requirements: 9.5_

- [x] 16.2 Create setup and deployment guides


  - Write README with project overview and setup instructions
  - Create local development setup guide
  - Write deployment guide for AWS
  - Document environment variables and configuration
  - Create troubleshooting guide
  - _Requirements: 9.5_

- [x] 16.3 Perform final integration and testing


  - Deploy to staging environment
  - Run smoke tests on staging
  - Perform load testing (100 concurrent users)
  - Verify all integrations (OpenAI, Stripe, S3, Email)
  - Test with real payment in Stripe test mode
  - _Requirements: 8.1, 8.2, 8.5_
