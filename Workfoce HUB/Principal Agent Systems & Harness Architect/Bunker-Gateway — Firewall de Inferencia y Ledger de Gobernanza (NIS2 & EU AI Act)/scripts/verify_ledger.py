"""Standalone script to verify the cryptographic integrity of audit_nis2_ledger.jsonl."""

import sys
from pathlib import Path

# Add src to path
base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir / "src"))

from bunker_gateway.core.config import load_gateway_config
from bunker_gateway.ledger.immutable_ledger import ImmutableLedger


def main():
    config = load_gateway_config()
    ledger_path = base_dir / config.ledger_file_path
    ledger = ImmutableLedger(str(ledger_path))

    print(f"Checking ledger at: {ledger_path}")
    is_valid = ledger.verify_chain()

    if is_valid:
        print("[SUCCESS] All ledger blocks in SHA-256 chain are valid and non-tampered.")
        sys.exit(0)
    else:
        print("[CRITICAL] Ledger hash-chain corruption or tampering detected!")
        sys.exit(1)


if __name__ == "__main__":
    main()
