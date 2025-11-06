# Authentication System - Quick Start Guide

## Overview

The CultureBridge authentication system provides secure user registration, login, and role-based access control using JWT tokens.

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/culturebridge

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# App Configuration
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000
```

### 3. Run Database Migrations

```bash
# Create database tables
alembic upgrade head
```

### 4. Test the Implementation

```bash
# Run manual tests
python test_auth_manual.py

# Run automated tests
pytest tests/test_auth.py -v
```

### 5. Start the Server

```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access API Documentation

Open your browser and visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/signup` | Register new user | No |
| POST | `/auth/login` | Login user | No |
| POST | `/auth/refresh` | Refresh access token | No |
| POST | `/auth/reset-password` | Request password reset | No |
| POST | `/auth/reset-password/confirm` | Confirm password reset | No |
| POST | `/auth/change-password` | Change password | Yes |
| GET | `/auth/me` | Get current user | Yes |
| POST | `/auth/logout` | Logout user | No |

## Usage Examples

### 1. Register a New User

```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "password": "securepass123",
    "role": "client"
  }'
```

**Response:**
```json
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "client@example.com",
    "role": "client",
    "is_active": true,
    "email_verified": false,
    "created_at": "2025-11-05T10:30:00Z"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "password": "securepass123"
  }'
```

### 3. Access Protected Endpoint

```bash
# Save the access token from login/signup response
TOKEN="your_access_token_here"

curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Refresh Token

```bash
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your_refresh_token_here"
  }'
```

### 5. Change Password

```bash
curl -X POST "http://localhost:8000/auth/change-password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "securepass123",
    "new_password": "newsecurepass456"
  }'
```

## User Roles

The system supports three user roles:

1. **client** - Users seeking coaching services
2. **coach** - Users providing coaching services
3. **admin** - Platform administrators

## Role-Based Access Control

### Using in FastAPI Endpoints

```python
from fastapi import APIRouter, Depends
from app.middleware.auth_middleware import (
    get_current_user,
    require_admin,
    require_client,
    require_coach,
    require_role
)
from app.models.user import User, UserRole

router = APIRouter()

# Any authenticated user
@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return {"user_id": user.id}

# Admin only
@router.get("/admin/users")
async def get_all_users(user: User = Depends(require_admin)):
    return {"users": []}

# Client only
@router.post("/booking")
async def create_booking(user: User = Depends(require_client)):
    return {"booking_id": "123"}

# Coach only
@router.get("/coach/bookings")
async def get_coach_bookings(user: User = Depends(require_coach)):
    return {"bookings": []}

# Multiple roles
@router.get("/community/posts")
async def get_posts(
    user: User = Depends(require_role([UserRole.CLIENT, UserRole.COACH]))
):
    return {"posts": []}
```

### Checking Resource Ownership

```python
from app.middleware.auth_middleware import ownership_checker

@router.put("/coaches/{coach_id}")
async def update_coach(
    coach_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user owns this coach profile or is admin
    ownership_checker.check_coach_ownership(user, coach_id, db)
    
    # Update coach profile
    return {"message": "Coach updated"}
```

## Security Features

### Password Security
- ✅ Bcrypt hashing with 12 salt rounds
- ✅ Minimum 8 character requirement
- ✅ Secure password verification

### Token Security
- ✅ Access tokens expire after 24 hours
- ✅ Refresh tokens expire after 7 days
- ✅ Token signature verification
- ✅ Token type validation

### API Security
- ✅ HTTP Bearer authentication
- ✅ Role-based access control
- ✅ Resource ownership verification
- ✅ Proper error handling

## Error Handling

### Common Error Responses

**401 Unauthorized** - Invalid or missing token
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden** - Insufficient permissions
```json
{
  "detail": "Admin access required"
}
```

**400 Bad Request** - Invalid input
```json
{
  "detail": "Email already registered"
}
```

**422 Unprocessable Entity** - Validation error
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

## Testing

### Manual Testing

```bash
# Test core functionality
python test_auth_manual.py
```

### Automated Testing

```bash
# Run all auth tests
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/test_auth.py --cov=app.services --cov=app.utils --cov=app.middleware

# Run specific test
pytest tests/test_auth.py::test_signup_success -v
```

### Using Swagger UI

1. Visit http://localhost:8000/docs
2. Click on an endpoint (e.g., POST /auth/signup)
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"
6. View the response

For protected endpoints:
1. First login or signup to get a token
2. Click the "Authorize" button at the top
3. Enter: `Bearer your_token_here`
4. Click "Authorize"
5. Now you can access protected endpoints

## Integration with Frontend

### React/Next.js Example

```typescript
// auth.service.ts
const API_URL = 'http://localhost:8000';

export const authService = {
  async signup(email: string, password: string, role: string) {
    const response = await fetch(`${API_URL}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, role })
    });
    return response.json();
  },

  async login(email: string, password: string) {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    
    // Store tokens
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    
    return data;
  },

  async getCurrentUser() {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_URL}/auth/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  },

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
};
```

## Troubleshooting

### Issue: "Could not validate credentials"
- Check if token is expired (24h for access token)
- Verify token is sent in Authorization header
- Use refresh token to get new access token

### Issue: "Email already registered"
- User already exists with that email
- Try logging in instead
- Use password reset if forgotten

### Issue: "Invalid email or password"
- Check credentials are correct
- Ensure password meets minimum requirements
- Verify user account is active

### Issue: "Admin access required"
- User doesn't have required role
- Check user role in database
- Use correct user account for admin operations

## Next Steps

1. ✅ Authentication system is complete
2. Implement profile management (Task 4)
3. Add email service for password reset
4. Implement rate limiting
5. Add audit logging
6. Consider 2FA for enhanced security

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the implementation guide in `AUTHENTICATION_IMPLEMENTATION.md`
3. Run manual tests with `test_auth_manual.py`
4. Check the test suite in `tests/test_auth.py`

## Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- JWT.io: https://jwt.io/
- Bcrypt: https://github.com/pyca/bcrypt/
- Pydantic: https://docs.pydantic.dev/
