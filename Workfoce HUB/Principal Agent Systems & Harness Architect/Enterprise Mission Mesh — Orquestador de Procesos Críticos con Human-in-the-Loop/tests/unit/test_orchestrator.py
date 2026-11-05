"""Unit tests for MissionOrchestrator and state machine."""

import pytest
from enterprise_mission_mesh.core.orchestrator import MissionOrchestrator
from enterprise_mission_mesh.core.state import (
    HumanDecisionType,
    MissionProposal,
    MissionStatus,
    RiskLevel,
)


def test_mission_lifecycle_state_machine(test_orchestrator: MissionOrchestrator):
    """Test full standard transition: Submit -> PENDING_HITL/DISPATCHED -> Approved -> Completed."""
    proposal = MissionProposal(
        agent_id="ai-hr-specialist",
        action_type="KRONOS_ADJUST_ENTRY",
        target_entity_id="user_123",
        parameters={"clock_in": "2026-10-23T08:00:00Z", "delta_minutes": 30},
        confidence_score=0.98,
        risk_level=RiskLevel.HIGH,
    )
    mission = test_orchestrator.submit_mission(proposal)
    assert mission.status == MissionStatus.DISPATCHED
    assert mission.risk_level == RiskLevel.HIGH
    assert len(mission.dispatched_channels) > 0

    # Human supervisor approval
    updated = test_orchestrator.apply_human_decision(
        mission.id,
        decision=HumanDecisionType.APPROVE,
        decided_by="mgr_456",
        token=mission.approve_token,
    )
    assert updated.status == MissionStatus.COMPLETED
    assert updated.decided_by == "mgr_456"


def test_mission_rejection(test_orchestrator: MissionOrchestrator):
    """Test supervisor rejection transition."""
    proposal = MissionProposal(
        agent_id="ai-finance",
        action_type="FINANCIAL_REFUND",
        target_entity_id="order_999",
        parameters={"amount": 450.0},
        confidence_score=0.88,
    )
    mission = test_orchestrator.submit_mission(proposal)
    assert mission.status == MissionStatus.DISPATCHED

    rejected = test_orchestrator.apply_human_decision(
        mission.id,
        decision=HumanDecisionType.REJECT,
        decided_by="cfo_user",
        reason="Presupuesto agotado",
        token=mission.reject_token,
    )
    assert rejected.status == MissionStatus.REJECTED
    assert rejected.decision_reason == "Presupuesto agotado"


def test_mission_explanation_request(test_orchestrator: MissionOrchestrator):
    """Test supervisor asking for explanation transitions to EXPLAINING and back to PENDING_HITL."""
    proposal = MissionProposal(
        agent_id="hr-agent",
        action_type="KRONOS_ADJUST_ENTRY",
        target_entity_id="user_444",
        parameters={"delta_minutes": 60, "is_overtime": True},
        confidence_score=0.96,
    )
    mission = test_orchestrator.submit_mission(proposal)
    explained = test_orchestrator.apply_human_decision(
        mission.id,
        decision=HumanDecisionType.EXPLAIN,
        decided_by="supervisor_1",
        token=mission.explain_token,
    )
    assert explained.status == MissionStatus.PENDING_HITL
    assert explained.explanation is not None
    assert "INFORME DE JUSTIFICACIÓN" in explained.explanation


def test_auto_execution_low_risk(test_orchestrator: MissionOrchestrator):
    """Test low risk action with high confidence completes autonomously without HITL."""
    proposal = MissionProposal(
        agent_id="monitoring-agent",
        action_type="NOTIFY_USER",
        target_entity_id="user_777",
        parameters={"message": "Recordatorio de reunión"},
        confidence_score=0.99,
    )
    mission = test_orchestrator.submit_mission(proposal)
    assert mission.status == MissionStatus.COMPLETED
    assert mission.risk_level == RiskLevel.LOW
