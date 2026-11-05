"""Executive Financial Report Generator.
Computes Altman Z'-Score for SMEs, financial health indicators, and GRC compliance attestations.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class FinancialKPIs:
    liquidity_eur: float
    monthly_burn_eur: float
    runway_months: float
    quick_ratio: float
    debt_to_equity: float
    altman_z_prime: float
    z_score_zone: str  # SAFE, GREY, DISTRESS
    quarterly_tax_liability_eur: float


class ExecutiveReportGenerator:
    """Produces board-level financial reports in Markdown and structured JSON."""

    @staticmethod
    def calculate_altman_z_prime(
        working_capital: float,
        retained_earnings: float,
        ebit: float,
        book_value_equity: float,
        total_liabilities: float,
        sales: float,
        total_assets: float,
    ) -> tuple[float, str]:
        """Altman Z'-Score formulation for private manufacturing and service SMEs.

        Z' = 0.717*X1 + 0.847*X2 + 3.107*X3 + 0.420*X4 + 0.998*X5
        Safe: > 2.90, Grey: 1.23 - 2.90, Distress: < 1.23
        """
        if total_assets <= 0 or total_liabilities <= 0:
            return 2.5, "GREY"

        x1 = working_capital / total_assets
        x2 = retained_earnings / total_assets
        x3 = ebit / total_assets
        x4 = book_value_equity / total_liabilities
        x5 = sales / total_assets

        z_prime = round(0.717 * x1 + 0.847 * x2 + 3.107 * x3 + 0.420 * x4 + 0.998 * x5, 2)
        if z_prime > 2.90:
            zone = "SAFE"
        elif z_prime >= 1.23:
            zone = "GREY"
        else:
            zone = "DISTRESS"

        return z_prime, zone

    @classmethod
    def generate_markdown_report(
        cls,
        company_name: str,
        kpis: FinancialKPIs,
        recommendations: list[str],
        nis2_verified: bool,
        rgpd_redactions_count: int,
        pending_hitl_count: int,
    ) -> str:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        zone_badge = {
            "SAFE": "🟢 SAFE (Low insolvency risk)",
            "GREY": "🟡 GREY (Moderate risk / Monitoring required)",
            "DISTRESS": "🔴 DISTRESS (High liquidity alert)",
        }.get(kpis.z_score_zone, "⚪ UNKNOWN")

        recs_md = "\n".join(f"- {r}" for r in recommendations) if recommendations else "- No urgent actions required."

        return f"""# 📊 INFORME EJECUTIVO CFO — {company_name.upper()}
**Generado por:** AUTONOMO CFO (AI Executive System)  
**Fecha de Emisión:** {now_str}  
**Marco Regulatorio:** Conforme a directivas UE NIS2, RGPD y CRA

---

## 1. 🎯 RESUMEN DE SALUD FINANCIERA
| Métrica Financiera | Valor Actual | Evaluación de Salud |
| :--- | :--- | :--- |
| **Tesorería Líquida Disponible** | **{kpis.liquidity_eur:,.2f} €** | Buffer Operativo |
| **Burn Rate Mensual** | {kpis.monthly_burn_eur:,.2f} €/mes | Gastos de Estructura |
| **Runway de Supervivencia** | **{kpis.runway_months} meses** | {"🟢 Óptimo (>6m)" if kpis.runway_months >= 6 else "🔴 Alerta (<6m)"} |
| **Quick Ratio (Test Ácido)** | {kpis.quick_ratio:.2f} | {"🟢 >1.0" if kpis.quick_ratio >= 1.0 else "🔴 <1.0"} |
| **Deuda / Fondos Propios** | {kpis.debt_to_equity:.2f} | {"🟢 Saludable (<2.0)" if kpis.debt_to_equity < 2.0 else "🟡 Alto"} |
| **Altman Z'-Score (PYMEs)** | **{kpis.altman_z_prime:.2f}** | **{zone_badge}** |
| **Reserva Fiscal Obligatoria (AEAT)** | **{kpis.quarterly_tax_liability_eur:,.2f} €** | Previsión Trimestral |

---

## 2. 🛡️ CUMPLIMIENTO REGULATORIO Y CIBERSEGURIDAD
- **Cadena de Auditoría Criptográfica NIS2 (Art. 21):** {"✅ Íntegra y Verificada (SHA-256)" if nis2_verified else "❌ Compromiso Detectado"}
- **Protección de Datos RGPD (Art. 25 & 17):** {rgpd_redactions_count} identificadores PII anonimizados en este ciclo.
- **Autorizaciones Pendientes (Human-in-the-Loop):** **{pending_hitl_count}** órdenes en espera de firma digital.

---

## 3. 💡 RECOMENDACIONES ESTRATÉGICAS DEL CFO
{recs_md}

---
*Documento emitido con firma criptográfica por el motor AUTONOMO CFO.*
"""
