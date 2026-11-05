"""Unit tests for ActionLedger, SQLite WAL mode and cryptographic chain."""

from pathlib import Path
from enterprise_mission_mesh.core.state import (
    AgentEmitterType,
    Mission,
    MissionStatus,
    RiskLevel,
    RollbackRecord,
)
from enterprise_mission_mesh.saga.action_ledger import ActionLedger


def test_action_ledger_prevents_duplicate_execution(tmp_path: Path):
    db_file = tmp_path / "ledger_idem.db"
    ledger = ActionLedger(db_path=str(db_file), secret_key="test_secret")
    idem_key = "kronos_adj_user123_20261023"

    m = Mission(
        idempotency_key=idem_key,
        agent_id="hr-bot",
        agent_type=AgentEmitterType.HR_OPERATIONS,
        action_type="KRONOS_ADJUST_ENTRY",
        target_entity_id="user_123",
        parameters={"delta": 15},
        confidence_score=0.98,
        risk_level=RiskLevel.MEDIUM,
    )
    ledger.record_mission(m)

    assert ledger.is_duplicate_execution(idem_key) is True
    assert ledger.is_duplicate_execution("non_existent_key") is False


def test_action_ledger_sha256_chain_integrity(tmp_path: Path):
    db_file = tmp_path / "ledger_chain.db"
    ledger = ActionLedger(db_path=str(db_file), secret_key="secure_hmac_key")

    # Record 5 sequential blocks
    h1 = ledger.record_ledger_block("msn_1", "ACTION_A", {"value": 100})
    h2 = ledger.record_ledger_block("msn_2", "ACTION_B", {"value": 200})
    h3 = ledger.record_ledger_block("msn_3", "ACTION_C", {"value": 300})

    assert h1 != h2 != h3
    valid, errors = ledger.verify_chain_integrity()
    assert valid is True
    assert len(errors) == 0


def test_action_ledger_rollback_persistence(tmp_path: Path):
    db_file = tmp_path / "ledger_rb.db"
    ledger = ActionLedger(db_path=str(db_file))

    rb = RollbackRecord(
        mission_id="msn_999",
        requested_by="auditor_test",
        reason="Discrepancia en fichaje",
        success=True,
        compensating_details={"restored": True},
    )
    ledger.record_rollback(rb)

    rollbacks = ledger.list_rollbacks()
    assert len(rollbacks) == 1
    assert rollbacks[0]["mission_id"] == "msn_999"
    assert rollbacks[0]["success"] == 1
