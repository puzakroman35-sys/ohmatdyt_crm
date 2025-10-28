# JWT Authentication Implementation

## Overview

JWT (JSON Web Token) authentication has been implemented for the Ohmatdyt CRM API. This provides secure, stateless authentication for all API endpoints.

## Features

- ✅ Access tokens (30 minutes expiration)
- ✅ Refresh tokens (7 days expiration)
- ✅ Role-based access control (OPERATOR, EXECUTOR, ADMIN)
- ✅ Protected endpoints with Bearer token authentication
- ✅ CORS configuration from environment variables
- ✅ Password strength validation

## Endpoints

### Authentication Endpoints

#### POST /auth/login
Login with username and password.

**Request:**
```json
{
  "username": "admin",
  "password": "Admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "role": "ADMIN",
    "is_active": true,
    "created_at": "2025-10-28T12:00:00",
    "updated_at": "2025-10-28T12:00:00"
  }
}
```

#### POST /auth/refresh
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### GET /auth/me
Get current user information.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": "uuid",
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "Admin User",
  "role": "ADMIN",
  "is_active": true,
  "created_at": "2025-10-28T12:00:00",
  "updated_at": "2025-10-28T12:00:00"
}
```

#### POST /auth/logout
Logout (client-side token removal).

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:** 204 No Content

## Using Protected Endpoints

All `/api/*` endpoints require authentication. Include the access token in the Authorization header:

```bash
curl -H "Authorization: Bearer {access_token}" http://localhost:8000/api/users
```

## Role-Based Access Control

### OPERATOR
- Can create and view own requests (future implementation)
- Can view own user profile
- Can update own profile (limited fields)

### EXECUTOR
- All OPERATOR permissions
- Can view and process requests in assigned categories (future implementation)
- Can view own user profile
- Can update own profile (limited fields)

### ADMIN
- Full system access
- Can manage all users
- Can access all endpoints
- Can view and modify all resources

## Environment Variables

Configure JWT settings in `.env`:

```bash
# JWT/Auth
JWT_SECRET=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Security Best Practices

1. **Secret Key**: Use a strong, random secret key in production
2. **HTTPS**: Always use HTTPS in production
3. **Token Storage**: Store tokens securely (httpOnly cookies or secure storage)
4. **Token Expiration**: Keep access tokens short-lived (15-30 minutes)
5. **Refresh Tokens**: Store refresh tokens securely, rotate on use
6. **CORS**: Configure CORS origins appropriately for your frontend

## Password Requirements

- Minimum 8 characters
- Must contain at least one letter (a-z, A-Z)
- Must contain at least one digit (0-9)

## Error Responses

### 401 Unauthorized
Invalid or expired token, or invalid credentials.

```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
Valid token but insufficient permissions.

```json
{
  "detail": "Admin privileges required"
}
```

## Testing

Run authentication tests:

```bash
docker compose exec api pytest tests/test_auth.py -v
```

## Integration with Frontend

### Login Flow

1. User submits credentials to `/auth/login`
2. Backend validates credentials
3. Backend returns access_token and refresh_token
4. Frontend stores tokens (localStorage or httpOnly cookie)
5. Frontend includes access_token in all API requests

### Token Refresh Flow

1. Access token expires
2. Frontend detects 401 error
3. Frontend sends refresh_token to `/auth/refresh`
4. Backend validates refresh_token
5. Backend returns new access_token
6. Frontend retries original request with new token

### Logout Flow

1. Frontend sends logout request to `/auth/logout` (optional)
2. Frontend removes tokens from storage
3. Frontend redirects to login page

## Example Usage

### Python (httpx)

```python
import httpx

# Login
response = httpx.post("http://localhost:8000/auth/login", json={
    "username": "admin",
    "password": "Admin123"
})
tokens = response.json()
access_token = tokens["access_token"]

# Use protected endpoint
headers = {"Authorization": f"Bearer {access_token}"}
response = httpx.get("http://localhost:8000/api/users", headers=headers)
users = response.json()
```

### JavaScript (fetch)

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'Admin123'
  })
});

const { access_token } = await loginResponse.json();

// Use protected endpoint
const usersResponse = await fetch('http://localhost:8000/api/users', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});

const users = await usersResponse.json();
```

## Implementation Files

- `app/auth.py` - JWT token creation and verification
- `app/dependencies.py` - FastAPI dependencies for authentication
- `app/routers/auth.py` - Authentication endpoints
- `app/schemas.py` - Authentication request/response schemas
- `tests/test_auth.py` - Authentication tests

## Next Steps

- [ ] Implement token blacklist (Redis) for logout
- [ ] Add rate limiting for login endpoint
- [ ] Add 2FA support (optional)
- [ ] Implement password reset flow
- [ ] Add refresh token rotation
- [ ] Add OAuth2 support (optional)
