"""M365 Excel Automation Ghost & dbt Transformation Synthesizer.

Provides two key enterprise integration capabilities:
1. Generates typed TypeScript Office Scripts for zero-install Excel automation in Microsoft 365.
2. Generates dbt (data build tool) SQL models for cloud data warehouses (Snowflake, BigQuery, Postgres).
"""

from __future__ import annotations

from pydantic import BaseModel


class GeneratedOfficeScript(BaseModel):
    script_name: str
    target_sheet: str
    typescript_code: str
    purpose: str


class GeneratedDBTModel(BaseModel):
    model_name: str
    materialized: str  # table, view, incremental
    sql_query: str
    description: str


class M365ExcelGhost:
    """Enterprise code generator for Excel Office Scripts and dbt transformations."""

    def generate_reconciliation_office_script(self, sheet_name: str = "Reconciliation") -> GeneratedOfficeScript:
        """Generates typed TypeScript Office Script that applies accounting rules and highlights discrepancies."""
        ts_code = f"""/**
 * Office Script: Automated Multichannel Reconciliation Formatter
 * Applied to Worksheet: {sheet_name}
 */
function main(workbook: ExcelScript.Workbook) {{
    const sheet = workbook.getWorksheet("{sheet_name}") ?? workbook.getActiveWorksheet();
    const usedRange = sheet.getUsedRange();

    if (!usedRange) {{
        console.log("Empty sheet, skipping execution.");
        return;
    }}

    // 1. Format Header
    const headerRange = sheet.getRange("A1:G1");
    headerRange.getFormat().getFill().setColor("#003366");
    headerRange.getFormat().getFont().setColor("#FFFFFF");
    headerRange.getFormat().getFont().setBold(true);

    // 2. Apply Currency Formatting to Amount Columns (D, E, F)
    const rowCount = usedRange.getRowCount();
    if (rowCount > 1) {{
        sheet.getRange(`D2:F${{rowCount}}`).setNumberFormatLocal("#,##0.00 €");
    }}

    // 3. Conditional Formatting: Highlight Discrepancies in Red
    const statusRange = sheet.getRange(`G2:G${{rowCount}}`);
    const condFormat = statusRange.addConditionalFormat(ExcelScript.ConditionalFormatType.cellValue);
    const rule = condFormat.getCellValue();
    rule.setRule({{
        formula1: '"DISCREPANCY"',
        operator: ExcelScript.ConditionalCellValueOperator.equalTo
    }});
    rule.getFormat().getFill().setColor("#FFC7CE");
    rule.getFormat().getFont().setColor("#9C0006");

    // 4. Auto-fit Columns
    usedRange.getFormat().autofitColumns();
    console.log("Reconciliation formatting applied successfully.");
}}
"""
        return GeneratedOfficeScript(
            script_name="FormatReconciliationSheet.ts",
            target_sheet=sheet_name,
            typescript_code=ts_code,
            purpose="Applies corporate styling, EUR formatting, and red highlights to unresolved discrepancies.",
        )

    def generate_dbt_reconciliation_model(self) -> GeneratedDBTModel:
        """Generates a dbt SQL transformation model joining Stripe, ERP, and Carrier data."""
        sql = """{{
  config(
    materialized = 'incremental',
    unique_key = 'order_ref',
    schema = 'finance'
  )
}}

with gateway_sales as (
    select
        order_ref,
        sum(gross_amount) as gateway_gross,
        sum(fee_amount) as gateway_fees,
        sum(net_amount) as gateway_net,
        max(captured_at) as gateway_timestamp
    from {{ ref('stg_stripe_transactions') }}
    {% if is_incremental() %}
    where captured_at >= (select max(gateway_timestamp) from {{ this }})
    {% endif %}
    group by 1
),

erp_entries as (
    select
        order_ref,
        sum(debit_amount) as erp_booked_amount,
        max(entry_date) as erp_booking_date
    from {{ ref('stg_odoo_general_ledger') }}
    group by 1
)

select
    g.order_ref,
    g.gateway_gross,
    g.gateway_fees,
    g.gateway_net,
    coalesce(e.erp_booked_amount, 0.0) as erp_booked_amount,
    round(g.gateway_net - coalesce(e.erp_booked_amount, 0.0), 2) as discrepancy_amount,
    case
        when e.erp_booked_amount is null then 'MISSING_ERP_ENTRY'
        when abs(g.gateway_net - e.erp_booked_amount) > 0.01 then 'AMOUNT_MISMATCH'
        else 'RECONCILED'
    end as reconciliation_status,
    current_timestamp as audited_at
from gateway_sales g
left join erp_entries e on g.order_ref = e.order_ref
"""
        return GeneratedDBTModel(
            model_name="fct_multichannel_reconciliation",
            materialized="incremental",
            sql_query=sql,
            description="Incremental reconciliation model joining Stripe gateway with ERP general ledger.",
        )
