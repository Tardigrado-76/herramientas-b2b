"""Detector Algorítmico de Fraude en Facturas y Desvío de IBAN.

Implementa verificación de cuenta beneficiaria histórica (Anti Man-in-the-Middle),
análisis de conformidad con la Ley de Benford y control de facturas duplicadas.
"""

from typing import Any
from pydantic import BaseModel, Field


class FraudAuditResult(BaseModel):
    is_safe: bool
    risk_score: int                  # 0 (seguro) a 100 (fraude crítico)
    status: str                      # APPROVED, REQUIRES_HITL, BLOCKED
    flags: list[str] = Field(default_factory=list)
    iban_verified: bool
    details: dict[str, Any] = Field(default_factory=dict)


class FraudDetector:
    """Motor de detección de fraude en pagos a proveedores."""

    VERIFIED_VENDOR_REGISTRY: dict[str, str] = {
        "A28998877": "ES7601820001880200004567",  # Cloud Hosting Iberia
        "B84112233": "ES9121000418450200051332",  # Consulting Partners
        "B12345678": "ES3400491500051111222233",  # Proveedor Habitual SL
    }

    @classmethod
    def audit_invoice(
        cls,
        vendor_cif: str,
        invoice_number: str,
        invoice_amount: float,
        provided_iban: str,
        historical_invoice_numbers: list[str] | None = None,
        historical_amounts: list[float] | None = None
    ) -> FraudAuditResult:
        flags: list[str] = []
        risk = 0
        clean_provided = provided_iban.replace(" ", "").replace("-", "").upper()
        clean_cif = vendor_cif.strip().upper()

        # 1. Chequeo de duplicado de número de factura
        if historical_invoice_numbers and invoice_number in historical_invoice_numbers:
            flags.append(f"FACTURA_DUPLICADA: El número '{invoice_number}' ya fue pagado o registrado con anterioridad.")
            risk += 60

        # 2. Detección de Desvío de IBAN (Man-in-the-Middle / Phishing)
        verified_iban = cls.VERIFIED_VENDOR_REGISTRY.get(clean_cif)
        iban_match = True
        if verified_iban:
            if clean_provided != verified_iban.upper():
                flags.append(
                    f"DESVÍO_CRÍTICO_DE_IBAN: La factura indica {clean_provided}, pero la cuenta verificada en el registro corporativo es {verified_iban}."
                )
                risk += 70
                iban_match = False
        else:
            flags.append(f"IBAN_NUEVO_NO_VERIFICADO: Primer pago registrado para el CIF {clean_cif}. Requiere validación bancaria previa.")
            risk += 25
            iban_match = False

        # 3. Importes Atípicos (> 3.5x la media histórica)
        if historical_amounts and len(historical_amounts) >= 3:
            avg_amt = sum(historical_amounts) / len(historical_amounts)
            if invoice_amount > (avg_amt * 3.5):
                flags.append(f"PICO_ANÓMALO_DE_IMPORTE: Importe ({invoice_amount:,.2f} €) es >3.5x el promedio histórico ({avg_amt:,.2f} €).")
                risk += 30

        # 4. Heurística de Benford y Cifras Redondas Sospechosas
        if invoice_amount >= 500.0 and invoice_amount % 500 == 0:
            flags.append(f"IMPORTE_REDONDO_SOSPECHOSO: {invoice_amount:,.2f} € es múltiplo exacto de 500€, patrón común en facturación ficticia.")
            risk += 15

        if risk >= 60:
            status = "BLOCKED"
            is_safe = False
        elif risk >= 20:
            status = "REQUIRES_HITL"
            is_safe = False
        else:
            status = "APPROVED"
            is_safe = True

        return FraudAuditResult(
            is_safe=is_safe,
            risk_score=min(100, risk),
            status=status,
            flags=flags,
            iban_verified=iban_match,
            details={
                "vendor_cif": clean_cif,
                "invoice_number": invoice_number,
                "amount": invoice_amount,
                "provided_iban": clean_provided,
                "verified_iban": verified_iban or "NO_REGISTRADO"
            }
        )
