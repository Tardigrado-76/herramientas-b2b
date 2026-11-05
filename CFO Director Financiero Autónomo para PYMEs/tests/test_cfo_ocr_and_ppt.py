"""Unit tests for PaddleOCRInvoiceParser and CFOPPTDeckGenerator."""

from tools.cfo_ppt_deck_generator import CFOPPTDeckGenerator
from tools.paddleocr_invoice_parser import PaddleOCRInvoiceParser

SAMPLE_OCR_LINES = [
    "TECNOLOGIAS AVANZADAS S.A.",
    "NIF: B87654321",
    "FACTURA NUM.: FAC-2026-099",
    "FECHA: 15/10/2026",
    "CONCEPTO: SERVICIOS CLOUD ENTERPRISE",
    "BASE IMPONIBLE: 10.000,00",
    "IVA 21%: 2.100,00",
    "TOTAL FACTURA: 12.100,00",
]

SAMPLE_TABLE_DATA = [
    ["Servidor Cloud vCPU 16", "2", "500.00", "1000.00"],
    ["Almacenamiento NVMe 1TB", "4", "100.00", "400.00"],
]


def test_paddleocr_text_parsing():
    parser = PaddleOCRInvoiceParser()
    invoice = parser.parse_ocr_text(SAMPLE_OCR_LINES)
    
    assert invoice.is_valid is True
    assert invoice.supplier_nif == "B87654321"
    assert invoice.invoice_number == "FAC-2026-099"
    assert invoice.total_amount == 12100.00
    assert invoice.subtotal == 10000.00


def test_paddleocr_table_parsing():
    parser = PaddleOCRInvoiceParser()
    items = parser.parse_table_structure(SAMPLE_TABLE_DATA)
    
    assert len(items) == 2
    assert items[0].description == "Servidor Cloud vCPU 16"
    assert items[0].quantity == 2.0
    assert items[0].total == 1000.00


def test_cfo_ppt_deck_generator():
    generator = CFOPPTDeckGenerator(company_name="Innovación PYME S.L.")
    deck = generator.generate_board_deck_payload(
        z_score=3.15,
        ebitda=125000.00,
        runway_months=14.5,
        tax_contingency=22000.00,
    )
    
    assert deck.company_name == "Innovación PYME S.L."
    assert len(deck.slides) == 3
    assert deck.slides[1]["kpis"][0]["status"] == "Zona Segura"
