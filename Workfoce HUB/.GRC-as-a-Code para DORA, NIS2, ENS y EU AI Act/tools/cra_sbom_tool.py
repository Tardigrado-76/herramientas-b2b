"""CRA Supply Chain & SBOM Audit Tool.
Audits software assets against CycloneDX SBOM, VEX status, and input injection shielding.
"""

from __future__ import annotations

import sys
from pathlib import Path
_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from dataclasses import asdict
from typing import Any, Dict
from pydantic import Field

from compliance.cra_engine import CRAComplianceEngine
from tools.base import BaseTool


class CRASBOMTool(BaseTool):
    """Audits software supply chain transparency and vulnerability management under Cyber Resilience Act (CRA)."""

    supply_chain_telemetry: Dict[str, Any] = Field(..., description="Telemetry (CycloneDX SBOM, VEX, default credentials, updates, injection shield)")

    def run(self) -> Dict[str, Any]:
        engine = CRAComplianceEngine()
        res = engine.audit_software_supply_chain(self.supply_chain_telemetry)
        return {
            "framework": res["framework"],
            "compliance_score": res["compliance_score"],
            "status": res["status"],
            "total_checks": res["total_checks"],
            "passed_checks": res["passed_checks"],
            "findings": [asdict(f) for f in res["findings"]],
        }
