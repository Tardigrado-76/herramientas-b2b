"""
NIS2 Compliance Module - Call Session Audit, SHA-256 Ledger & Critical Escalation
Complies with EU Directive 2022/2555 (NIS2 Articles 21 & 23).
"""
import hashlib
import json
import time
from typing import Any


class NIS2ContactAuditLedger:
    """
    Immutable cryptographic audit ledger recording every multichannel contact session,
    agent transfer, transcript hash, and security anomaly.
    """

    def __init__(self, ledger_file: str | None = None):
        self.ledger_file = ledger_file
        self.entries: list[dict[str, Any]] = []
        self._last_hash = "GENESIS_NIS2_OMNICALL_LEDGER_00000000000000000000"

    def record_interaction(
        self,
        tenant_id: str,
        session_id: str,
        channel: str,
        action: str,
        agent_role: str,
        status: str,
        metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Record a tamper-evident multichannel interaction into the hash chain.
        """
        payload = {
            "index": len(self.entries) + 1,
            "timestamp": time.time(),
            "tenant_id": tenant_id,
            "session_id": session_id,
            "channel": channel,
            "action": action,
            "agent_role": agent_role,
            "status": status,
            "metadata": metadata or {},
            "prev_hash": self._last_hash
        }
        
        canonical_str = json.dumps(payload, sort_keys=True)
        block_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
        
        entry = {**payload, "hash": block_hash}
        self.entries.append(entry)
        self._last_hash = block_hash

        if self.ledger_file:
            with open(self.ledger_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

        return entry

    def verify_ledger(self) -> bool:
        """
        Verifies the cryptographic chain across all interaction entries.
        """
        expected_prev = "GENESIS_NIS2_OMNICALL_LEDGER_00000000000000000000"
        for entry in self.entries:
            if entry.get("prev_hash") != expected_prev:
                return False
            payload = {k: v for k, v in entry.items() if k != "hash"}
            canonical_str = json.dumps(payload, sort_keys=True)
            computed_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
            if computed_hash != entry.get("hash"):
                return False
            expected_prev = entry.get("hash")
        return True

    def check_telecom_incident(self, entry: dict[str, Any]) -> dict[str, Any] | None:
        """
        NIS2 Art. 23: Early warning for contact center disruption (SIP DDoS, prompt injection via voice/audio,
        data leakage attempts). Generates 24h CSIRT alert.
        """
        status = entry.get("status", "")
        meta = entry.get("metadata", {})
        if status == "SECURITY_ALERT" or meta.get("audio_injection") or meta.get("call_flooding"):
            return {
                "incident_id": f"INC-NIS2-CALL-{int(time.time())}-{entry.get('index')}",
                "severity": "CRITICAL" if meta.get("audio_injection") else "HIGH",
                "tenant_id": entry.get("tenant_id"),
                "session_id": entry.get("session_id"),
                "channel": entry.get("channel"),
                "detected_action": entry.get("action"),
                "timestamp": entry.get("timestamp"),
                "csirt_notification_required": True,
                "deadline_hours": 24,
                "reason": meta.get("reason", "Malicious or anomalous telecom intrusion attempt.")
            }
        return None
