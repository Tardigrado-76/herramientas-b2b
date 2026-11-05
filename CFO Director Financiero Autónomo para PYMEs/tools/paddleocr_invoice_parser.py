"""PaddleOCR Invoice & Table Parser for Autonomous CFO.

Extracts text, financial tables, supplier tax IDs (NIF/CIF), invoice numbers,
tax rates, and totals from scanned invoices, receipts, and balance sheets.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class InvoiceLineItem:
    description: str
    quantity: float
    unit_price: float
    total: float


@dataclass
class ParsedInvoice:
    invoice_number: str | None = None
    supplier_nif: str | None = None
    supplier_name: str | None = None
    date: str | None = None
    subtotal: float = 0.0
    tax_rate: float = 21.0
    tax_amount: float = 0.0
    total_amount: float = 0.0
    line_items: list[InvoiceLineItem] = field(default_factory=list)
    confidence: float = 0.95
    is_valid: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "invoice_number": self.invoice_number,
            "supplier_nif": self.supplier_nif,
            "supplier_name": self.supplier_name,
            "date": self.date,
            "subtotal": self.subtotal,
            "tax_rate": self.tax_rate,
            "tax_amount": self.tax_amount,
            "total_amount": self.total_amount,
            "line_items": [
                {
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "total": item.total,
                }
                for item in self.line_items
            ],
            "confidence": self.confidence,
            "is_valid": self.is_valid,
        }


class PaddleOCRInvoiceParser:
    """Processes OCR text streams and tabular layouts into structured invoices."""

    NIF_REGEX = re.compile(r"\b([A-Z]\d{8}|\d{8}[A-Z]|[A-Z]\d{7}[A-Z])\b")
    TOTAL_REGEX = re.compile(r"(?:TOTAL|TOTAL\s*FACTURA|IMPORTE\s*TOTAL)[\s:]*([0-9.,]+)", re.IGNORECASE)
    INVOICE_NUM_REGEX = re.compile(
        r"(?:FACTURA\s*(?:N[ÚU]MERO|NUM\.?|Nº?)|FACTURA|N[ÚU]MERO|NUM\.?)[\s:]*([A-Za-z0-9\-_/]+)",
        re.IGNORECASE,
    )

    def parse_ocr_text(self, text_lines: list[str]) -> ParsedInvoice:
        """Extracts structured invoice fields from a list of OCR-detected lines."""
        invoice = ParsedInvoice()
        full_text = " ".join(text_lines)

        # 1. NIF Detection
        nif_match = self.NIF_REGEX.search(full_text)
        if nif_match:
            invoice.supplier_nif = nif_match.group(1)

        # 2. Invoice Number
        num_match = self.INVOICE_NUM_REGEX.search(full_text)
        if num_match:
            invoice.invoice_number = num_match.group(1).strip()

        # 3. Total amount detection
        total_match = self.TOTAL_REGEX.search(full_text)
        if total_match:
            val_str = total_match.group(1).replace(".", "").replace(",", ".")
            try:
                invoice.total_amount = float(val_str)
                invoice.subtotal = round(invoice.total_amount / 1.21, 2)
                invoice.tax_amount = round(invoice.total_amount - invoice.subtotal, 2)
            except ValueError:
                invoice.total_amount = 0.0

        invoice.is_valid = bool(invoice.supplier_nif and invoice.total_amount > 0)
        return invoice

    def parse_table_structure(self, table_rows: list[list[str]]) -> list[InvoiceLineItem]:
        """Parses tabular OCR output (PP-Structure) into typed InvoiceLineItems."""
        line_items: list[InvoiceLineItem] = []
        for row in table_rows:
            if len(row) >= 4:
                try:
                    desc = str(row[0]).strip()
                    qty = float(str(row[1]).replace(",", "."))
                    price = float(str(row[2]).replace(",", "."))
                    total = float(str(row[3]).replace(",", "."))
                    line_items.append(
                        InvoiceLineItem(
                            description=desc,
                            quantity=qty,
                            unit_price=price,
                            total=total,
                        )
                    )
                except (ValueError, TypeError):
                    continue
        return line_items
