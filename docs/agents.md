# Multi-Agent System Specification

## Overview

The system consists of five specialized agents orchestrated by LangGraph, each with distinct responsibilities in the debugging workflow.

## Agent Specifications

### 1. Testing Agent

**Responsibility**: Execute tests and capture failures

**Inputs**:
- `project_path`: Path to project directory
- `test_framework`: Framework type (pytest, jest, unittest, etc.)
- `test_paths`: Specific test files to run (optional)

**Process**:
1. Identify test framework
2. Execute test suite
3. Capture pass/fail results
4. Extract error messages and stack traces
5. Classify failure types
6. Generate test report

**Outputs**:
```python
{
    "test_results": {
        "framework": "pytest",
        "total_tests": 15,
        "passed": 12,
        "failed": 2,
        "skipped": 1,
        "execution_time": 3.45,
        "test_details": [...]
    },
    "failures": [
        {
            "test_name": "test_login_invalid_password",
            "error": "AssertionError: Expected 401, got 200",
            "traceback": "...",
            "timestamp": "2024-01-30T10:30:00Z"
        }
    ],
    "test_count": 15,
    "passed_count": 12,
    "failed_count": 2
}
```

**Error Handling**:
- Test framework not found → Fallback to pytest
- No tests found → Report empty test suite
- Test timeout → Mark as failed with timeout error

---

### 2. Debugging Agent

**Responsibility**: Perform root-cause analysis and diagnose failures

**Core Methodology** (from system prompt):
1. Understand intended behavior
2. Analyze the failure (expected vs actual)
3. Classify the failure type
4. Trace through system architecture
5. Perform root-cause analysis
6. Distinguish root cause from symptoms
7. Evaluate fix strategy

**Inputs**:
- `failures`: List of failures from Testing Agent
- `test_results`: Full test execution results
- `source_code`: Relevant source code files
- `requirements`: Original system requirements
- `architecture`: System architecture description

**Failure Classifications**:
```python
LOGIC_ERROR           # Incorrect logic/algorithm
TYPE_ERROR            # Type mismatch issues
RUNTIME_ERROR         # Unexpected runtime conditions
API_ERROR             # API contract violations
DATABASE_ERROR        # Database-related issues
AUTHENTICATION_ERROR  # Auth/security issues
SECURITY_ERROR        # Vulnerability detected
```

**Analysis Process**:
1. Extract evidence from failure
2. Trace execution path
3. Identify exact failure point
4. Determine root cause (not just symptom)
5. Assess confidence level
6. Check security implications

**Outputs**:
```python
{
    "analyses": [
        {
            "test_name": "test_login_invalid_password",
            "failure_type": "LOGIC_ERROR",
            "evidence": [
                "Test: test_login_invalid_password",
                "Error: Expected 401, got 200",
                "Traceback available: true",
                "Stack depth: 5",
                "First frame: File auth.py, line 42"
            ],
            "trace": {
                "entry_point": "HTTP endpoint",
                "middleware": ["Authentication", "CORS", "Logging"],
                "handler": "Route handler",
                "failure_point": "Service layer"
            },
            "root_cause": {
                "category": "LOGIC_ERROR",
                "description": "Function returns None for invalid credentials instead of raising exception",
                "location": "app/services/auth.py",
                "causal_chain": [
                    "User enters invalid password",
                    "Repository returns False",
                    "Service returns None instead of raising InvalidCredentialsError",
                    "Route treats None as successful login",
                    "Returns 200 instead of 401"
                ]
            },
            "affected_components": ["Authentication Service", "User Repository"],
            "confidence": 95,
            "security_implications": "MEDIUM: Authentication bypass possible"
        }
    ],
    "grouped_by_root_cause": {
        "Function returns None in error cases": ["test_login_invalid_password"]
    },
    "priority": [
        {"test": "test_login_invalid_password", "priority": 1, "confidence": 95}
    ]
}
```

**Key Principles**:
- Confidence scoring (0-100)
- Evidence-based diagnosis
- Distinguish root cause from symptoms
- Security implications flagged
- Minimal safe fixes only

---

### 3. Coding Agent

**Responsibility**: Implement proposed fixes

**Inputs**:
- `analysis`: Debugging analysis results
- `source_code`: Relevant source code
- `project_structure`: Project layout

**Process**:
1. Review root cause analysis
2. Determine fix strategy (minimal change)
3. Generate code changes
4. Validate fix safety
5. Generate regression tests
6. Assess risk level

**Outputs**:
```python
{
    "proposed_fixes": [
        {
            "test_name": "test_login_invalid_password",
            "affected_component": "app/services/auth.py",
            "fix_type": "add_error_handling",
            "code_change": {
                "file": "app/services/auth.py",
                "function": "authenticate_user",
                "before": "user = repository.find_user(username)\nuser.id",
                "after": "user = repository.find_user(username)\nif user is None:\n    raise UserNotFoundError()\nuser.id"
            },
            "risk_level": "low"
        }
    ],
    "validations": [
        {
            "fix_test": "test_login_invalid_password",
            "valid": true,
            "checks": {
                "syntax_correct": true,
                "no_security_issues": true,
                "maintains_api_contract": true,
                "no_breaking_changes": true
            }
        }
    ],
    "implementation_ready": true,
    "regression_tests": [
        {
            "test_name": "test_login_invalid_password_returns_401",
            "description": "Verify invalid password returns 401",
            "test_code": "def test_login_invalid_password():\n    response = client.post(...)\n    assert response.status_code == 401"
        }
    ]
}
```

**Validation Criteria**:
- Syntax correctness
- No security regressions
- API contract maintained
- No breaking changes
- Code quality

---

### 4. Architect Agent

**Responsibility**: Review architectural implications

**Inputs**:
- `proposed_fixes`: Fixes from Coding Agent
- `architecture`: Current system architecture
- `constraints`: Architectural constraints

**Process**:
1. Review each fix for design impact
2. Check architectural consistency
3. Identify cross-cutting concerns
4. Assess scalability implications
5. Evaluate maintainability impact

**Outputs**:
```python
{
    "reviews": [
        {
            "test_name": "test_login_invalid_password",
            "impacts": ["Authentication Service", "User Management"],
            "consistency": "Changes align with current architecture",
            "scalability": "No scalability concerns",
            "maintainability": "Improves code maintainability",
            "approved": true
        }
    ],
    "cross_cutting_concerns": [
        {
            "concern": "Error Handling",
            "description": "All authentication errors should be handled consistently",
            "affected_fixes": 1
        }
    ],
    "architectural_fit": {
        "overall_fit": "Excellent",
        "consistency": 95,
        "alignment_with_patterns": 90
    }
}
```

**Review Criteria**:
- Design pattern alignment
- Consistency with architecture
- Scalability impact
- Maintainability considerations
- Cross-module dependencies

---

### 5. Project Manager Agent

**Responsibility**: Prioritization and implementation planning

**Inputs**:
- `analysis`: Debugging analysis
- `proposed_fixes`: Proposed code fixes
- `architectural_review`: Architect review
- `requirements`: Project requirements

**Process**:
1. Prioritize fixes by impact and effort
2. Identify conflicts between fixes
3. Estimate implementation effort
4. Create implementation plan
5. Manage requirements and constraints

**Outputs**:
```python
{
    "priorities": [
        {
            "rank": 1,
            "fix": "test_login_invalid_password",
            "severity": "high",
            "effort": "low",
            "impact": "high",
            "recommendation": "Implement immediately"
        }
    ],
    "conflicts": [
        {
            "type": "dependency",
            "description": "Fix A must be implemented before Fix B",
            "resolution": "Follow priority order"
        }
    ],
    "effort_estimates": {
        "total_hours": 4,
        "total_days": 1,
        "by_priority": [...]
    },
    "implementation_plan": [
        {
            "phase": "Phase 1",
            "fixes": ["test_login_invalid_password"],
            "timeline": "Day 1",
            "deliverables": ["Code changes", "Tests", "Documentation"]
        }
    ]
}
```

**Prioritization Factors**:
1. Security severity
2. Data corruption/loss risk
3. System stability
4. Business impact
5. Implementation effort

---

## Agent Communication

### Message Protocol

```python
{
    "sender": "debugging_agent",
    "recipient": "coding_agent",
    "message_type": "request",
    "content": {
        "analysis_id": "uuid",
        "root_causes": [...],
        "affected_components": [...]
    },
    "timestamp": "2024-01-30T10:30:00Z"
}
```

### State Flow

```
Initial State
    ↓
Testing Agent executes
    ↓ (enriched with test results)
Debugging Agent analyzes
    ↓ (enriched with analysis)
Coding Agent implements
    ↓ (enriched with fixes)
Architect Agent reviews
    ↓ (enriched with review)
Project Manager prioritizes
    ↓ (final state)
Complete Workflow Result
```

---

## Agent Configuration

### Timeouts
```python
agent_timeout: int = 300  # 5 minutes per agent
max_agent_iterations: int = 5
```

### Resource Limits
```python
max_test_duration: int = 600  # 10 minutes
max_analysis_depth: int = 10  # Call stack depth
max_file_size: int = 52428800  # 50MB
```

### LLM Integration

When integrated with LLMs, agents use:
- Model: GPT-4 (configurable)
- Temperature: 0.1 (for deterministic analysis)
- Max tokens: 8192
- Prompt engineering for consistency

---

## Error Handling Strategy

### Testing Agent Failures
- Exception: Fall back to summary analysis
- Timeout: Mark tests as inconclusive
- Missing files: Report missing dependencies

### Debugging Agent Failures
- Insufficient evidence: Return low confidence
- Parse errors: Use fallback classification
- No root cause found: Escalate for manual review

### Coding Agent Failures
- Invalid fixes: Rollback to previous state
- Validation failure: Request architect review
- Syntax error: Report and suggest alternatives

### Architect Agent Failures
- Conflicting reviews: Escalate to Project Manager
- Missing architecture: Use default assumptions

### Project Manager Failures
- Conflict resolution: All options presented
- No viable plan: Escalate for manual planning

---

## Testing & Verification

### Agent Unit Tests
```python
def test_debugging_agent_classifies_logic_error()
def test_coding_agent_generates_valid_fixes()
def test_architect_agent_identifies_risks()
def test_project_manager_priorities_by_severity()
```

### Integration Tests
```python
def test_full_workflow_execution()
def test_agent_state_propagation()
def test_error_handling_and_recovery()
```

### Validation
- All outputs match expected schemas
- Confidence scores are calibrated
- Fixes pass regression tests
- Prioritization is consistent

---

## Future Enhancements

1. **LLM Integration**: Use GPT-4 for analysis
2. **Machine Learning**: Learn from historical fixes
3. **Custom Plugins**: User-defined agent types
4. **Parallel Execution**: Multiple agents in parallel
5. **Async Task Queue**: Background job processing
6. **Webhooks**: Real-time notifications

