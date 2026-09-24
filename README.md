# AI-Driven Multi-Agent Software Debugging System

A production-grade full-stack system that orchestrates multiple AI agents to autonomously diagnose, analyze, and propose fixes for software defects.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React/TypeScript Frontend                 │
│                   (Dashboard & Monitoring)                   │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────┐
│                   FastAPI Backend                            │
│            LangGraph Multi-Agent Orchestration               │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │Testing Agent │  │Debugging Ag  │  │Coding Agent  │       │
│  │              │  │              │  │              │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │Architect Ag  │  │Project Mgr   │                         │
│  │              │  │              │                         │
│  └──────────────┘  └──────────────┘                         │
├──────────────────────────────────────────────────────────────┤
│    SQLAlchemy ORM    │    PostgreSQL Database                │
└──────────────────────────────────────────────────────────────┘
```

## Multi-Agent System

### 1. **Testing Agent**
- Executes test suites
- Captures failures and stack traces
- Provides evidence to other agents

### 2. **Debugging Agent**
- Analyzes failure evidence
- Performs root-cause analysis
- Classifies failure types
- Proposes minimal safe fixes

### 3. **Coding Agent**
- Implements fixes recommended by Debugging Agent
- Modifies source code
- Ensures code quality and security

### 4. **Architect Agent**
- Reviews structural implications
- Evaluates design impact
- Recommends architectural changes

### 5. **Project Manager Agent**
- Handles requirement clarification
- Manages prioritization
- Resolves conflicts

## Features

- 🤖 **Multi-Agent Orchestration** — LangGraph-powered agent coordination
- 🔍 **Advanced Root-Cause Analysis** — Systematic debugging methodology
- 🛡️ **Security-First** — Security implications flagged automatically
- 📊 **Real-time Monitoring** — React dashboard tracking agent progress
- 🗄️ **PostgreSQL Integration** — Persistent state management
- 🐳 **Docker Support** — Complete containerization
- ✅ **Comprehensive Testing** — pytest and integration tests
- 📚 **Full Documentation** — Architecture, APIs, and guides

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Docker & Docker Compose

### Setup

```bash
# Clone and navigate
cd debugging-agent

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"

# Frontend setup
cd ../frontend
npm install

# Start services
docker-compose up -d

# Run migrations
cd ../backend
alembic upgrade head

# Start backend
uvicorn app.main:app --reload

# In another terminal, start frontend
cd frontend
npm run dev
```

Access the dashboard at `http://localhost:5173`

## Project Structure

```
debugging-agent/
├── backend/                    # FastAPI + LangGraph backend
│   ├── app/
│   │   ├── agents/            # Multi-agent implementations
│   │   ├── api/               # REST endpoints
│   │   ├── models/            # SQLAlchemy models
│   │   ├── services/          # Business logic
│   │   ├── config.py          # Configuration
│   │   └── main.py            # FastAPI app
│   ├── migrations/            # Alembic migrations
│   ├── tests/                 # pytest test suite
│   ├── pyproject.toml         # Project metadata
│   └── requirements.txt        # Python dependencies
├── frontend/                  # React + TypeScript frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API clients
│   │   ├── hooks/             # Custom React hooks
│   │   ├── types/             # TypeScript types
│   │   └── App.tsx            # Root component
│   ├── public/                # Static assets
│   ├── vite.config.ts         # Vite configuration
│   └── package.json           # Node dependencies
├── shared/                    # Shared types and constants
│   ├── schemas.ts             # TypeScript schemas
│   └── constants.ts           # Shared constants
├── docs/                      # Documentation
│   ├── architecture.md        # System design
│   ├── agents.md              # Agent specifications
│   └── api.md                 # API documentation
├── docker-compose.yml         # Container orchestration
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Environment Variables

See `.env.example` for all available options:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/debugging_agent

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Frontend
VITE_API_URL=http://localhost:8000

# LLM Configuration
OPENAI_API_KEY=your_key_here
MODEL_NAME=gpt-4
```

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=app tests/

# Frontend tests
cd frontend
npm run test
```

### Code Quality

```bash
# Backend linting and formatting
cd backend
ruff check .
black .
mypy app/

# Frontend linting
cd frontend
npm run lint
```

## API Endpoints

### Agent Management
- `POST /api/agents/execute` — Execute debugging workflow
- `GET /api/agents/{id}/status` — Get agent execution status
- `GET /api/agents/{id}/results` — Retrieve analysis results

### Test Management
- `POST /api/tests/run` — Trigger test execution
- `GET /api/tests/{id}/results` — Get test results
- `GET /api/failures` — List detected failures

### Code Analysis
- `GET /api/codebase/info` — Codebase metadata
- `POST /api/analysis/run` — Start analysis
- `GET /api/fixes` — Proposed fixes

See [docs/api.md](docs/api.md) for full API documentation.

## Workflow Example

1. **User uploads codebase** → Frontend sends to backend
2. **Testing Agent runs** → Executes test suite, captures failures
3. **Debugging Agent analyzes** → Performs root-cause analysis
4. **System generates report** → Evidence, classification, root cause
5. **Coding Agent proposes fix** → Minimal code changes recommended
6. **Dashboard updates** → User reviews findings and recommendations
7. **Optional: Apply fix** → Backend can commit changes

## Security

- ✅ SQL injection prevention (SQLAlchemy parameterized queries)
- ✅ CORS properly configured
- ✅ Input validation on all endpoints
- ✅ Authentication/Authorization ready for integration
- ✅ No secrets in code (environment variables)
- ✅ Security headers in HTTP responses

## Performance

- Async/await throughout backend
- Connection pooling for database
- Frontend code-splitting and lazy loading
- Efficient agent state management

## Monitoring

Real-time dashboard shows:
- Agent execution status
- Test execution progress
- Failure classification
- Root-cause analysis timeline
- Recommended fixes review queue

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test
3. Format code: `black` and `ruff`
4. Submit PR

## License

MIT License - see LICENSE file for details

## Architecture Deep Dive

See [docs/architecture.md](docs/architecture.md) for:
- Agent state machine
- Message passing protocol
- Failure classification taxonomy
- Database schema
- Integration patterns

## Agent Specifications

See [docs/agents.md](docs/agents.md) for:
- Testing Agent capabilities
- Debugging Agent methodology
- Coding Agent constraints
- Architect Agent review criteria
- Project Manager resolution process

---

**Built with LangGraph, FastAPI, SQLAlchemy, PostgreSQL, React, and TypeScript**
