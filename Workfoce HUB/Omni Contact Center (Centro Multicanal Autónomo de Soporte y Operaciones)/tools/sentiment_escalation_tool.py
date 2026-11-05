"""
Sentiment & Escalation Tool - Evaluates customer emotional state and triggers supervisor transfer.
"""
from typing import Any, ClassVar

from pydantic import Field

from tools.base import BaseTool


class SentimentEscalationTool(BaseTool):
    """
    Real-time sentiment evaluation and supervisor escalation determination during a contact session.
    """
    utterance: str = Field(..., description="Customer utterance or message")
    accumulated_frustration_score: int = Field(default=0, description="Running frustration score (0 to 100)")

    FRUSTRATION_KEYWORDS: ClassVar[list[str]] = [
        "angry", "furious", "unacceptable", "lawyer", "demand", "cancel my subscription",
        "scam", "ridiculous", "talk to human", "real person", "manager", "horrible service",
        "incompetent", "demand a refund", "fraud"
    ]

    POSITIVE_KEYWORDS: ClassVar[list[str]] = [
        "thank you", "great", "helpful", "perfect", "resolved", "awesome", "appreciate"
    ]

    def run(self) -> dict[str, Any]:
        text_lower = self.utterance.lower()
        
        frustration_hits = [w for w in self.FRUSTRATION_KEYWORDS if w in text_lower]
        positive_hits = [w for w in self.POSITIVE_KEYWORDS if w in text_lower]

        delta = (len(frustration_hits) * 30) - (len(positive_hits) * 20)
        new_score = max(0, min(100, self.accumulated_frustration_score + delta))

        # Sentiment classification
        if new_score >= 60:
            sentiment = "NEGATIVE_CRITICAL"
        elif new_score >= 30:
            sentiment = "NEGATIVE_MILD"
        elif positive_hits:
            sentiment = "POSITIVE"
        else:
            sentiment = "NEUTRAL"

        escalate_to_human = new_score >= 60 or "talk to human" in text_lower or "manager" in text_lower

        return {
            "success": True,
            "sentiment": sentiment,
            "frustration_score": new_score,
            "detected_triggers": frustration_hits,
            "escalate_to_human": escalate_to_human,
            "recommended_action": "TRANSFER_TO_SUPERVISOR" if escalate_to_human else "CONTINUE_AUTOMATION"
        }
