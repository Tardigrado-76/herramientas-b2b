"""Autonomous GRC Council Multi-Agent Engine.
Orchestrates the Compliance Council using Swarms and Agency-Swarm design patterns.
"""

from __future__ import annotations

import sys
from pathlib import Path
_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

import json
from typing import Any, Dict, List, Optional

from agents.personas import (
    CISO_LEAD_JUDGE_PROMPT,
    CRA_SECOPS_PROMPT,
    GDPR_PRIVACY_AUDITOR_PROMPT,
    NIS2_SENTINEL_PROMPT,
)
from reporting.executive_dictamen import ExecutiveDictamenGenerator
from sealer.merkle_bunker import EvidenceSeal, MerkleBunkerSealer
from tools.cra_sbom_tool import CRASBOMTool
from tools.nis2_audit_tool import NIS2AuditTool
from tools.remediation_planner_tool import RemediationPlannerTool
from tools.rgpd_audit_tool import RGPDAuditTool


class ComplianceSentinelEngine:
    """Central multi-agent GRC engine evaluating NIS2, RGPD, and CRA conformity."""

    def __init__(
        self,
        tenant_id: str = "tenant_grc_01",
        company_name: str = "Innovación Corporativa S.L.",
        model_name: str = "gpt-5.4",
        sealer: Optional[MerkleBunkerSealer] = None,
    ):
        self.tenant_id = tenant_id
        self.company_name = company_name
        self.model_name = model_name
        self.sealer = sealer or MerkleBunkerSealer()

        self._init_swarms_agents()

    def _init_swarms_agents(self) -> None:
        """Initializes Swarms Agent primitives if environment is configured."""
        try:
            from swarms import Agent

            self.swarms_ciso = Agent(
                agent_name="CISO_Lead_Judge",
                agent_description="Lead CISO synthesizing European GRC findings.",
                system_prompt=CISO_LEAD_JUDGE_PROMPT,
                model_name=self.model_name,
                max_loops=1,
            )
            self.swarms_nis2 = Agent(
                agent_name="NIS2_Sentinel",
                agent_description="NIS2 cybersecurity risk management auditor.",
                system_prompt=NIS2_SENTINEL_PROMPT,
                model_name=self.model_name,
                max_loops=1,
            )
            self.swarms_gdpr = Agent(
                agent_name="GDPR_Auditor",
                agent_description="DPO privacy architect auditing TOMs and DPIAs.",
                system_prompt=GDPR_PRIVACY_AUDITOR_PROMPT,
                model_name=self.model_name,
                max_loops=1,
            )
            self.swarms_cra = Agent(
                agent_name="CRA_SecOps",
                agent_description="CRA software supply chain and SBOM validator.",
                system_prompt=CRA_SECOPS_PROMPT,
                model_name=self.model_name,
                max_loops=1,
            )
            self.has_live_swarms = True
        except Exception:
            self.has_live_swarms = False

    def run_full_compliance_audit(
        self,
        company_name: Optional[str] = None,
        telemetry: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Executes a unified, multi-agent audit across NIS2, RGPD, and CRA.

        Pipeline:
        1. NIS2 Technical Audit (Art. 21 & 23).
        2. RGPD Privacy Audit (Art. 32 TOMs & Art. 35 DPIA).
        3. CRA Supply Chain & SBOM Audit (Art. 10 & 11).
        4. Remediation Planning (Prioritized backlog & sprints).
        5. Merkle Tree Cryptographic Sealing (Immutable audit trail).
        6. Executive Board Dictamen Generation.
        """
        target_company = company_name or self.company_name
        input_telemetry = telemetry or {}

        # 1. NIS2 Audit
        nis2_tool = NIS2AuditTool(telemetry_data=input_telemetry)
        nis2_res = nis2_tool.run()

        # 2. RGPD Audit
        rgpd_tool = RGPDAuditTool(privacy_telemetry=input_telemetry)
        rgpd_res = rgpd_tool.run()

        # 3. CRA Audit
        cra_tool = CRASBOMTool(supply_chain_telemetry=input_telemetry)
        cra_res = cra_tool.run()

        # Consolidate findings
        all_findings = []
        all_findings.extend(nis2_res["findings"])
        all_findings.extend(rgpd_res["findings"])
        all_findings.extend(cra_res["findings"])

        # 4. Remediation Planning
        planner_tool = RemediationPlannerTool(findings=all_findings)
        remediation_res = planner_tool.run()

        # Calculate weighted Global Compliance Score
        # NIS2: 35%, RGPD: 35%, CRA: 30%
        w_score = (
            (nis2_res["compliance_score"] * 0.35)
            + (rgpd_res["compliance_score"] * 0.35)
            + (cra_res["compliance_score"] * 0.30)
        )
        global_score = round(w_score, 1)

        if global_score >= 85.0 and remediation_res["critical_blockers"] == 0:
            global_status = "GREEN"
        elif global_score >= 60.0:
            global_status = "AMBER"
        else:
            global_status = "RED"

        # 5. Merkle Bunker Cryptographic Sealing
        evidence_dict = {
            "nis2_audit.json": json.dumps(nis2_res, sort_keys=True),
            "rgpd_audit.json": json.dumps(rgpd_res, sort_keys=True),
            "cra_audit.json": json.dumps(cra_res, sort_keys=True),
            "remediation_plan.json": json.dumps(remediation_res, sort_keys=True),
        }
        seal = self.sealer.issue_seal(
            company_name=target_company,
            evidence_items=evidence_dict,
            frameworks=["NIS2", "RGPD", "CRA"],
        )

        # 6. Executive Dictamen Generation
        markdown_dictamen = ExecutiveDictamenGenerator.generate_markdown_dictamen(
            company_name=target_company,
            nis2_score=nis2_res["compliance_score"],
            rgpd_score=rgpd_res["compliance_score"],
            cra_score=cra_res["compliance_score"],
            global_score=global_score,
            global_status=global_status,
            total_gaps=remediation_res["total_gaps_identified"],
            critical_gaps=remediation_res["critical_blockers"],
            remediation_sprints=remediation_res["estimated_remediation_sprints"],
            seal=seal,
        )

        return {
            "company_name": target_company,
            "global_score": global_score,
            "global_status": global_status,
            "framework_scores": {
                "nis2": nis2_res["compliance_score"],
                "rgpd": rgpd_res["compliance_score"],
                "cra": cra_res["compliance_score"],
            },
            "audits": {
                "nis2": nis2_res,
                "rgpd": rgpd_res,
                "cra": cra_res,
            },
            "remediation": remediation_res,
            "evidence_seal": seal.__dict__,
            "markdown_dictamen": markdown_dictamen,
        }
