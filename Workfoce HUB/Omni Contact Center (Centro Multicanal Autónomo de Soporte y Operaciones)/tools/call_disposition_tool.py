"""
Call Disposition & Wrap-Up Tool - Summarizes interaction, generates CRM tags, and records CSAT.
"""
import time
from typing import Any, ClassVar

from pydantic import Field

from tools.base import BaseTool


class CallDispositionTool(BaseTool):
    """
    Finalizes the contact session, tags disposition category, and produces the CRM summary record.
    """
    session_id: str = Field(..., description="Unique session ID")
    full_transcript: str = Field(..., description="Full sanitized interaction transcript")
    final_sentiment: str = Field(default="NEUTRAL", description="POSITIVE, NEUTRAL, NEGATIVE_MILD, NEGATIVE_CRITICAL")
    resolved_by_ai: bool = Field(default=True, description="Whether the inquiry was resolved autonomously")

    DISPOSITION_CODES: ClassVar[list[str]] = [
        "BILLING_INQUIRY_RESOLVED",
        "TECHNICAL_SUPPORT_RESOLVED",
        "SUBSCRIPTION_CANCELED",
        "ESCALATED_TO_HUMAN_TIER_2",
        "INFORMATION_PROVIDED",
        "COMPLAINT_LOGGED"
    ]

    def run(self) -> dict[str, Any]:
        transcript_lower = self.full_transcript.lower()
        
        # Categorize disposition
        if not self.resolved_by_ai or "transfer_to_supervisor" in transcript_lower:
            disposition = "ESCALATED_TO_HUMAN_TIER_2"
        elif "refund" in transcript_lower or "invoice" in transcript_lower or "billing" in transcript_lower:
            disposition = "BILLING_INQUIRY_RESOLVED"
        elif "bug" in transcript_lower or "api" in transcript_lower or "error" in transcript_lower:
            disposition = "TECHNICAL_SUPPORT_RESOLVED"
        elif "cancel" in transcript_lower:
            disposition = "SUBSCRIPTION_CANCELED"
        else:
            disposition = "INFORMATION_PROVIDED"

        # Executive summary
        summary = (
            f"Customer session {self.session_id} concluded with disposition {disposition}. "
            f"Sentiment: {self.final_sentiment}. "
            f"Autonomous resolution: {self.resolved_by_ai}."
        )

        return {
            "success": True,
            "session_id": self.session_id,
            "disposition_code": disposition,
            "resolved_by_ai": self.resolved_by_ai,
            "summary": summary,
            "closed_at": time.time()
        }
