"""Invoice Processing and OCR Verification Tool.
Extracts structured accounting data from invoices/receipts with mathematical and tax consistency validation.
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import Field

from .base import BaseTool


class InvoiceOCRTool(BaseTool):
    """Parses raw text or OCR output from an invoice, verifies arithmetic and tax rates (IVA/IRPF)."""

    invoice_raw_text: str = Field(..., description="Raw text or OCR string of the invoice")
    tenant_id: str = Field(default="default_sme", description="Unique tenant identifier")

    def run(self) -> dict[str, Any]:
        text = self.invoice_raw_text

        # Heuristic/Regex extractor for standard Spanish invoice parameters
        cif_match = re.search(r"\b([ABCDEFGHJKLMNPQRSUVWabcdefghjklmnpqrsuvw]\d{7}[0-9A-Ja-j]|\d{8}[A-Za-z])\b", text)
        total_match = re.search(r"(?:total|importe total|total factura)[\s:=]*€?\s*([\d\.,]+)", text, re.IGNORECASE)
        base_match = re.search(r"(?:base imponible|subtotal|base)[\s:=]*€?\s*([\d\.,]+)", text, re.IGNORECASE)
        iva_match = re.search(r"(?:iva|i\.v\.a\.)[\s:=]*(\d{1,2})[\s%]*€?\s*([\d\.,]+)?", text, re.IGNORECASE)
        irpf_match = re.search(r"(?:irpf|retenci[oó]n)[\s:=]*(\d{1,2})[\s%]*€?\s*([\d\.,]+)?", text, re.IGNORECASE)
        iban_match = re.search(r"\b(ES\d{2}(?:[ \-]?[0-9A-Z]){20})\b", text, re.IGNORECASE)
        inv_num_match = re.search(
            r"(?:factura\s*(?:n[ºoú\.]*)?|n[ºoú\.]*\s*factura|invoice\s*(?:no\.?)?|n[ºoú]\.?)[\s:=#]*([A-Za-z0-9\-_/]+)",
            text,
            re.IGNORECASE,
        )

        def _clean_num(val_str: str | None) -> float:
            if not val_str:
                return 0.0
            clean = val_str.replace("€", "").strip()
            if "," in clean and "." in clean:
                clean = clean.replace(".", "").replace(",", ".")
            elif "," in clean:
                clean = clean.replace(",", ".")
            try:
                return float(clean)
            except ValueError:
                return 0.0

        base_amount = _clean_num(base_match.group(1)) if base_match else 0.0
        total_amount = _clean_num(total_match.group(1)) if total_match else 0.0

        vat_rate = float(iva_match.group(1)) if iva_match else 21.0
        vat_amount = _clean_num(iva_match.group(2)) if (iva_match and iva_match.group(2)) else round(base_amount * (vat_rate / 100.0), 2)

        irpf_rate = float(irpf_match.group(1)) if irpf_match else 0.0
        irpf_amount = _clean_num(irpf_match.group(2)) if (irpf_match and irpf_match.group(2)) else round(base_amount * (irpf_rate / 100.0), 2)

        # Back-calculate if base was missing but total was present
        if base_amount == 0.0 and total_amount > 0.0:
            effective_mult = 1.0 + (vat_rate / 100.0) - (irpf_rate / 100.0)
            base_amount = round(total_amount / effective_mult, 2)
            vat_amount = round(base_amount * (vat_rate / 100.0), 2)
            irpf_amount = round(base_amount * (irpf_rate / 100.0), 2)
        elif total_amount == 0.0 and base_amount > 0.0:
            total_amount = round(base_amount + vat_amount - irpf_amount, 2)

        # Mathematical verification
        expected_total = round(base_amount + vat_amount - irpf_amount, 2)
        math_consistent = abs(expected_total - total_amount) <= 0.05

        vendor_cif = cif_match.group(1).upper() if cif_match else "UNKNOWN_CIF"
        iban = iban_match.group(1).replace(" ", "").replace("-", "") if iban_match else "UNKNOWN_IBAN"
        invoice_number = inv_num_match.group(1) if inv_num_match else "INV-UNASSIGNED"

        return {
            "vendor_cif": vendor_cif,
            "invoice_number": invoice_number,
            "base_amount": base_amount,
            "vat_rate": vat_rate,
            "vat_amount": vat_amount,
            "irpf_rate": irpf_rate,
            "irpf_amount": irpf_amount,
            "total_amount": total_amount,
            "expected_total": expected_total,
            "math_consistent": math_consistent,
            "iban": iban,
            "confidence_score": 0.95 if math_consistent else 0.65,
        }
