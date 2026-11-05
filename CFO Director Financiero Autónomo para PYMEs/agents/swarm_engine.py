"""Autonomous CFO Multi-Agent Swarm Engine.
Orchestrates the CFO Council using Swarms and Agency-Swarm design patterns.
"""

from __future__ import annotations

from typing import Any

from autonomo_cfo.agents.personas import (
    CFO_ORCHESTRATOR_PROMPT,
    GRC_SENTINEL_PROMPT,
    RISK_FRAUD_PROMPT,
    TAX_ACCOUNTANT_PROMPT,
)
from autonomo_cfo.compliance.cra_security import CRASecurityManager
from autonomo_cfo.compliance.nis2_audit import NIS2AuditManager
from autonomo_cfo.compliance.rgpd_vault import RGPDVault
from autonomo_cfo.hitl.approval_gate import ApprovalTicket, HITLApprovalGate
from autonomo_cfo.reporting.executive_report import (
    ExecutiveReportGenerator,
    FinancialKPIs,
)
from autonomo_cfo.tools.cash_flow_tool import CashFlowForecasterTool
from autonomo_cfo.tools.fraud_detector_tool import FraudDetectorTool
from autonomo_cfo.tools.invoice_ocr_tool import InvoiceOCRTool
from autonomo_cfo.tools.tax_ledger_tool import TaxLedgerTool


class AutonomoCFOEngine:
    """The central executive multi-agent engine for AUTONOMO CFO."""

    def __init__(
        self,
        tenant_id: str = "sme_corp_01",
        company_name: str = "Innovación & Crecimiento S.L.",
        model_name: str = "gpt-5.4",
        audit_manager: NIS2AuditManager | None = None,
        rgpd_vault: RGPDVault | None = None,
        hitl_gate: HITLApprovalGate | None = None,
    ):
        self.tenant_id = tenant_id
        self.company_name = company_name
        self.model_name = model_name

        # Compliance & Security infrastructure
        self.audit_mgr = audit_manager or NIS2AuditManager()
        self.rgpd_vault = rgpd_vault or RGPDVault()
        self.hitl_gate = hitl_gate or HITLApprovalGate(audit_mgr=self.audit_mgr)

        # Verified vendor registry: {cif: verified_iban}
        self.vendor_registry: dict[str, str] = {
            "B12345678": "ES9121000418450200051332",
            "A87654321": "ES0014650100402030405060",
        }
        # Recorded invoice history: {cif: [invoice_numbers]}
        self.invoice_history: dict[str, list[str]] = {
            "B12345678": ["INV-2026-001", "INV-2026-002"],
        }
        # Historical amounts: {cif: [amounts]}
        self.amount_history: dict[str, list[float]] = {
            "B12345678": [1200.0, 1250.0, 1180.0, 1300.0],
        }

        # Initialize Swarms Agent instances if swarms is installed and configured
        self._init_swarms_agents()

        # Audit initialization
        self.audit_mgr.record_event(
            tenant_id=self.tenant_id,
            action="CFO_ENGINE_INITIALIZED",
            actor="SYSTEM",
            payload={"company": self.company_name, "model": self.model_name},
        )

    def _init_swarms_agents(self) -> None:
        """Initializes Swarms Agent primitives if environment is configured."""
        try:
            from swarms import Agent

            self.swarms_cfo = Agent(
                agent_name="CFO_Executive",
                agent_description="Autonomous Chief Financial Officer overseeing capital and solvency.",
                system_prompt=CFO_ORCHESTRATOR_PROMPT,
                model_name=self.model_name,
                max_loops=1,
            )
            self.swarms_accountant = Agent(
                agent_name="Tax_Accountant",
                agent_description="Tax controller for OCR audit and AEAT compliance.",
                system_prompt=TAX_ACCOUNTANT_PROMPT,
                model_name=self.model_name,
                max_loops=1,
            )
            self.swarms_risk = Agent(
                agent_name="Risk_Analyst",
                agent_description="Quantitative fraud analyst and IBAN diversion hunter.",
                system_prompt=RISK_FRAUD_PROMPT,
                model_name=self.model_name,
                max_loops=1,
            )
            self.swarms_grc = Agent(
                agent_name="GRC_Sentinel",
                agent_description="Compliance sentinel enforcing NIS2, RGPD, and CRA regulations.",
                system_prompt=GRC_SENTINEL_PROMPT,
                model_name=self.model_name,
                max_loops=1,
            )
            self.has_live_swarms = True
        except (ImportError, RuntimeError, OSError, ValueError, TypeError):
            self.has_live_swarms = False

    def process_invoice_pipeline(self, raw_invoice_text: str) -> dict[str, Any]:
        """Full end-to-end processing pipeline for incoming invoices and receipts.

        Steps:
        1. CRA Input Sanitization: blocks prompt injections.
        2. RGPD PII Redaction: strips names, DNIs, phone numbers.
        3. Tax Accountant OCR Audit: extracts figures, validates math.
        4. Risk & Fraud Audit: checks IBAN diversion and duplicates.
        5. HITL Evaluation: locks transaction for human signature if risk >= 40 or amount >= 1,000€.
        6. NIS2 Immutable Audit Logging.
        """
        # Step 1: CRA Input Sanitization
        sanitized_text, is_safe, threats = CRASecurityManager.sanitize_input(raw_invoice_text)
        if not is_safe:
            incident = self.audit_mgr.create_incident(
                tenant_id=self.tenant_id,
                severity="HIGH",
                description=f"Prompt injection or malicious payload detected in invoice: {threats}",
            )
            return {
                "status": "REJECTED_SECURITY",
                "reason": "CRA Security Violation: Input contains prohibited patterns.",
                "incident_id": incident.incident_id,
                "threats": threats,
            }

        # Step 2: RGPD PII Redaction
        clean_text, pii_metrics = self.rgpd_vault.redact_pii(sanitized_text)

        # Step 3: Tax Accountant OCR Tool Execution
        ocr_tool = InvoiceOCRTool(invoice_raw_text=clean_text, tenant_id=self.tenant_id)
        ocr_res = ocr_tool.run()

        # Step 4: Risk & Fraud Tool Execution
        cif = ocr_res["vendor_cif"]
        known_iban = self.vendor_registry.get(cif)
        known_invoices = self.invoice_history.get(cif, [])
        known_amounts = self.amount_history.get(cif, [])

        fraud_tool = FraudDetectorTool(
            vendor_cif=cif,
            invoice_number=ocr_res["invoice_number"],
            invoice_amount=ocr_res["total_amount"],
            provided_iban=ocr_res["iban"],
            historical_vendor_iban=known_iban,
            historical_amounts=known_amounts,
            known_invoice_numbers=known_invoices,
        )
        fraud_res = fraud_tool.run()

        # Step 5: Decision Logic & HITL Gate
        requires_hitl = (
            fraud_res["requires_hitl_approval"]
            or ocr_res["total_amount"] >= 1000.0
            or not ocr_res["math_consistent"]
        )

        approval_ticket: ApprovalTicket | None = None
        if requires_hitl:
            hitl_reasons = []
            if fraud_res["flags"]:
                hitl_reasons.extend(fraud_res["flags"])
            if ocr_res["total_amount"] >= 1000.0:
                hitl_reasons.append(f"Amount {ocr_res['total_amount']}€ exceeds automated threshold (1,000€).")
            if not ocr_res["math_consistent"]:
                hitl_reasons.append("Invoice math inconsistency detected.")

            approval_ticket = self.hitl_gate.request_approval(
                tenant_id=self.tenant_id,
                action_type="PAYMENT_AUTHORIZATION",
                amount=ocr_res["total_amount"],
                beneficiary_iban=ocr_res["iban"],
                reason="; ".join(hitl_reasons),
            )
            decision_status = "PENDING_HUMAN_APPROVAL"
        else:
            # Register in verified history
            if cif in self.invoice_history:
                self.invoice_history[cif].append(ocr_res["invoice_number"])
                self.amount_history[cif].append(ocr_res["total_amount"])
            decision_status = "AUTOMATICALLY_APPROVED"

        # Step 6: Immutable NIS2 Audit Log
        event_payload = {
            "ocr": ocr_res,
            "fraud": fraud_res,
            "pii_redacted": pii_metrics,
            "decision": decision_status,
            "ticket_id": approval_ticket.ticket_id if approval_ticket else None,
        }
        audit_block = self.audit_mgr.record_event(
            tenant_id=self.tenant_id,
            action="INVOICE_PROCESSED",
            actor="AUTONOMO_CFO_ENGINE",
            payload=event_payload,
        )

        return {
            "status": decision_status,
            "invoice_data": ocr_res,
            "fraud_audit": fraud_res,
            "pii_metrics": pii_metrics,
            "hitl_ticket": approval_ticket.__dict__ if approval_ticket else None,
            "audit_block_hash": audit_block.block_hash,
            "audit_index": audit_block.index,
        }

    def generate_full_executive_report(
        self,
        current_liquidity: float,
        monthly_burn: float,
        working_capital: float,
        retained_earnings: float,
        ebit: float,
        equity: float,
        liabilities: float,
        sales: float,
        collected_vat: float,
        deductible_vat: float,
    ) -> dict[str, Any]:
        """Generates a complete executive board report with cash flow and tax forecasts."""
        # 1. Cash flow projection
        cf_tool = CashFlowForecasterTool(
            current_cash=current_liquidity,
            monthly_burn_rate=monthly_burn,
            expected_receivables_30d=sales * 0.4,
            expected_payables_30d=monthly_burn * 0.8,
        )
        cf_res = cf_tool.run()

        # 2. Tax calculations
        tax_tool = TaxLedgerTool(
            quarter="2T",
            collected_vat=collected_vat,
            deductible_vat=deductible_vat,
            withheld_irpf=monthly_burn * 0.05,
            net_ebitda=ebit,
        )
        tax_res = tax_tool.run()

        # 3. Financial KPIs and Altman Z'-Score
        total_assets = max(1.0, current_liquidity + working_capital)
        z_score, z_zone = ExecutiveReportGenerator.calculate_altman_z_prime(
            working_capital=working_capital,
            retained_earnings=retained_earnings,
            ebit=ebit,
            book_value_equity=equity,
            total_liabilities=liabilities,
            sales=sales,
            total_assets=total_assets,
        )

        quick_ratio = round(current_liquidity / max(1.0, liabilities * 0.5), 2)
        debt_to_equity = round(liabilities / max(1.0, equity), 2)

        kpis = FinancialKPIs(
            liquidity_eur=current_liquidity,
            monthly_burn_eur=monthly_burn,
            runway_months=cf_res["runway_months"],
            quick_ratio=quick_ratio,
            debt_to_equity=debt_to_equity,
            altman_z_prime=z_score,
            z_score_zone=z_zone,
            quarterly_tax_liability_eur=tax_res["total_mandatory_tax_reserve"],
        )

        recs = []
        if cf_res["runway_months"] < 6.0:
            recs.append(f"CRITICAL: Runway is {cf_res['runway_months']} months. Accelerate collections or trim OPEX.")
        if tax_res["total_mandatory_tax_reserve"] > (current_liquidity * 0.4):
            recs.append("TAX ALERT: Quarterly tax reserve exceeds 40% of liquid cash. Segregate funds immediately.")
        if z_zone != "SAFE":
            recs.append("SOLVENCY WARNING: Altman Z'-Score indicates heightened balance-sheet exposure.")

        nis2_ok = self.audit_mgr.verify_chain_integrity()
        markdown_doc = ExecutiveReportGenerator.generate_markdown_report(
            company_name=self.company_name,
            kpis=kpis,
            recommendations=recs,
            nis2_verified=nis2_ok,
            rgpd_redactions_count=12,
            pending_hitl_count=len([t for t in self.hitl_gate._tickets.values() if t.status == "PENDING"]),
        )

        return {
            "kpis": kpis.__dict__,
            "cash_flow": cf_res,
            "tax_reserve": tax_res,
            "nis2_integrity": nis2_ok,
            "markdown_report": markdown_doc,
        }
