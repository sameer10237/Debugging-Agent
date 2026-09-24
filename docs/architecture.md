# System Architecture

## Overview

The AI-Driven Multi-Agent Software Debugging System is a production-grade full-stack application that orchestrates multiple specialized AI agents to autonomously diagnose, analyze, and propose fixes for software defects.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Frontend (React + TypeScript)                │
│              - Project Management Dashboard                  │
│              - Execution Monitoring                          │
│              - Results Visualization                         │
└─────────────────────────┬─────────────────────────────────────┘
                          │ REST API (FastAPI)
                          │ HTTP/WebSocket
┌─────────────────────────▼─────────────────────────────────────┐
│                   Backend (Python/FastAPI)                    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         LangGraph Agent Orchestrator                 │   │
│  │                                                      │   │
│  │  [Testing] ──→ [Debugging] ──→ [Coding] ──→         │   │
│  │                                  [Architect] ──→     │   │
│  │                                  [Project Manager]   │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                    │
│  ┌──────────────────────▼──────────────────────────────┐   │
│  │      SQLAlchemy ORM + PostgreSQL Database           │   │
│  │  - Projects, Executions, Agents, Analyses, Fixes    │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### Frontend Layer

**Technology**: React 18 + TypeScript + Vite

**Key Components**:
- `Dashboard` - Overall system status and statistics
- `ProjectList` - Manage projects and trigger analyses
- `ExecutionDetail` - View detailed results of executions
- `API Client` - Axios-based HTTP client

**Features**:
- Real-time status updates
- Multi-project support
- Execution history tracking
- Results export

### Backend Layer

**Technology**: FastAPI + Python 3.11

**Main Components**:

#### 1. **Agent Orchestration** (LangGraph)
   - **Base Agent** - Abstract base class for all agents
   - **AgentOrchestrator** - Coordinates agent execution and state management

#### 2. **Specialized Agents**

   **Testing Agent**:
   - Executes test suites (pytest, jest, etc.)
   - Captures failures and stack traces
   - Provides evidence for other agents
   - Input: Project path, test framework
   - Output: Test results, failures list

   **Debugging Agent**:
   - Performs advanced root-cause analysis
   - Classifies failure types
   - Traces execution paths
   - Generates evidence-based diagnoses
   - Input: Test failures, source code
   - Output: Root causes, confidence scores

   **Coding Agent**:
   - Proposes minimal code changes
   - Validates fixes for safety
   - Generates regression tests
   - Input: Debugging analysis
   - Output: Proposed fixes, test cases

   **Architect Agent**:
   - Reviews architectural implications
   - Checks design consistency
   - Identifies cross-cutting concerns
   - Input: Proposed fixes, architecture
   - Output: Approval/recommendations

   **Project Manager Agent**:
   - Prioritizes fixes
   - Manages requirements
   - Estimates effort
   - Resolves conflicts
   - Input: All previous agent outputs
   - Output: Implementation plan

#### 3. **REST API**
   - `/api/health` - Health checks
   - `/api/projects` - Project CRUD operations
   - `/api/executions` - Workflow execution endpoints
   - `/api/analyses` - Analysis results (extended)

#### 4. **Data Models** (SQLAlchemy)
   - `Project` - Project metadata
   - `Execution` - Workflow executions
   - `AgentExecution` - Individual agent runs
   - `TestRun` - Test execution results
   - `Failure` - Detected failures
   - `Analysis` - Analysis results
   - `ProposedFix` - Proposed code fixes

### Database Layer

**Technology**: PostgreSQL 16

**Key Tables**:
```
projects
├── id (UUID, PK)
├── name (String)
├── description (Text)
└── repository_url (String)

executions
├── id (UUID, PK)
├── project_id (FK)
├── status (ENUM: pending, running, completed, failed)
└── metadata (JSON)

agent_executions
├── id (UUID, PK)
├── execution_id (FK)
├── agent_name (String)
├── status (ENUM)
└── input/output_data (JSON)

analyses
├── id (UUID, PK)
├── execution_id (FK)
├── failure_type (ENUM)
├── root_cause (Text)
├── confidence (Integer: 0-100)
└── recommendations (JSON)
```

## Workflow Execution

### Standard Debugging Workflow

```
1. User Creates Project
   └─ Project uploaded to system

2. Testing Phase
   ├─ Testing Agent executes tests
   ├─ Captures failures and stack traces
   └─ Produces test report

3. Debugging Phase
   ├─ Debugging Agent analyzes failures
   ├─ Performs root-cause analysis
   ├─ Classifies failure types
   └─ Produces diagnostic report

4. Coding Phase
   ├─ Coding Agent reviews diagnosis
   ├─ Proposes minimal fixes
   ├─ Generates regression tests
   └─ Produces fix recommendations

5. Architect Review
   ├─ Architect Agent reviews fixes
   ├─ Checks architectural fit
   ├─ Identifies cross-cutting concerns
   └─ Produces architectural review

6. Project Management
   ├─ Project Manager prioritizes fixes
   ├─ Estimates effort
   ├─ Resolves conflicts
   └─ Creates implementation plan

7. Results Presentation
   └─ Dashboard displays findings and recommendations
```

## Data Flow

### Request Flow
```
User Input (Frontend)
    ↓
REST API Endpoint (FastAPI)
    ↓
Authentication/Validation
    ↓
Database Operations (SQLAlchemy)
    ↓
Agent Orchestrator
    ↓
Individual Agents
    ↓
Results stored in DB
    ↓
Response returned to Frontend
```

### State Management

**Execution State**:
- Passed through LangGraph workflow
- Updated by each agent
- Persisted to database
- Accessible via API

```python
execution_state = {
    "project_id": "uuid",
    "test_results": {...},
    "failures": [...],
    "analyses": [...],
    "proposed_fixes": [...],
    "architectural_review": {...},
    "implementation_plan": {...}
}
```

## Key Design Patterns

### 1. **Agent Pattern**
- Each agent has single responsibility
- Agents are composable and orchestrated
- Results flow through execution state
- Error handling at agent level

### 2. **Repository Pattern**
- Data access abstraction
- SQLAlchemy models + async sessions
- Connection pooling
- Transaction management

### 3. **Service Layer**
- Business logic encapsulation
- Validation and error handling
- State management
- Coordination between layers

### 4. **API Contract Pattern**
- Pydantic models for request/response validation
- Consistent error responses
- OpenAPI/Swagger documentation
- Status codes as specification

## Security Considerations

### 1. **Authentication & Authorization**
- Bearer token support (ready for JWT)
- Per-project isolation
- Role-based access control (future)

### 2. **Data Protection**
- Secrets in environment variables
- No credentials in code/logs
- SQL injection prevention (SQLAlchemy parameterized queries)
- Input validation on all endpoints

### 3. **Code Execution**
- Sandboxed test execution
- File upload restrictions
- Resource limits
- Audit logging

## Deployment Architecture

### Development
- All services in docker-compose
- Hot-reload for frontend/backend
- Local PostgreSQL instance

### Production
- Kubernetes-ready architecture
- Container image per service
- Environment-based configuration
- Health checks and auto-restart

```
Frontend: nginx/serve
    ↓
Backend: Gunicorn + FastAPI
    ↓
PostgreSQL: Replicated DB
Redis: Caching/Task Queue
```

## Performance Characteristics

### Scaling
- Async/await throughout
- Connection pooling (20 connections default)
- Stateless API design
- Horizontal scaling ready

### Response Times
- API endpoints: < 100ms
- Test execution: Variable (project dependent)
- Analysis generation: 2-10s
- Full workflow: 10-30s average

## Monitoring & Observability

### Logging
- Structured logging (JSON)
- Per-agent logging
- Request/response logging
- Error tracking

### Metrics
- Execution duration
- Success/failure rates
- Agent performance
- Database query times

### Health Checks
- `/api/health` - Service health
- `/api/ready` - Readiness probe
- Database connectivity
- External service availability

## Extension Points

### Adding New Agents
1. Extend `BaseAgent` class
2. Implement `execute()` method
3. Register with orchestrator
4. Add routes if needed

### Adding Analysis Types
1. Extend `Failure` model
2. Add classification logic to Debugging Agent
3. Extend recommendations engine

### Adding Storage Backends
1. Implement database adapter
2. Maintain SQLAlchemy interface
3. Update connection pooling

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18, TypeScript, Vite | UI/UX |
| Backend API | FastAPI, Pydantic | REST endpoints |
| Orchestration | LangGraph | Agent coordination |
| ORM | SQLAlchemy | Data persistence |
| Database | PostgreSQL | Persistent storage |
| Caching | Redis | Cache/queue |
| Containerization | Docker | Deployment |
| IaC | Docker Compose | Local development |

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
