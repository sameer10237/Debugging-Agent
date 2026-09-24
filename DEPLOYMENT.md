# Deployment & Execution Guide

Complete guide for running and deploying the AI Debugging Agent system.

## 🚀 Quick Start (Local Development)

### Prerequisites

```bash
# Python 3.11 (the pinned AI dependencies are not yet compatible with Python 3.13)
python3.11 --version

# Node.js 18+
node --version

# Docker (optional but recommended)
docker --version
docker-compose --version
```

### 1. Clone & Setup Project Structure

```bash
# Project structure should be:
debugging-agent/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── celery_app.py
│   │   ├── websocket_manager.py
│   │   ├── exceptions.py
│   │   └── services/
│   │       └── llm_service.py
│   ├── tests/
│   │   └── test_comprehensive.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ExecutionMonitor.tsx
│   │   │   ├── ExecutionMonitor.css
│   │   │   ├── AnalysisResults.tsx
│   │   │   └── AnalysisResults.css
│   │   └── main.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── IMPROVEMENTS.md
└── README.md
```

### 2. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your settings
nano .env  # or open in editor

# Essential variables to set:
# - OPENAI_API_KEY=sk-your-key-here
# - DATABASE_URL=postgresql+asyncpg://...
# - REDIS_URL=redis://localhost:6379/0
```

### 3. Backend Setup

```bash
cd backend

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start backend server (Terminal 1)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Celery Setup (Terminal 2)

```bash
cd backend
source venv/bin/activate  # or activate your env

# Start Celery Worker
celery -A app.celery_app worker --loglevel=info --concurrency=4

# Optional: In another terminal, start Celery Beat (scheduler)
celery -A app.celery_app beat --loglevel=info
```

### 5. Frontend Setup (Terminal 3)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 6. Redis (Terminal 4, if not using Docker)

```bash
# Make sure Redis is running
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### 7. Access the Application

```
Frontend:    http://localhost:5173
Backend:     http://localhost:8000
API Docs:    http://localhost:8000/docs
Redis CLI:   redis-cli (if installed locally)
```

---

## 🐳 Docker Deployment (Recommended)

### Quick Start with Docker Compose

```bash
# Navigate to project root
cd debugging-agent

# Set your OpenAI API key
export OPENAI_API_KEY=sk-your-key-here

# Build and start all services
docker-compose up --build

# Services will be available at:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

### Understanding Docker Compose Services

```yaml
Services:
1. db (PostgreSQL)
   - Database for project/execution data
   - Port: 5432
   - Health check: Automatic

2. redis
   - Message broker for Celery
   - Cache layer
   - Port: 6379
   - Health check: Automatic

3. backend (FastAPI)
   - Main API server
   - Port: 8000
   - Includes: REST API, WebSocket endpoint
   - Depends on: db, redis

4. celery_worker
   - Background job processor
   - Runs long-running workflows
   - Concurrency: 4 workers
   - Depends on: redis, backend

5. celery_beat
   - Task scheduler
   - Runs periodic jobs
   - Depends on: redis, backend

6. frontend (React)
   - Web UI
   - Port: 5173
   - Depends on: backend
```

### Docker Compose Commands

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Rebuild images
docker-compose up --build

# Remove volumes (WARNING: deletes database)
docker-compose down -v

# Scale specific service
docker-compose up -d --scale celery_worker=3

# Run one-off command
docker-compose exec backend pytest
docker-compose exec backend alembic upgrade head
```

---

## 📋 Running Tests

### Unit & Integration Tests

```bash
# Backend tests
cd backend

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_comprehensive.py

# Run specific test
pytest tests/test_comprehensive.py::test_health_check

# Run with specific marker
pytest -m asyncio
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS/Linux
# or navigate to htmlcov/index.html in browser
```

### Running Tests in Docker

```bash
# Run tests in container
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=app
```

---

## 🔍 Monitoring & Debugging

### API Documentation

```
http://localhost:8000/docs           # Swagger UI
http://localhost:8000/redoc          # ReDoc
```

### Logs

```bash
# Backend logs
docker-compose logs backend

# Celery worker logs
docker-compose logs celery_worker

# Follow live logs
docker-compose logs -f

# View PostgreSQL logs
docker-compose logs db
```

### Database Access

```bash
# Connect to PostgreSQL
psql postgresql://debug_user:debug_password@localhost:5432/debugging_agent

# Or via Docker
docker-compose exec db psql -U debug_user -d debugging_agent

# Useful queries
SELECT * FROM projects;
SELECT * FROM executions;
SELECT * FROM agent_executions;
```

### Redis CLI

```bash
# Connect to Redis
redis-cli

# Useful commands
KEYS *                          # List all keys
GET execution:uuid             # Get execution data
LRANGE execution:uuid:messages 0 -1  # Get all messages
FLUSHDB                        # Clear database (be careful!)
```

### Celery Monitoring

```bash
# View active tasks
celery -A app.celery_app inspect active

# View registered tasks
celery -A app.celery_app inspect registered

# View workers
celery -A app.celery_app inspect stats

# Or use web UI
pip install flower
celery -A app.celery_app flower
# Access at http://localhost:5555
```

---

## 🌐 Production Deployment

### Pre-Deployment Checklist

```bash
✅ Set strong SECRET_KEY in .env
✅ Set DEBUG=false
✅ Configure OPENAI_API_KEY
✅ Set up PostgreSQL (managed service recommended)
✅ Set up Redis (managed service recommended)
✅ Configure CORS origins for your domain
✅ Set up SSL/TLS certificate
✅ Configure database backups
✅ Set up error tracking (Sentry)
✅ Configure monitoring and alerts
✅ Run full test suite
✅ Load test application
✅ Plan disaster recovery
```

### Environment Variables (Production)

```bash
# .env for production
DEBUG=false
LOG_LEVEL=INFO

# Security
SECRET_KEY=generate-with-`openssl rand -hex 32`
ALGORITHM=HS256

# Database (use managed service)
DATABASE_URL=postgresql://user:password@db.example.com/debugging_agent
DATABASE_POOL_SIZE=50
DATABASE_POOL_RECYCLE=3600

# Redis (use managed service)
REDIS_URL=redis://:password@redis.example.com:6379/0

# LLM
OPENAI_API_KEY=sk-prod-key-here
MODEL_NAME=gpt-4
MODEL_TEMPERATURE=0.1

# CORS (your domain)
CORS_ORIGINS=https://yourdomain.com

# Frontend URL
FRONTEND_URL=https://yourdomain.com

# Enable Celery
CELERY_WORKER_CONCURRENCY=10

# Error tracking
SENTRY_DSN=https://key@sentry.io/123456
```

### Docker Production Build

```bash
# Build for production
docker build -t debugging-agent:latest backend/
docker build -t debugging-agent-ui:latest frontend/

# Push to registry
docker tag debugging-agent:latest myregistry.azurecr.io/debugging-agent:latest
docker push myregistry.azurecr.io/debugging-agent:latest

# Deploy with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
# Example: Deploy to Kubernetes
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/postgres-pvc.yml
kubectl apply -f k8s/backend-deployment.yml
kubectl apply -f k8s/celery-deployment.yml
kubectl apply -f k8s/frontend-deployment.yml
kubectl apply -f k8s/service.yml
kubectl apply -f k8s/ingress.yml

# Check status
kubectl get pods -n debugging-agent
kubectl get svc -n debugging-agent
```

### Cloud Platforms

#### AWS Deployment

```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

docker tag debugging-agent:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/debugging-agent:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/debugging-agent:latest

# Deploy with ECS or EKS
# (See AWS documentation for specific steps)
```

#### Azure Deployment

```bash
# Login to Azure
az login

# Create resource group
az group create -n debugging-agent -l eastus

# Deploy container instances
az container create \
  --resource-group debugging-agent \
  --name backend \
  --image debugging-agent:latest \
  --cpu 2 \
  --memory 4 \
  --environment-variables OPENAI_API_KEY=$OPENAI_API_KEY

# Or use Azure App Service
az webapp up -n debugging-agent-api -g debugging-agent --runtime python:3.11
```

#### Google Cloud Deployment

```bash
# Build and push to Google Cloud
gcloud builds submit --tag gcr.io/my-project/debugging-agent:latest backend/

# Deploy to Cloud Run
gcloud run deploy debugging-agent \
  --image gcr.io/my-project/debugging-agent:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY
```

---

## 🔐 Security Best Practices

### API Security

```python
# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# CORS
CORS_ORIGINS=https://yourdomain.com  # Don't use *

# HTTPS
# Always use SSL/TLS in production
# Redirect HTTP to HTTPS

# Authentication
# Add JWT tokens for API endpoints
# Implement API key management
```

### Database Security

```sql
-- Create limited user
CREATE USER api_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE debugging_agent TO api_user;
GRANT USAGE ON SCHEMA public TO api_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO api_user;

-- Use connection pooling
DATABASE_POOL_SIZE=50
DATABASE_POOL_RECYCLE=3600

-- Enable SSL connections
postgresql://user:pass@host/db?sslmode=require
```

### Secret Management

```bash
# Use environment variables
export OPENAI_API_KEY=sk-...
export DATABASE_URL=postgresql://...

# Never commit secrets to git
echo ".env" > .gitignore

# Use secret management service
# - AWS Secrets Manager
# - Azure Key Vault
# - Google Cloud Secret Manager
# - HashiCorp Vault
```

---

## 📊 Performance Tuning

### Database Optimization

```python
# Connection pooling
DATABASE_POOL_SIZE=50      # production: 10-50
DATABASE_POOL_RECYCLE=3600  # Recycle connections every hour

# Add indexes
CREATE INDEX idx_execution_project ON executions(project_id);
CREATE INDEX idx_execution_status ON executions(status);
CREATE INDEX idx_agent_execution ON agent_executions(execution_id);
```

### Celery Optimization

```python
# Worker concurrency
CELERY_WORKER_CONCURRENCY=4  # Match CPU count

# Task routing
CELERY_TASK_ROUTING = {
    'app.celery_app.run_debugging_workflow': {'queue': 'workflow'},
    'app.celery_app.check_execution_status': {'queue': 'monitoring'},
}

# Priority
CELERY_TASK_ACKS_LATE=True  # Requeue on worker failure
CELERY_TASK_REJECT_ON_WORKER_LOST=True
```

### Frontend Optimization

```bash
# Build optimization
npm run build  # Production build with tree-shaking

# Enable compression
# Gzip responses in nginx/proxy

# CDN
# Serve static assets from CDN

# Caching
# Set cache headers for static files
```

---

## 🔄 Backup & Recovery

### Database Backups

```bash
# Create backup
pg_dump -U debug_user debugging_agent > backup.sql

# Restore backup
psql -U debug_user debugging_agent < backup.sql

# Or via Docker
docker-compose exec db pg_dump -U debug_user debugging_agent > backup.sql
```

### Automated Backups (AWS RDS)

```bash
# Enable automated backups
# - Retention: 30 days
# - Backup window: 3:00 AM UTC
# - Multi-AZ: Enabled for HA
```

---

## 📈 Scaling Strategies

### Horizontal Scaling

```bash
# Scale Celery workers
docker-compose up -d --scale celery_worker=3

# Load balancing
# Use nginx/HAProxy for backend
# nginx.conf:
#   upstream backend {
#     server backend:8000;
#     server backend2:8000;
#   }
```

### Database Scaling

```bash
# Read replicas
# PostgreSQL physical replication
# - Primary (writes)
# - Read replicas (reads)

# Partitioning
# Partition large tables (executions, agent_executions)
# by date or project_id
```

---

## 🆘 Troubleshooting

### Common Issues

#### "Connection refused"
```bash
# Check if services are running
docker-compose ps

# Check port availability
lsof -i :8000  # Backend
lsof -i :5173  # Frontend
lsof -i :5432  # PostgreSQL

# Restart services
docker-compose restart
```

#### "OpenAI API rate limited"
```bash
# Wait before retrying
# Upgrade API tier
# Implement rate limiting in app

# Check API quota
curl https://api.openai.com/dashboard/account/rate-limits
```

#### "Database connection pool exhausted"
```bash
# Increase pool size
DATABASE_POOL_SIZE=100

# Check for connection leaks
SELECT count(*) FROM pg_stat_activity;

# Restart backend
docker-compose restart backend
```

#### "Celery task not executing"
```bash
# Check Celery is running
docker-compose exec celery_worker celery inspect active

# Check Redis connection
redis-cli ping

# View task queue
redis-cli LRANGE celery_queue 0 -1

# Restart Celery
docker-compose restart celery_worker
```

### Debug Mode

```bash
# Enable debug logging
LOG_LEVEL=DEBUG

# Check application logs
docker-compose logs -f backend

# Connect to backend
docker-compose exec backend bash
python -c "import app; print(app.config)"
```

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)

---

**Deployment successful! 🎉**

For questions or issues, refer to the troubleshooting section or open an issue on GitHub.
