"""Ideal Customer Profile (ICP) Classifier and Buyer Persona Generator Tool.
Scores prospective leads against target enterprise criteria.
"""

from __future__ import annotations

from typing import Any, Dict, List
from pydantic import Field

from .base import BaseTool


class ICPPersonaTool(BaseTool):
    """Evaluates whether a prospect company matches the target ICP criteria and generates persona profile."""

    company_name: str = Field(..., description="Legal or trade name of the company")
    industry_sector: str = Field(..., description="Industry sector (e.g., Tecnología, Logística, Fintech, Industrial)")
    headcount_range: str = Field(default="11-50", description="Company employee range: 1-10, 11-50, 51-200, 201-500, 500+")
    annual_revenue_tier: str = Field(default="1M-5M", description="Revenue tier: <1M, 1M-5M, 5M-20M, 20M+")
    identified_tech_stack: List[str] = Field(default_factory=list, description="Known tech stack tools (e.g. AWS, SAP, Salesforce, Python)")
    target_decision_maker_role: str = Field(default="CTO", description="Target role: CTO, CISO, CEO, Director Operaciones, CFO")

    def run(self) -> Dict[str, Any]:
        score = 0
        reasons: List[str] = []

        # 1. Sector Weighting
        high_value_sectors = ["tecnología", "software", "fintech", "logística", "salud", "ecommerce", "industrial"]
        if any(sec in self.industry_sector.lower() for sec in high_value_sectors):
            score += 35
            reasons.append(f"Sector '{self.industry_sector}' matches high-readiness target industries.")
        else:
            score += 15

        # 2. Company Size / Headcount Weighting (Sweet spot: 11-200 employees)
        if self.headcount_range in ["11-50", "51-200"]:
            score += 30
            reasons.append("Headcount in optimal agile B2B segment (11-200 empleados).")
        elif self.headcount_range in ["201-500", "500+"]:
            score += 25
            reasons.append("Enterprise scale: longer sales cycle but higher ACV.")
        else:
            score += 10
            reasons.append("Micro-SME: budget constraints possible.")

        # 3. Decision Maker Match
        high_leverage_roles = ["cto", "ciso", "ceo", "director general", "director operaciones", "cfo"]
        if self.target_decision_maker_role.lower() in high_leverage_roles:
            score += 25
            reasons.append(f"Role '{self.target_decision_maker_role}' has direct procurement authority.")
        else:
            score += 10

        # 4. Tech Stack Synergy
        if self.identified_tech_stack:
            score += 10
            reasons.append(f"Identified {len(self.identified_tech_stack)} tech stack components.")

        qualification_tier = "TIER_1_PRIORITY" if score >= 80 else ("TIER_2_QUALIFIED" if score >= 60 else "TIER_3_NURTURE")

        # Buyer Persona Guidance
        persona_guidance = {
            "CTO": "Focus on developer velocity, technical debt reduction, modern AI pipelines (RAG/LangGraph) and API security.",
            "CISO": "Focus on NIS2, DORA, ENS Categoría Alta, cryptographic custody and supply chain vulnerability posture.",
            "CEO": "Focus on operational margin expansion, automated workforce scaling, and rapid ROI without headcount bloat.",
            "CFO": "Focus on cost reduction, automated reconciliations, fraud prevention and predictable software licensing.",
        }.get(self.target_decision_maker_role.upper(), "Focus on efficiency and measurable business value.")

        return {
            "company_name": self.company_name,
            "qualification_score": min(100, score),
            "qualification_tier": qualification_tier,
            "reasons": reasons,
            "target_role": self.target_decision_maker_role,
            "persona_messaging_angle": persona_guidance,
            "is_marketable": score >= 50,
        }
