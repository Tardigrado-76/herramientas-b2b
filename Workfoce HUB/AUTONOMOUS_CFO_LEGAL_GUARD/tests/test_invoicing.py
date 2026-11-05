import pytest
from legal_guard.electronic_invoicing import ElectronicInvoiceEngine, InvoiceComplianceFormat

def test_verifactu_electronic_invoicing():
    inv1 = ElectronicInvoiceEngine.generate_compliant_invoice_record(
        invoice_number="EXP-2026-0001",
        issuer_cif="B98765432",
        recipient_cif="A11223344",
        total_amount=12100.0,
        format_type=InvoiceComplianceFormat.VERIFACTU,
        vat_rate_pct=21.0
    )
    
    assert inv1.compliance_passed is True
    assert inv1.subtotal == 10000.0
    assert inv1.vat_amount == 2100.0
    assert len(inv1.record_hash) == 64
    assert "agenciatributaria.gob.es/verifactu" in inv1.qr_data
    
    # Second invoice chaining
    inv2 = ElectronicInvoiceEngine.generate_compliant_invoice_record(
        invoice_number="EXP-2026-0002",
        issuer_cif="B98765432",
        recipient_cif="A11223344",
        total_amount=6050.0,
        format_type=InvoiceComplianceFormat.VERIFACTU,
        vat_rate_pct=21.0
    )
    
    assert len(inv2.record_hash) == 64
    assert inv2.compliance_passed is True
