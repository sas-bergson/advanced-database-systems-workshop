# User Model

User account and authentication model.

**Class:** `User`  
**Module:** `app/models/user.py`

## Overview

Represents user accounts with authentication and profile data.

## Database Columns

| Column          | Type         | Description               |
| --------------- | ------------ | ------------------------- |
| `id`            | INTEGER      | Unique user identifier    |
| `username`      | VARCHAR(80)  | Unique username for login |
| `email`         | VARCHAR(120) | Unique email address      |
| `password_hash` | VARCHAR(256) | Bcrypt password hash      |
| `created_at`    | TIMESTAMP    | Account creation date     |
| `is_admin`      | BOOLEAN      | Administrator flag        |

## Relationships

- **orders**: User has many orders (1:N)
- **cart_items**: User has shopping cart items (1:N)

## Key Methods

- `set_password(password)` - Hash and store password
- `check_password(password)` - Verify password
- `to_dict()` - Convert to dictionary
- `is_authenticated` - Check if user is logged in

## Source Code

File: [`app/models/user.py`](../../app/models/user.py)

---

**Auto-generated documentation** - See [DOCUMENTATION.md](../../DOCUMENTATION.md) for details.
