import pytest
from pathlib import Path
from aegis.runner import AegisRunner
from aegis.models import TestCategory

def test_runner_load_dataset():
    runner = AegisRunner()
    ds_path = Path(__file__).resolve().parent.parent / "datasets" / "functional" / "routing_tests.yaml"
    cases = runner.load_dataset(str(ds_path))
    assert len(cases) == 40
    assert cases[0].id == "FUNC-SQL-01"
    assert cases[0].category == TestCategory.FUNCTIONAL
    assert cases[0].expected_server == "sqlite"

def test_runner_run_suite_functional():
    runner = AegisRunner()
    ds_path = Path(__file__).resolve().parent.parent / "datasets" / "functional" / "routing_tests.yaml"
    summary = runner.run_suite(str(ds_path))
    assert summary.total_tests == 40
    assert summary.passed_tests == 40
    assert summary.pass_rate_percent == 100.0
    assert summary.quality_gate_passed is True

def test_runner_run_suite_adversarial():
    runner = AegisRunner()
    ds_path = Path(__file__).resolve().parent.parent / "datasets" / "adversarial" / "prompt_injection.yaml"
    summary = runner.run_suite(str(ds_path))
    assert summary.total_tests == 30
    assert summary.passed_tests == 30
    assert summary.quality_gate_passed is True
