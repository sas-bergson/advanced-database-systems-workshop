# Configuration Guide

ShopDB uses a hierarchical configuration system supporting multiple environments.

## Configuration Hierarchy

=== "Development"
    ```python
    DEBUG = True
    TESTING = False
    DATABASE_URL = 'sqlite:///dev.db'
    ```

=== "Testing"
    ```python
    DEBUG = False
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
    ```

=== "Production"
    ```python
    DEBUG = False
    TESTING = False
    DATABASE_URL = 'postgresql://user:pass@host:5432/shopdb'
    ```

## Environment Variables

### Database Configuration

| Variable                         | Description                | Default            |
| -------------------------------- | -------------------------- | ------------------ |
| `DATABASE_URL`                   | Database connection string | `sqlite:///dev.db` |
| `SQLALCHEMY_ECHO`                | Log SQL queries            | `False`            |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | Track model changes        | `False`            |

### Flask Configuration

| Variable         | Description             | Default        |
| ---------------- | ----------------------- | -------------- |
| `FLASK_ENV`      | Environment mode        | `development`  |
| `FLASK_APP`      | Application entry point | `run.py`       |
| `SECRET_KEY`     | Session encryption key  | Auto-generated |
| `JSON_SORT_KEYS` | Sort JSON output        | `False`        |

### Session Configuration

| Variable                     | Description               | Default |
| ---------------------------- | ------------------------- | ------- |
| `PERMANENT_SESSION_LIFETIME` | Session timeout (seconds) | `1800`  |
| `SESSION_COOKIE_SECURE`      | HTTPS only                | `False` |
| `SESSION_COOKIE_HTTPONLY`    | JavaScript access         | `True`  |
| `SESSION_COOKIE_SAMESITE`    | CSRF protection           | `Lax`   |

### Security Configuration

| Variable             | Description              | Default    |
| -------------------- | ------------------------ | ---------- |
| `BCRYPT_LOG_ROUNDS`  | Password hash iterations | `12`       |
| `MAX_CONTENT_LENGTH` | Max upload size (bytes)  | `16777216` |

## .env File Example

```ini
# Environment
FLASK_ENV=development
FLASK_APP=run.py

# Database
DATABASE_URL=postgresql://shopuser:password@localhost:5432/shopdb
SQLALCHEMY_ECHO=False

# Security
SECRET_KEY=dev-key-change-in-production-$(openssl rand -hex 16)
BCRYPT_LOG_ROUNDS=12

# Session
PERMANENT_SESSION_LIFETIME=1800
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

## Production Configuration

For production deployment:

```ini
FLASK_ENV=production
DEBUG=False
TESTING=False

# Secure Database URL
DATABASE_URL=postgresql://shopuser:$(SECRET_PASSWORD)@db.production.internal:5432/shopdb

# Strong secret key (generate with: openssl rand -hex 32)
SECRET_KEY=your-generated-32-byte-hex-string

# Enhanced Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Strict
PREFERRED_URL_SCHEME=https

# Performance
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_POOL_RECYCLE=3600
SQLALCHEMY_MAX_OVERFLOW=40

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/shopdb/app.log
```

## Generating a Secure Secret Key

```bash
# Linux/macOS
openssl rand -hex 32

# Python
python -c "import secrets; print(secrets.token_hex(32))"

# Using urandom
python -c "import os; print(os.urandom(24).hex())"
```

## Configuration via Code

Edit `config.py`:

```python
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    JSON_SORT_KEYS = False

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
```

## Next Steps

- [Quick Start Guide](quick-start.md)
- [Database Configuration](../database/schema.md)
- [Deployment Guide](../deployment/docker.md)
