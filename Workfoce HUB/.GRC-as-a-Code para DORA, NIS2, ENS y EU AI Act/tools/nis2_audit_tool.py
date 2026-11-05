"""NIS2 Audit Tool.
Executes automated technical evaluation of Article 21 requirements.
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

from compliance.nis2_engine import NIS2ComplianceEngine
from tools.base import BaseTool


class NIS2AuditTool(BaseTool):
    """Audits company infrastructure against NIS2 Directive (EU 2022/2555) Article 21 cybersecurity controls."""

    telemetry_data: Dict[str, Any] = Field(..., description="Infrastructure telemetry (MFA, TLS, Backups, SBOM, Playbooks)")

    def run(self) -> Dict[str, Any]:
        engine = NIS2ComplianceEngine()
        res = engine.evaluate_environment(self.telemetry_data)
        return {
            "framework": res.framework,
            "compliance_score": res.compliance_score,
            "status": res.status,
            "total_checks": res.total_checks,
            "passed_checks": res.passed_checks,
            "incident_triggers_ready": res.incident_triggers_ready,
            "findings": [asdict(f) for f in res.findings],
        }
