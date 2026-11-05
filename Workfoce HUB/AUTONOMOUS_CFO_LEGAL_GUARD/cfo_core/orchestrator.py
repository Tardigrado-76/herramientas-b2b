"""Orquestador Central del Consejo de Agentes IA para Autonomous CFO & Legal Guard.

Coordina los 4 roles del consejo financiero-legal:
1. CFO Executive (Estrategia, Runway y Asignación de Capital)
2. Tax Accountant (OCR de Facturas, Asientos y Conciliación)
3. Risk Analyst (Detección de Fraude de IBAN y Ratios Z')
4. GRC Sentinel (Facturación Crea y Crece, NIS2 y RGPD)
"""

from typing import Any
from pydantic import BaseModel, Field

from cfo_core.solvency import AltmanZScoreCalculator, SolvencyReport
from cfo_core.cashflow import CashFlowProjector, CashFlowSummary
from cfo_core.reconciliation import BankReconciler, BankTransaction, InvoiceItem, ReconciliationMatch


class ExecutiveSummary(BaseModel):
    tenant_id: str
    company_name: str
    company_cif: str
    timestamp: str
    solvency: SolvencyReport
    cashflow: CashFlowSummary
    unreconciled_transactions_count: int
    flagged_fraud_alerts_count: int
    tax_reserve_quarterly: float
    overall_health: str  # EXCELLENT, STABLE, WARNING, DISTRESS
    key_actions: list[str] = Field(default_factory=list)


class CFOExecutiveOrchestrator:
    """Motor de orquestación ejecutiva del consejo de agentes autónomos."""

    def __init__(
        self,
        tenant_id: str = "pyme-madrid-01",
        company_name: str = "Innovaciones Digitales S.L.",
        company_cif: str = "B87654321",
        inference_mode: str = "local",
        model_name: str = "llama3.3:latest"
    ):
        self.tenant_id = tenant_id
        self.company_name = company_name
        self.company_cif = company_cif
        self.inference_mode = inference_mode
        self.model_name = model_name

    def evaluate_company_health(
        self,
        current_cash: float,
        monthly_burn: float,
        working_capital: float,
        retained_earnings: float,
        ebit: float,
        equity: float,
        total_liabilities: float,
        sales: float,
        receivables_30d: float = 0.0,
        payables_30d: float = 0.0,
        collected_vat_q: float = 0.0,
        deductible_vat_q: float = 0.0,
        unreconciled_count: int = 0,
        fraud_alerts_count: int = 0
    ) -> ExecutiveSummary:
        from datetime import datetime, timezone

        # 1. Solvencia matemática Altman Z'
        solvency = AltmanZScoreCalculator.calculate(
            working_capital=working_capital,
            retained_earnings=retained_earnings,
            ebit=ebit,
            equity=equity,
            total_liabilities=total_liabilities,
            sales=sales
        )

        # 2. Proyecciones de Tesorería a 90 días
        cashflow = CashFlowProjector.project(
            current_cash=current_cash,
            monthly_burn_rate=monthly_burn,
            receivables_30d=receivables_30d,
            payables_30d=payables_30d
        )

        # 3. Estimación de Reserva Fiscal Trimestral (IVA neto + 25% IS preliminar sobre EBIT)
        net_vat = max(0.0, collected_vat_q - deductible_vat_q)
        preliminary_is = max(0.0, ebit * 0.25)
        tax_reserve = round(net_vat + preliminary_is, 2)

        # 4. Diagnóstico Global del Consejo
        actions: list[str] = []
        if solvency.zone.value == "DISTRESS_ZONE" or cashflow.overdraft_risk:
            health = "DISTRESS"
            actions.append("ALERTA CRÍTICA: Activar comité de urgencia por riesgo de iliquidez a corto plazo.")
            actions.append("Retener pagos no esenciales y priorizar cobros vencidos.")
        elif solvency.zone.value == "GREY_ZONE" or cashflow.distress_alert:
            health = "WARNING"
            actions.append("ALERTA PREVENTIVA: Balance en zona gris o tesorería bajo el colchón mínimo de seguridad.")
            actions.append("Optimizar fondo de maniobra y renegociar plazos con proveedores.")
        elif cashflow.runway_months >= 6.0 and solvency.zone.value == "SAFE_ZONE":
            health = "EXCELLENT"
            actions.append("Estado financiero impecable: Solvencia en zona segura y runway > 6 meses.")
            actions.append("Evaluar reinversión en I+D o expansión comercial.")
        else:
            health = "STABLE"
            actions.append("Operación financiera estable. Mantener disciplina de gasto y cobros.")

        if fraud_alerts_count > 0:
            actions.append(f"SEGURIDAD: Hay {fraud_alerts_count} facturas con alertas de posible fraude o discrepancia de IBAN.")

        return ExecutiveSummary(
            tenant_id=self.tenant_id,
            company_name=self.company_name,
            company_cif=self.company_cif,
            timestamp=datetime.now(timezone.utc).isoformat(),
            solvency=solvency,
            cashflow=cashflow,
            unreconciled_transactions_count=unreconciled_count,
            flagged_fraud_alerts_count=fraud_alerts_count,
            tax_reserve_quarterly=tax_reserve,
            overall_health=health,
            key_actions=actions
        )
