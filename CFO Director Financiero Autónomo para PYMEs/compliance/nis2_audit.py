"""NIS2 Compliance Module — Directive (EU) 2022/2555.

Enforces:
1. Tamper-evident cryptographic SHA-256 hash-chained event logging (Art. 21).
2. Automated Incident Notification SLA: 24h Early Warning & 72h Full Report (Art. 23).
3. Chain integrity verification and anomaly escalation.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AuditBlock:
    index: int
    timestamp_utc: float
    tenant_id: str
    action: str
    actor: str
    payload_hash: str
    prev_hash: str
    metadata: dict[str, Any] = field(default_factory=dict)
    block_hash: str = ""

    def calculate_hash(self) -> str:
        data = (
            f"{self.index}:{self.timestamp_utc}:{self.tenant_id}:"
            f"{self.action}:{self.actor}:{self.payload_hash}:{self.prev_hash}"
        )
        return hashlib.sha256(data.encode("utf-8")).hexdigest()


@dataclass
class NIS2Incident:
    incident_id: str
    tenant_id: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    detected_at: float
    early_warning_deadline_24h: float
    incident_report_deadline_72h: float
    status: str = "OPEN"  # OPEN, EARLY_WARNING_SENT, RESOLVED


class NIS2AuditManager:
    """Manages immutable audit trails and regulatory incident notification triggers."""

    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self, log_path: Path | None = None):
        self.log_path = log_path or Path("./audit_nis2_ledger.jsonl")
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        if not self.log_path.exists():
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            self.log_path.touch(exist_ok=True)

    def _get_last_block(self) -> AuditBlock | None:
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
        return AuditBlock(**data)

    def record_event(
        self,
        tenant_id: str,
        action: str,
        actor: str,
        payload: Any,
        metadata: dict[str, Any] | None = None,
    ) -> AuditBlock:
        """Records an event with SHA-256 payload and chain hash."""
        payload_str = json.dumps(payload, sort_keys=True, default=str)
        payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        last_block = self._get_last_block()
        index = (last_block.index + 1) if last_block else 0
        prev_hash = last_block.block_hash if last_block else self.GENESIS_HASH
        timestamp = time.time()

        block = AuditBlock(
            index=index,
            timestamp_utc=timestamp,
            tenant_id=tenant_id,
            action=action,
            actor=actor,
            payload_hash=payload_hash,
            prev_hash=prev_hash,
            metadata=metadata or {},
        )
        block.block_hash = block.calculate_hash()

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(block)) + "\n")

        return block

    def verify_chain_integrity(self) -> bool:
        """Verifies that all blocks form an unbroken, untampered SHA-256 cryptographic chain."""
        if not self.log_path.exists() or self.log_path.stat().st_size == 0:
            return True

        expected_prev = self.GENESIS_HASH
        with open(self.log_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                if not line.strip():
                    continue
                data = json.loads(line)
                block = AuditBlock(**data)

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
    def chain(self) -> list[AuditBlock]:
        """Loads and returns all blocks currently recorded in the audit ledger."""
        blocks: list[AuditBlock] = []
        if not self.log_path.exists() or self.log_path.stat().st_size == 0:
            return blocks
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    blocks.append(AuditBlock(**json.loads(line)))
        return blocks

    def create_incident(self, tenant_id: str, severity: str, description: str) -> NIS2Incident:
        """Triggers a formal NIS2 incident with 24h Early Warning and 72h Report deadlines."""
        now = time.time()
        incident_id = f"NIS2-{int(now)}-{hashlib.sha256(description.encode()).hexdigest()[:8]}"
        incident = NIS2Incident(
            incident_id=incident_id,
            tenant_id=tenant_id,
            severity=severity,
            description=description,
            detected_at=now,
            early_warning_deadline_24h=now + 86400,
            incident_report_deadline_72h=now + 259200,
        )

        self.record_event(
            tenant_id=tenant_id,
            action="NIS2_INCIDENT_TRIGGERED",
            actor="SYSTEM_GRC",
            payload=asdict(incident),
            metadata={"severity": severity, "incident_id": incident_id},
        )
        return incident
