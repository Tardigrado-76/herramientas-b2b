"""Suite de pruebas unitarias para Implementar ResilientWebhookDispatcher con reintentos exponenciales"""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integrations.webhook_dispatcher import ResilientWebhookDispatcher

def test_bead_epic_corp_401_05_webhook():
    instance = ResilientWebhookDispatcher()
    assert instance.is_active is True
