"""
Multichannel Adapters: SIP/Voice WebRTC, WhatsApp Cloud API, Web Chat, and Email.
Conforms to ponytail minimalism: standard library representations and structured payloads.
"""
import time
import uuid
from typing import Any, ClassVar


class MultichannelAdapter:
    """
    Normalizes incoming inbound interactions from telephony, WhatsApp, WebRTC and WebChat
    into a standardized ContactSession object.
    """

    SUPPORTED_CHANNELS: ClassVar[list[str]] = ["voice_sip", "whatsapp", "web_chat", "email"]

    @classmethod
    def normalize_inbound_interaction(
        cls,
        channel: str,
        caller_id: str,
        payload_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Creates a unified inbound session payload across any communication channel.
        """
        if channel not in cls.SUPPORTED_CHANNELS:
            raise ValueError(f"Channel '{channel}' is not supported. Choose from {cls.SUPPORTED_CHANNELS}")

        session_id = f"SESS-{channel[:3].upper()}-{uuid.uuid4().hex[:8]}"
        
        # Extract initial message/speech content
        content = ""
        if channel == "voice_sip":
            content = payload_data.get("speech_transcript") or payload_data.get("audio_event", "INCOMING_CALL_RINGING")
        elif channel == "whatsapp":
            content = payload_data.get("text_body", "")
        elif channel == "web_chat":
            content = payload_data.get("message", "")
        elif channel == "email":
            content = f"Subject: {payload_data.get('subject', '')}\n\n{payload_data.get('body', '')}"

        return {
            "session_id": session_id,
            "channel": channel,
            "caller_id": caller_id,
            "timestamp": time.time(),
            "raw_content": content,
            "channel_metadata": payload_data,
            "status": "INGESTED"
        }

    @classmethod
    def format_outbound_response(
        cls,
        channel: str,
        session_id: str,
        response_text: str,
        tts_voice_id: str | None = "es-ES-Neural-Voice-1"
    ) -> dict[str, Any]:
        """
        Formats outbound message for the specific channel (e.g. SIP TTS audio or WhatsApp payload).
        """
        if channel == "voice_sip":
            return {
                "session_id": session_id,
                "channel": channel,
                "action": "SPEAK_AND_LISTEN",
                "text": response_text,
                "tts_voice_id": tts_voice_id,
                "barge_in_allowed": True
            }
        elif channel == "whatsapp":
            return {
                "session_id": session_id,
                "channel": channel,
                "action": "SEND_MESSAGE",
                "recipient_type": "individual",
                "text": {"body": response_text}
            }
        elif channel == "web_chat":
            return {
                "session_id": session_id,
                "channel": channel,
                "action": "DISPATCH_SOCKET_EVENT",
                "event": "bot_message",
                "message": response_text
            }
        else: # email
            return {
                "session_id": session_id,
                "channel": channel,
                "action": "SEND_EMAIL_REPLY",
                "body": response_text
            }
