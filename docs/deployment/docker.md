# Docker Deployment

Deploy ShopDB using Docker containers.

## Dockerfile

```dockerfile
# Use official Python runtime as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR $APP_HOME

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser $APP_HOME
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["python", "run.py"]
```

## Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: shopdb_postgres
    environment:
      POSTGRES_DB: shopdb
      POSTGRES_USER: shopuser
      POSTGRES_PASSWORD: shoppassword
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
      - ./database/stored_procedures.sql:/docker-entrypoint-initdb.d/02-procedures.sql
      - ./database/materialized_views.sql:/docker-entrypoint-initdb.d/03-views.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U shopuser"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build: .
    container_name: shopdb_web
    environment:
      FLASK_APP: run.py
      FLASK_ENV: production
      DATABASE_URL: postgresql://shopuser:shoppassword@db:5432/shopdb
      SECRET_KEY: ${SECRET_KEY:-change-me-in-production}
    ports:
      - "5000:5000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  docs:
    image: squidfunk/mkdocs-material:latest
    container_name: shopdb_docs
    ports:
      - "8000:8000"
    volumes:
      - ./:/docs
    command: serve --dev-addr=0.0.0.0:8000

volumes:
  postgres_data:
```

## Building Images

```bash
# Build application image
docker build -t shopdb:latest .

# Build with specific tag
docker build -t shopdb:1.0.0 .

# Build without cache
docker build --no-cache -t shopdb:latest .
```

## Running Containers

### Start Full Stack

```bash
docker-compose up -d
```

### View Logs

```bash
docker-compose logs -f web
docker-compose logs -f db
```

### Access Services

- Application: http://localhost:5000
- Documentation: http://localhost:8000
- Database: localhost:5432

### Stop Services

```bash
docker-compose down

# Remove volumes too
docker-compose down -v
```

## Image Security

### Non-root User
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

### Minimal Base Image
```dockerfile
FROM python:3.11-slim  # Smaller than 'python:3.11'
```

### No Unnecessary Layers
```dockerfile
RUN apt-get update && \
    apt-get install -y package && \
    rm -rf /var/lib/apt/lists/*  # Clean cache in same layer
```

## Production Considerations

### Environment Variables
```bash
# Store in .env file
SECRET_KEY=prod-secret-key-here
DATABASE_URL=postgresql://user:pass@prod-db:5432/shopdb
FLASK_ENV=production
```

### Resource Limits

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### Database Backup

```bash
# Backup database
docker-compose exec db pg_dump -U shopuser shopdb > backup.sql

# Restore database
docker-compose exec -T db psql -U shopuser shopdb < backup.sql
```

## Next Steps

- [Production Setup](production.md)
- [CI/CD Pipeline](cicd.md)
- [Installation Guide](../getting-started/installation.md)
