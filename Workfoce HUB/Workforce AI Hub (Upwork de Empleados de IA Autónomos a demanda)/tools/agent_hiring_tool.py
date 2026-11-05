"""
Agent Hiring Tool - Instantiates and binds AI Employees with SLA contracts.
"""
import time
from typing import Any, ClassVar

from pydantic import Field

from tools.base import BaseTool


class AgentHiringTool(BaseTool):
    """
    Hires and configures an on-demand AI employee role with clear deliverables and SLA.
    """
    tenant_id: str = Field(..., description="Unique client tenant identifier")
    role_name: str = Field(..., description="Role to hire (e.g. GTM_Engineer, Sales_Representative)")
    contract_hours: int = Field(default=40, description="Monthly contracted hours or execution quota")
    sla_response_minutes: int = Field(default=15, description="Target response latency in minutes")

    AVAILABLE_ROLES: ClassVar[list[str]] = [
        "GTM_Engineer",
        "SEO_AEO_Specialist",
        "FullStack_WebDev",
        "Social_Media_Manager",
        "Ad_Manager",
        "Sales_Representative",
        "Customer_Satisfaction",
        "Chief_of_Staff"
    ]

    def run(self) -> dict[str, Any]:
        if self.role_name not in self.AVAILABLE_ROLES:
            return {
                "success": False,
                "error": f"Role '{self.role_name}' is not supported. Available roles: {self.AVAILABLE_ROLES}"
            }

        worker_id = f"WRK-{self.role_name[:3].upper()}-{abs(hash(f'{self.tenant_id}:{time.time()}')) % 10000:04d}"
        
        contract = {
            "worker_id": worker_id,
            "tenant_id": self.tenant_id,
            "role": self.role_name,
            "status": "ACTIVE",
            "contract_hours": self.contract_hours,
            "sla_response_minutes": self.sla_response_minutes,
            "hired_at": time.time(),
            "capabilities": self._get_capabilities(self.role_name)
        }
        
        return {
            "success": True,
            "message": f"Successfully hired {self.role_name} for tenant {self.tenant_id}.",
            "contract": contract
        }

    def _get_capabilities(self, role: str) -> list[str]:
        mapping = {
            "GTM_Engineer": ["pipeline_automation", "crm_sync", "funnel_optimization"],
            "SEO_AEO_Specialist": ["keyword_research", "answer_engine_opt", "technical_audit"],
            "FullStack_WebDev": ["landing_pages", "fastapi_backends", "bug_fixes"],
            "Social_Media_Manager": ["content_calendar", "multiplatform_posts", "trend_jacking"],
            "Ad_Manager": ["copywriting", "budget_optimization", "ad_creative_testing"],
            "Sales_Representative": ["lead_scoring", "outbound_sequences", "objection_handling"],
            "Customer_Satisfaction": ["ticket_resolution", "sentiment_triage", "escalation"],
            "Chief_of_Staff": ["orchestration", "cross_agent_dispatch", "executive_summary"]
        }
        return mapping.get(role, ["general_task_execution"])
