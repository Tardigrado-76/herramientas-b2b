"""Suite de pruebas unitarias para Implementar ImmutableAuditLedger con encadenamiento SHA-256"""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from security.audit_ledger import ImmutableAuditLedger

def test_bead_epic_corp_401_04_audit():
    instance = ImmutableAuditLedger()
    assert instance.is_active is True
