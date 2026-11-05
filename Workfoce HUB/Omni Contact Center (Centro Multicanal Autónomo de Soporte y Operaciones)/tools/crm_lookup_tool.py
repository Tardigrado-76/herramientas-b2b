"""
CRM & Knowledge Base Lookup Tool - Connects to customer records, contracts, and knowledge base.
"""
from typing import Any, ClassVar

from pydantic import Field

from tools.base import BaseTool


class CRMLookupTool(BaseTool):
    """
    Retrieves customer account status, historical support tickets, and service level tier.
    """
    customer_id: str = Field(..., description="Unique customer ID or masked identifier")
    lookup_type: str = Field(default="account_profile", description="account_profile, ticket_history, or knowledge_base")

    # In-memory mock database of accounts
    _MOCK_ACCOUNTS: ClassVar[dict[str, dict[str, Any]]] = {
        "CUST-001": {
            "name": "Acme Corp",
            "tier": "VIP_ENTERPRISE",
            "open_tickets": 0,
            "mrr_eur": 2400.0,
            "account_manager": "Elena Rodriguez"
        },
        "CUST-002": {
            "name": "Beta Logistics",
            "tier": "STANDARD",
            "open_tickets": 2,
            "mrr_eur": 450.0,
            "account_manager": "Carlos Garcia"
        }
    }

    _MOCK_KB: ClassVar[dict[str, str]] = {
        "refund_policy": "Full refunds are granted within 30 days of contract start without penalty.",
        "api_outage": "In the event of an API incident, all traffic reroutes automatically to backup cluster EU-West.",
        "sip_setup": "SIP trunk credentials can be generated via the Enterprise Security portal under Settings."
    }

    def run(self) -> dict[str, Any]:
        if self.lookup_type == "knowledge_base":
            kb_match = self._MOCK_KB.get(self.customer_id.lower(), "Standard knowledge article: Please refer to documentation.")
            return {"success": True, "result_type": "knowledge_article", "content": kb_match}

        account = self._MOCK_ACCOUNTS.get(self.customer_id)
        if account:
            return {
                "success": True,
                "result_type": "customer_profile",
                "customer_id": self.customer_id,
                "data": account
            }

        return {
            "success": True,
            "result_type": "customer_profile",
            "customer_id": self.customer_id,
            "data": {
                "name": "Standard Guest",
                "tier": "STANDARD",
                "open_tickets": 0,
                "mrr_eur": 0.0,
                "account_manager": "General Pool"
            }
        }
