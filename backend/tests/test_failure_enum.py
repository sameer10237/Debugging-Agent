"""Unit tests for FailureTypeEnum normalization and error handling."""

from app.models import FailureTypeEnum


def test_failure_type_enum_accepts_title_case():
    """Ensure Title Case values from DebuggingAgent resolve correctly."""
    assert FailureTypeEnum("Type Error") == FailureTypeEnum.TYPE_ERROR
    assert FailureTypeEnum("Logic Error") == FailureTypeEnum.LOGIC_ERROR
    assert FailureTypeEnum("Database Error") == FailureTypeEnum.DATABASE_ERROR
    assert FailureTypeEnum("Authentication Error") == FailureTypeEnum.AUTHENTICATION_ERROR
    assert FailureTypeEnum("Security Error") == FailureTypeEnum.SECURITY_ERROR
    assert FailureTypeEnum("Runtime Error") == FailureTypeEnum.RUNTIME_ERROR


def test_failure_type_enum_accepts_uppercase():
    """Ensure uppercase strings from ImprovedDebuggingAgent resolve correctly."""
    assert FailureTypeEnum("TYPE_ERROR") == FailureTypeEnum.TYPE_ERROR
    assert FailureTypeEnum("LOGIC_ERROR") == FailureTypeEnum.LOGIC_ERROR
    assert FailureTypeEnum("RUNTIME_ERROR") == FailureTypeEnum.RUNTIME_ERROR


def test_failure_type_enum_falls_back_to_unknown():
    """Ensure unexpected or arbitrary string values gracefully fall back to UNKNOWN."""
    assert FailureTypeEnum("completely_new_error") == FailureTypeEnum.UNKNOWN
    assert FailureTypeEnum("") == FailureTypeEnum.UNKNOWN
