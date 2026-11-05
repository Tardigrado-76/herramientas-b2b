"""Remediation Roadmap Planner Tool.
Synthesizes non-compliant findings into a prioritized technical remediation plan.
"""

from __future__ import annotations

import sys
from pathlib import Path
_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from typing import Any, Dict, List
from pydantic import Field

from tools.base import BaseTool


class RemediationPlannerTool(BaseTool):
    """Generates an action-oriented technical remediation plan sorted by risk severity."""

    findings: List[Dict[str, Any]] = Field(..., description="List of findings from NIS2, RGPD, and CRA audits")

    def run(self) -> Dict[str, Any]:
        # Filter for failed checks
        failed_findings = [f for f in self.findings if not f.get("passed", False)]

        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        sorted_findings = sorted(
            failed_findings,
            key=lambda x: severity_order.get(x.get("severity", "LOW"), 4),
        )

        roadmap_items = []
        total_estimated_sprints = 0

        for idx, f in enumerate(sorted_findings, start=1):
            sev = f.get("severity", "LOW")
            sprint_est = 2 if sev == "CRITICAL" else (1 if sev in ["HIGH", "MEDIUM"] else 0.5)
            total_estimated_sprints += sprint_est

            roadmap_items.append({
                "priority_rank": idx,
                "rule_id": f.get("rule_id"),
                "framework": f.get("framework"),
                "title": f.get("title"),
                "severity": sev,
                "remediation_action": f.get("remediation_guidance"),
                "estimated_sprints": sprint_est,
                "iso27001_mapping": f.get("iso27001_mapping", []),
            })

        return {
            "total_gaps_identified": len(failed_findings),
            "critical_blockers": sum(1 for f in failed_findings if f.get("severity") == "CRITICAL"),
            "high_risks": sum(1 for f in failed_findings if f.get("severity") == "HIGH"),
            "estimated_remediation_sprints": total_estimated_sprints,
            "remediation_roadmap": roadmap_items,
        }
