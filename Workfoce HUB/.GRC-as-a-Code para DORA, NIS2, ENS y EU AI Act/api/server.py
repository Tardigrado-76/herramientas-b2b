"""Production FastAPI Gateway for COMPLIANCE SENTINEL.
Exposes RESTful endpoints for Automated GRC Audits, CycloneDX SBOMs, and Cryptographic Evidence Seals.
"""

from __future__ import annotations

import sys
from pathlib import Path
_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from typing import Any, Dict, Optional
from fastapi import Depends, FastAPI, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from agents.council_engine import ComplianceSentinelEngine
from compliance.cra_engine import CRAComplianceEngine
from sealer.merkle_bunker import EvidenceSeal

app = FastAPI(
    title="COMPLIANCE SENTINEL — Autonomous GRC-as-a-Code Engine API",
    description="Multi-agent regulatory audit engine compliant with NIS2, RGPD, and Cyber Resilience Act (CRA).",
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

engine = ComplianceSentinelEngine()
API_KEY_SECRET = "sentinel-prod-secret-token-2026"


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Enforces CRA requirement: no unauthenticated administrative access."""
    if not x_api_key or x_api_key != API_KEY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CRA Security Violation: Invalid or missing API key.",
        )
    return x_api_key


# Request / Response Models
class FullScanRequest(BaseModel):
    company_name: str = Field(default="Corporación Target S.L.", description="Audited company name")
    telemetry: Dict[str, Any] = Field(
        default_factory=lambda: {
            "mfa_enforced": True,
            "tls_enforced": True,
            "automated_backups": True,
            "supply_chain_sbom_present": True,
            "incident_playbook_tested": True,
            "vulnerability_patching_active": True,
            "employee_cyber_training": True,
            "pii_encryption_at_rest": True,
            "pii_anonymization_in_transit": True,
            "dpia_performed_for_ai": True,
            "breach_response_protocol_72h": True,
            "right_to_erasure_crypto_shredding": True,
            "records_of_processing_rat": True,
            "sbom_cyclonedx_generated": True,
            "vex_vulnerability_disclosed": True,
            "zero_default_credentials": True,
            "automated_security_updates": True,
            "input_sanitization_shield": True,
        },
        description="Infrastructure and privacy telemetry dictionary",
    )


class SealVerificationRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    seal_id: str
    company_name: str
    timestamp_utc: float
    merkle_root: str
    leaf_count: int
    leaf_hashes: Dict[str, str]
    frameworks: list[str]
    hmac_signature: str


# 1. Health & Readiness
@app.get("/health", tags=["Monitoring"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "COMPLIANCE SENTINEL",
        "version": "1.0.0",
        "frameworks_supported": ["NIS2 (UE 2022/2555)", "RGPD (UE 2016/679)", "CRA (UE 2024/2847)"],
    }


# 2. CRA CycloneDX SBOM Endpoint (Art. 11)
@app.get("/sbom", tags=["CRA Compliance"])
def get_cyclonedx_sbom():
    """Returns official CycloneDX v1.5 JSON SBOM for cybersecurity auditors."""
    return CRAComplianceEngine.generate_cyclonedx_sbom()


# 3. Full Multi-Agent Audit Scan
@app.post("/audit/full-scan", tags=["GRC Council Operations"])
def run_full_scan(req: FullScanRequest, api_key: str = Depends(verify_api_key)):
    """Executes a complete multi-agent compliance scan and emits a cryptographically sealed dictamen."""
    result = engine.run_full_compliance_audit(
        company_name=req.company_name,
        telemetry=req.telemetry,
    )
    return result


# 4. Merkle Seal Verification
@app.post("/seal/verify", tags=["Evidence Bunker"])
def verify_evidence_seal(req: SealVerificationRequest, api_key: str = Depends(verify_api_key)):
    """Verifies that an evidence seal has not been altered or tampered with."""
    seal = EvidenceSeal(**req.model_dump())
    is_valid = engine.sealer.verify_seal(seal)
    return {
        "seal_id": req.seal_id,
        "is_valid": is_valid,
        "status": "AUTHENTIC_UNBROKEN" if is_valid else "TAMPERING_OR_FORGERY_DETECTED",
    }
