"""Pytest fixtures and test environment setup for Bunker-Gateway."""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from bunker_gateway.core.config import GatewayConfig, UpstreamConfig
from bunker_gateway.core.proxy import ProxyEngine
from bunker_gateway.firewall.injection_shield import InjectionShield
from bunker_gateway.firewall.pii_sanitizer import PIIVault
from bunker_gateway.firewall.secret_detector import SecretDetector
from bunker_gateway.firewall.tool_guard import ToolGuard
from bunker_gateway.ledger.immutable_ledger import ImmutableLedger
from bunker_gateway.resilience.circuit_breaker import CircuitBreaker
from bunker_gateway.resilience.rate_limiter import BudgetGuard
from bunker_gateway.main import app


@pytest.fixture
def tmp_ledger(tmp_path: Path) -> ImmutableLedger:
    ledger_file = tmp_path / "test_audit_ledger.jsonl"
    return ImmutableLedger(str(ledger_file))


@pytest.fixture
def test_config(tmp_path: Path) -> GatewayConfig:
    return GatewayConfig(
        host="127.0.0.1",
        port=8080,
        environment="test",
        ledger_file_path=str(tmp_path / "test_audit_ledger.jsonl"),
        abac_policy_file=str(tmp_path / "test_abac.yaml"),
    )


@pytest.fixture
def test_proxy(test_config: GatewayConfig, tmp_ledger: ImmutableLedger) -> ProxyEngine:
    return ProxyEngine(
        config=test_config,
        pii_vault=PIIVault(),
        injection_shield=InjectionShield(),
        secret_detector=SecretDetector(),
        tool_guard=ToolGuard(),
        circuit_breaker=CircuitBreaker(),
        budget_guard=BudgetGuard(),
        ledger=tmp_ledger,
    )


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
