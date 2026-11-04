"""Tests ensuring models do not share mutable default instances."""

from app.models import Analysis, Execution, ProposedFix


def test_json_defaults_produce_independent_objects():
    """Verify that multiple instances get fresh dict/list objects rather than shared singletons."""
    # Test Execution metadata default callable
    col_execution_metadata = Execution.__table__.columns["metadata"]
    assert callable(col_execution_metadata.default.arg)
    default1 = col_execution_metadata.default.arg(None)
    default2 = col_execution_metadata.default.arg(None)
    assert default1 == {}
    assert default1 is not default2

    # Test Analysis evidence default callable
    col_evidence = Analysis.__table__.columns["evidence"]
    assert callable(col_evidence.default.arg)
    list1 = col_evidence.default.arg(None)
    list2 = col_evidence.default.arg(None)
    assert list1 == []
    assert list1 is not list2

    # Test ProposedFix regression_tests default callable
    col_tests = ProposedFix.__table__.columns["regression_tests"]
    assert callable(col_tests.default.arg)
    tests1 = col_tests.default.arg(None)
    tests2 = col_tests.default.arg(None)
    assert tests1 == []
    assert tests1 is not tests2
