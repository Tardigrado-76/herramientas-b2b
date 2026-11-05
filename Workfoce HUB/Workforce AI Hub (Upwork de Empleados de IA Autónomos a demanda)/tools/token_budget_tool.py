"""
Token Budget Tool - Enforces inference quota, cost accounting, and budget guardrails per tenant.
"""
from typing import Any, ClassVar

from pydantic import Field

from tools.base import BaseTool


class TokenBudgetTool(BaseTool):
    """
    Monitors and enforces token expenditure limits across agent task executions.
    """
    tenant_id: str = Field(..., description="Tenant ID")
    tokens_to_consume: int = Field(..., description="Estimated tokens consumed by current LLM run")
    monthly_budget_usd: float = Field(default=100.0, description="Monthly spending limit in USD")
    cost_per_1k_tokens: float = Field(default=0.002, description="Blended cost per 1k tokens")

    # In-memory ledger of usage
    _usage_store: ClassVar[dict[str, int]] = {}

    def run(self) -> dict[str, Any]:
        current_consumed = self._usage_store.get(self.tenant_id, 0)
        projected_consumed = current_consumed + self.tokens_to_consume
        
        projected_cost = (projected_consumed / 1000.0) * self.cost_per_1k_tokens
        
        if projected_cost > self.monthly_budget_usd:
            return {
                "success": False,
                "allowed": False,
                "error": "BUDGET_EXCEEDED",
                "details": f"Projected cost ${projected_cost:.4f} exceeds monthly budget ${self.monthly_budget_usd:.2f}."
            }

        # Update usage
        self._usage_store[self.tenant_id] = projected_consumed
        
        return {
            "success": True,
            "allowed": True,
            "tokens_consumed_task": self.tokens_to_consume,
            "total_tokens_consumed": projected_consumed,
            "accumulated_cost_usd": round(projected_cost, 4),
            "remaining_budget_usd": round(self.monthly_budget_usd - projected_cost, 4)
        }
