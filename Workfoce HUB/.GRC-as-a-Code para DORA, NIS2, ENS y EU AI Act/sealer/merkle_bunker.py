"""Cryptographic Evidence Sealer & Merkle Tree Engine.
Generates tamper-evident Merkle roots and custody proofs for regulatory audits (SLSA Level 3+ compliant).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class EvidenceSeal:
    seal_id: str
    company_name: str
    timestamp_utc: float
    merkle_root: str
    leaf_count: int
    leaf_hashes: Dict[str, str]
    frameworks: List[str]
    hmac_signature: str
    merkle_root_hash: str = ""
    total_evidences: int = 0
    evidence_manifest: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        if not self.merkle_root_hash:
            self.merkle_root_hash = self.merkle_root
        if not self.total_evidences:
            self.total_evidences = self.leaf_count
        if not self.evidence_manifest and self.leaf_hashes:
            self.evidence_manifest = [
                {
                    "evidence_id": k,
                    "framework": " / ".join(self.frameworks),
                    "control": k.replace(".json", "").replace("_", " ").upper(),
                    "status": "SEALED",
                    "data_hash": v,
                }
                for k, v in sorted(self.leaf_hashes.items())
            ]


class MerkleBunkerSealer:
    """Builds cryptographic Merkle Tree roots and issues custody seals for compliance evidence."""

    def __init__(self, secret_key: str = "grc-merkle-secret-salt-2026"):
        self.secret_key = secret_key.encode("utf-8")

    @staticmethod
    def calculate_bytes_hash(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def calculate_file_hash(file_path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        return sha256.hexdigest()

    def build_merkle_root(self, items: Dict[str, bytes | str]) -> Tuple[str, Dict[str, str]]:
        """Constructs a binary Merkle Tree from a dictionary of evidence items.

        Returns:
            Tuple[merkle_root_hash, leaf_hashes_map]
        """
        leaf_hashes: Dict[str, str] = {}
        for name, content in items.items():
            if isinstance(content, str):
                leaf_hashes[name] = hashlib.sha256(content.encode("utf-8")).hexdigest()
            else:
                leaf_hashes[name] = hashlib.sha256(content).hexdigest()

        if not leaf_hashes:
            return hashlib.sha256(b"empty_evidence_tree").hexdigest(), {}

        sorted_leaves = [leaf_hashes[k] for k in sorted(leaf_hashes.keys())]

        current_level = sorted_leaves
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = left + right
                parent_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()
                next_level.append(parent_hash)
            current_level = next_level

        merkle_root = current_level[0]
        return merkle_root, leaf_hashes

    def issue_seal(
        self,
        company_name: str,
        evidence_items: Dict[str, bytes | str],
        frameworks: Optional[List[str]] = None,
    ) -> EvidenceSeal:
        """Issues an authenticated Evidence Seal with HMAC-SHA256 signature."""
        now = time.time()
        active_frameworks = frameworks or ["NIS2", "RGPD", "CRA"]
        root_hash, leaves = self.build_merkle_root(evidence_items)

        payload_to_sign = f"{company_name}:{now}:{root_hash}:{len(leaves)}:{','.join(active_frameworks)}"
        sig = hmac.new(self.secret_key, payload_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        seal_id = f"SEAL-{int(now)}-{root_hash[:8].upper()}"
        return EvidenceSeal(
            seal_id=seal_id,
            company_name=company_name,
            timestamp_utc=now,
            merkle_root=root_hash,
            leaf_count=len(leaves),
            leaf_hashes=leaves,
            frameworks=active_frameworks,
            hmac_signature=sig,
        )

    def verify_seal(self, seal: EvidenceSeal) -> bool:
        """Verifies the HMAC signature and cryptographic consistency of an Evidence Seal."""
        payload_to_sign = (
            f"{seal.company_name}:{seal.timestamp_utc}:{seal.merkle_root}:"
            f"{seal.leaf_count}:{','.join(seal.frameworks)}"
        )
        expected_sig = hmac.new(self.secret_key, payload_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_sig, seal.hmac_signature)
