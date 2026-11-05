import pytest
from aegis.models import TestResult, TestCategory, AgentExecutionOutput, MetricEvaluation
from aegis.metrics import MetricsAggregator

def test_metrics_aggregator_calculation():
    r1 = TestResult(
        test_case_id="T1",
        category=TestCategory.FUNCTIONAL,
        passed=True,
        overall_score=90.0,
        execution_output=AgentExecutionOutput(latency_ms=100.0)
    )
    r2 = TestResult(
        test_case_id="T2",
        category=TestCategory.FUNCTIONAL,
        passed=True,
        overall_score=100.0,
        execution_output=AgentExecutionOutput(latency_ms=200.0)
    )
    r3 = TestResult(
        test_case_id="T3",
        category=TestCategory.ADVERSARIAL,
        passed=False,
        overall_score=50.0,
        execution_output=AgentExecutionOutput(latency_ms=300.0)
    )

    summary = MetricsAggregator.aggregate("Sample Suite", [r1, r2, r3])
    assert summary.total_tests == 3
    assert summary.passed_tests == 2
    assert summary.failed_tests == 1
    assert round(summary.pass_rate_percent, 1) == 66.7
    assert round(summary.overall_score, 1) == 80.0
    assert summary.category_scores["functional"] == 95.0
    assert summary.category_scores["adversarial"] == 50.0
    assert summary.average_latency_ms == 200.0

def test_metrics_aggregator_empty_results():
    summary = MetricsAggregator.aggregate("Empty Suite", [])
    assert summary.total_tests == 0
    assert summary.overall_score == 0.0
    assert summary.quality_gate_passed is False
