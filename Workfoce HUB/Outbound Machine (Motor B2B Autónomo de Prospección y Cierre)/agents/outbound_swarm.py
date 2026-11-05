"""Autonomous Outbound Multi-Agent Swarm Engine.
Orchestrates ICP discovery, enrichment, copywriting, compliance, dispatch, and human handoffs.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

import sys
from pathlib import Path
_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from compliance.cra_outbound_security import CRAOutboundSecurityManager
from compliance.nis2_dispatch_audit import NIS2DispatchAuditManager
from compliance.rgpd_optout_manager import RGPDOptOutManager
from sequences.cadence_manager import OutboundCadenceManager, ProspectCadenceState
from tools.email_dispatcher_tool import EmailDispatcherTool
from tools.icp_persona_tool import ICPPersonaTool
from tools.lead_enricher_tool import LeadEnricherTool
from tools.pitch_generator_tool import PitchGeneratorTool
from agents.personas import (
    OBJECTION_HANDLER_PROMPT,
    RESEARCHER_PROMPT,
    SALES_COPYWRITER_PROMPT,
    SDR_DIRECTOR_PROMPT,
)


class OutboundSwarmEngine:
    """Central autonomous engine for the OUTBOUND MACHINE."""

    def __init__(
        self,
        tenant_id: str = "tenant_outbound_01",
        sender_name: str = "José Luis Rodríguez Casal",
        sender_email: str = "josecasal.tech@gmail.com",
        model_name: str = "gpt-5.4",
        audit_manager: Optional[NIS2DispatchAuditManager] = None,
        optout_manager: Optional[RGPDOptOutManager] = None,
        cadence_manager: Optional[OutboundCadenceManager] = None,
    ):
        self.tenant_id = tenant_id
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.model_name = model_name

        self.audit_mgr = audit_manager or NIS2DispatchAuditManager()
        self.optout_mgr = optout_manager or RGPDOptOutManager()
        self.cadence_mgr = cadence_manager or OutboundCadenceManager()

        self._init_swarms_agents()

    def _init_swarms_agents(self) -> None:
        """Initializes Swarms Agent primitives if environment is configured."""
        try:
            from swarms import Agent

            self.swarms_sdr = Agent(
                agent_name="SDR_Director",
                agent_description="Autonomous Outbound Lead Generation Director.",
                system_prompt=SDR_DIRECTOR_PROMPT,
                model_name=self.model_name,
                max_loops=1,
            )
            self.swarms_researcher = Agent(
                agent_name="Tech_Researcher",
                agent_description="Deep technical analyst and company gap investigator.",
                system_prompt=RESEARCHER_PROMPT,
                model_name=self.model_name,
                max_loops=1,
            )
            self.swarms_copywriter = Agent(
                agent_name="Outbound_Copywriter",
                agent_description="B2B sales copywriter crafting hyper-personalized emails.",
                system_prompt=SALES_COPYWRITER_PROMPT,
                model_name=self.model_name,
                max_loops=1,
            )
            self.swarms_objection = Agent(
                agent_name="Objection_Handler",
                agent_description="Consultative objection solver and SDR human handoff trigger.",
                system_prompt=OBJECTION_HANDLER_PROMPT,
                model_name=self.model_name,
                max_loops=1,
            )
            self.has_live_swarms = True
        except Exception:
            self.has_live_swarms = False

    def process_prospect_outbound(
        self,
        company_raw_name: str,
        industry_sector: str,
        website_url: Optional[str] = None,
        contact_name: Optional[str] = None,
        contact_email: Optional[str] = None,
        decision_maker_role: str = "CTO",
        notes_or_snippet: Optional[str] = None,
        dry_run: bool = True,
        campaign_id: str = "camp_q4_ai_grc",
    ) -> Dict[str, Any]:
        """Full end-to-end outbound pipeline execution for a single prospect company.

        Pipeline:
        1. CRA Input Sanitization: filters malicious prompt injections in notes/snippets.
        2. ICP Persona Qualification: scores the company against target profile.
        3. Lead Enrichment: normalizes corporate name, infers domain and corporate email.
        4. RGPD Check: verifies recipient against suppression Robinson list.
        5. Personalized Pitch Generation: crafts tailored copy matching role & technical gap.
        6. CRA Quality Review: checks subject line and body against anti-spam/anti-phishing rules.
        7. Dispatch & Cadence Enrollment: delivers email or draft, logs in NIS2 audit ledger.
        """
        # Step 1: CRA Input Sanitization
        raw_input = f"{company_raw_name} {notes_or_snippet or ''}"
        sanitized_input, is_safe, threats = CRAOutboundSecurityManager.sanitize_prospect_input(raw_input)
        if not is_safe:
            return {
                "status": "REJECTED_SECURITY",
                "reason": "CRA Violation: Input contains prohibited prompt injection patterns.",
                "threats": threats,
            }

        # Step 2: ICP Qualification
        icp_tool = ICPPersonaTool(
            company_name=company_raw_name,
            industry_sector=industry_sector,
            target_decision_maker_role=decision_maker_role,
        )
        icp_res = icp_tool.run()
        if not icp_res["is_marketable"]:
            return {
                "status": "DISQUALIFIED_LOW_ICP",
                "icp_score": icp_res["qualification_score"],
                "reasons": icp_res["reasons"],
            }

        # Step 3: Lead Enrichment
        enricher_tool = LeadEnricherTool(
            company_raw_name=company_raw_name,
            website_url=website_url,
            known_contact_name=contact_name,
            notes_or_scraped_snippet=notes_or_snippet,
        )
        enrich_res = enricher_tool.run()

        target_email = contact_email or enrich_res["inferred_email_patterns"][0]
        clean_company = enrich_res["clean_company_name"]

        # Step 4: RGPD Suppression Check
        if self.optout_mgr.is_suppressed(target_email):
            return {
                "status": "SUPPRESSED_OPTOUT",
                "recipient": target_email,
                "message": "Lead is registered in suppression list per RGPD Art. 21.",
            }

        # Step 5: Pitch Generation
        trigger_gap = f"automatización de pipelines en su stack {', '.join(enrich_res['detected_tech_stack'])}" if enrich_res["detected_tech_stack"] else "modernización de flujos y cumplimiento NIS2/RGPD"
        pitch_tool = PitchGeneratorTool(
            company_name=clean_company,
            sector=industry_sector,
            decision_maker_role=decision_maker_role,
            contact_name=contact_name,
            specific_trigger_or_gap=trigger_gap,
            sender_name=self.sender_name,
        )
        pitch_res = pitch_tool.run()

        # Step 6: Dispatch & NIS2 Logging
        dispatcher = EmailDispatcherTool(
            recipient_email=target_email,
            subject=pitch_res["subject"],
            html_body=pitch_res["html_body"],
            sender_email=self.sender_email,
            sender_display_name=self.sender_name,
            campaign_id=campaign_id,
            tenant_id=self.tenant_id,
            dry_run=dry_run,
            optout_manager=self.optout_mgr,
            audit_manager=self.audit_mgr,
        )
        dispatch_res = dispatcher.run()

        # Step 7: Cadence Enrollment
        prospect_id = f"PRSP-{uuid.uuid4().hex[:8].upper()}"
        if dispatch_res["status"] == "SUCCESS":
            self.cadence_mgr.enroll_prospect(
                prospect_id=prospect_id,
                email=target_email,
                company=clean_company,
            )

        return {
            "status": dispatch_res["status"],
            "prospect_id": prospect_id,
            "company": clean_company,
            "recipient_email": target_email,
            "icp_qualification": icp_res,
            "enrichment": enrich_res,
            "pitch": pitch_res,
            "dispatch": dispatch_res,
        }

    def trigger_human_sdr_handoff(
        self,
        prospect_id: str,
        prospect_email: str,
        company_name: str,
        incoming_reply_text: str,
    ) -> Dict[str, Any]:
        """Escalates warm lead to human SDR when positive intent or questions are received."""
        # 1. Update cadence state
        self.cadence_mgr.record_reply_or_interest(prospect_id)

        # 2. Analyze reply sentiment and intent
        lower_reply = incoming_reply_text.lower()
        is_meeting_request = any(kw in lower_reply for kw in ["llamada", "reunión", "demo", "calendly", "jueves", "viernes", "agendar", "call"])
        is_optout = any(kw in lower_reply for kw in ["baja", "borrar", "no me interesa", "unsubscribe", "quitar"])

        if is_optout:
            self.optout_mgr.add_opt_out(prospect_email)
            self.cadence_mgr.record_opt_out(prospect_id)
            self.audit_mgr.record_dispatch(
                tenant_id=self.tenant_id,
                campaign_id="inbound_reply",
                recipient_email=prospect_email,
                action="OPTOUT_HONORED",
                payload={"reply": incoming_reply_text},
            )
            return {
                "action": "OPTOUT_REGISTERED",
                "prospect_id": prospect_id,
                "message": "Lead permanently removed from outreach lists per RGPD Art. 21.",
            }

        # 3. Log NIS2 Handoff Audit Event
        audit_block = self.audit_mgr.record_dispatch(
            tenant_id=self.tenant_id,
            campaign_id="inbound_reply",
            recipient_email=prospect_email,
            action="HANDOFF_ESCALATED",
            payload={"reply_text": incoming_reply_text, "meeting_requested": is_meeting_request},
        )

        brief = {
            "handoff_id": f"HANDOFF-{uuid.uuid4().hex[:8].upper()}",
            "prospect_id": prospect_id,
            "company_name": company_name,
            "prospect_email": prospect_email,
            "reply_snippet": incoming_reply_text,
            "meeting_intent_detected": is_meeting_request,
            "recommended_next_action": "Schedule 15-min discovery call via Calendar link" if is_meeting_request else "Send 2-bullet tailored response addressing specific inquiry",
            "audit_hash": audit_block.block_hash,
        }
        return {"action": "HANDOFF_SUCCESS", "brief": brief}
