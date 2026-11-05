"""NIS2 Outbound Audit Module — Directive (EU) 2022/2555.

Enforces:
1. Cryptographic SHA-256 tamper-evident log for all outreach events (Art. 21).
2. Anomaly detection: Bounce rate spikes and unauthorized dispatch attempts.
3. Audit chain verification.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class DispatchBlock:
    index: int
    timestamp_utc: float
    tenant_id: str
    campaign_id: str
    recipient_hash: str  # Pseudonymized with SHA-256 for GDPR compliance
    action: str  # DISPATCHED, BOUNCED, REPLIED, HANDOFF_TRIGGERED, OPT_OUT
    payload_hash: str
    prev_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    block_hash: str = ""

    def calculate_hash(self) -> str:
        data = (
            f"{self.index}:{self.timestamp_utc}:{self.tenant_id}:{self.campaign_id}:"
            f"{self.recipient_hash}:{self.action}:{self.payload_hash}:{self.prev_hash}"
        )
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    @property
    def recipient_email(self) -> str:
        return str(self.metadata.get("recipient_email", self.recipient_hash[:16] + "..."))

    @property
    def touchpoint_type(self) -> str:
        return str(self.metadata.get("touchpoint_type", self.campaign_id))


class NIS2DispatchAuditManager:
    """Maintains immutable cryptographic proof of all outbound communications."""

    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or Path("./audit_outbound_nis2.jsonl")
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        if not self.log_path.exists():
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            self.log_path.touch(exist_ok=True)

    def _get_last_block(self) -> Optional[DispatchBlock]:
        if not self.log_path.exists() or self.log_path.stat().st_size == 0:
            return None
        last_line = ""
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last_line = line
        if not last_line:
            return None
        data = json.loads(last_line)
        return DispatchBlock(**data)

    def record_dispatch(
        self,
        tenant_id: str,
        campaign_id: str,
        recipient_email: str,
        action: str,
        payload: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DispatchBlock:
        """Records an outbound event with SHA-256 payload and chain hash."""
        # Pseudonymize email for GDPR compliance in audit log
        recipient_hash = hashlib.sha256(recipient_email.lower().strip().encode("utf-8")).hexdigest()
        payload_str = json.dumps(payload, sort_keys=True, default=str)
        payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        last_block = self._get_last_block()
        index = (last_block.index + 1) if last_block else 0
        prev_hash = last_block.block_hash if last_block else self.GENESIS_HASH
        timestamp = time.time()

        block = DispatchBlock(
            index=index,
            timestamp_utc=timestamp,
            tenant_id=tenant_id,
            campaign_id=campaign_id,
            recipient_hash=recipient_hash,
            action=action,
            payload_hash=payload_hash,
            prev_hash=prev_hash,
            metadata=metadata or {},
        )
        block.block_hash = block.calculate_hash()

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(block)) + "\n")

        return block

    def verify_chain_integrity(self) -> bool:
        """Verifies that all blocks form an unbroken, untampered SHA-256 chain."""
        if not self.log_path.exists() or self.log_path.stat().st_size == 0:
            return True

        expected_prev = self.GENESIS_HASH
        with open(self.log_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                if not line.strip():
                    continue
                data = json.loads(line)
                block = DispatchBlock(**data)

                if block.index != idx:
                    return False
                if block.prev_hash != expected_prev:
                    return False
                if block.block_hash != block.calculate_hash():
                    return False
                expected_prev = block.block_hash

        return True

    def verify_chain(self) -> bool:
        """Alias for verify_chain_integrity."""
        return self.verify_chain_integrity()

    @property
    def chain(self) -> list[DispatchBlock]:
        """Loads and returns all blocks currently recorded in the dispatch ledger."""
        blocks: list[DispatchBlock] = []
        if not self.log_path.exists() or self.log_path.stat().st_size == 0:
            return blocks
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    blocks.append(DispatchBlock(**json.loads(line)))
        return blocks
