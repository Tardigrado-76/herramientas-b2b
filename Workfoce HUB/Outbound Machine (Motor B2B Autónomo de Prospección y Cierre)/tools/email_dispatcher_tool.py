"""Email Dispatcher Tool with Rate Limiting and Regulatory Safeguards.
Enforces Robinson suppression checks, CRA anti-abuse validation, and NIS2 audit recording.
"""

from __future__ import annotations

import email.utils
import smtplib
import ssl
import time
from email.message import EmailMessage
from typing import Any, Dict, Optional
from pydantic import Field

import sys
from pathlib import Path
_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from tools.base import BaseTool
from compliance.cra_outbound_security import CRAOutboundSecurityManager
from compliance.nis2_dispatch_audit import NIS2DispatchAuditManager
from compliance.rgpd_optout_manager import RGPDOptOutManager


class EmailDispatcherTool(BaseTool):
    """Dispatches cold outreach emails via SMTP with compliance filters and rate-limiting."""

    recipient_email: str = Field(..., description="Target business email address")
    subject: str = Field(..., description="Subject line of the email")
    html_body: str = Field(..., description="HTML content of the message")
    sender_email: str = Field(default="outbound@quantigrade.ai", description="Verified sender address")
    sender_display_name: str = Field(default="José Luis Rodríguez Casal", description="Display name for header")
    reply_to: str = Field(default="josecasal.tech@gmail.com", description="Direct reply-to address")
    campaign_id: str = Field(default="camp_q4_enterprise", description="Campaign identifier")
    tenant_id: str = Field(default="sme_01", description="Tenant company identifier")
    dry_run: bool = Field(default=True, description="When True, simulates dispatch and logs without opening SMTP socket")
    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP server host")
    smtp_port: int = Field(default=587, description="SMTP server port")
    smtp_user: Optional[str] = Field(None, description="SMTP username")
    smtp_password: Optional[str] = Field(None, description="SMTP password")
    optout_manager: Optional[Any] = Field(None, description="Optional injected RGPDOptOutManager")
    audit_manager: Optional[Any] = Field(None, description="Optional injected NIS2DispatchAuditManager")

    def run(self) -> Dict[str, Any]:
        optout_mgr = self.optout_manager or RGPDOptOutManager()
        audit_mgr = self.audit_manager or NIS2DispatchAuditManager()

        # 1. RGPD Suppression / Robinson Check
        if optout_mgr.is_suppressed(self.recipient_email):
            audit_mgr.record_dispatch(
                tenant_id=self.tenant_id,
                campaign_id=self.campaign_id,
                recipient_email=self.recipient_email,
                action="BLOCKED_BY_OPTOUT",
                payload={"reason": "Recipient previously exercised Right of Opposition (Robinson List)."},
            )
            return {
                "status": "BLOCKED_OPTOUT",
                "recipient": self.recipient_email,
                "message": "Recipient has opted out; outreach cancelled per RGPD Art. 21.",
            }

        # 2. CRA Quality and Anti-Phishing Guard
        is_safe_copy, warnings = CRAOutboundSecurityManager.validate_outbound_pitch(
            subject=self.subject,
            body=self.html_body,
            is_first_contact=True,
        )
        if not is_safe_copy:
            return {
                "status": "REJECTED_CRA_HYGIENE",
                "recipient": self.recipient_email,
                "warnings": warnings,
            }

        # 3. Append RGPD Legal Footer with 1-click Unsubscribe
        final_html = optout_mgr.append_legal_footer(
            html_body=self.html_body,
            recipient_email=self.recipient_email,
        )

        # 4. Message Assembly
        msg = EmailMessage()
        msg["Subject"] = self.subject
        msg["From"] = email.utils.formataddr((self.sender_display_name, self.sender_email))
        msg["To"] = self.recipient_email
        msg["Reply-To"] = self.reply_to
        msg["Message-ID"] = email.utils.make_msgid(domain=self.sender_email.split("@")[-1])
        msg["Date"] = email.utils.formatdate(localtime=True)
        msg.set_content("Please enable HTML viewing for this message.")
        msg.add_alternative(final_html, subtype="html")

        # 5. Dispatch or Dry-run
        dispatch_success = False
        error_msg = None
        if self.dry_run:
            dispatch_success = True
            time.sleep(0.05)  # Simulate small delay
        else:
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    if self.smtp_user and self.smtp_password:
                        server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
                dispatch_success = True
            except Exception as e:
                dispatch_success = False
                error_msg = str(e)

        # 6. Immutable NIS2 Audit Log
        action_name = "DISPATCHED" if dispatch_success else "DISPATCH_FAILED"
        audit_block = audit_mgr.record_dispatch(
            tenant_id=self.tenant_id,
            campaign_id=self.campaign_id,
            recipient_email=self.recipient_email,
            action=action_name,
            payload={
                "subject": self.subject,
                "dry_run": self.dry_run,
                "error": error_msg,
            },
            metadata={"dry_run": self.dry_run},
        )

        return {
            "status": "SUCCESS" if dispatch_success else "FAILED",
            "recipient": self.recipient_email,
            "dry_run": self.dry_run,
            "audit_hash": audit_block.block_hash,
            "error": error_msg,
        }
