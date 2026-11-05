"""
Unit tests for SDP Accounting Connector (Semantic Discovery Protocol)
Validates dynamic connector resolution, progressive disclosure, and token savings for SME CFO.
"""
from __future__ import annotations

import pytest
from autonomo_cfo.tools.sdp_accounting_connector import (
    AccountingConnectorSchema,
    SDPAccountingConnector,
)


@pytest.fixture
def connector_registry():
    return SDPAccountingConnector()


def test_sdp_accounting_connector_registration(connector_registry):
    connectors = connector_registry.list_connectors()
    assert len(connectors) >= 5

    connector_ids = {c.connector_id for c in connectors}
    expected = {"a3innuva_erp", "holded_api", "sage_50", "contasol_bridge", "stripe_billing"}
    assert expected.issubset(connector_ids)


def test_sdp_accounting_connector_semantic_search(connector_registry):
    # Query for invoicing / billing
    matches = connector_registry.discover_connectors("facturación recurrente y pasarela de cobros", top_k=2)
    assert len(matches) > 0
    top_match = matches[0]
    assert top_match.connector_id in {"stripe_billing", "holded_api"}
    assert top_match.confidence_score > 0.3

    # Query for Spanish official tax / journal books
    matches_tax = connector_registry.discover_connectors("asientos contables diario y modelos oficiales aeat", top_k=2)
    assert len(matches_tax) > 0
    top_tax = matches_tax[0]
    assert top_tax.connector_id in {"a3innuva_erp", "sage_50", "contasol_bridge"}


def test_sdp_accounting_connector_progressive_disclosure(connector_registry):
    # Step 1: Lightweight metadata (Tier 0)
    meta = connector_registry.get_connector_metadata("a3innuva_erp")
    assert meta is not None
    assert meta.estimated_tier0_tokens < 100

    # Step 2: Hydrate full schema (Tier 1) on demand
    full_spec = connector_registry.resolve_connector("a3innuva_erp")
    assert isinstance(full_spec, AccountingConnectorSchema)
    assert "asientos" in full_spec.capabilities
    assert full_spec.auth_type == "OAUTH2_MUTUAL_TLS"
    assert len(full_spec.endpoints) >= 2


def test_sdp_accounting_token_savings(connector_registry):
    metrics = connector_registry.compute_token_savings()
    assert metrics["savings_percentage"] >= 80.0
    assert metrics["tier0_total_tokens"] < metrics["tier1_full_tokens"]
