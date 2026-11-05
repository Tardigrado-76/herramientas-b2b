"""Pasarela Open Banking PSD2 para lectura y conciliación de extractos bancarios."""

from typing import Any
from cfo_core.reconciliation import BankTransaction


class PSD2BankingGateway:
    """Gateway de conexión bancaria bajo directiva PSD2 (Berlin Group / Redsys)."""

    def __init__(self, certificate_path: str | None = None):
        self.certificate_path = certificate_path
        self.is_connected = True  # Simulación operativa con feed activo

    def fetch_recent_transactions(self, days: int = 7) -> list[BankTransaction]:
        """Obtiene las transacciones bancarias recientes multientidad."""
        return [
            BankTransaction(
                transaction_id="TX-SANTANDER-901",
                date="2026-10-21",
                amount=5445.0,
                description="TRANSF CONSULTING PARTNERS EUROPA SL",
                counterparty_name="Consulting Partners Europa S.L.",
                counterparty_iban="ES9121000418450200051332",
                reference="HLD-2026-089"
            ),
            BankTransaction(
                transaction_id="TX-BBVA-902",
                date="2026-10-20",
                amount=-2178.0,
                description="PAGO PROVEEDOR CLOUD HOSTING IBERIA",
                counterparty_name="Cloud Hosting Iberia S.A.",
                counterparty_iban="ES7601820001880200004567",
                reference="HLD-2026-090"
            ),
            BankTransaction(
                transaction_id="TX-CAIXA-903",
                date="2026-10-19",
                amount=-1450.0,
                description="TRANSFERENCIA PROVEEDOR SERVICIOS DIVERSOS",
                counterparty_name="Suministros Generales SL",
                counterparty_iban="ES1200491500051234567890",
                reference="FAC-PENDIENTE"
            )
        ]

    @classmethod
    def generate_simulated_transactions(cls) -> list[BankTransaction]:
        return cls().fetch_recent_transactions()

PSD2BankingFeeder = PSD2BankingGateway
