"""Monthly Closing & Spanish Tax Agency (AEAT) Filing Agent.

Automates corporate monthly/quarterly tax closing procedures for Spanish legal entities:
1. Modelo 303: Declaración Trimestral de IVA (Base Imponible, Cuotas Repercutidas, IVA Soportado Deducible).
2. Modelo 111: Retenciones IRPF (Nóminas de trabajadores y retenciones a profesionales independientes).
3. Produces audit-certified fiscal submission packages with SHA-256 seals.
"""

from __future__ import annotations

import hashlib
from typing import Any

from pydantic import BaseModel


class InvoiceRecord(BaseModel):
    invoice_id: str
    invoice_type: str  # ISSUED (Ventas), RECEIVED (Gastos/Compras)
    counterparty_nif: str
    counterparty_name: str
    base_amount: float
    vat_rate: float  # 0.21, 0.10, 0.04
    vat_amount: float
    retention_rate: float = 0.0  # e.g., 0.15 for IRPF profesionales
    retention_amount: float = 0.0
    date: str


class Modelo303Settlement(BaseModel):
    modelo: str = "303"
    period: str  # e.g. "1T-2026", "2T-2026"
    company_cif: str
    company_name: str
    base_devengada_21: float
    cuota_devengada_21: float
    base_devengada_10: float
    cuota_devengada_10: float
    base_devengada_04: float
    cuota_devengada_04: float
    total_cuota_devengada: float
    base_soportada_deducible: float
    total_cuota_soportada: float
    resultado_autoliquidacion: float  # Positive = A Ingresar, Negative = A Devolver/Compensar
    submission_seal: str


class Modelo111Settlement(BaseModel):
    modelo: str = "111"
    period: str
    company_cif: str
    trabajadores_count: int
    trabajadores_rendimientos: float
    trabajadores_retenciones: float
    profesionales_count: int
    profesionales_rendimientos: float
    profesionales_retenciones: float
    total_a_ingresar: float
    submission_seal: str


class MonthlyClosingAgent:
    """Automates Spanish fiscal settlement and ledger balancing."""

    def __init__(self, company_cif: str = "B-12345678", company_name: str = "Enterprise Logistics SL") -> None:
        self.company_cif = company_cif
        self.company_name = company_name

    def compute_modelo_303(self, invoices: list[InvoiceRecord], period: str = "1T-2026") -> Modelo303Settlement:
        """Calculates AEAT Modelo 303 figures from issued and received invoices."""
        base_21 = sum(i.base_amount for i in invoices if i.invoice_type == "ISSUED" and abs(i.vat_rate - 0.21) < 0.001)
        cuota_21 = sum(i.vat_amount for i in invoices if i.invoice_type == "ISSUED" and abs(i.vat_rate - 0.21) < 0.001)

        base_10 = sum(i.base_amount for i in invoices if i.invoice_type == "ISSUED" and abs(i.vat_rate - 0.10) < 0.001)
        cuota_10 = sum(i.vat_amount for i in invoices if i.invoice_type == "ISSUED" and abs(i.vat_rate - 0.10) < 0.001)

        base_04 = sum(i.base_amount for i in invoices if i.invoice_type == "ISSUED" and abs(i.vat_rate - 0.04) < 0.001)
        cuota_04 = sum(i.vat_amount for i in invoices if i.invoice_type == "ISSUED" and abs(i.vat_rate - 0.04) < 0.001)

        total_devengada = cuota_21 + cuota_10 + cuota_04

        base_soportada = sum(i.base_amount for i in invoices if i.invoice_type == "RECEIVED")
        cuota_soportada = sum(i.vat_amount for i in invoices if i.invoice_type == "RECEIVED")

        resultado = round(total_devengada - cuota_soportada, 2)

        seal = hashlib.sha256(
            f"{self.company_cif}:{period}:{total_devengada}:{cuota_soportada}:{resultado}".encode()
        ).hexdigest()

        return Modelo303Settlement(
            period=period,
            company_cif=self.company_cif,
            company_name=self.company_name,
            base_devengada_21=round(base_21, 2),
            cuota_devengada_21=round(cuota_21, 2),
            base_devengada_10=round(base_10, 2),
            cuota_devengada_10=round(cuota_10, 2),
            base_devengada_04=round(base_04, 2),
            cuota_devengada_04=round(cuota_04, 2),
            total_cuota_devengada=round(total_devengada, 2),
            base_soportada_deducible=round(base_soportada, 2),
            total_cuota_soportada=round(cuota_soportada, 2),
            resultado_autoliquidacion=resultado,
            submission_seal=seal,
        )

    def compute_modelo_111(
        self,
        payroll_records: list[dict[str, Any]],
        professional_invoices: list[InvoiceRecord],
        period: str = "1T-2026",
    ) -> Modelo111Settlement:
        """Calculates AEAT Modelo 111 figures for payroll and independent professionals."""
        trab_rend = sum(p.get("gross_salary", 0.0) for p in payroll_records)
        trab_ret = sum(p.get("irpf_withheld", 0.0) for p in payroll_records)

        prof_rend = sum(i.base_amount for i in professional_invoices if i.retention_rate > 0)
        prof_ret = sum(i.retention_amount for i in professional_invoices if i.retention_rate > 0)

        total_ingresar = round(trab_ret + prof_ret, 2)
        seal = hashlib.sha256(
            f"{self.company_cif}:{period}:{trab_ret}:{prof_ret}:{total_ingresar}".encode()
        ).hexdigest()

        return Modelo111Settlement(
            period=period,
            company_cif=self.company_cif,
            trabajadores_count=len(payroll_records),
            trabajadores_rendimientos=round(trab_rend, 2),
            trabajadores_retenciones=round(trab_ret, 2),
            profesionales_count=len(professional_invoices),
            profesionales_rendimientos=round(prof_rend, 2),
            profesionales_retenciones=round(prof_ret, 2),
            total_a_ingresar=total_ingresar,
            submission_seal=seal,
        )
