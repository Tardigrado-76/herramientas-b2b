import pytest
from cfo_core.reconciliation import BankReconciler, BankTransaction, InvoiceItem, ReconciliationStatus

def test_bank_reconciliation_exact_and_fuzzy():
    bank_entries = [
        BankTransaction(
            transaction_id="B1",
            date="2026-10-21",
            amount=12450.00,
            description="Cobro Factura INV-001 de DISTRIBUCIONES",
            counterparty_name="DISTRIBUCIONES NORTE"
        ),
        BankTransaction(
            transaction_id="B2",
            date="2026-10-20",
            amount=-3450.00,
            description="Pago Factura INV-002 Logistica",
            counterparty_name="LOGISTICA IBERIA"
        )
    ]
    
    erp_invoices = [
        InvoiceItem(
            invoice_id="INV-001",
            invoice_number="INV-001",
            vendor_or_client="DISTRIBUCIONES NORTE",
            cif="B98765432",
            amount=12450.00,
            date="2026-10-21",
            is_income=True,
            status="PENDING"
        ),
        InvoiceItem(
            invoice_id="INV-002",
            invoice_number="INV-002",
            vendor_or_client="LOGISTICA IBERIA",
            cif="B12345678",
            amount=3450.00,
            date="2026-10-20",
            is_income=False,
            status="PENDING"
        )
    ]
    
    matches = BankReconciler.reconcile(bank_entries, erp_invoices)
    assert len(matches) == 2
    matched_items = [m for m in matches if m.status == ReconciliationStatus.MATCHED]
    assert len(matched_items) == 2
