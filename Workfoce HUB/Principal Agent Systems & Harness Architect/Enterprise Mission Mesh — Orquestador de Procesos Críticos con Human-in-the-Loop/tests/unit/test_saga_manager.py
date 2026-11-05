"""Unit tests for SagaTransactionManager 2-phase execution."""

from pathlib import Path
from enterprise_mission_mesh.core.state import (
    AgentEmitterType,
    Mission,
    MissionStatus,
    RiskLevel,
)
from enterprise_mission_mesh.saga.action_ledger import ActionLedger
from enterprise_mission_mesh.saga.transaction_manager import SagaTransactionManager


def test_saga_successful_commit(tmp_path: Path):
    ledger = ActionLedger(db_path=str(tmp_path / "saga_test.db"))
    saga = SagaTransactionManager(ledger)

    mission = Mission(
        idempotency_key="saga_idem_1",
        agent_id="test_agent",
        agent_type=AgentEmitterType.CUSTOM,
        action_type="TEST_ACTION",
        target_entity_id="entity_1",
        parameters={"delta": 10},
        confidence_score=0.99,
        risk_level=RiskLevel.LOW,
        status=MissionStatus.SUBMITTED,
    )
    ledger.record_mission(mission)

    res = saga.execute_mission(mission, forward_callable=lambda p: {"applied": p["delta"]})
    assert res.success is True
    assert res.data["applied"] == 10

    # Verify committed state in ledger
    committed = ledger.get_mission(mission.id)
    assert committed.status == MissionStatus.COMPLETED
    assert committed.sha256_hash is not None


def test_saga_failure_and_compensation(tmp_path: Path):
    ledger = ActionLedger(db_path=str(tmp_path / "saga_fail.db"))
    saga = SagaTransactionManager(ledger)

    compensated = False

    def forward_fail(p):
        raise ConnectionResetError("ERP Backend Unreachable")

    def comp_action(p):
        nonlocal compensated
        compensated = True

    mission = Mission(
        idempotency_key="saga_idem_fail",
        agent_id="test_agent",
        agent_type=AgentEmitterType.CUSTOM,
        action_type="CRITICAL_PAYMENT",
        target_entity_id="acc_99",
        parameters={"amount": 500},
        compensating_parameters={"revert_amount": 500},
        confidence_score=0.99,
        risk_level=RiskLevel.CRITICAL,
        status=MissionStatus.APPROVED,
    )
    ledger.record_mission(mission)

    res = saga.execute_mission(mission, forward_callable=forward_fail, compensate_callable=comp_action)
    assert res.success is False
    assert compensated is True
    assert mission.status == MissionStatus.FAILED
