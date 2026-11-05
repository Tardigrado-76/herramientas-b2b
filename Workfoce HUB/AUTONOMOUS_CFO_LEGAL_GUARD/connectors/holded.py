"""Conector especializado para Holded Cloud ERP."""

from typing import Any
from pydantic import BaseModel


class HoldedInvoice(BaseModel):
    id: str
    contact_name: str
    contact_cif: str
    desc: str
    date: str
    subtotal: float
    taxes: float
    total: float
    status: str  # 0=unpaid, 1=paid, 2=partially_paid


class HoldedConnector:
    """Cliente simulado y API handler para sincronización con Holded."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.is_connected = bool(api_key and len(api_key) > 5)

    def fetch_invoices(self, doc_type: str = "invoice") -> list[HoldedInvoice]:
        """Obtiene facturas emitidas o recibidas."""
        # Datos estándar de demostración operativa
        return [
            HoldedInvoice(
                id="HLD-2026-089",
                contact_name="Consulting Partners Europa S.L.",
                contact_cif="B84112233",
                desc="Servicios mensuales de asesoría estratégica",
                date="2026-10-15",
                subtotal=4500.0,
                taxes=945.0,
                total=5445.0,
                status="unpaid"
            ),
            HoldedInvoice(
                id="HLD-2026-090",
                contact_name="Cloud Hosting Iberia S.A.",
                contact_cif="A28998877",
                desc="Servidores dedicados e infraestructura cloud Q3",
                date="2026-10-18",
                subtotal=1800.0,
                taxes=378.0,
                total=2178.0,
                status="unpaid"
            )
        ]

    def sync_invoice_status(self, invoice_id: str, new_status: str) -> dict[str, Any]:
        return {
            "connector": "holded_api",
            "invoice_id": invoice_id,
            "status": "SUCCESS",
            "message": f"Factura {invoice_id} actualizada a {new_status} en Holded."
        }
