"""RGPD Privacy & TOMs Audit Tool.
Executes evaluation of Technical & Organizational Measures (Art. 32) and DPIA (Art. 35).
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

from compliance.rgpd_engine import RGPDComplianceEngine
from tools.base import BaseTool


class RGPDAuditTool(BaseTool):
    """Audits company data privacy measures against Regulation (EU) 2016/679 (GDPR)."""

    privacy_telemetry: Dict[str, Any] = Field(..., description="Telemetry (encryption, anonymization, DPIA, 72h breach protocol, crypto-shredding)")

    def run(self) -> Dict[str, Any]:
        engine = RGPDComplianceEngine()
        res = engine.evaluate_privacy_posture(self.privacy_telemetry)
        return {
            "framework": res.framework,
            "compliance_score": res.compliance_score,
            "status": res.status,
            "total_checks": res.total_checks,
            "passed_checks": res.passed_checks,
            "breach_notification_sla_seconds": res.breach_notification_sla_seconds,
            "findings": [asdict(f) for f in res.findings],
        }
