"""
Task Router Tool - Dynamically routes incoming business tasks to the most suitable AI Employee.
"""
import re
from re import Pattern
from typing import Any, ClassVar

from pydantic import Field

from tools.base import BaseTool


class TaskRouterTool(BaseTool):
    """
    Evaluates incoming job requests, identifies intent, and assigns the task to the optimal employee.
    """
    task_description: str = Field(..., description="Full text description of the work to be performed")
    priority: str = Field(default="NORMAL", description="Task priority: LOW, NORMAL, HIGH, URGENT")

    ROUTING_RULES: ClassVar[list[tuple[Pattern[str], str]]] = [
        (re.compile(r'\b(seo|ranking|google|keywords|search engine|aeo|perplexity)\b', re.IGNORECASE), "SEO_AEO_Specialist"),
        (re.compile(r'\b(code|bug|fastapi|frontend|html|css|javascript|python|endpoint|deploy)\b', re.IGNORECASE), "FullStack_WebDev"),
        (re.compile(r'\b(social|twitter|linkedin|post|instagram|thread|calendar)\b', re.IGNORECASE), "Social_Media_Manager"),
        (re.compile(r'\b(ad|ads|campaign|ppc|facebook ads|meta ads|roas|google ads)\b', re.IGNORECASE), "Ad_Manager"),
        (re.compile(r'\b(prospect|lead|leads|outbound|cold call|email sequence|sequence|b2b|pipeline|sales)\b', re.IGNORECASE), "Sales_Representative"),
        (re.compile(r'\b(support|ticket|refund|customer complaint|helpdesk|satisfaction)\b', re.IGNORECASE), "Customer_Satisfaction"),
        (re.compile(r'\b(gtm|funnel|webhook|crm|hubspot|zapier|analytics integration)\b', re.IGNORECASE), "GTM_Engineer"),
    ]

    def run(self) -> dict[str, Any]:
        assigned_role = "Chief_of_Staff" # Default orchestrator
        match_reason = "Default cross-agent coordination by Chief of Staff"

        for pattern, role in self.ROUTING_RULES:
            if pattern.search(self.task_description):
                assigned_role = role
                match_reason = f"Keyword match against specialized capability: {pattern.pattern}"
                break

        return {
            "success": True,
            "assigned_role": assigned_role,
            "priority": self.priority,
            "routing_reason": match_reason,
            "estimated_turnaround_hours": 2 if self.priority == "URGENT" else 6
        }
