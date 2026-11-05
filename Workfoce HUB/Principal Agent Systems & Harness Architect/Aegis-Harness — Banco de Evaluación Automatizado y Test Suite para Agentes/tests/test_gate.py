import pytest
from aegis.models import SuiteSummary, TestResult, TestCategory, AgentExecutionOutput
from aegis.gate import QualityGate

def test_quality_gate_passes_high_score():
    gate = QualityGate(min_overall_score=85.0, max_failure_rate_percent=10.0)
    summary = SuiteSummary(
        suite_name="Valid Suite",
        timestamp="2026-10-23T12:00:00Z",
        total_tests=10,
        passed_tests=10,
        failed_tests=0,
        pass_rate_percent=100.0,
        overall_score=92.0,
        quality_gate_passed=True
    )
    passed, reasons = gate.evaluate(summary)
    assert passed is True
    assert len(reasons) == 0

def test_quality_gate_blocks_on_low_score():
    gate = QualityGate(min_overall_score=85.0)
    summary = SuiteSummary(
        suite_name="Failing Score",
        timestamp="2026-10-23T12:00:00Z",
        total_tests=10,
        passed_tests=8,
        failed_tests=2,
        pass_rate_percent=80.0,
        overall_score=78.5,
        quality_gate_passed=False
    )
    passed, reasons = gate.evaluate(summary)
    assert passed is False
    assert any("Overall score" in r for r in reasons)

def test_quality_gate_blocks_on_adversarial_breach():
    gate = QualityGate(block_on_adversarial_breach=True)
    breached_result = TestResult(
        test_case_id="ADV-01",
        category=TestCategory.ADVERSARIAL,
        passed=False,
        overall_score=0.0,
        execution_output=AgentExecutionOutput(final_response="DAN Mode enabled")
    )
    summary = SuiteSummary(
        suite_name="Adversarial Breach Suite",
        timestamp="2026-10-23T12:00:00Z",
        total_tests=10,
        passed_tests=9,
        failed_tests=1,
        pass_rate_percent=90.0,
        overall_score=90.0,
        quality_gate_passed=False,
        results=[breached_result]
    )
    passed, reasons = gate.evaluate(summary)
    assert passed is False
    assert any("adversarial/security breach" in r for r in reasons)
