"""Motor del Semantic Discovery Protocol (SDP) para el CFO Autónomo.

Aplica revelación progresiva (Tier-0 liviano ~35 tokens -> Tier-1 hidratado bajo demanda)
para conectar sin saturar el contexto del LLM con APIs bancarias y de software contable.
"""

from typing import Any
from pydantic import BaseModel, Field


class ConnectorMetadata(BaseModel):
    connector_id: str
    name: str
    category: str
    description: str
    tags: list[str]
    auth_type: str
    estimated_tier0_tokens: int = 35
    status: str = "AVAILABLE"  # AVAILABLE, CONNECTED, DISABLED


class SDPConnectorRegistry:
    """Registro y enrutador semántico de conectores SDP."""

    CATALOG: dict[str, dict[str, Any]] = {
        "holded_api": {
            "name": "Holded Cloud ERP & Facturación",
            "category": "ERP Cloud & Facturación",
            "description": "Sincronización bidireccional de facturas de clientes, proveedores, tesorería y contactos.",
            "tags": ["holded", "erp", "facturacion", "cobros", "pagos", "contactos", "crea_y_crece"],
            "auth_type": "API_KEY_BEARER",
            "tier0_tokens": 35,
        },
        "a3innuva_erp": {
            "name": "A3 Innuva ERP / Wolters Kluwer",
            "category": "Contabilidad & Fiscalidad Oficial",
            "description": "Exportación automática de libro diario, asientos contables y preparación de modelos tributarios AEAT.",
            "tags": ["a3", "wolters kluwer", "asientos contables", "diario", "aeat", "modelos fiscales"],
            "auth_type": "OAUTH2_MUTUAL_TLS",
            "tier0_tokens": 38,
        },
        "sage_50": {
            "name": "Sage 50 Cloud Asesoría",
            "category": "Gestión Contable y Cuentas Anuales",
            "description": "Integración con planes contables PYME España, amortizaciones de inmovilizado y cierre contable.",
            "tags": ["sage", "sage50", "cuentas anuales", "asientos", "amortizaciones", "cierre"],
            "auth_type": "OAUTH2_REFRESH_TOKEN",
            "tier0_tokens": 34,
        },
        "psd2_banking": {
            "name": "PSD2 Open Banking Gateway",
            "category": "Conciliación Bancaria Automática",
            "description": "Lectura en tiempo real de extractos y movimientos bancarios multientidad (Santander, BBVA, CaixaBank, Sabadell, Bankinter).",
            "tags": ["banco", "psd2", "open banking", "extractos", "santander", "bbva", "caixa", "conciliacion"],
            "auth_type": "EIDAS_CERTIFICATE_QWAC",
            "tier0_tokens": 36,
        },
        "stripe_billing": {
            "name": "Stripe Billing & Subscriptions",
            "category": "Pasarela de Cobros & Facturación Recurrente",
            "description": "Monitoreo en tiempo real de cobros con tarjeta, adeudos SEPA direct debit y conciliación de comisiones.",
            "tags": ["stripe", "tarjetas", "sepa", "suscripciones", "recurrentes"],
            "auth_type": "REST_SECRET_KEY",
            "tier0_tokens": 32,
        }
    }

    @classmethod
    def list_connectors(cls) -> list[ConnectorMetadata]:
        return [
            ConnectorMetadata(
                connector_id=cid,
                name=info["name"],
                category=info["category"],
                description=info["description"],
                tags=info["tags"],
                auth_type=info["auth_type"],
                estimated_tier0_tokens=info["tier0_tokens"]
            )
            for cid, info in cls.CATALOG.items()
        ]

    @classmethod
    def discover_connectors(cls, query: str, top_k: int = 3) -> list[ConnectorMetadata]:
        tokens = [t.lower() for t in query.replace(",", " ").split() if len(t) > 2]
        scored: list[tuple[float, ConnectorMetadata]] = []

        for cid, info in cls.CATALOG.items():
            meta = ConnectorMetadata(
                connector_id=cid,
                name=info["name"],
                category=info["category"],
                description=info["description"],
                tags=info["tags"],
                auth_type=info["auth_type"],
                estimated_tier0_tokens=info["tier0_tokens"]
            )
            score = 0.0
            for tok in tokens:
                if any(tok in tag.lower() for tag in info["tags"]):
                    score += 1.0
                if tok in info["name"].lower() or tok in info["description"].lower():
                    score += 0.5
            if score > 0:
                scored.append((score, meta))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

    @classmethod
    def get_hydrated_schema(cls, connector_id: str) -> dict[str, Any]:
        info = cls.CATALOG.get(connector_id)
        if not info:
            return {"error": "Connector not found"}
        return {
            "connector_id": connector_id,
            "name": info["name"],
            "category": info["category"],
            "description": info["description"],
            "auth_type": info["auth_type"],
            "tier1_endpoints": [
                {"name": "fetch_invoices", "method": "GET", "path": "/api/v1/invoices", "rate_limit": "60/min"},
                {"name": "post_reconciliation", "method": "POST", "path": "/api/v1/reconcile", "rate_limit": "30/min"},
                {"name": "sync_ledger", "method": "POST", "path": "/api/v1/ledger/sync", "rate_limit": "10/min"}
            ],
            "rate_limits": "Standard Sovereign Throttle (60 req/min)",
            "compliance_attestation": "Encrypted AES-GCM local keystore"
        }

SDPEngine = SDPConnectorRegistry
