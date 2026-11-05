"""Módulo Legal Guard: Cumplimiento Normativo, OCR Antifraude, Facturación y Búnker NIS2."""

from legal_guard.invoice_ocr import InvoiceOCRParser, ParsedInvoice
from legal_guard.fraud_detector import FraudDetector, FraudAuditResult
from legal_guard.electronic_invoicing import ElectronicInvoiceEngine, InvoiceComplianceFormat
from legal_guard.bunker_ledger import BunkerLedger, AuditBlock
from legal_guard.gdpr_shredder import GDPRShredder

__all__ = [
    "InvoiceOCRParser",
    "ParsedInvoice",
    "FraudDetector",
    "FraudAuditResult",
    "ElectronicInvoiceEngine",
    "InvoiceComplianceFormat",
    "BunkerLedger",
    "AuditBlock",
    "GDPRShredder",
]
