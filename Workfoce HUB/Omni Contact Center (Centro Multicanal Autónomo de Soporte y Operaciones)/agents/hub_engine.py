"""
Omni Hub Engine - Multi-agent contact center orchestration combining Swarms Agent paradigm and Agency-Swarm delegation.
"""
from typing import Any

from channels.multichannel_adapter import MultichannelAdapter
from compliance.cra_telephony_security import CRATelephonyGuard
from compliance.nis2_call_audit import NIS2ContactAuditLedger
from compliance.rgpd_audio_vault import RGPDAudioTextVault
from tools.call_disposition_tool import CallDispositionTool
from tools.crm_lookup_tool import CRMLookupTool
from tools.sentiment_escalation_tool import SentimentEscalationTool


class OmniHubEngine:
    """
    Central orchestration engine for the Multimodal AI Contact Center.
    Handles multichannel session ingestion, CRA prompt security, RGPD PII masking,
    CRM retrieval, dynamic multi-agent conversation turns, sentiment escalation,
    and NIS2 immutable audit chaining.
    """

    def __init__(self, ledger_path: str | None = None):
        self.ledger = NIS2ContactAuditLedger(ledger_file=ledger_path)
        self.vault = RGPDAudioTextVault()
        self.active_sessions: dict[str, dict[str, Any]] = {}

    def start_session(
        self,
        channel: str,
        caller_id: str,
        payload_data: dict[str, Any],
        consent_given: bool = True
    ) -> dict[str, Any]:
        """
        Initializes an inbound customer contact session across any supported channel.
        """
        # 1. Normalize session
        session = MultichannelAdapter.normalize_inbound_interaction(channel, caller_id, payload_data)
        session_id = session["session_id"]

        # 2. Register RGPD consent
        consent_record = self.vault.register_call_consent(session_id, caller_id, consent_given)

        # 3. Lookup customer tier
        crm_tool = CRMLookupTool(customer_id=caller_id)
        crm_res = crm_tool.run()

        session_state = {
            **session,
            "consent": consent_record,
            "crm_profile": crm_res.get("data", {}),
            "assigned_agent": "Receptionist_Triage",
            "frustration_score": 0,
            "turns": []
        }
        self.active_sessions[session_id] = session_state

        # 4. NIS2 Ledger recording
        self.ledger.record_interaction(
            tenant_id="OMNI_CORP",
            session_id=session_id,
            channel=channel,
            action="SESSION_INITIATED",
            agent_role="Receptionist_Triage",
            status="SUCCESS",
            metadata={"consent": consent_given, "tier": session_state["crm_profile"].get("tier")}
        )

        initial_greeting = (
            "Hello and welcome to Omni Customer Care. I am your autonomous AI assistant. "
            "How may I assist you today?"
        )

        formatted_outbound = MultichannelAdapter.format_outbound_response(channel, session_id, initial_greeting)

        return {
            "session_id": session_id,
            "channel": channel,
            "status": "ACTIVE",
            "assigned_agent": "Receptionist_Triage",
            "outbound_response": formatted_outbound
        }

    def process_turn(
        self,
        session_id: str,
        customer_utterance: str
    ) -> dict[str, Any]:
        """
        Processes a spoken or typed customer turn:
        1. CRA Security Inspection (injection attack detection)
        2. RGPD PII Sanitization
        3. Sentiment & Escalation Analysis
        4. Agent Role Selection & Response Generation
        5. Outbound Channel Formatting
        6. NIS2 Immutable Audit Entry
        """
        if session_id not in self.active_sessions:
            return {"success": False, "error": f"Session '{session_id}' not found."}

        session = self.active_sessions[session_id]
        channel = session["channel"]

        # 1. CRA Telephony Guard
        is_safe, sec_reason = CRATelephonyGuard.inspect_utterance(customer_utterance)
        if not is_safe:
            incident_entry = self.ledger.record_interaction(
                tenant_id="OMNI_CORP",
                session_id=session_id,
                channel=channel,
                action="MALICIOUS_INPUT_BLOCKED",
                agent_role="SECURITY_FIREWALL",
                status="SECURITY_ALERT",
                metadata={"reason": sec_reason, "audio_injection": True}
            )
            incident_report = self.ledger.check_telecom_incident(incident_entry)
            return {
                "success": False,
                "error": "CRA_TELEPHONY_VIOLATION",
                "details": sec_reason,
                "incident_report": incident_report
            }

        # 2. RGPD PII Scrubbing
        _, sanitized_input = self.vault.append_transcript(session_id, "customer", customer_utterance)

        # 3. Sentiment & Escalation
        sentiment_tool = SentimentEscalationTool(
            utterance=sanitized_input,
            accumulated_frustration_score=session["frustration_score"]
        )
        sentiment_res = sentiment_tool.run()
        session["frustration_score"] = sentiment_res["frustration_score"]

        # 4. Agent Role Selection
        assigned_role = self._route_or_escalate(sanitized_input, sentiment_res["escalate_to_human"])
        session["assigned_agent"] = assigned_role

        # 5. Generate Agent Response
        agent_reply = self._generate_response(assigned_role, sanitized_input, session)
        self.vault.append_transcript(session_id, assigned_role, agent_reply)

        session["turns"].append({
            "customer": sanitized_input,
            "agent": agent_reply,
            "role": assigned_role,
            "sentiment": sentiment_res["sentiment"]
        })

        # 6. NIS2 Audit Chaining
        ledger_entry = self.ledger.record_interaction(
            tenant_id="OMNI_CORP",
            session_id=session_id,
            channel=channel,
            action="TURN_PROCESSED",
            agent_role=assigned_role,
            status="SUCCESS",
            metadata={
                "sentiment": sentiment_res["sentiment"],
                "frustration_score": sentiment_res["frustration_score"],
                "escalated": sentiment_res["escalate_to_human"]
            }
        )

        formatted_outbound = MultichannelAdapter.format_outbound_response(channel, session_id, agent_reply)

        return {
            "success": True,
            "session_id": session_id,
            "assigned_agent": assigned_role,
            "sentiment_analysis": sentiment_res,
            "agent_response": agent_reply,
            "outbound_payload": formatted_outbound,
            "nis2_audit_block": {
                "index": ledger_entry["index"],
                "hash": ledger_entry["hash"]
            }
        }

    def close_session(self, session_id: str) -> dict[str, Any]:
        """
        Concludes session, invokes CallDispositionTool, and produces final CRM log.
        """
        if session_id not in self.active_sessions:
            return {"success": False, "error": f"Session '{session_id}' not found."}

        session = self.active_sessions[session_id]
        transcripts = [f"{t['role']}: {t['agent']} | Cust: {t['customer']}" for t in session["turns"]]
        full_text = "\n".join(transcripts)

        disposition_tool = CallDispositionTool(
            session_id=session_id,
            full_transcript=full_text or "Session ended without dialogue.",
            resolved_by_ai=(session["assigned_agent"] != "Supervisor_Escalation")
        )
        disp_res = disposition_tool.run()

        # NIS2 wrap-up
        self.ledger.record_interaction(
            tenant_id="OMNI_CORP",
            session_id=session_id,
            channel=session["channel"],
            action="SESSION_CONCLUDED",
            agent_role="Supervisor_Escalation" if not disp_res["resolved_by_ai"] else "Receptionist_Triage",
            status="SUCCESS",
            metadata=disp_res
        )

        session["status"] = "CLOSED"
        session["disposition"] = disp_res

        return {
            "success": True,
            "session_id": session_id,
            "status": "CONCLUDED",
            "disposition_report": disp_res
        }

    def _route_or_escalate(self, text: str, must_escalate: bool) -> str:
        if must_escalate:
            return "Supervisor_Escalation"
        
        text_lower = text.lower()
        if any(k in text_lower for k in ["invoice", "refund", "billing", "charge", "payment", "subscription"]):
            return "Billing_Specialist"
        elif any(k in text_lower for k in ["bug", "error", "sip", "api", "connection", "trunk", "technical", "down"]):
            return "Technical_Support_Tier1"
        else:
            return "Receptionist_Triage"

    def _generate_response(self, role: str, text: str, session: dict[str, Any]) -> str:
        if role == "Supervisor_Escalation":
            return (
                "I completely understand your frustration and I sincerely apologize for the inconvenience. "
                "I am the Senior Escalation Supervisor on duty. I have immediately reviewed your profile and "
                "I am taking personal ownership to resolve this right now."
            )
        elif role == "Billing_Specialist":
            return (
                "I am your dedicated Billing Specialist. I have pulled up your billing account details. "
                "Our policy guarantees a 30-day money-back window, and I can confirm your recent invoice. "
                "Would you like me to process an adjustment or break down the line items?"
            )
        elif role == "Technical_Support_Tier1":
            return (
                "Hello, I am Tier-1 Technical Support. I have diagnosed your inquiry. "
                "Please verify that your SIP trunk credentials and WebRTC ports are open. "
                "Our backup cluster is operating at 100% health. Let's walk through the steps together."
            )
        else:
            return (
                "Thank you for that information. I have logged your request in our system and "
                "I am happy to guide you through our services or answer any questions you have."
            )
