# Authentication and Authorization System Implementation

## Overview

This document describes the implementation of Task 3: "Implement authentication and authorization system" for the CultureBridge MVP platform.

## Implementation Summary

All three subtasks have been completed:

### ✅ 3.1 Create JWT utilities and authentication service
### ✅ 3.2 Implement authentication middleware and dependencies  
### ✅ 3.3 Create authentication API endpoints

## Files Created

### 1. JWT Utilities (`backend/app/utils/jwt_utils.py`)

**Purpose**: Token generation, validation, and refresh logic

**Key Functions**:
- `create_access_token()` - Generate JWT access tokens (24h expiry)
- `create_refresh_token()` - Generate refresh tokens (7d expiry)
- `verify_token()` - Verify and decode JWT tokens
- `verify_refresh_token()` - Verify refresh token type
- `create_password_reset_token()` - Generate password reset tokens (1h expiry)
- `verify_password_reset_token()` - Verify password reset tokens

**Requirements Addressed**: 1.1, 1.2, 1.4

### 2. Password Utilities (`backend/app/utils/password.py`)

**Purpose**: Password hashing with bcrypt (12 salt rounds)

**Key Functions**:
- `hash_password()` - Hash passwords using bcrypt with 12 salt rounds
- `verify_password()` - Verify password against hash

**Requirements Addressed**: 1.1, 1.4

### 3. Authentication Service (`backend/app/services/auth_service.py`)

**Purpose**: Business logic for signup, login, and password reset

**Key Methods**:
- `signup()` - Register new users with email, password, and role
- `login()` - Authenticate users and return JWT tokens
- `refresh_access_token()` - Generate new access token from refresh token
- `request_password_reset()` - Generate password reset token
- `reset_password()` - Reset password with valid token
- `change_password()` - Change password for authenticated users

**Features**:
- Email validation
- Password strength validation (minimum 8 characters)
- Duplicate email detection
- Account status checking
- Automatic token generation

**Requirements Addressed**: 1.1, 1.2, 1.3, 1.4

### 4. Authentication Middleware (`backend/app/middleware/auth_middleware.py`)

**Purpose**: JWT validation and role-based access control

**Key Components**:

#### FastAPI Dependencies:
- `get_current_user()` - Extract and validate user from JWT token
- `get_current_active_user()` - Get current active user
- `get_optional_user()` - Optional authentication (returns None if no token)

#### Role-Based Access Control:
- `require_role()` - Decorator factory for custom role requirements
- `require_admin()` - Require admin role
- `require_client()` - Require client role
- `require_coach()` - Require coach role
- `require_client_or_admin()` - Require client or admin role
- `require_coach_or_admin()` - Require coach or admin role

#### Ownership Checking:
- `ResourceOwnershipChecker` - Class for checking resource ownership
- `ownership_checker.check_ownership()` - Verify user owns resource or is admin
- `ownership_checker.check_coach_ownership()` - Verify coach ownership
- `ownership_checker.check_client_ownership()` - Verify client ownership

**Requirements Addressed**: 1.2, 7.3

### 5. Authentication Schemas (`backend/app/schemas/auth.py`)

**Purpose**: Pydantic models for request/response validation

**Schemas Created**:
- `SignupRequest` - User registration data
- `LoginRequest` - Login credentials
- `TokenResponse` - JWT tokens response
- `RefreshTokenRequest` - Token refresh request
- `RefreshTokenResponse` - New access token response
- `PasswordResetRequest` - Password reset request
- `PasswordResetResponse` - Password reset response
- `PasswordResetConfirmRequest` - Password reset confirmation
- `PasswordResetConfirmResponse` - Password reset success
- `ChangePasswordRequest` - Password change request
- `UserResponse` - User data response
- `AuthResponse` - Combined user + tokens response
- `ErrorResponse` - Standard error response

**Features**:
- Email validation using EmailStr
- Password length validation (min 8 characters)
- Comprehensive examples for API documentation
- Type safety with Pydantic

**Requirements Addressed**: 1.1, 1.2, 1.3, 1.5

### 6. Authentication Router (`backend/app/routers/auth.py`)

**Purpose**: API endpoints for authentication

**Endpoints Implemented**:

#### POST /auth/signup
- Register new user with email, password, and role
- Returns user data and JWT tokens
- Status: 201 Created

#### POST /auth/login
- Authenticate user with email and password
- Returns user data and JWT tokens
- Status: 200 OK

#### POST /auth/refresh
- Generate new access token from refresh token
- Returns new access token
- Status: 200 OK

#### POST /auth/reset-password
- Request password reset (sends email in production)
- Returns success message
- Status: 200 OK

#### POST /auth/reset-password/confirm
- Reset password using token from email
- Returns success message
- Status: 200 OK

#### POST /auth/change-password
- Change password for authenticated user
- Requires authentication token
- Status: 200 OK

#### GET /auth/me
- Get current authenticated user information
- Requires authentication token
- Status: 200 OK

#### POST /auth/logout
- Logout user (client-side token removal)
- Status: 204 No Content

**Features**:
- Comprehensive OpenAPI documentation
- Proper HTTP status codes
- Error handling with descriptive messages
- Security headers (WWW-Authenticate)

**Requirements Addressed**: 1.1, 1.2, 1.3, 1.5

### 7. Main Application Update (`backend/app/main.py`)

**Changes**:
- Imported auth router
- Configured CORS from environment settings
- Registered auth router with FastAPI app

### 8. Test Suite (`backend/tests/test_auth.py`)

**Purpose**: Integration tests for authentication endpoints

**Tests Created**:
- `test_signup_success()` - Successful user registration
- `test_signup_duplicate_email()` - Duplicate email handling
- `test_signup_invalid_password()` - Password validation
- `test_login_success()` - Successful login
- `test_login_invalid_credentials()` - Invalid credentials
- `test_login_wrong_password()` - Wrong password
- `test_refresh_token()` - Token refresh
- `test_get_current_user()` - Get current user info
- `test_get_current_user_unauthorized()` - Unauthorized access
- `test_password_reset_request()` - Password reset request
- `test_password_reset_confirm()` - Password reset confirmation
- `test_change_password()` - Password change

**Coverage**: All major authentication flows

## Security Features Implemented

### 1. Password Security
- ✅ Bcrypt hashing with 12 salt rounds (as per requirements)
- ✅ Minimum 8 character password requirement
- ✅ Password validation on signup and reset

### 2. JWT Security
- ✅ Access tokens expire after 24 hours
- ✅ Refresh tokens expire after 7 days
- ✅ Token signature verification
- ✅ Token type validation (access vs refresh vs reset)
- ✅ Expiration time validation

### 3. API Security
- ✅ HTTP Bearer authentication
- ✅ Role-based access control (RBAC)
- ✅ Resource ownership verification
- ✅ Proper HTTP status codes (401, 403)
- ✅ WWW-Authenticate headers

### 4. Data Validation
- ✅ Email format validation
- ✅ Password strength validation
- ✅ Input sanitization via Pydantic
- ✅ SQL injection prevention via SQLAlchemy ORM

## Requirements Coverage

### Requirement 1.1 - User Registration ✅
- User can register with email, password, and role
- Account created with assigned role (Client, Coach, Admin)
- Password encrypted with bcrypt (12 salt rounds)
- Returns JWT token valid for 24 hours

### Requirement 1.2 - User Authentication ✅
- User can login with valid credentials
- Returns JWT token valid for 24 hours
- Token refresh functionality implemented
- Current user extraction from JWT

### Requirement 1.3 - Password Reset ✅
- User can request password reset
- Reset token generated (1 hour expiry)
- Password reset confirmation endpoint
- Email integration ready (TODO: email service)

### Requirement 1.4 - Password Encryption ✅
- All passwords encrypted with bcrypt
- 12 salt rounds as specified
- Secure password verification

### Requirement 1.5 - HTTPS Communication ✅
- HTTPS enforcement ready (configured at deployment level)
- Secure token transmission via Bearer authentication

### Requirement 7.3 - Role-Based Access Control ✅
- Admin, Coach, Client role enforcement
- Ownership verification for resources
- Flexible role checking decorators
- Permission matrix implementation ready

## API Documentation

The authentication endpoints are fully documented with:
- OpenAPI/Swagger specifications
- Request/response examples
- Error response documentation
- Authentication requirements
- Detailed descriptions

Access the interactive API docs at: `http://localhost:8000/docs`

## Usage Examples

### 1. User Signup
```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "role": "client"
  }'
```

### 2. User Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 3. Access Protected Endpoint
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

### 4. Refresh Token
```bash
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

### 5. Password Reset
```bash
# Request reset
curl -X POST "http://localhost:8000/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'

# Confirm reset
curl -X POST "http://localhost:8000/auth/reset-password/confirm" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "<reset_token>",
    "new_password": "newsecurepassword123"
  }'
```

## Integration with Other Components

### Database Models
- Uses existing `User` model from `app.models.user`
- Integrates with `UserRole` enum
- Leverages SQLAlchemy relationships

### Configuration
- Uses settings from `app.config`
- JWT configuration (secret, algorithm, expiry)
- CORS configuration
- Environment-specific behavior

### Future Integration Points
- Email service for password reset emails
- Redis for token blacklisting (logout)
- Rate limiting middleware
- Audit logging for authentication events

## Testing

### Running Tests
```bash
# Install dependencies
pip install -r requirements.txt

# Run authentication tests
pytest backend/tests/test_auth.py -v

# Run with coverage
pytest backend/tests/test_auth.py --cov=app --cov-report=html
```

### Test Database
Tests use SQLite in-memory database for isolation and speed.

## Next Steps

### Immediate
1. ✅ All authentication endpoints implemented
2. ✅ JWT utilities complete
3. ✅ Role-based access control ready
4. ✅ Test suite created

### Future Enhancements
1. Implement email service for password reset
2. Add token blacklisting with Redis
3. Implement rate limiting
4. Add audit logging
5. Add 2FA support
6. Add OAuth providers (Google, LinkedIn)

## Conclusion

Task 3 "Implement authentication and authorization system" has been **successfully completed** with all three subtasks:

- ✅ 3.1 JWT utilities and authentication service
- ✅ 3.2 Authentication middleware and dependencies
- ✅ 3.3 Authentication API endpoints

The implementation provides a secure, scalable, and well-documented authentication system that meets all specified requirements and follows industry best practices.
