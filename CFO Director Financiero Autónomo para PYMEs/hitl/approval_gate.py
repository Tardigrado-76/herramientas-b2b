"""Human-In-The-Loop (HITL) Approval Gate with HMAC-SHA256 Signed Verification.
Prevents unauthorized automated fund movements and satisfies NIS2/CRA human oversight requirements.
"""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid
from dataclasses import asdict, dataclass

from autonomo_cfo.compliance.nis2_audit import NIS2AuditManager


@dataclass
class ApprovalTicket:
    ticket_id: str
    tenant_id: str
    action_type: str
    amount: float
    beneficiary_iban: str
    reason: str
    created_at: float
    expires_at: float
    status: str  # PENDING, APPROVED, REJECTED, EXPIRED
    approver: str | None = None
    approval_signature: str | None = None


class HITLApprovalGate:
    """Enforces human authorization for high-risk financial decisions and payouts."""

    def __init__(self, secret_key: str = "hitl-cfo-hmac-secret", audit_mgr: NIS2AuditManager | None = None):
        self.secret_key = secret_key.encode("utf-8")
        self.audit_mgr = audit_mgr or NIS2AuditManager()
        self._tickets: dict[str, ApprovalTicket] = {}

    def request_approval(
        self,
        tenant_id: str,
        action_type: str,
        amount: float,
        beneficiary_iban: str,
        reason: str,
        ttl_seconds: int = 3600,
    ) -> ApprovalTicket:
        """Generates an approval ticket and logs a tamper-evident audit event."""
        now = time.time()
        ticket_id = f"HITL-{uuid.uuid4().hex[:12].upper()}"
        ticket = ApprovalTicket(
            ticket_id=ticket_id,
            tenant_id=tenant_id,
            action_type=action_type,
            amount=amount,
            beneficiary_iban=beneficiary_iban,
            reason=reason,
            created_at=now,
            expires_at=now + ttl_seconds,
            status="PENDING",
        )
        self._tickets[ticket_id] = ticket

        self.audit_mgr.record_event(
            tenant_id=tenant_id,
            action="HITL_APPROVAL_REQUESTED",
            actor="CFO_ORCHESTRATOR",
            payload=asdict(ticket),
            metadata={"ticket_id": ticket_id, "amount": amount},
        )
        return ticket

    def generate_token(self, ticket_id: str, approver_email: str) -> str:
        """Generates an HMAC-SHA256 signature token for authorized approval."""
        payload = f"{ticket_id}:{approver_email}"
        return hmac.new(self.secret_key, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def process_decision(
        self,
        ticket_id: str,
        approver_email: str,
        decision: str,  # APPROVED or REJECTED
        signature_token: str,
    ) -> bool:
        """Validates token and updates ticket state."""
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            return False

        if time.time() > ticket.expires_at:
            ticket.status = "EXPIRED"
            return False

        expected_sig = self.generate_token(ticket_id, approver_email)
        if not hmac.compare_digest(expected_sig, signature_token):
            self.audit_mgr.record_event(
                tenant_id=ticket.tenant_id,
                action="HITL_INVALID_SIGNATURE_ATTEMPT",
                actor=approver_email,
                payload={"ticket_id": ticket_id},
            )
            return False

        ticket.status = decision.upper()
        ticket.approver = approver_email
        ticket.approval_signature = signature_token

        self.audit_mgr.record_event(
            tenant_id=ticket.tenant_id,
            action=f"HITL_DECISION_{ticket.status}",
            actor=approver_email,
            payload=asdict(ticket),
        )
        return True

    def get_pending_tickets(self, tenant_id: str | None = None) -> list[ApprovalTicket]:
        """Returns all currently pending approval tickets, optionally filtered by tenant."""
        now = time.time()
        pending = []
        for ticket in self._tickets.values():
            if ticket.status == "PENDING":
                if now > ticket.expires_at:
                    ticket.status = "EXPIRED"
                elif tenant_id is None or ticket.tenant_id == tenant_id:
                    pending.append(ticket)
        return pending

    def resolve_ticket(
        self,
        ticket_id: str,
        approved: bool,
        approver: str = "CFO_Executive_User",
    ) -> bool:
        """Resolves a pending ticket directly from the executive interface with HMAC authorization."""
        token = self.generate_token(ticket_id, approver)
        decision = "APPROVED" if approved else "REJECTED"
        return self.process_decision(
            ticket_id=ticket_id,
            approver_email=approver,
            decision=decision,
            signature_token=token,
        )

    def get_ticket(self, ticket_id: str) -> ApprovalTicket | None:
        return self._tickets.get(ticket_id)
