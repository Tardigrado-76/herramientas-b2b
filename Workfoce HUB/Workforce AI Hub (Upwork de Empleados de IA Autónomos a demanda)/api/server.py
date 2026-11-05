"""
FastAPI Production Server for WORKFORCE AI
Endpoints for health, compliance (NIS2, RGPD, CRA), onboarding, hiring, and task execution.
"""
import sys
from pathlib import Path

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from typing import Any

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from agents.hub_engine import WorkforceHubEngine
from agents.personas import WORKFORCE_PERSONAS
from compliance.cra_agent_security import CRASecurityGuard

app = FastAPI(
    title="WORKFORCE AI - Autonomous On-Demand Enterprise Workforce",
    version="1.0.0",
    description="Compliant autonomous AI employee system conforming to NIS2, RGPD, and CRA."
)

# Global engine instance
hub_engine = WorkforceHubEngine()


# Request / Response Schemas
class OnboardRequest(BaseModel):
    tenant_id: str = Field(..., example="tenant-corp-01")
    company_name: str = Field(..., example="Acme Corporation")
    contact_email: str = Field(..., example="admin@acme.com")


class HireRequest(BaseModel):
    tenant_id: str = Field(..., example="tenant-corp-01")
    role: str = Field(..., example="GTM_Engineer")
    quota_hours: int = Field(default=40, example=40)


class TaskDispatchRequest(BaseModel):
    tenant_id: str = Field(..., example="tenant-corp-01")
    task_id: str = Field(..., example="TASK-9901")
    prompt: str = Field(..., example="Build a landing page with a contact form in FastAPI.")
    forced_role: str | None = Field(default=None, example="FullStack_WebDev")


class CryptoShredRequest(BaseModel):
    tenant_id: str = Field(..., example="tenant-corp-01")


@app.get("/health", tags=["System"])
def health_check() -> dict[str, Any]:
    return {
        "status": "HEALTHY",
        "app": "WORKFORCE AI",
        "version": "1.0.0",
        "active_roles": list(WORKFORCE_PERSONAS.keys()),
        "compliance": {
            "nis2": "Art. 21/23 Cryptographic Execution Ledger Active",
            "rgpd": "Art. 17/25 Privacy By Design & Crypto-Shred Active",
            "cra": "Art. 10/11 CycloneDX SBOM & Injection Firewall Active"
        }
    }


@app.get("/compliance/sbom", tags=["CRA Compliance"])
def get_cyclonedx_sbom() -> dict[str, Any]:
    """CRA Art. 11 Machine-readable Software Bill of Materials (SBOM)."""
    return CRASecurityGuard.generate_cyclonedx_sbom()


@app.get("/compliance/ledger/verify", tags=["NIS2 Compliance"])
def verify_ledger() -> dict[str, Any]:
    """NIS2 Art. 21 Integrity verification of all recorded agent actions."""
    is_valid = hub_engine.ledger.verify_integrity()
    return {
        "ledger_intact": is_valid,
        "total_recorded_blocks": len(hub_engine.ledger.entries),
        "status": "VERIFIED" if is_valid else "TAMPERED"
    }


@app.post("/tenant/onboard", tags=["Workforce Management"])
def onboard_tenant(req: OnboardRequest) -> dict[str, Any]:
    res = hub_engine.onboard_tenant(
        tenant_id=req.tenant_id,
        company_name=req.company_name,
        contact_email=req.contact_email
    )
    return res


@app.post("/tenant/hire", tags=["Workforce Management"])
def hire_worker(req: HireRequest) -> dict[str, Any]:
    res = hub_engine.hire_employee(
        tenant_id=req.tenant_id,
        role=req.role,
        quota_hours=req.quota_hours
    )
    if not res.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res.get("error"))
    return res


@app.post("/task/dispatch", tags=["Task Orchestration"])
def dispatch_task(req: TaskDispatchRequest) -> dict[str, Any]:
    res = hub_engine.execute_task(
        tenant_id=req.tenant_id,
        task_id=req.task_id,
        prompt=req.prompt,
        forced_role=req.forced_role
    )
    if not res.get("success"):
        if res.get("error") == "CRA_SECURITY_VIOLATION":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=res)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res)
    return res


@app.post("/tenant/crypto-shred", tags=["RGPD Compliance"])
def crypto_shred(req: CryptoShredRequest) -> dict[str, Any]:
    """RGPD Art. 17 Irreversible deletion of tenant memory and cryptographic keys."""
    res = hub_engine.vault.crypto_shred_tenant(req.tenant_id)
    hub_engine.ledger.record_execution(
        tenant_id=req.tenant_id,
        agent_role="RGPD_OFFICER",
        task_id="CRYPTO_SHRED",
        action="TENANT_SHREDDED",
        status="SUCCESS",
        cost_tokens=0,
        details=res
    )
    return res
