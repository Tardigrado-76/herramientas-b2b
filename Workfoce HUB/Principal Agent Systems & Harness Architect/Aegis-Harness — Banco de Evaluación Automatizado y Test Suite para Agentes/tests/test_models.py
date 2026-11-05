import pytest
from aegis.models import (
    TestCase, TestCategory, AgentExecutionOutput, MetricEvaluation, TestResult, SuiteSummary
)

def test_test_case_validation():
    tc = TestCase(
        id="TC-001",
        category=TestCategory.FUNCTIONAL,
        description="Query employee table in SQLite",
        input_query="Dame los usuarios de la base de datos",
        expected_server="sqlite",
        expected_tool="query",
        expected_args={"sql": "SELECT * FROM users"}
    )
    assert tc.id == "TC-001"
    assert tc.category == TestCategory.FUNCTIONAL
    assert tc.max_latency_ms == 3500

def test_metric_evaluation_score_bounds():
    m = MetricEvaluation(name="tool_precision", score=95.5, passed=True, details="OK")
    assert m.score == 95.5
    assert m.passed is True

    with pytest.raises(Exception):
        MetricEvaluation(name="invalid", score=150.0, passed=False)

def test_suite_summary_serialization():
    summary = SuiteSummary(
        suite_name="Functional Battery",
        timestamp="2026-10-23T12:00:00Z",
        total_tests=10,
        passed_tests=10,
        failed_tests=0,
        pass_rate_percent=100.0,
        overall_score=94.5,
        quality_gate_passed=True
    )
    assert summary.pass_rate_percent == 100.0
    assert summary.quality_gate_passed is True
