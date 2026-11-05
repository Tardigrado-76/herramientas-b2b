"""Calculadora determinista del modelo de solvencia Altman Z'-Score para PYMEs privadas.

Implementa la formulación canónica de Altman (1983) para empresas no cotizadas
y de servicios, prediciendo solvencia con hasta 24 meses de antelación.
"""

from enum import Enum
from pydantic import BaseModel, Field


class SolvencyZone(str, Enum):
    SAFE_ZONE = "SAFE_ZONE"          # Z' > 2.90 (Baja probabilidad de quiebra)
    GREY_ZONE = "GREY_ZONE"          # 1.23 <= Z' <= 2.90 (Precaución)
    DISTRESS_ZONE = "DISTRESS_ZONE"  # Z' < 1.23 (Riesgo alto de insolvencia)


class SolvencyReport(BaseModel):
    altman_z_prime: float = Field(..., description="Puntuación Z' de Altman")
    zone: SolvencyZone = Field(..., description="Zona de riesgo asignada")
    zone_description: str
    working_capital_ratio: float
    retained_earnings_ratio: float
    ebit_ratio: float
    equity_to_debt_ratio: float
    asset_turnover_ratio: float
    recommendation: str
    bankruptcy_risk_pct: float


class AltmanZScoreCalculator:
    """Motor de cálculo matemático para el Altman Z'-Score de PYMEs."""

    @staticmethod
    def calculate(
        working_capital: float,
        retained_earnings: float,
        ebit: float,
        equity: float,
        total_liabilities: float,
        sales: float,
        total_assets: float | None = None
    ) -> SolvencyReport:
        """Calcula el índice Z' y desglosa los componentes clave.
        
        Si total_assets no se proporciona, se asume Activo = Fondos Propios + Pasivo Total.
        """
        assets = total_assets if total_assets and total_assets > 0 else (equity + total_liabilities)
        if assets <= 0:
            assets = 1.0  # Prevención de división por cero

        debt = total_liabilities if total_liabilities > 0 else 1.0

        # Ratios financieros X1 a X5
        x1 = working_capital / assets
        x2 = retained_earnings / assets
        x3 = ebit / assets
        x4 = equity / debt
        x5 = sales / assets

        # Ponderación Altman Z' para PYMEs no cotizadas
        z_prime = round(
            (0.717 * x1) + (0.847 * x2) + (3.107 * x3) + (0.420 * x4) + (0.998 * x5),
            2
        )

        if z_prime > 2.90:
            zone = SolvencyZone.SAFE_ZONE
            desc = "Zona Segura: Balance sólido, bajo riesgo de insolvencia financiera."
            recom = "Solvencia óptima. Recomendado: Inversión en crecimiento o amortización voluntaria."
            risk_pct = 5.0
        elif 1.23 <= z_prime <= 2.90:
            zone = SolvencyZone.GREY_ZONE
            desc = "Zona Gris: Estabilidad moderada. Requiere supervisión activa de cobros."
            recom = "Monitorear cobros a 60 días, moderar reparto de dividendos y vigilar deuda a corto plazo."
            risk_pct = 35.0
        else:
            zone = SolvencyZone.DISTRESS_ZONE
            desc = "Zona de Dificultad: Alto riesgo de insolvencia o asfixia financiera."
            recom = "ALERTA CRÍTICA: Reestructurar deuda urgente, acelerar cobro de facturas y contener burn rate."
            risk_pct = 85.0

        return SolvencyReport(
            altman_z_prime=z_prime,
            zone=zone,
            zone_description=desc,
            working_capital_ratio=round(x1, 3),
            retained_earnings_ratio=round(x2, 3),
            ebit_ratio=round(x3, 3),
            equity_to_debt_ratio=round(x4, 3),
            asset_turnover_ratio=round(x5, 3),
            recommendation=recom,
            bankruptcy_risk_pct=risk_pct
        )
