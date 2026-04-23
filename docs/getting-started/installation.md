# Installation Guide

This guide will help you set up ShopDB on your local machine.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Git
- pip (Python package manager)

## Step 1: Clone the Repository

```bash
git clone https://github.com/your-org/advanced-database-systems-workshop.git
cd advanced-database-systems-workshop
```

## Step 2: Create Virtual Environment

=== "macOS/Linux"
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

=== "Windows"
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

## Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Set Up PostgreSQL

### Create Database

```bash
psql -U postgres
CREATE DATABASE shopdb;
CREATE USER shopuser WITH PASSWORD 'shoppassword';
ALTER ROLE shopuser SET client_encoding TO 'utf8';
ALTER ROLE shopuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE shopuser SET default_transaction_deferrable TO on;
ALTER ROLE shopuser SET default_timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE shopdb TO shopuser;
\q
```

### Initialize Schema

```bash
psql -U shopuser -d shopdb -f database/schema.sql
psql -U shopuser -d shopdb -f database/stored_procedures.sql
psql -U shopuser -d shopdb -f database/materialized_views.sql
```

## Step 5: Configure Environment

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://shopuser:shoppassword@localhost:5432/shopdb

# Flask Configuration
FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=your-secret-key-here

# Session Configuration
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

## Step 6: Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Step 7: Create Admin User (Optional)

```bash
python -c "
from app import create_app
from app.models.user import User
app = create_app()
with app.app_context():
    admin = User(username='admin', email='admin@example.com', is_admin=True)
    admin.set_password('admin123')
    from app import db
    db.session.add(admin)
    db.session.commit()
    print('Admin user created successfully!')
"
```

## Verification

Visit the application:

- **Home Page:** http://localhost:5000/
- **Products:** http://localhost:5000/products
- **Login:** http://localhost:5000/auth/login

## Troubleshooting

### PostgreSQL Connection Error

```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
- Ensure PostgreSQL is running
- Verify DATABASE_URL in `.env`
- Check database credentials

### Module Not Found

```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
pip install -r requirements.txt
```

### Permission Denied

```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
chmod +x run.py
chmod -R 755 app/
```

## Next Steps

- [Quick Start Guide](quick-start.md)
- [Configuration Reference](configuration.md)
- [Architecture Overview](../architecture/overview.md)
