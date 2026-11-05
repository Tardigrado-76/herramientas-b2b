"""
Beads Ledger ('bd') - Libro Mayor de Tareas Persistido en Git / Archivo.
Inspirado en el sistema Beads de Gas Town (Steve Yegge).
Mantiene el estado permanente de las tareas resistiendo compactaciones de contexto.
"""

import json
import os
from enum import Enum
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field


class BeadStatus(str, Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    IN_WORKTREE = "IN_WORKTREE"
    VALIDATING = "VALIDATING"
    DONE = "DONE"
    KILLED = "KILLED"


class BeadItem(BaseModel):
    bead_id: str
    contract_id: str
    title: str
    target_file: str
    status: BeadStatus = BeadStatus.OPEN
    assigned_polecat_id: str | None = None
    worktree_path: str | None = None
    tokens_spent: int = 0
    token_budget: int = 40000
    consecutive_test_fails: int = 0
    created_at: str = ""
    updated_at: str = ""
    kill_reason: str | None = None
    pr_id: str | None = None


class BeadsLedger:
    """Gestor del libro de tareas Beads ('bd') persistente."""

    def __init__(self, ledger_file: str = "storage/beads/beads_ledger.jsonl"):
        self.ledger_file = ledger_file
        os.makedirs(os.path.dirname(os.path.abspath(self.ledger_file)), exist_ok=True)
        self.beads: dict[str, BeadItem] = {}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.ledger_file):
            return
        with open(self.ledger_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line.strip())
                        item = BeadItem.model_validate(data)
                        self.beads[item.bead_id] = item
                    except Exception:
                        pass

    def _save(self) -> None:
        with open(self.ledger_file, "w", encoding="utf-8") as f:
            for item in self.beads.values():
                f.write(json.dumps(item.model_dump()) + "\n")

    def register_bead(self, bead_id: str, contract_id: str, title: str, target_file: str, token_budget: int = 40000) -> BeadItem:
        now_iso = datetime.now(timezone.utc).isoformat()
        item = BeadItem(
            bead_id=bead_id,
            contract_id=contract_id,
            title=title,
            target_file=target_file,
            token_budget=token_budget,
            created_at=now_iso,
            updated_at=now_iso
        )
        self.beads[bead_id] = item
        self._save()
        return item

    def update_status(self, bead_id: str, status: BeadStatus, **kwargs: Any) -> BeadItem:
        item = self.beads.get(bead_id)
        if not item:
            raise KeyError(f"Bead '{bead_id}' no encontrado en el ledger.")
        item.status = status
        item.updated_at = datetime.now(timezone.utc).isoformat()
        for k, v in kwargs.items():
            if hasattr(item, k):
                setattr(item, k, v)
        self._save()
        return item

    def get_bead(self, bead_id: str) -> BeadItem | None:
        return self.beads.get(bead_id)

    def list_all_beads(self) -> list[BeadItem]:
        return list(self.beads.values())
