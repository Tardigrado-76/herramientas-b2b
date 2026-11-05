"""Suite de pruebas unitarias para Implementar SubscriptionLifecycleManager con gestión de estados"""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from domain.subscription_manager import SubscriptionLifecycleManager

def test_bead_epic_corp_401_03_billing():
    instance = SubscriptionLifecycleManager()
    assert instance.is_active is True
