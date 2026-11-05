"""Pytest fixtures for Enterprise Mission Mesh test suite."""

import pytest
from pathlib import Path
from enterprise_mission_mesh.core.config import MeshConfig
from enterprise_mission_mesh.core.orchestrator import MissionOrchestrator
from enterprise_mission_mesh.gate.confidence_gate import ConfidenceGate
from enterprise_mission_mesh.hitl.escalation_engine import EscalationEngine
from enterprise_mission_mesh.hitl.explanation_agent import ExplanationAgent
from enterprise_mission_mesh.saga.action_ledger import ActionLedger
from enterprise_mission_mesh.connectors.kronos_connector import KronosConnector


@pytest.fixture
def tmp_config(tmp_path: Path) -> MeshConfig:
    db_file = tmp_path / "test_mesh.db"
    return MeshConfig(
        environment="test",
        min_auto_confidence=0.95,
        hitl_timeout_seconds=5,
        hmac_secret_key="test_hmac_secret_key_12345",
        db_path=str(db_file),
        audit_export_dir=str(tmp_path / "exports"),
        default_channel="local_portal",
        enabled_channels=["slack", "teams", "telegram", "webhook", "email", "discord", "whatsapp", "local_portal"],
        kronos_base_url="http://127.0.0.1:3000",
        portal_host="127.0.0.1",
        portal_port=8765,
    )


@pytest.fixture
def test_ledger(tmp_config: MeshConfig) -> ActionLedger:
    return ActionLedger(db_path=tmp_config.db_path, secret_key=tmp_config.hmac_secret_key)


@pytest.fixture
def test_gate(tmp_config: MeshConfig) -> ConfidenceGate:
    return ConfidenceGate(min_auto_confidence=tmp_config.min_auto_confidence)


@pytest.fixture
def test_orchestrator(tmp_config: MeshConfig, test_ledger: ActionLedger, test_gate: ConfidenceGate) -> MissionOrchestrator:
    escalation = EscalationEngine(tmp_config)
    explanation = ExplanationAgent()
    return MissionOrchestrator(
        config=tmp_config,
        ledger=test_ledger,
        gate=test_gate,
        escalation=escalation,
        explanation_agent=explanation,
    )


@pytest.fixture
def mock_kronos(tmp_config: MeshConfig) -> KronosConnector:
    return KronosConnector(config=tmp_config)
