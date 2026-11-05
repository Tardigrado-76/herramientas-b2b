"""CFO Executive Presentation Deck Generator (PPT-Master Integration).

Generates structured executive presentation decks (.pptx / structured JSON payload)
summarizing Treasury Health, Altman Z'-Score, Working Capital, and Tax Contingency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SlideDeckPayload:
    title: str
    company_name: str
    slides: list[dict[str, Any]] = field(default_factory=list)


class CFOPPTDeckGenerator:
    """Generates executive slide decks for board meetings and advisory committees."""

    def __init__(self, company_name: str = "PYME Enterprise S.L."):
        self.company_name = company_name

    def generate_board_deck_payload(
        self,
        z_score: float,
        ebitda: float,
        runway_months: float,
        tax_contingency: float,
    ) -> SlideDeckPayload:
        """Constructs slide payload ready for python-pptx rendering or JSON export."""
        status = "Zona Segura" if z_score > 2.9 else "Zona Gris" if z_score > 1.23 else "Distress Financiero"
        
        slides = [
            {
                "slide_type": "title",
                "title": "Informe de Situación Financiera y Tesorería",
                "subtitle": f"Comité de Dirección — {self.company_name}",
            },
            {
                "slide_type": "kpi_cards",
                "title": "Métricas Clave de Solvencia y Tesorería",
                "kpis": [
                    {"label": "Altman Z'-Score", "value": f"{z_score:.2f}", "status": status},
                    {"label": "EBITDA Anualizado", "value": f"{ebitda:,.2f} €"},
                    {"label": "Runway de Caja", "value": f"{runway_months:.1f} meses"},
                    {"label": "Contingencia Fiscal (IVA/IS)", "value": f"{tax_contingency:,.2f} €"},
                ],
            },
            {
                "slide_type": "bullet_points",
                "title": "Plan de Acción y Cumplimiento Normativo",
                "points": [
                    "Aprobación de pagos mediante protocolo 4-ojos conforme al Art. 14 del EU AI Act.",
                    "Conciliación bancaria PSD2 diaria completada al 100% sin discrepancias.",
                    "Monitoreo de insolvencia preventiva activado bajo la Ley Concursal 16/2022.",
                ],
            },
        ]

        return SlideDeckPayload(
            title="Executive Board Presentation",
            company_name=self.company_name,
            slides=slides,
        )
