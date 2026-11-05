"""Búnker Criptográfico Local y Libro Mayor Inmutable bajo NIS2 y RGPD."""

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field


class AuditBlock(BaseModel):
    block_index: int
    timestamp: str
    action_type: str                 # INVOICE_PROCESSED, PAYMENT_APPROVED, RECONCILIATION_SYNC, FRAUD_ALERT
    actor: str
    details: dict[str, Any]
    previous_hash: str
    block_hash: str
    hmac_signature: str


class BunkerLedger:
    """Libro mayor criptográfico local inmutable y a prueba de manipulaciones."""

    def __init__(self, ledger_file: str = "data/audit_ledger/audit_nis2_ledger.jsonl", secret_key: str = "quantigrade_bunker_cfo_key"):
        self.ledger_file = ledger_file
        self.secret_key = secret_key
        os.makedirs(os.path.dirname(self.ledger_file), exist_ok=True)
        if not os.path.exists(self.ledger_file):
            with open(self.ledger_file, "w", encoding="utf-8") as f:
                pass  # Crear archivo vacío

    def _get_last_block(self) -> dict[str, Any] | None:
        if not os.path.exists(self.ledger_file):
            return None
        last_line = None
        with open(self.ledger_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last_line = line.strip()
        if last_line:
            try:
                return json.loads(last_line)
            except json.JSONDecodeError:
                return None
        return None

    def record_action(self, action_type: str, actor: str, details: dict[str, Any]) -> AuditBlock:
        last = self._get_last_block()
        idx = (last["block_index"] + 1) if last else 1
        prev_hash = last["block_hash"] if last else "0" * 64
        now_iso = datetime.now(timezone.utc).isoformat()

        payload = f"{idx}|{now_iso}|{action_type}|{actor}|{json.dumps(details, sort_keys=True)}|{prev_hash}"
        block_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        # Firma HMAC para garantizar origen e integridad
        sig = hmac.new(self.secret_key.encode("utf-8"), block_hash.encode("utf-8"), hashlib.sha256).hexdigest()

        block = AuditBlock(
            block_index=idx,
            timestamp=now_iso,
            action_type=action_type,
            actor=actor,
            details=details,
            previous_hash=prev_hash,
            block_hash=block_hash,
            hmac_signature=sig
        )

        with open(self.ledger_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(block.model_dump()) + "\n")

        return block

    def verify_ledger_integrity(self) -> tuple[bool, int, str]:
        """Verifica que la cadena de hashes del ledger no haya sido alterada."""
        if not os.path.exists(self.ledger_file):
            return True, 0, "Ledger vacío, integridad intacta."

        prev_hash = "0" * 64
        count = 0

        with open(self.ledger_file, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    return False, line_idx, f"Línea {line_idx} corrupta (JSON inválido)."

                if data["previous_hash"] != prev_hash:
                    return False, line_idx, f"Ruptura de cadena en bloque {data['block_index']}: hash previo no coincide."

                payload = f"{data['block_index']}|{data['timestamp']}|{data['action_type']}|{data['actor']}|{json.dumps(data['details'], sort_keys=True)}|{data['previous_hash']}"
                expected_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

                if expected_hash != data["block_hash"]:
                    return False, line_idx, f"Hash adulterado en bloque {data['block_index']}."

                prev_hash = data["block_hash"]
                count += 1

        return True, count, f"Integridad verificada con éxito en {count} bloques sellados bajo NIS2."

    def get_all_blocks(self) -> list[AuditBlock]:
        """Recupera todos los bloques de auditoría registrados."""
        if not os.path.exists(self.ledger_file):
            return []
        blocks = []
        with open(self.ledger_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        blocks.append(AuditBlock.model_validate_json(line.strip()))
                    except Exception:
                        pass
        return blocks
