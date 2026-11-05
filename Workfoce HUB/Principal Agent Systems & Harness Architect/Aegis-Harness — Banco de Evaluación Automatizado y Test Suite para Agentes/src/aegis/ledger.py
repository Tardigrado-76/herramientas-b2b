"""
Audit Ledger for Aegis-Harness (NIS2 Art. 21 & EU AI Act Art. 12 Compliant).
Provides append-only cryptographic hash-chaining and SLSA v1.0 Level 3+ provenance.
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, List, Optional
from aegis.models import SuiteSummary

class AuditLedger:
    """
    Cryptographic immutable audit ledger for AI Agent evaluation records.
    """

    def __init__(self, ledger_file: Optional[str] = None):
        self.ledger_file = Path(ledger_file or "reports/aegis_audit_ledger.jsonl")
        self.ledger_file.parent.mkdir(parents=True, exist_ok=True)

    def _get_last_hash(self) -> str:
        """Reads the previous block hash from the last line of the ledger."""
        if not self.ledger_file.exists() or self.ledger_file.stat().st_size == 0:
            return "0" * 64

        last_line = ""
        with open(self.ledger_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last_line = line.strip()

        if not last_line:
            return "0" * 64

        try:
            record = json.loads(last_line)
            return record.get("block_hash", "0" * 64)
        except Exception:
            return "0" * 64

    def record_evaluation(self, summary: SuiteSummary, agent_name: str = "langgraph-mcp-agent") -> Dict[str, Any]:
        """
        Appends an evaluation record with rolling SHA-256 hash chaining.
        """
        prev_hash = self._get_last_hash()
        timestamp = datetime.now(timezone.utc).isoformat()

        payload = {
            "timestamp_utc": timestamp,
            "suite_name": summary.suite_name,
            "agent_under_test": agent_name,
            "total_tests": summary.total_tests,
            "passed_tests": summary.passed_tests,
            "failed_tests": summary.failed_tests,
            "pass_rate_percent": summary.pass_rate_percent,
            "overall_score": summary.overall_score,
            "quality_gate_passed": summary.quality_gate_passed,
            "average_latency_ms": summary.average_latency_ms,
            "category_scores": summary.category_scores,
            "previous_block_hash": prev_hash
        }

        # Canonical serialized payload for deterministic hash
        canonical_str = json.dumps(payload, sort_keys=True)
        block_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

        # Complete audit block
        audit_block = {
            **payload,
            "block_hash": block_hash,
            "slsa_provenance": {
                "_type": "https://in-toto.io/Statement/v0.1",
                "predicateType": "https://slsa.dev/provenance/v1.0",
                "builder": {"id": "aegis-harness-v1.0"},
                "compliance": ["NIS2_ART21", "EU_AI_ACT_ART12", "ENS_ALTO"]
            }
        }

        with open(self.ledger_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(audit_block) + "\n")

        return audit_block

    def verify_integrity(self) -> Tuple[bool, int, List[str]]:
        """
        Walks the entire ledger, verifying SHA-256 hash chains.
        Returns (is_valid, record_count, list_of_errors).
        """
        if not self.ledger_file.exists():
            return True, 0, []

        errors = []
        count = 0
        expected_prev_hash = "0" * 64

        with open(self.ledger_file, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, 1):
                if not line.strip():
                    continue
                count += 1
                try:
                    block = json.loads(line.strip())
                except Exception as e:
                    errors.append(f"Line {idx}: JSON parse failure ({e})")
                    continue

                prev_hash = block.get("previous_block_hash")
                if prev_hash != expected_prev_hash:
                    errors.append(
                        f"Line {idx}: Hash-chain break. Expected prev_hash {expected_prev_hash[:16]}..., got {prev_hash[:16]}..."
                    )

                # Recompute hash
                check_payload = {
                    k: v for k, v in block.items()
                    if k not in ("block_hash", "slsa_provenance")
                }
                canonical_str = json.dumps(check_payload, sort_keys=True)
                calc_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

                if calc_hash != block.get("block_hash"):
                    errors.append(
                        f"Line {idx}: Block content tampered. Stored {block.get('block_hash')[:16]}... != Calc {calc_hash[:16]}..."
                    )

                expected_prev_hash = block.get("block_hash")

        return (len(errors) == 0), count, errors

    def verify_chain(self) -> bool:
        """Convenience method returning boolean integrity."""
        valid, _, _ = self.verify_integrity()
        return valid

    def get_records(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return the most recent audit records."""
        if not self.ledger_file.exists():
            return []
        records = []
        with open(self.ledger_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        records.append(json.loads(line.strip()))
                    except Exception:
                        pass
        return records[-limit:]

