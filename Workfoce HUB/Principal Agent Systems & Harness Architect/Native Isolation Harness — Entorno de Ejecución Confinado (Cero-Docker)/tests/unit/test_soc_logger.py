"""Unit tests for SOCLogger and MITREMapper."""

from pathlib import Path
from native_isolation_harness.telemetry.soc_logger import SOCLogger
from native_isolation_harness.telemetry.mitre_mapper import MITREMapper


def test_mitre_mapper_classifications():
    t_id, c_id, _ = MITREMapper.classify("PATH_TRAVERSAL")
    assert t_id == "T1083"
    assert c_id == "CAPEC-126"

    t_id, c_id, _ = MITREMapper.classify("PROHIBITED_BINARY")
    assert t_id == "T1059.003"
    assert c_id == "CAPEC-242"

    t_id, c_id, _ = MITREMapper.classify("MEMORY_LIMIT")
    assert t_id == "T1499.001"
    assert c_id == "CAPEC-130"


def test_soc_logger_writes_sanitized_incident(tmp_path):
    log_file = tmp_path / "soc_incidents.jsonl"
    logger = SOCLogger(log_path=str(log_file))

    event = logger.log_incident(
        incident_type="PATH_TRAVERSAL",
        severity="CRITICAL",
        agent_id="adversarial-agent-01",
        session_id="sess_attack_99",
        command=["python", "script.py", "--key", "sk-12345678901234567890abcdef"],
        details={"attempted_path": "../../secret.env"},
    )

    assert event["event_id"].startswith("soc_")
    assert event["severity"] == "CRITICAL"
    assert event["mitre_technique_id"] == "T1083"
    assert "sk-[REDACTED]" in event["command"]
    assert log_file.exists()

    recent = logger.get_recent_incidents(10)
    assert len(recent) == 1
    assert recent[0]["event_id"] == event["event_id"]
