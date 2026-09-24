"""SQLAlchemy models for the debugging system."""

from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, JSON, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from datetime import datetime
from uuid import uuid4
import enum


class User(Base):
    """Registered application user."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(512), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ExecutionStatusEnum(str, enum.Enum):
    """Execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FailureTypeEnum(str, enum.Enum):
    """Failure type classification."""
    LOGIC_ERROR = "logic_error"
    TYPE_ERROR = "type_error"
    SYNTAX_ERROR = "syntax_error"
    RUNTIME_ERROR = "runtime_error"
    API_ERROR = "api_error"
    DATABASE_ERROR = "database_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    CONFIGURATION_ERROR = "configuration_error"
    DEPENDENCY_ERROR = "dependency_error"
    CONCURRENCY_ERROR = "concurrency_error"
    STATE_MANAGEMENT_ERROR = "state_management_error"
    VALIDATION_ERROR = "validation_error"
    INTEGRATION_ERROR = "integration_error"
    TEST_ERROR = "test_error"
    ENVIRONMENT_ERROR = "environment_error"
    SECURITY_ERROR = "security_error"
    PERFORMANCE_ERROR = "performance_error"
    UNKNOWN = "unknown"


class Project(Base):
    """Represents a software project being debugged."""
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    repository_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    executions = relationship("Execution", back_populates="project", cascade="all, delete-orphan")
    tests = relationship("TestRun", back_populates="project", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="project", cascade="all, delete-orphan")


class Execution(Base):
    """Represents a debugging workflow execution."""
    __tablename__ = "executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    status = Column(Enum(ExecutionStatusEnum), default=ExecutionStatusEnum.PENDING, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    execution_metadata = Column("metadata", JSON, nullable=True, default={})
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="executions")
    agents = relationship("AgentExecution", back_populates="execution", cascade="all, delete-orphan")
    analysis = relationship("Analysis", uselist=False, back_populates="execution")


class AgentExecution(Base):
    """Represents execution of a specific agent."""
    __tablename__ = "agent_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("executions.id"), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False)  # testing, debugging, coding, architect, project_manager
    status = Column(Enum(ExecutionStatusEnum), default=ExecutionStatusEnum.PENDING, nullable=False)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    execution = relationship("Execution", back_populates="agents")


class TestRun(Base):
    """Represents a test execution."""
    __tablename__ = "test_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    test_file = Column(String(512), nullable=False)
    test_name = Column(String(255), nullable=False)
    status = Column(Enum(ExecutionStatusEnum), default=ExecutionStatusEnum.PENDING, nullable=False)
    passed = Column(Boolean, nullable=True)
    output = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    traceback = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)  # milliseconds
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="tests")


class Failure(Base):
    """Represents a detected test failure."""
    __tablename__ = "failures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    test_run_id = Column(UUID(as_uuid=True), ForeignKey("test_runs.id"), nullable=False, index=True)
    failure_type = Column(Enum(FailureTypeEnum), default=FailureTypeEnum.UNKNOWN, nullable=False)
    message = Column(Text, nullable=False)
    expected = Column(Text, nullable=True)
    actual = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Analysis(Base):
    """Represents debugging analysis results."""
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("executions.id"), nullable=False, unique=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    failure_type = Column(Enum(FailureTypeEnum), nullable=True)
    root_cause = Column(Text, nullable=True)
    evidence = Column(JSON, nullable=True, default=[])
    affected_files = Column(JSON, nullable=True, default=[])
    affected_functions = Column(JSON, nullable=True, default=[])
    confidence = Column(Integer, nullable=True)  # 0-100
    recommendations = Column(JSON, nullable=True, default=[])
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    execution = relationship("Execution", back_populates="analysis")
    project = relationship("Project", back_populates="analyses")


class ProposedFix(Base):
    """Represents a proposed fix."""
    __tablename__ = "proposed_fixes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False, index=True)
    file_path = Column(String(512), nullable=False)
    change_description = Column(Text, nullable=False)
    code_before = Column(Text, nullable=True)
    code_after = Column(Text, nullable=True)
    risk_level = Column(String(50), nullable=True)  # low, medium, high
    regression_tests = Column(JSON, nullable=True, default=[])
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
