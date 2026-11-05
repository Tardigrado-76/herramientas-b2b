"""Suite de pruebas unitarias para Implementar AuthTokenProvider con firma HMAC y rotación"""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.auth_provider import AuthTokenProvider

def test_bead_epic_corp_401_01_auth():
    instance = AuthTokenProvider()
    assert instance.is_active is True
