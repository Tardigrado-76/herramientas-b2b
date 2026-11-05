"""Cash Flow Forecaster Tool.
Projects 30/60/90-day liquidity, working capital requirements, and financial runway.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from .base import BaseTool


class CashFlowForecasterTool(BaseTool):
    """Calculates 30, 60, and 90-day cash flow forecasts, runway, and liquidity distress alerts."""

    current_cash: float = Field(..., description="Current available liquid cash across all bank accounts in EUR")
    monthly_burn_rate: float = Field(..., description="Monthly fixed operating expenditures (payroll, rent, utilities)")
    expected_receivables_30d: float = Field(default=0.0, description="Customer invoices expected to be collected within 30 days")
    expected_payables_30d: float = Field(default=0.0, description="Supplier/tax payables due within 30 days")
    expected_receivables_60d: float = Field(default=0.0, description="Receivables expected between day 31 and 60")
    expected_payables_60d: float = Field(default=0.0, description="Payables expected between day 31 and 60")
    expected_receivables_90d: float = Field(default=0.0, description="Receivables expected between day 61 and 90")
    expected_payables_90d: float = Field(default=0.0, description="Payables expected between day 61 and 90")
    safety_cushion_months: float = Field(default=2.0, description="Minimum recommended liquidity cushion in months of burn rate")

    def run(self) -> dict[str, Any]:
        # 30 days projection
        net_30 = self.expected_receivables_30d - (self.expected_payables_30d + self.monthly_burn_rate)
        proj_30 = round(self.current_cash + net_30, 2)

        # 60 days projection
        net_60 = self.expected_receivables_60d - (self.expected_payables_60d + self.monthly_burn_rate)
        proj_60 = round(proj_30 + net_60, 2)

        # 90 days projection
        net_90 = self.expected_receivables_90d - (self.expected_payables_90d + self.monthly_burn_rate)
        proj_90 = round(proj_60 + net_90, 2)

        # Runway calculation
        runway_months = (
            round(self.current_cash / self.monthly_burn_rate, 1)
            if self.monthly_burn_rate > 0
            else 999.0
        )

        min_recommended_cash = round(self.monthly_burn_rate * self.safety_cushion_months, 2)
        distress_warning = min(proj_30, proj_60, proj_90) < min_recommended_cash
        overdraft_risk = min(proj_30, proj_60, proj_90) < 0.0

        return {
            "current_cash": self.current_cash,
            "projected_cash_30d": proj_30,
            "projected_cash_60d": proj_60,
            "projected_cash_90d": proj_90,
            "runway_months": runway_months,
            "minimum_recommended_cash": min_recommended_cash,
            "distress_warning": distress_warning,
            "overdraft_risk": overdraft_risk,
            "status": "CRITICAL" if overdraft_risk else ("WARNING" if distress_warning else "HEALTHY"),
        }
