"""
Quality Gate Tool - Automated QA evaluation of agent deliverables before user delivery.
"""
import re
from typing import Any

from pydantic import Field

from tools.base import BaseTool


class QualityGateTool(BaseTool):
    """
    Acts as automated editorial/technical reviewer verifying completeness, tone, and safety.
    """
    deliverable_text: str = Field(..., description="The generated output produced by the AI employee")
    role_name: str = Field(..., description="Role that produced the deliverable")
    min_length_chars: int = Field(default=50, description="Minimum length threshold for acceptance")

    def run(self) -> dict[str, Any]:
        issues: list[str] = []
        
        # 1. Length check
        if len(self.deliverable_text.strip()) < self.min_length_chars:
            issues.append(f"Deliverable too brief ({len(self.deliverable_text.strip())} chars < {self.min_length_chars})")

        # 2. Placeholder detection
        placeholders = re.findall(r'(\[TODO\]|\[INSERT.*?\]|YOUR_COMPANY_HERE|Lorem ipsum)', self.deliverable_text, re.IGNORECASE)
        if placeholders:
            issues.append(f"Unresolved placeholders detected: {list(set(placeholders))}")

        # 3. Role-specific quality checks
        if self.role_name == "FullStack_WebDev":
            # Must not have markdown code blocks that are incomplete or syntax errors
            if "```" in self.deliverable_text and self.deliverable_text.count("```") % 2 != 0:
                issues.append("Unclosed code block syntax detected in web dev deliverable.")
        elif self.role_name == "SEO_AEO_Specialist":
            if not any(k in self.deliverable_text.lower() for k in ["keyword", "h1", "title", "search", "meta", "query"]):
                issues.append("SEO deliverable lacks standard search/ranking terminology.")
        elif self.role_name == "Customer_Satisfaction" and not any(k in self.deliverable_text.lower() for k in ["thank you", "help", "apologize", "assist", "welcome", "glad", "sorry"]):
            issues.append("Customer satisfaction response lacks empathetic tone or greeting.")

        passed = len(issues) == 0
        score = max(0, 100 - (len(issues) * 35))

        return {
            "success": True,
            "passed": passed,
            "quality_score": score,
            "issues": issues,
            "recommendation": "APPROVED_FOR_DELIVERY" if passed else "NEEDS_REVISION"
        }
