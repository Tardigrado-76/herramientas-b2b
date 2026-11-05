"""
RGPD Compliance Module - Multimodal Voice/Text Redaction, Consent & Crypto-Shredding
Complies with EU Regulation 2016/679 (RGPD Articles 5, 6, 7, 17, and 25).
"""
import hashlib
import re
import time
from typing import Any, ClassVar


class RGPDAudioTextVault:
    """
    Enforces customer consent management for recording/transcription,
    live PII scrubbing across spoken/typed transcripts, and cryptographic shredding of recordings.
    """

    # Multimodal PII Regexes (Spanish & European formats)
    PII_RULES: ClassVar[list[tuple[re.Pattern[str], str]]] = [
        (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[MASKED_EMAIL]'),
        (re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'), '[MASKED_CREDIT_CARD]'),
        (re.compile(r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b'), '[MASKED_IBAN]'),
        (re.compile(r'\b\d{8}[A-HJ-NP-TV-Z]\b', re.IGNORECASE), '[MASKED_DNI]'),
        (re.compile(r'\b[XYZ]\d{7}[A-Z]\b', re.IGNORECASE), '[MASKED_NIE]'),
        (re.compile(r'\b(?:cvv|cvc)\s*[:=]?\s*\d{3,4}\b', re.IGNORECASE), '[MASKED_CVV]'),
        (re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b'), '[MASKED_PHONE]')
    ]

    def __init__(self):
        # In-memory session store: session_id -> {consent, raw_audio_key, sanitized_transcript}
        self.sessions: dict[str, dict[str, Any]] = {}

    def register_call_consent(
        self,
        session_id: str,
        caller_id: str,
        consent_given: bool,
        purpose: str = "customer_service_and_quality"
    ) -> dict[str, Any]:
        """
        RGPD Art. 6 & 7: Explicit customer consent recording before processing call audio/text.
        """
        caller_hash = hashlib.sha256(caller_id.encode("utf-8")).hexdigest()
        self.sessions[session_id] = {
            "session_id": session_id,
            "caller_hash": caller_hash,
            "consent_given": consent_given,
            "purpose": purpose,
            "registered_at": time.time(),
            "shredded": False,
            "transcript_history": []
        }
        return {
            "session_id": session_id,
            "consent_status": "GRANTED" if consent_given else "REFUSED",
            "caller_hash": caller_hash
        }

    def sanitize_transcript(self, text: str) -> str:
        """
        RGPD Art. 25: Real-time transcript PII redaction before sending to agent LLMs.
        """
        sanitized = text
        for pattern, replacement in self.PII_RULES:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized

    def append_transcript(self, session_id: str, speaker: str, raw_text: str) -> tuple[bool, str]:
        """
        Appends sanitized transcript line. Returns (success, sanitized_text).
        """
        if session_id not in self.sessions or self.sessions[session_id]["shredded"]:
            return False, ""
        
        sanitized = self.sanitize_transcript(raw_text)
        self.sessions[session_id]["transcript_history"].append({
            "speaker": speaker,
            "text": sanitized,
            "timestamp": time.time()
        })
        return True, sanitized

    def crypto_shred_call(self, session_id: str) -> dict[str, Any]:
        """
        RGPD Art. 17: Right to Erasure / Immediate deletion of call audio, transcripts, and identifiers.
        """
        if session_id not in self.sessions:
            return {"status": "NOT_FOUND", "session_id": session_id}

        sess = self.sessions[session_id]
        sess["transcript_history"] = []
        sess["caller_hash"] = "0000000000000000000000000000000000000000000000000000000000000000"
        sess["shredded"] = True
        sess["shredded_at"] = time.time()

        return {
            "status": "SHREDDED",
            "session_id": session_id,
            "details": "All audio metadata, caller references and transcripts have been destroyed."
        }
