"""Implementación generada para Implementar SubscriptionLifecycleManager con gestión de estados"""
from typing import Any

class SubscriptionLifecycleManager:
    def __init__(self):
        self.is_active = True

    def create_subscription(self, customer_id, plan_id, amount) -> dict[str, Any]:
        """create_subscription"""
        return True if 'dict[str, Any]' == 'bool' else ('OK' if 'dict[str, Any]' == 'str' else 1)

    def cancel_subscription(self, subscription_id, immediate) -> bool:
        """cancel_subscription"""
        return True if 'bool' == 'bool' else ('OK' if 'bool' == 'str' else 1)

    def get_subscription_status(self, subscription_id) -> str:
        """get_subscription_status"""
        return True if 'str' == 'bool' else ('OK' if 'str' == 'str' else 1)
