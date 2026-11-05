import pytest
import tempfile
import os
from gastown_engine.witness_watchdog import TheWitness
from gastown_engine.beads_ledger import BeadsLedger, BeadStatus

def test_witness_kills_on_consecutive_test_failures():
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger_file = os.path.join(tmpdir, "test_beads.jsonl")
        autopsy_dir = os.path.join(tmpdir, "autopsies")
        ledger = BeadsLedger(ledger_file=ledger_file)
        witness = TheWitness(max_consecutive_fails=3, autopsy_dir=autopsy_dir)

        bead = ledger.register_bead("bead-loop-01", "SC-LOOP", "Infinite Loop Bead", "services/loop.py")
        bead.consecutive_test_fails = 3

        should_kill, reason = witness.evaluate_polecat(bead, ledger, last_error="AssertionError: Loop fail")
        assert should_kill is True
        assert "INFINITE_LOOP_DETECTED" in reason

        updated = ledger.get_bead("bead-loop-01")
        assert updated.status == BeadStatus.KILLED
        assert len(witness.list_autopsies()) == 1

def test_witness_kills_on_token_overdraft():
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger_file = os.path.join(tmpdir, "test_beads2.jsonl")
        autopsy_dir = os.path.join(tmpdir, "autopsies2")
        ledger = BeadsLedger(ledger_file=ledger_file)
        witness = TheWitness(max_token_budget=40000, autopsy_dir=autopsy_dir)

        bead = ledger.register_bead("bead-token-01", "SC-TOKEN", "Token Overdraft Bead", "services/token.py", token_budget=40000)
        bead.tokens_spent = 45000

        should_kill, reason = witness.evaluate_polecat(bead, ledger)
        assert should_kill is True
        assert "TOKEN_BUDGET_EXHAUSTION" in reason

        updated = ledger.get_bead("bead-token-01")
        assert updated.status == BeadStatus.KILLED
