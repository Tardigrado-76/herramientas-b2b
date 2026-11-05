"""Unit tests for ConfidenceGate and ImpactClassifier."""

from enterprise_mission_mesh.core.state import RiskLevel, RoutingDecision
from enterprise_mission_mesh.gate.confidence_gate import ConfidenceGate
from enterprise_mission_mesh.gate.impact_classifier import ImpactClassifier


def test_confidence_gate_routes_high_risk_to_hitl():
    gate = ConfidenceGate(min_auto_confidence=0.95)

    # 1. Low risk action with 0.99 confidence -> AUTO_EXECUTE
    dec1 = gate.evaluate(action_type="NOTIFY_USER", confidence=0.99, parameters={"msg": "hello"})
    assert dec1.route == RoutingDecision.AUTO_EXECUTE
    assert dec1.risk_level == RiskLevel.LOW

    # 2. Critical labor modification in Kronos -> Strictly requires HITL
    dec2 = gate.evaluate(
        action_type="KRONOS_MODIFY_TIME_ENTRY",
        confidence=0.99,
        parameters={"delta_minutes": 45, "is_overtime": True},
    )
    assert dec2.route == RoutingDecision.REQUIRE_HITL
    assert dec2.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)


def test_confidence_gate_escalates_low_confidence():
    gate = ConfidenceGate(min_auto_confidence=0.95)

    # Low risk action but confidence is below 0.95 -> Escalate to HITL
    dec = gate.evaluate(action_type="NOTIFY_USER", confidence=0.82)
    assert dec.route == RoutingDecision.REQUIRE_HITL
    assert "LOW_CONFIDENCE_ESCALATION" in dec.reason


def test_logical_flaw_rejection():
    gate = ConfidenceGate()

    # Inconsistent / impossible negative financial amount or extreme clock delta
    dec = gate.evaluate(action_type="FINANCIAL_REFUND", confidence=0.99, parameters={"amount": -50.0})
    assert dec.route == RoutingDecision.REJECT_OUTRIGHT
    assert "LOGICAL_CONSISTENCY_FAILURE" in dec.reason


def test_impact_classifier_kronos_overtime():
    classifier = ImpactClassifier(max_auto_time_delta_minutes=15)
    risk, reason = classifier.classify("KRONOS_ADJUST_ENTRY", {"delta_minutes": 20, "is_overtime": True})
    assert risk == RiskLevel.HIGH
    assert "OVERTIME" in reason or "DISCREPANCY" in reason
