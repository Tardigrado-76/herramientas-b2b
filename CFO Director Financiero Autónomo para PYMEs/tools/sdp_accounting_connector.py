"""
Semantic Discovery Protocol (SDP) - Accounting & ERP Dynamic Connector for AUTONOMO CFO.
Implements progressive disclosure to prevent prompt bloat while dynamically connecting
to official Spanish accounting software, cloud invoicing, and banking APIs.
"""
from __future__ import annotations

import re
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from .base import BaseTool


class ConnectorMetadata(BaseModel):
    """Tier-0 lightweight metadata for semantic discovery (~30-40 tokens)."""
    connector_id: str
    name: str
    category: str
    description: str
    tags: list[str]
    estimated_tier0_tokens: int = 35


class AccountingConnectorSchema(BaseModel):
    """Tier-1 fully hydrated connector specification."""
    connector_id: str
    name: str
    category: str
    description: str
    auth_type: str
    capabilities: list[str]
    endpoints: list[str]
    full_json_schema: dict[str, Any]
    estimated_full_tokens: int = 1450


class DiscoveryMatch(BaseModel):
    """Result of semantic discovery routing."""
    connector_id: str
    name: str
    confidence_score: float
    matched_tags: list[str]
    estimated_tokens_saved: int


class SDPAccountingConnector(BaseTool):
    """Dynamic Semantic Discovery Protocol tool for SME Accounting & ERP connectors."""

    query: str = Field(default="", description="Search query or operational intent (e.g. 'facturación recurrente', 'asientos contables diario')")
    connector_id_to_hydrate: str | None = Field(default=None, description="Optional connector_id to resolve to full schema")

    CATALOG: ClassVar[dict[str, dict[str, Any]]] = {
        "a3innuva_erp": {
            "name": "A3 Innuva ERP / Wolters Kluwer",
            "category": "Contabilidad & Fiscalidad Oficial",
            "description": "Integración para generación de asientos contables oficiales, libro diario, balances de sumas y saldos y modelos AEAT.",
            "tags": ["a3", "wolters kluwer", "asientos contables", "diario", "balances", "modelos oficiales aeat", "sumas y saldos"],
            "auth_type": "OAUTH2_MUTUAL_TLS",
            "capabilities": ["asientos", "diario", "modelos_tributarios", "balances"],
            "endpoints": ["/api/v1/ledger/entries", "/api/v1/taxes/modelos", "/api/v1/financial/balance"],
            "tier0_tokens": 38,
            "full_tokens": 1520,
        },
        "holded_api": {
            "name": "Holded Cloud ERP & Invoicing",
            "category": "Facturación & Tesorería Cloud",
            "description": "Sincronización bidireccional de facturas emitidas, recibidas, contactos fiscales y conciliación de movimientos de tesorería.",
            "tags": ["holded", "facturación recurrente", "invoicing", "contactos", "tesoreria", "pagos", "cobros", "pasarela de cobros"],
            "auth_type": "API_KEY_BEARER",
            "capabilities": ["facturacion", "contactos", "cobros", "tesoreria"],
            "endpoints": ["/invoicing/v1/documents/invoice", "/invoicing/v1/contacts", "/treasury/v1/cashflow"],
            "tier0_tokens": 36,
            "full_tokens": 1420,
        },
        "sage_50": {
            "name": "Sage 50 Cloud Asesoría",
            "category": "Gestión Contable y Cuentas Anuales",
            "description": "Conector nativo para planes contables PYME en España, amortizaciones automáticas y cierre contable.",
            "tags": ["sage", "sage 50", "cuentas anuales", "amortizaciones", "asientos contables", "cierre contable", "modelos oficiales aeat"],
            "auth_type": "OAUTH2_REFRESH_TOKEN",
            "capabilities": ["asientos", "amortizaciones", "cierre", "cuentas_anuales"],
            "endpoints": ["/api/v2/accounting/entries", "/api/v2/fixed-assets/amortization"],
            "tier0_tokens": 34,
            "full_tokens": 1380,
        },
        "contasol_bridge": {
            "name": "Software DELSOL ContaSOL",
            "category": "Contabilidad Estándar Española",
            "description": "Pasarela para volcados masivos al diario contable ContaSOL y cálculo de ratios financieros.",
            "tags": ["contasol", "delsol", "diario", "asientos contables", "sumas y saldos", "ratios", "modelos oficiales aeat"],
            "auth_type": "LOCAL_PIPE_OAUTH",
            "capabilities": ["diario", "asientos", "sumas_y_saldos", "ratios"],
            "endpoints": ["/delsol/bridge/entries", "/delsol/bridge/reports/sumas_saldos"],
            "tier0_tokens": 32,
            "full_tokens": 1290,
        },
        "stripe_billing": {
            "name": "Stripe Billing & Subscriptions",
            "category": "Pasarela de Cobros & Facturación Recurrente",
            "description": "Monitoreo en tiempo real de pagos con tarjeta, adeudos SEPA, cobros recurrentes de suscripciones y conciliación de comisiones.",
            "tags": ["stripe", "billing", "facturación recurrente", "pasarela de cobros", "tarjetas", "sepa", "reconciliacion"],
            "auth_type": "REST_SECRET_KEY",
            "capabilities": ["cobros", "suscripciones", "reconciliacion", "recurrentes"],
            "endpoints": ["/v1/invoices", "/v1/charges", "/v1/subscriptions"],
            "tier0_tokens": 35,
            "full_tokens": 1490,
        },
        "open_banking_psd2": {
            "name": "PSD2 Open Banking Gateway",
            "category": "Conciliación Bancaria Automática",
            "description": "Lectura directa de extractos bancarios multientidad, detección de discrepancias y conciliación con facturas emitidas.",
            "tags": ["banco", "psd2", "open banking", "santander", "bbva", "extractos", "conciliacion bancaria"],
            "auth_type": "EIDAS_CERTIFICATE",
            "capabilities": ["extractos", "conciliacion", "saldos"],
            "endpoints": ["/psd2/v1/accounts", "/psd2/v1/transactions"],
            "tier0_tokens": 35,
            "full_tokens": 1360,
        },
    }

    def list_connectors(self) -> list[ConnectorMetadata]:
        """Returns Tier-0 lightweight metadata for all registered accounting connectors."""
        return [
            ConnectorMetadata(
                connector_id=cid,
                name=info["name"],
                category=info["category"],
                description=info["description"],
                tags=info["tags"],
                estimated_tier0_tokens=info["tier0_tokens"]
            )
            for cid, info in self.CATALOG.items()
        ]

    def discover_connectors(self, query: str, top_k: int = 3) -> list[DiscoveryMatch]:
        """Lightweight semantic keyword router for progressive disclosure."""
        tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]
        matches: list[DiscoveryMatch] = []

        for cid, info in self.CATALOG.items():
            matched_tags = []
            score = 0.0

            text_corpus = f"{info['name']} {info['category']} {info['description']} {' '.join(info['tags'])}".lower()

            for token in tokens:
                if token in text_corpus:
                    score += 0.25
                for tag in info["tags"]:
                    if token in tag or tag in token:
                        score += 0.35
                        if tag not in matched_tags:
                            matched_tags.append(tag)

            if score > 0.0:
                norm_score = min(round(score, 2), 0.99)
                saved_tokens = max(0, info["full_tokens"] - info["tier0_tokens"])
                matches.append(
                    DiscoveryMatch(
                        connector_id=cid,
                        name=info["name"],
                        confidence_score=norm_score,
                        matched_tags=matched_tags,
                        estimated_tokens_saved=saved_tokens
                    )
                )

        matches.sort(key=lambda x: x.confidence_score, reverse=True)
        return matches[:top_k]

    def get_connector_metadata(self, connector_id: str) -> ConnectorMetadata | None:
        """Retrieves Tier-0 metadata for a specific connector."""
        info = self.CATALOG.get(connector_id)
        if not info:
            return None
        return ConnectorMetadata(
            connector_id=connector_id,
            name=info["name"],
            category=info["category"],
            description=info["description"],
            tags=info["tags"],
            estimated_tier0_tokens=info["tier0_tokens"]
        )

    def resolve_connector(self, connector_id: str) -> AccountingConnectorSchema | None:
        """Hydrates full connector schema on demand (Tier 1)."""
        info = self.CATALOG.get(connector_id)
        if not info:
            return None

        return AccountingConnectorSchema(
            connector_id=connector_id,
            name=info["name"],
            category=info["category"],
            description=info["description"],
            auth_type=info["auth_type"],
            capabilities=info["capabilities"],
            endpoints=info["endpoints"],
            full_json_schema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": info["capabilities"]},
                    "payload": {"type": "object", "description": f"Executable parameters for {info['name']}"}
                },
                "required": ["action", "payload"]
            },
            estimated_full_tokens=info["full_tokens"]
        )

    def compute_token_savings(self) -> dict[str, float]:
        """Calculates token economy metrics between Tier 0 and Tier 1 schemas."""
        tier0_total = sum(item["tier0_tokens"] for item in self.CATALOG.values())
        tier1_total = sum(item["full_tokens"] for item in self.CATALOG.values())
        saved = max(0, tier1_total - tier0_total)
        pct = (saved / tier1_total * 100.0) if tier1_total > 0 else 0.0

        return {
            "tier0_total_tokens": tier0_total,
            "tier1_full_tokens": tier1_total,
            "tokens_saved": saved,
            "savings_percentage": round(pct, 2)
        }

    def run(self) -> dict[str, Any]:
        """Executes tool logic for multi-agent framework integration."""
        if self.connector_id_to_hydrate:
            schema = self.resolve_connector(self.connector_id_to_hydrate)
            if not schema:
                return {"status": "ERROR", "message": f"Connector {self.connector_id_to_hydrate} not found."}
            return {"status": "HYDRATED", "schema": schema.model_dump()}

        if self.query:
            matches = self.discover_connectors(self.query)
            return {
                "status": "DISCOVERED",
                "query": self.query,
                "matches": [m.model_dump() for m in matches],
                "token_savings": self.compute_token_savings()
            }

        return {
            "status": "CATALOG_LIST",
            "connectors": [c.model_dump() for c in self.list_connectors()],
            "token_savings": self.compute_token_savings()
        }
