"""Unit tests for ImmutableLedger and Merkle Sealer."""

from pathlib import Path
import json
from bunker_gateway.ledger.immutable_ledger import ImmutableLedger
from bunker_gateway.ledger.sealer import CryptoBunkerSealer


def test_ledger_hash_chaining_and_tamper_detection(tmp_path: Path):
    ledger_path = tmp_path / "audit_nis2_ledger.jsonl"
    ledger = ImmutableLedger(file_path=str(ledger_path))

    # Append 3 sequential records
    h1 = ledger.append({"agent": "langgraph", "action": "chat", "tokens": 120})
    h2 = ledger.append({"agent": "gtm", "action": "tool", "tokens": 450})
    h3 = ledger.append({"agent": "sales", "action": "chat", "tokens": 200})

    assert h1 != h2 != h3
    assert ledger.verify_chain() is True

    # Tamper with the ledger file (change 1 byte)
    with open(ledger_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    data = json.loads(lines[1])
    data["tokens"] = 999999  # Malicious tampering
    lines[1] = json.dumps(data) + "\n"

    with open(ledger_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    assert ledger.verify_chain() is False


def test_cryptobunker_sealer_epoch_manifest(tmp_path: Path):
    ledger_path = tmp_path / "audit_seal_test.jsonl"
    manifest_dir = tmp_path / "manifests"
    ledger = ImmutableLedger(file_path=str(ledger_path))

    for i in range(5):
        ledger.append({"agent": f"agent_{i}", "action": "eval", "tokens": 100 * i})

    sealer = CryptoBunkerSealer(ledger=ledger, company_name="Test Enterprise Corp", output_dir=str(manifest_dir))
    manifest = sealer.seal_epoch()

    assert manifest["merkle_root"] is not None
    assert "ECDSA_P256_SIG_" in manifest["signatures"]["classical_ecdsa_p256"]
    assert "PQC_ML_DSA_87_SIG_" in manifest["signatures"]["post_quantum_ml_dsa_87"]
    assert manifest["compliance_attestation"]["eu_ai_act_article_12"] is True
