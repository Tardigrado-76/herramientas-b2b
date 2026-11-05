"""Unit tests for Autonomous CFO Wave 3 Enterprise Enhancements.

Covers:
- MultichannelReconciler (4-way Stripe, Marketplace, Carrier, ERP matching)
- M365ExcelGhost (Office Scripts TypeScript & dbt model generation)
- MonthlyClosingAgent (Spanish AEAT Modelo 303 & Modelo 111 calculation)
"""


from agents.monthly_closing_agent import InvoiceRecord, MonthlyClosingAgent
from tools.m365_excel_ghost import M365ExcelGhost
from tools.multichannel_reconciler import ChannelTransaction, MultichannelReconciler


class TestMultichannelReconciler:
    def test_clean_matched_reconciliation(self):
        reconciler = MultichannelReconciler()
        gtw = [
            ChannelTransaction(
                tx_id="tx_1",
                channel="STRIPE",
                order_ref="ORD-1001",
                gross_amount=100.0,
                fee_amount=2.5,
                net_amount=97.5,
                status="CAPTURED",
            )
        ]
        erp = [
            ChannelTransaction(
                tx_id="erp_1",
                channel="ERP",
                order_ref="ORD-1001",
                gross_amount=100.0,
                net_amount=97.5,
                status="BOOKED",
            )
        ]

        report = reconciler.reconcile_batch(
            gateway_txs=gtw,
            marketplace_txs=[],
            carrier_txs=[],
            erp_txs=erp,
        )

        assert report.total_orders_analyzed == 1
        assert report.matched_count == 1
        assert report.discrepancy_count == 0
        assert len(report.reconciliation_seal) == 64

    def test_missing_erp_discrepancy(self):
        reconciler = MultichannelReconciler()
        gtw = [
            ChannelTransaction(
                tx_id="tx_2",
                channel="STRIPE",
                order_ref="ORD-2002",
                gross_amount=250.0,
                fee_amount=5.0,
                net_amount=245.0,
                status="CAPTURED",
            )
        ]

        report = reconciler.reconcile_batch(
            gateway_txs=gtw,
            marketplace_txs=[],
            carrier_txs=[],
            erp_txs=[],  # Missing in ERP!
        )

        assert report.discrepancy_count == 1
        disc = report.discrepancies[0]
        assert disc.order_ref == "ORD-2002"
        assert disc.discrepancy_type == "MISSING_ERP_ENTRY"
        assert disc.amount_diff == 245.0
        assert "572000" in disc.suggested_adjusting_entry["debit"]


class TestM365ExcelGhost:
    def test_office_script_generation(self):
        ghost = M365ExcelGhost()
        script = ghost.generate_reconciliation_office_script(sheet_name="AuditQ1")

        assert script.script_name == "FormatReconciliationSheet.ts"
        assert "ExcelScript.Workbook" in script.typescript_code
        assert "AuditQ1" in script.typescript_code
        assert "setNumberFormatLocal" in script.typescript_code
        assert "DISCREPANCY" in script.typescript_code

    def test_dbt_model_generation(self):
        ghost = M365ExcelGhost()
        model = ghost.generate_dbt_reconciliation_model()

        assert model.model_name == "fct_multichannel_reconciliation"
        assert "materialized = 'incremental'" in model.sql_query
        assert "stg_stripe_transactions" in model.sql_query
        assert "stg_odoo_general_ledger" in model.sql_query


class TestMonthlyClosingAgent:
    def test_modelo_303_calculation(self):
        agent = MonthlyClosingAgent(company_cif="B-87654321", company_name="Iberian Retail Tech SL")
        invoices = [
            InvoiceRecord(
                invoice_id="INV-001",
                invoice_type="ISSUED",
                counterparty_nif="A-11111111",
                counterparty_name="Cliente A",
                base_amount=1000.0,
                vat_rate=0.21,
                vat_amount=210.0,
                date="2026-02-10",
            ),
            InvoiceRecord(
                invoice_id="INV-002",
                invoice_type="ISSUED",
                counterparty_nif="B-22222222",
                counterparty_name="Cliente B",
                base_amount=500.0,
                vat_rate=0.10,
                vat_amount=50.0,
                date="2026-02-15",
            ),
            InvoiceRecord(
                invoice_id="EXP-001",
                invoice_type="RECEIVED",
                counterparty_nif="C-33333333",
                counterparty_name="Proveedor Cloud",
                base_amount=400.0,
                vat_rate=0.21,
                vat_amount=84.0,
                date="2026-02-20",
            ),
        ]

        settlement = agent.compute_modelo_303(invoices, period="1T-2026")
        assert settlement.base_devengada_21 == 1000.0
        assert settlement.cuota_devengada_21 == 210.0
        assert settlement.base_devengada_10 == 500.0
        assert settlement.cuota_devengada_10 == 50.0
        assert settlement.total_cuota_devengada == 260.0
        assert settlement.total_cuota_soportada == 84.0
        # 260 - 84 = 176.0 EUR to pay
        assert settlement.resultado_autoliquidacion == 176.0
        assert len(settlement.submission_seal) == 64

    def test_modelo_111_calculation(self):
        agent = MonthlyClosingAgent(company_cif="B-87654321")
        payrolls = [
            {"employee": "Worker 1", "gross_salary": 2500.0, "irpf_withheld": 375.0},
            {"employee": "Worker 2", "gross_salary": 2000.0, "irpf_withheld": 280.0},
        ]
        pro_invoices = [
            InvoiceRecord(
                invoice_id="PROF-01",
                invoice_type="RECEIVED",
                counterparty_nif="12345678Z",
                counterparty_name="Abogado Fiscalista",
                base_amount=1000.0,
                vat_rate=0.21,
                vat_amount=210.0,
                retention_rate=0.15,
                retention_amount=150.0,
                date="2026-02-25",
            )
        ]

        settlement = agent.compute_modelo_111(payrolls, pro_invoices, period="1T-2026")
        assert settlement.trabajadores_count == 2
        assert settlement.trabajadores_retenciones == 655.0
        assert settlement.profesionales_retenciones == 150.0
        assert settlement.total_a_ingresar == 805.0
        assert len(settlement.submission_seal) == 64
