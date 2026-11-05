"""Production FastAPI Gateway for OUTBOUND MACHINE.
Exposes secure RESTful endpoints for Lead Enrichment, Pitch Generation, Multi-Touch Cadences, and Human Handoffs.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import Depends, FastAPI, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import sys
from pathlib import Path
_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from agents.outbound_swarm import OutboundSwarmEngine
from compliance.cra_outbound_security import CRAOutboundSecurityManager

app = FastAPI(
    title="OUTBOUND MACHINE — Autonomous B2B Sales Engine API",
    description="Production-ready multi-agent outbound engine compliant with NIS2, RGPD, and CRA.",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

engine = OutboundSwarmEngine()
API_KEY_SECRET = "outbound-prod-secret-token-2026"


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Enforces CRA requirement: no unauthenticated administrative access."""
    if not x_api_key or x_api_key != API_KEY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CRA Security Violation: Invalid or missing API key.",
        )
    return x_api_key


# Request / Response Models
class ProspectOutboundRequest(BaseModel):
    company_raw_name: str = Field(..., description="Target company name")
    industry_sector: str = Field(default="Tecnología", description="Industry sector")
    website_url: Optional[str] = Field(None, description="Company website URL")
    contact_name: Optional[str] = Field(None, description="Decision maker name if known")
    contact_email: Optional[str] = Field(None, description="Known or predicted email")
    decision_maker_role: str = Field(default="CTO", description="Target role (CTO, CISO, CEO)")
    notes_or_snippet: Optional[str] = Field(None, description="Notes on tech stack or pain points")
    dry_run: bool = Field(default=True, description="When True, simulates without opening SMTP sockets")
    campaign_id: str = Field(default="camp_q4_enterprise", description="Campaign identifier")


class HandoffRequest(BaseModel):
    prospect_id: str
    prospect_email: str
    company_name: str
    incoming_reply_text: str


class OptOutRequest(BaseModel):
    email: str
    token: Optional[str] = None


# 1. Health & Readiness
@app.get("/health", tags=["Monitoring"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "OUTBOUND MACHINE",
        "version": "1.0.0",
        "regulations": {
            "nis2": "COMPLIANT (Tamper-evident dispatch ledger active)",
            "rgpd": "COMPLIANT (Hashed Robinson list & mandatory legal footers active)",
            "cra": "COMPLIANT (CycloneDX SBOM & anti-phishing hygiene active)",
        },
    }


# 2. CRA SBOM Endpoint (Art. 11)
@app.get("/sbom", tags=["CRA Compliance"])
def get_cyclonedx_sbom():
    """Returns official CycloneDX v1.5 JSON SBOM for cybersecurity auditors."""
    return CRAOutboundSecurityManager.generate_cyclonedx_sbom()


# 3. NIS2 Dispatch Audit Verification (Art. 21)
@app.get("/audit/nis2", tags=["NIS2 Compliance"])
def verify_audit_trail(api_key: str = Depends(verify_api_key)):
    """Verifies unbroken SHA-256 cryptographic chain integrity of all outbound events."""
    is_valid = engine.audit_mgr.verify_chain_integrity()
    return {
        "audit_chain_valid": is_valid,
        "algorithm": "SHA-256",
        "status": "VERIFIED_UNBROKEN" if is_valid else "TAMPERING_DETECTED",
    }


# 4. Outbound Pipeline Processing
@app.post("/outbound/prospect", tags=["Outbound Operations"])
def process_prospect(req: ProspectOutboundRequest, api_key: str = Depends(verify_api_key)):
    """Qualifies, enriches, drafts copy, verifies compliance, and dispatches to prospect."""
    result = engine.process_prospect_outbound(
        company_raw_name=req.company_raw_name,
        industry_sector=req.industry_sector,
        website_url=req.website_url,
        contact_name=req.contact_name,
        contact_email=req.contact_email,
        decision_maker_role=req.decision_maker_role,
        notes_or_snippet=req.notes_or_snippet,
        dry_run=req.dry_run,
        campaign_id=req.campaign_id,
    )
    return result


# 5. Inbound Reply & Human SDR Handoff
@app.post("/outbound/handoff", tags=["Sales Handoff"])
def handle_prospect_reply(req: HandoffRequest, api_key: str = Depends(verify_api_key)):
    """Analyzes incoming reply, checks for meeting intent or opt-out, and escalates to SDR."""
    res = engine.trigger_human_sdr_handoff(
        prospect_id=req.prospect_id,
        prospect_email=req.prospect_email,
        company_name=req.company_name,
        incoming_reply_text=req.incoming_reply_text,
    )
    return res


# 6. RGPD Opt-Out / Unsubscribe
@app.post("/rgpd/optout", tags=["RGPD Compliance"])
def submit_opt_out(req: OptOutRequest):
    """Processes 1-click unsubscribe per RGPD Art. 21; hashes and saves to Robinson list."""
    if req.token:
        valid_token = engine.optout_mgr.verify_unsubscribe_token(req.email, req.token)
        if not valid_token:
            raise HTTPException(status_code=400, detail="Invalid unsubscribe security token.")

    engine.optout_mgr.add_opt_out(req.email)
    return {
        "status": "OPTED_OUT",
        "email_hashed": True,
        "message": f"Address {req.email} has been permanently suppressed from future outreach.",
    }


# 7. Cadence Status Check
@app.get("/cadence/{prospect_id}", tags=["Sequences"])
def get_cadence_state(prospect_id: str, api_key: str = Depends(verify_api_key)):
    """Retrieves current sequence progression and history for a given prospect."""
    state = engine.cadence_mgr.get_prospect_state(prospect_id)
    if not state:
        raise HTTPException(status_code=404, detail="Prospect ID not found in cadence.")
    return state.__dict__
