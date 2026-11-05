"""Motor de Conciliación Bancaria Diaria Desatendida (PSD2 / Open Banking).

Cruza movimientos de cuenta bancaria con facturas emitidas (cobros) y recibidas (pagos),
detecta discrepancias en céntimos y genera asientos automáticos de conciliación.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class ReconciliationStatus(str, Enum):
    MATCHED = "MATCHED"              # Coincidencia exacta de importe y referencia/CIF
    PROBABLE_MATCH = "PROBABLE_MATCH"# Coincidencia de importe con diferencia de fechas
    DISCREPANCY = "DISCREPANCY"      # Diferencia en céntimos (comisiones o retenciones)
    UNMATCHED = "UNMATCHED"          # Movimiento sin factura identificada


class BankTransaction(BaseModel):
    transaction_id: str
    date: str
    amount: float                    # Positivo = ingreso, Negativo = gasto
    description: str
    counterparty_iban: str | None = None
    counterparty_name: str | None = None
    reference: str | None = None


class InvoiceItem(BaseModel):
    invoice_id: str
    invoice_number: str
    vendor_or_client: str
    cif: str
    amount: float
    date: str
    is_income: bool                  # True = emitida (cliente), False = recibida (proveedor)
    status: str = "PENDING"          # PENDING, PAID


class ReconciliationMatch(BaseModel):
    transaction_id: str
    invoice_id: str | None = None
    status: ReconciliationStatus
    confidence: float                # 0.0 a 1.0
    variance_amount: float = 0.0     # Diferencia en euros
    notes: str = ""
    suggested_action: str = ""


class BankReconciler:
    """Conciliador de transacciones bancarias contra libro de facturas."""

    @staticmethod
    def reconcile(
        transactions: list[BankTransaction],
        invoices: list[InvoiceItem],
        tolerance_cents: float = 0.05
    ) -> list[ReconciliationMatch]:
        matches: list[ReconciliationMatch] = []
        unmatched_invoices = {inv.invoice_id: inv for inv in invoices if inv.status == "PENDING"}

        for tx in transactions:
            is_credit = tx.amount > 0
            abs_tx_amt = abs(tx.amount)
            best_match: InvoiceItem | None = None
            best_score = 0.0
            variance = 0.0

            for inv_id, inv in unmatched_invoices.items():
                if inv.is_income != is_credit:
                    continue  # Si es ingreso bancario, busca factura emitida; si es gasto, factura recibida

                amt_diff = abs(abs_tx_amt - inv.amount)
                score = 0.0

                # 1. Coincidencia exacta de importe
                if amt_diff <= tolerance_cents:
                    score += 0.6
                elif amt_diff <= 2.0:  # Posible comisión bancaria o ajuste
                    score += 0.3

                # 2. Coincidencia en descripción (CIF, nombre o número de factura)
                desc_clean = tx.description.lower()
                if inv.invoice_number.lower() in desc_clean:
                    score += 0.35
                if inv.cif.lower() in desc_clean:
                    score += 0.25
                if inv.vendor_or_client.lower() in desc_clean:
                    score += 0.20

                if score > best_score and score >= 0.5:
                    best_score = score
                    best_match = inv
                    variance = round(abs_tx_amt - inv.amount, 2)

            if best_match and best_score >= 0.85:
                matches.append(ReconciliationMatch(
                    transaction_id=tx.transaction_id,
                    invoice_id=best_match.invoice_id,
                    status=ReconciliationStatus.MATCHED,
                    confidence=best_score,
                    variance_amount=variance,
                    notes=f"Emparejado con {best_match.invoice_number} ({best_match.vendor_or_client}).",
                    suggested_action="Conciliar automáticamente y marcar factura como COBRADA/PAGADA."
                ))
                unmatched_invoices.pop(best_match.invoice_id, None)
            elif best_match and best_score >= 0.5:
                matches.append(ReconciliationMatch(
                    transaction_id=tx.transaction_id,
                    invoice_id=best_match.invoice_id,
                    status=ReconciliationStatus.PROBABLE_MATCH if abs(variance) < 0.01 else ReconciliationStatus.DISCREPANCY,
                    confidence=best_score,
                    variance_amount=variance,
                    notes=f"Posible coincidencia con {best_match.invoice_number}. Discrepancia: {variance:+.2f} €.",
                    suggested_action="Revisar manualmente comisiones bancarias o retenciones aplicadas."
                ))
            else:
                matches.append(ReconciliationMatch(
                    transaction_id=tx.transaction_id,
                    invoice_id=None,
                    status=ReconciliationStatus.UNMATCHED,
                    confidence=0.0,
                    variance_amount=0.0,
                    notes=f"Sin factura correspondiente para {tx.description} ({tx.amount:,.2f} €).",
                    suggested_action="Solicitar factura al proveedor o clasificar como gasto recurrente/nómina."
                ))

        return matches
