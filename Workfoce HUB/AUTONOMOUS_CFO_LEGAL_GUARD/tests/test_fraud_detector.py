import pytest
from legal_guard.fraud_detector import FraudDetector

def test_legitimate_invoice():
    res = FraudDetector.audit_invoice(
        vendor_cif="B12345678",
        invoice_number="INV-2026-001",
        invoice_amount=3450.00,
        provided_iban="ES3400491500051111222233" # Verified in registry
    )
    assert res.is_safe is True
    assert res.status == "APPROVED"
    assert res.risk_score < 25
    assert len(res.flags) == 0

def test_man_in_the_middle_iban_hijack():
    res = FraudDetector.audit_invoice(
        vendor_cif="B12345678",
        invoice_number="INV-2026-002",
        invoice_amount=3450.00,
        provided_iban="ES0099998888777766665555" # Hacker IBAN
    )
    assert res.is_safe is False
    assert res.status == "BLOCKED"
    assert res.risk_score >= 60
    assert any("DESVÍO_CRÍTICO_DE_IBAN" in f for f in res.flags)

def test_duplicate_invoice_detection():
    historical = ["INV-2026-DUP"]
    res = FraudDetector.audit_invoice(
        vendor_cif="B12345678",
        invoice_number="INV-2026-DUP",
        invoice_amount=3450.00,
        provided_iban="ES3400491500051111222233",
        historical_invoice_numbers=historical
    )
    assert any("FACTURA_DUPLICADA" in f for f in res.flags)
