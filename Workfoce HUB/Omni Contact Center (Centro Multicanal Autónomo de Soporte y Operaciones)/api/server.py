"""
FastAPI Production Server for OMNI CONTACT - Contact Center IA Multimodal
Endpoints for session initiation, turn processing, supervisor escalation, disposition, and compliance (NIS2, RGPD, CRA).
"""
import sys
from pathlib import Path

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from typing import Any

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from agents.hub_engine import OmniHubEngine
from agents.personas import CONTACT_CENTER_PERSONAS
from compliance.cra_telephony_security import CRATelephonyGuard

app = FastAPI(
    title="OMNI CONTACT - Multimodal AI Contact Center",
    version="1.0.0",
    description="Enterprise Multimodal Contact Center with autonomous Voice/SIP, WhatsApp & WebChat agents complying with NIS2, RGPD, and CRA."
)

# Global engine instance
hub_engine = OmniHubEngine()


# Request / Response Schemas
class StartSessionRequest(BaseModel):
    channel: str = Field(..., example="voice_sip", description="voice_sip, whatsapp, web_chat, email")
    caller_id: str = Field(..., example="+34600123456", description="Caller number or customer email/ID")
    payload_data: dict[str, Any] = Field(default_factory=dict, description="Channel metadata or speech event")
    consent_given: bool = Field(default=True, description="RGPD consent for call recording/processing")


class ProcessTurnRequest(BaseModel):
    session_id: str = Field(..., example="SESS-VOI-12345678")
    customer_utterance: str = Field(..., example="I have an unexpected charge on my invoice and I want a refund.")


class CloseSessionRequest(BaseModel):
    session_id: str = Field(..., example="SESS-VOI-12345678")


class CryptoShredRequest(BaseModel):
    session_id: str = Field(..., example="SESS-VOI-12345678")


@app.get("/health", tags=["System"])
def health_check() -> dict[str, Any]:
    return {
        "status": "HEALTHY",
        "app": "OMNI CONTACT",
        "version": "1.0.0",
        "channels_supported": ["voice_sip", "whatsapp", "web_chat", "email"],
        "active_roles": list(CONTACT_CENTER_PERSONAS.keys()),
        "compliance": {
            "nis2": "Art. 21/23 Cryptographic Call Audit Ledger Active",
            "rgpd": "Art. 6/7/17/25 Multimodal Voice/Text Masking & Crypto-Shred Active",
            "cra": "Art. 10/11 Telephony Adversarial Firewall & CycloneDX SBOM Active"
        }
    }


@app.get("/compliance/sbom", tags=["CRA Compliance"])
def get_cyclonedx_sbom() -> dict[str, Any]:
    """CRA Art. 11 Machine-readable CycloneDX v1.5 JSON SBOM."""
    return CRATelephonyGuard.generate_cyclonedx_sbom()


@app.get("/compliance/ledger/verify", tags=["NIS2 Compliance"])
def verify_ledger() -> dict[str, Any]:
    """NIS2 Art. 21 Integrity verification of all recorded interaction blocks."""
    is_valid = hub_engine.ledger.verify_ledger()
    return {
        "ledger_intact": is_valid,
        "total_recorded_blocks": len(hub_engine.ledger.entries),
        "status": "VERIFIED" if is_valid else "TAMPERED"
    }


@app.post("/session/start", tags=["Telephony & Multimodal Inbound"])
def start_session(req: StartSessionRequest) -> dict[str, Any]:
    try:
        res = hub_engine.start_session(
            channel=req.channel,
            caller_id=req.caller_id,
            payload_data=req.payload_data,
            consent_given=req.consent_given
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/session/turn", tags=["Dialogue Management"])
def process_turn(req: ProcessTurnRequest) -> dict[str, Any]:
    res = hub_engine.process_turn(
        session_id=req.session_id,
        customer_utterance=req.customer_utterance
    )
    if not res.get("success"):
        if res.get("error") == "CRA_TELEPHONY_VIOLATION":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=res)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res)
    return res


@app.post("/session/close", tags=["Call Wrap-Up & CRM"])
def close_session(req: CloseSessionRequest) -> dict[str, Any]:
    res = hub_engine.close_session(req.session_id)
    if not res.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res.get("error"))
    return res


@app.post("/session/crypto-shred", tags=["RGPD Compliance"])
def crypto_shred(req: CryptoShredRequest) -> dict[str, Any]:
    """RGPD Art. 17 Irreversible deletion of audio, transcripts, and identifiers."""
    res = hub_engine.vault.crypto_shred_call(req.session_id)
    hub_engine.ledger.record_interaction(
        tenant_id="OMNI_CORP",
        session_id=req.session_id,
        channel="compliance_ops",
        action="CALL_CRYPTO_SHREDDED",
        agent_role="RGPD_DPO",
        status="SUCCESS",
        metadata=res
    )
    return res
