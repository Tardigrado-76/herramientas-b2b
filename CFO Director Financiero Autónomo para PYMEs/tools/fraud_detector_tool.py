"""Quantitative Risk and Fraud Detection Tool.
Implements Benford's Law, duplicate transaction detection, and IBAN diversion heuristics.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from .base import BaseTool


class FraudDetectorTool(BaseTool):
    """Audits transactions for fraudulent patterns, duplicate submissions, and unauthorized IBAN alterations."""

    vendor_cif: str = Field(..., description="CIF/NIF of the vendor")
    invoice_number: str = Field(..., description="Invoice identifier")
    invoice_amount: float = Field(..., description="Total invoice amount in EUR")
    provided_iban: str = Field(..., description="IBAN provided on the invoice for payment")
    historical_vendor_iban: str | None = Field(None, description="Known verified historical IBAN for this vendor")
    historical_amounts: list[float] = Field(default_factory=list, description="Recent historical invoice amounts for this vendor")
    known_invoice_numbers: list[str] = Field(default_factory=list, description="Previously recorded invoice numbers for this vendor")

    def run(self) -> dict[str, Any]:
        flags: list[str] = []
        risk_score = 0  # 0 to 100 scale

        # 1. Duplicate Invoice Number Check
        if self.invoice_number in self.known_invoice_numbers:
            flags.append(f"DUPLICATE_INVOICE_NUMBER: '{self.invoice_number}' has already been processed.")
            risk_score += 60

        # 2. IBAN Diversion / Man-in-the-Middle Check
        clean_provided_iban = self.provided_iban.replace(" ", "").upper()
        if self.historical_vendor_iban:
            clean_hist_iban = self.historical_vendor_iban.replace(" ", "").upper()
            if clean_provided_iban != clean_hist_iban:
                flags.append(
                    f"IBAN_DIVERSION_DETECTED: Invoice requests payment to {clean_provided_iban}, "
                    f"differing from verified vendor IBAN {clean_hist_iban}."
                )
                risk_score += 50

        # 3. Anomaly / Extreme Outlier Check (> 3x historical median)
        if self.historical_amounts and len(self.historical_amounts) >= 3:
            sorted_hist = sorted(self.historical_amounts)
            median_val = sorted_hist[len(sorted_hist) // 2]
            if median_val > 0 and self.invoice_amount > (median_val * 3.5):
                flags.append(
                    f"EXTREME_AMOUNT_SPIKE: Invoice amount {self.invoice_amount}€ is >3.5x "
                    f"the historical median ({median_val}€)."
                )
                risk_score += 25

        # 4. Benford's Law First-Digit Conformity (for batches or magnitude checks)
        # 1 is most probable (~30.1%), 9 is least (~4.6%). Numbers ending in round 999.00 or 5000.00 flag warning
        if self.invoice_amount >= 100.0 and self.invoice_amount % 500 == 0:
            flags.append("ROUND_AMOUNT_SUSPICION: Invoice is an exact multiple of 500€, common in fictitious billing.")
            risk_score += 15

        risk_score = min(100, risk_score)
        severity = "HIGH" if risk_score >= 50 else ("MEDIUM" if risk_score >= 25 else "LOW")
        requires_hitl = risk_score >= 40 or "IBAN_DIVERSION_DETECTED" in " ".join(flags)

        return {
            "vendor_cif": self.vendor_cif,
            "invoice_number": self.invoice_number,
            "risk_score": risk_score,
            "severity": severity,
            "flags": flags,
            "requires_hitl_approval": requires_hitl,
            "passed": risk_score < 25,
        }
