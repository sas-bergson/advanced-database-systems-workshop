# Authentication API

Authentication endpoints for user login and registration.

## Register User

Create a new user account.

**Endpoint:** `POST /auth/register`

**Parameters:**
- `username` (string, required) - Unique username
- `email` (string, required) - Unique email address
- `password` (string, required) - User password
- `confirm` (string, required) - Password confirmation

**Response:**
- Success: Redirect to login page
- Error: Show validation messages

## Login User

Authenticate user and create session.

**Endpoint:** `POST /auth/login`

**Parameters:**
- `username` (string, required) - Username or email
- `password` (string, required) - User password
- `remember_me` (boolean, optional) - Remember login

**Response:**
- Success: Redirect to home page
- Error: Show login form with error message

## Logout User

Destroy user session.

**Endpoint:** `GET /auth/logout`

**Response:**
- Redirect to home page

## Get Current User

Retrieve authenticated user information.

**Endpoint:** `GET /api/auth/user`

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "is_admin": false,
  "created_at": "2024-04-23T10:30:00"
}
```

**Status Codes:**
- `200` - User authenticated
- `401` - Not authenticated

---

**Auto-generated documentation** - See [DOCUMENTATION.md](../../DOCUMENTATION.md) for details.
