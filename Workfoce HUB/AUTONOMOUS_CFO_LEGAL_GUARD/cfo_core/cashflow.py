"""Proyector de Flujo de Caja y Runway de Tesorería a 30, 60 y 90 días."""

from typing import Any
from pydantic import BaseModel, Field


class CashFlowSummary(BaseModel):
    current_cash: float
    monthly_burn_rate: float
    runway_months: float
    projected_cash_30d: float
    projected_cash_60d: float
    projected_cash_90d: float
    minimum_safety_cash: float
    distress_alert: bool
    overdraft_risk: bool
    status: str  # HEALTHY, WARNING, CRITICAL
    recommendations: list[str] = Field(default_factory=list)


class CashFlowProjector:
    """Motor de cálculo predictivo de liquidez y tesorería operativa."""

    @staticmethod
    def project(
        current_cash: float,
        monthly_burn_rate: float,
        receivables_30d: float = 0.0,
        payables_30d: float = 0.0,
        receivables_60d: float = 0.0,
        payables_60d: float = 0.0,
        receivables_90d: float = 0.0,
        payables_90d: float = 0.0,
        safety_cushion_months: float = 2.0
    ) -> CashFlowSummary:
        # Proyecciones netas
        net_30 = receivables_30d - (payables_30d + monthly_burn_rate)
        proj_30 = round(current_cash + net_30, 2)

        net_60 = receivables_60d - (payables_60d + monthly_burn_rate)
        proj_60 = round(proj_30 + net_60, 2)

        net_90 = receivables_90d - (payables_90d + monthly_burn_rate)
        proj_90 = round(proj_60 + net_90, 2)

        # Runway en meses
        runway = round(current_cash / monthly_burn_rate, 1) if monthly_burn_rate > 0 else 999.0
        min_safety = round(monthly_burn_rate * safety_cushion_months, 2)

        distress = min(proj_30, proj_60, proj_90) < min_safety
        overdraft = min(proj_30, proj_60, proj_90) < 0.0

        if overdraft:
            status = "CRITICAL"
        elif distress:
            status = "WARNING"
        else:
            status = "HEALTHY"

        recs: list[str] = []
        if overdraft:
            recs.append("Riesgo inminente de descubierto bancario en el horizonte de 90 días.")
            recs.append("Activar línea de crédito póliza o negociar aplazamiento de pagos con proveedores clave.")
        elif distress:
            recs.append(f"La liquidez cae por debajo del colchón de seguridad recomendado ({min_safety:,.2f} €).")
            recs.append("Intensificar el cobro de facturas vencidas y posponer gastos no esenciales.")
        else:
            recs.append(f"Tesorería equilibrada con {runway} meses de autonomía financiera.")

        return CashFlowSummary(
            current_cash=current_cash,
            monthly_burn_rate=monthly_burn_rate,
            runway_months=runway,
            projected_cash_30d=proj_30,
            projected_cash_60d=proj_60,
            projected_cash_90d=proj_90,
            minimum_safety_cash=min_safety,
            distress_alert=distress,
            overdraft_risk=overdraft,
            status=status,
            recommendations=recs
        )
