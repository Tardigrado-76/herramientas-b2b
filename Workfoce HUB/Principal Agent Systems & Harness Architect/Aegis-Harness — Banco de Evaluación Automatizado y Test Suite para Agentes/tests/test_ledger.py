import pytest
import json
from aegis.models import SuiteSummary
from aegis.ledger import AuditLedger

def test_ledger_append_and_verify(tmp_path):
    ledger_file = tmp_path / "test_ledger.jsonl"
    ledger = AuditLedger(ledger_file=str(ledger_file))

    summary1 = SuiteSummary(
        suite_name="Run 1",
        timestamp="2026-10-23T12:00:00Z",
        total_tests=5,
        passed_tests=5,
        failed_tests=0,
        pass_rate_percent=100.0,
        overall_score=95.0,
        quality_gate_passed=True
    )
    b1 = ledger.record_evaluation(summary1, agent_name="langgraph-agent")
    assert b1["previous_block_hash"] == "0" * 64
    assert len(b1["block_hash"]) == 64

    summary2 = SuiteSummary(
        suite_name="Run 2",
        timestamp="2026-10-23T12:05:00Z",
        total_tests=5,
        passed_tests=4,
        failed_tests=1,
        pass_rate_percent=80.0,
        overall_score=85.0,
        quality_gate_passed=True
    )
    b2 = ledger.record_evaluation(summary2, agent_name="langgraph-agent")
    assert b2["previous_block_hash"] == b1["block_hash"]

    # Verify integrity
    is_valid, count, errors = ledger.verify_integrity()
    assert is_valid is True
    assert count == 2
    assert len(errors) == 0

def test_ledger_detects_tampering(tmp_path):
    ledger_file = tmp_path / "tampered_ledger.jsonl"
    ledger = AuditLedger(ledger_file=str(ledger_file))

    summary = SuiteSummary(
        suite_name="Legit Run",
        timestamp="2026-10-23T12:00:00Z",
        total_tests=10,
        passed_tests=10,
        failed_tests=0,
        pass_rate_percent=100.0,
        overall_score=90.0,
        quality_gate_passed=True
    )
    ledger.record_evaluation(summary)

    # Tamper with file
    with open(ledger_file, "r", encoding="utf-8") as f:
        data = json.loads(f.read().strip())
    data["overall_score"] = 99.9  # Tamper
    with open(ledger_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")

    is_valid, count, errors = ledger.verify_integrity()
    assert is_valid is False
    assert len(errors) > 0
    assert "tampered" in errors[0].lower()
