import pytest
import tempfile
import os
from legal_guard.bunker_ledger import BunkerLedger

def test_bunker_chain_integrity():
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger_file = os.path.join(tmpdir, "test_bunker.jsonl")
        bunker = BunkerLedger(ledger_file=ledger_file)
        
        # Append entries
        b1 = bunker.record_action("INVOICE_PROCESSED", "InvoicingAgent", {"id": "INV-1"})
        b2 = bunker.record_action("PAYMENT_APPROVED", "HumanCFO", {"id": "PAY-1"})
        b3 = bunker.record_action("FRAUD_CHECK_PASSED", "FraudDetector", {"id": "INV-1"})
        
        # Check chaining
        assert b1.block_index == 1
        assert b2.block_index == 2
        assert b2.previous_hash == b1.block_hash
        assert b3.previous_hash == b2.block_hash
        
        # Verify integrity
        is_valid, count, msg = bunker.verify_ledger_integrity()
        assert is_valid is True
        assert count == 3
