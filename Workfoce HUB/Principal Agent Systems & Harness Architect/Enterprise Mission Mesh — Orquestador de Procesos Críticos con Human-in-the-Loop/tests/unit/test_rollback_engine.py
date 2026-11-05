"""Unit tests for RollbackEngine and 1-Click compensating reversal."""

from pathlib import Path
from enterprise_mission_mesh.core.state import (
    AgentEmitterType,
    Mission,
    MissionStatus,
    RiskLevel,
)
from enterprise_mission_mesh.saga.action_ledger import ActionLedger
from enterprise_mission_mesh.saga.rollback_engine import RollbackEngine


def test_rollback_engine_reverts_completed_mission(tmp_path: Path):
    ledger = ActionLedger(db_path=str(tmp_path / "rollback_test.db"))
    engine = RollbackEngine(ledger)

    mission = Mission(
        idempotency_key="rb_test_1",
        agent_id="hr-specialist",
        agent_type=AgentEmitterType.HR_OPERATIONS,
        action_type="KRONOS_MODIFY_TIME_ENTRY",
        target_entity_id="emp_001",
        parameters={"clock_out": "18:00"},
        compensating_parameters={"clock_out": "16:30"},
        before_image={"clock_out": "16:30"},
        confidence_score=0.98,
        risk_level=RiskLevel.HIGH,
        status=MissionStatus.COMPLETED,
    )
    ledger.record_mission(mission)

    # Trigger 1-click rollback
    report = engine.rollback_mission(
        mission_id=mission.id,
        requested_by="auditor_maria",
        reason="Corrección inspectora",
    )
    assert report.success is True
    assert report.compensating_details.get("clock_out") == "16:30"

    # Verify mission status in ledger transitioned to ROLLED_BACK
    updated = ledger.get_mission(mission.id)
    assert updated.status == MissionStatus.ROLLED_BACK
    assert updated.rollback_record is not None


def test_rollback_rejected_on_non_completed_mission(tmp_path: Path):
    ledger = ActionLedger(db_path=str(tmp_path / "rollback_err.db"))
    engine = RollbackEngine(ledger)

    mission = Mission(
        idempotency_key="rb_test_2",
        agent_id="sales-bot",
        agent_type=AgentEmitterType.SALES_GTM,
        action_type="FINANCIAL_REFUND",
        target_entity_id="order_1",
        confidence_score=0.90,
        risk_level=RiskLevel.MEDIUM,
        status=MissionStatus.PENDING_HITL,
    )
    ledger.record_mission(mission)

    report = engine.rollback_mission(mission.id, requested_by="user", reason="test")
    assert report.success is False
    assert "CANNOT_ROLLBACK" in report.error
