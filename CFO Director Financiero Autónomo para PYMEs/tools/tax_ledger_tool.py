"""Tax and General Ledger Provisioning Tool (Spanish AEAT Compliance).
Calculates quarterly tax obligations: Modelo 303 (IVA), Modelo 111 (IRPF), and Corporate Tax reserves.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from .base import BaseTool


class TaxLedgerTool(BaseTool):
    """Calculates quarterly Spanish fiscal obligations and required bank reserves to avoid tax penalties."""

    quarter: str = Field(..., description="Quarter (e.g., '1T', '2T', '3T', '4T')")
    collected_vat: float = Field(..., description="IVA repercutido (collected from customer sales)")
    deductible_vat: float = Field(..., description="IVA soportado deducible (paid on validated business expenses)")
    withheld_irpf: float = Field(default=0.0, description="IRPF retenciones withheld from professionals/leases (Modelo 111/115)")
    net_ebitda: float = Field(default=0.0, description="Quarterly operating profit before taxes")
    is_startup_rate: bool = Field(default=False, description="True if company qualifies for 15% corporate tax rate instead of 25%")

    def run(self) -> dict[str, Any]:
        # 1. Modelo 303 (IVA)
        net_vat_liability = round(self.collected_vat - self.deductible_vat, 2)
        vat_payable = max(0.0, net_vat_liability)
        vat_credit = abs(min(0.0, net_vat_liability))

        # 2. Modelo 111/115 (IRPF)
        irpf_payable = round(max(0.0, self.withheld_irpf), 2)

        # 3. Impuesto de Sociedades (Quarterly provision / Modelo 202)
        tax_rate = 0.15 if self.is_startup_rate else 0.25
        corporate_tax_provision = round(max(0.0, self.net_ebitda * tax_rate), 2)

        # Total fiscal reserve required
        total_tax_reserve = round(vat_payable + irpf_payable + corporate_tax_provision, 2)

        return {
            "quarter": self.quarter,
            "modelo_303_iva": {
                "collected_vat": self.collected_vat,
                "deductible_vat": self.deductible_vat,
                "net_result": net_vat_liability,
                "status": "PAYABLE" if net_vat_liability > 0 else "COMPENSABLE",
                "payable_amount": vat_payable,
                "credit_amount": vat_credit,
            },
            "modelo_111_irpf": {
                "payable_amount": irpf_payable,
            },
            "corporate_tax_reserve": {
                "applicable_rate": tax_rate,
                "provision_amount": corporate_tax_provision,
            },
            "total_mandatory_tax_reserve": total_tax_reserve,
            "advice": (
                f"SME must quarantine {total_tax_reserve}€ in a dedicated tax sub-account "
                f"prior to the {self.quarter} tax deadline."
            ),
        }
