# Quick Start Guide

## Getting Started in 5 Minutes

### Prerequisites

- Docker & Docker Compose (recommended)
- OR Python 3.11+, Node 18+, PostgreSQL 14+
- Git

### Option 1: Docker Compose (Recommended)

Fastest way to get everything running:

```bash
# 1. Navigate to project
cd debugging-agent

# 2. Copy environment template
cp .env.example .env

# 3. Start all services
docker-compose up

# 4. Wait for services to be ready (watch the logs)
# When you see "Uvicorn running on http://0.0.0.0:8000", you're good!

# 5. Open in browser
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Expected startup time**: 2-3 minutes

**Services running**:
- ✅ Frontend (React) - http://localhost:5173
- ✅ Backend (FastAPI) - http://localhost:8000
- ✅ PostgreSQL Database - localhost:5432
- ✅ Redis Cache - localhost:6379

### Option 2: Local Development Setup

For development without Docker:

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Create .env file in backend directory
cp ../.env.example ../.env

# Run migrations (when database is ready)
alembic upgrade head

# Start server
uvicorn app.main:app --reload
# Server runs at http://localhost:8000
```

#### Frontend Setup

```bash
# In another terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
# Frontend runs at http://localhost:5173
```

#### Database Setup

You need PostgreSQL running:

```bash
# Mac (with Homebrew)
brew services start postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
# And install with default settings

# Linux
sudo systemctl start postgresql
```

Create database:
```bash
psql -U postgres -c "CREATE DATABASE debugging_agent OWNER debug_user"
```

---

## First Time Usage

### 1. Check System Status

Navigate to http://localhost:5173 and verify:
- Dashboard loads
- Status indicator shows "● Online"
- All stat cards display (0s are fine for new system)

### 2. Create a Project

On the "Projects" page:
1. Click "New Project"
2. Enter name: `test-project`
3. Enter description: `My first debugging analysis`
4. Click "Create Project"

### 3. Run an Analysis

1. Click "Run Analysis" on your project
2. Watch the Dashboard update in real-time
3. Execution status progresses through agents:
   - ⚙️ Testing Agent
   - 🔍 Debugging Agent
   - ✏️ Coding Agent
   - 🏗️ Architect Agent
   - 📋 Project Manager

### 4. View Results

Click on the execution to see:
- Agent execution timeline
- Root causes identified
- Proposed fixes
- Implementation plan

---

## API Endpoints (for testing)

Use curl or Postman to test the API:

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Create Project
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-project",
    "description": "Test project"
  }'
```

### List Projects
```bash
curl http://localhost:8000/api/projects
```

### Start Execution
```bash
curl -X POST http://localhost:8000/api/executions \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "PROJECT_UUID_HERE",
    "test_framework": "pytest",
    "test_paths": []
  }'
```

### Get Execution Status
```bash
curl http://localhost:8000/api/executions/EXECUTION_UUID_HERE
```

**Full API docs available at**: http://localhost:8000/docs

---

## Common Tasks

### View Logs

#### Backend Logs
```bash
# If using Docker
docker logs debugging-agent-backend

# If running locally
# Logs appear in terminal where uvicorn is running
```

#### Frontend Logs
```bash
# Browser console (Ctrl+Shift+J or Cmd+Option+J)
# Network tab to see API calls
```

### Access Database

```bash
# Connect with psql
psql -h localhost -U debug_user -d debugging_agent

# Common queries
\dt                    # List all tables
SELECT * FROM projects;  # View projects
SELECT * FROM executions;  # View executions
```

### Rebuild Containers

```bash
# Stop services
docker-compose down

# Rebuild
docker-compose build

# Restart
docker-compose up
```

### Reset Database

```bash
# Remove database volume
docker-compose down -v

# Restart (recreates empty database)
docker-compose up
```

---

## Troubleshooting

### "Connection refused" on localhost:8000

**Solution**: Backend not ready yet
- Wait 30-40 seconds for startup
- Check logs: `docker logs debugging-agent-backend`
- Verify database is running: `curl localhost:5432`

### "Cannot connect to database"

**Solution**: PostgreSQL not running
- Check status: `docker ps | grep postgres`
- Restart: `docker-compose restart db`
- Wait for health check to pass

### Frontend shows "API Offline"

**Solution**: Backend not responding
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check CORS settings in `.env`
- Browser console for errors (F12)

### Port already in use

**Solution**: Change ports or stop conflicting service

Edit `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change to different port
```

### Out of memory

**Solution**: Docker needs more resources
- Increase Docker resources in Docker Desktop settings
- Or stop other containers

---

## Development Workflow

### Making Changes to Backend

1. Backend files are mounted as volumes
2. Changes auto-reload (uvicorn reload mode)
3. No restart needed

### Making Changes to Frontend

1. Frontend files are mounted as volumes
2. Vite hot-reload on save
3. No restart needed

### Running Tests

```bash
# Backend tests
docker-compose exec backend pytest

# Or locally
cd backend
pytest

# With coverage
pytest --cov=app tests/

# Frontend tests
docker-compose exec frontend npm run test
```

### Code Quality

```bash
# Backend formatting
black backend/app

# Backend linting
ruff check backend/

# Frontend linting
docker-compose exec frontend npm run lint

# Type checking
docker-compose exec backend mypy app/
```

---

## Next Steps

1. **Explore the codebase**:
   - [backend/app/agents/](../backend/app/agents/) - Multi-agent system
   - [frontend/src/pages/](../frontend/src/pages/) - UI components
   - [docs/architecture.md](architecture.md) - System design

2. **Read the documentation**:
   - [README.md](../README.md) - Overview
   - [docs/architecture.md](architecture.md) - Architecture deep-dive
   - [docs/agents.md](agents.md) - Agent specifications

3. **Extend the system**:
   - Add new agents
   - Customize analysis logic
   - Connect to real LLM service

4. **Deploy**:
   - See [docker-compose.yml](../docker-compose.yml) for production setup
   - Use Kubernetes for scale
   - Configure CI/CD pipeline

---

## Getting Help

- **API Documentation**: http://localhost:8000/docs
- **Frontend Logs**: Browser DevTools (F12)
- **Backend Logs**: `docker logs debugging-agent-backend`
- **Database Issues**: `psql` command line or pgAdmin

---

## Performance Expectations

- **Dashboard load**: ~500ms
- **Project creation**: ~100ms
- **Full workflow execution**: 10-30 seconds (demo data)
- **With real tests**: Depends on test suite size

---

Enjoy debugging! 🚀
