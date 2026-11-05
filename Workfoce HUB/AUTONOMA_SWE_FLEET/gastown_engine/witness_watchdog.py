"""
The Witness - Perro Guardián (Watchdog) y Circuit Breaker Anti-Bucles Infinitos.
Inspirado en el Witness de Gas Town.
Supervisa el gasto de tokens y la persistencia de fallos; liquida agentes estancados.
"""

import json
import os
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field
from gastown_engine.beads_ledger import BeadItem, BeadStatus, BeadsLedger


class AutopsyReport(BaseModel):
    autopsy_id: str
    bead_id: str
    timestamp: str
    kill_reason: str
    tokens_consumed: int
    token_budget: int
    consecutive_test_fails: int
    last_error_summary: str
    forensic_notes: str


class TheWitness:
    """Watchdog supervisor que previene quiebras de presupuesto y bucles infinitos."""

    def __init__(
        self,
        max_token_budget: int = 40000,
        max_consecutive_fails: int = 3,
        autopsy_dir: str = "storage/autopsy_reports"
    ):
        self.max_token_budget = max_token_budget
        self.max_consecutive_fails = max_consecutive_fails
        self.autopsy_dir = autopsy_dir
        os.makedirs(self.autopsy_dir, exist_ok=True)
        self.kills_count = 0

    def evaluate_polecat(
        self,
        bead: BeadItem,
        ledger: BeadsLedger,
        last_error: str = ""
    ) -> tuple[bool, str | None]:
        """Evalúa las constantes vitales del agente.
        
        Retorna:
            (should_kill: bool, reason: str | None)
        """
        # 1. Regla de Presupuesto Máximo de Tokens
        if bead.tokens_spent > bead.token_budget:
            reason = f"TOKEN_BUDGET_EXHAUSTION: Gastó {bead.tokens_spent:,} tokens superando el límite de {bead.token_budget:,}."
            self._execute_kill(bead, ledger, reason, last_error)
            return True, reason

        # 2. Regla de Tres Fallos Consecutivos (Anti-Bucle Infinito)
        if bead.consecutive_test_fails >= self.max_consecutive_fails:
            reason = f"INFINITE_LOOP_DETECTED: El agente falló {bead.consecutive_test_fails} veces consecutivas el mismo test sin progresar."
            self._execute_kill(bead, ledger, reason, last_error)
            return True, reason

        return False, None

    def _execute_kill(
        self,
        bead: BeadItem,
        ledger: BeadsLedger,
        reason: str,
        last_error: str
    ) -> AutopsyReport:
        self.kills_count += 1
        now_iso = datetime.now(timezone.utc).isoformat()
        autopsy_id = f"AUTOPSY-{bead.bead_id}-{self.kills_count:03d}"

        report = AutopsyReport(
            autopsy_id=autopsy_id,
            bead_id=bead.bead_id,
            timestamp=now_iso,
            kill_reason=reason,
            tokens_consumed=bead.tokens_spent,
            token_budget=bead.token_budget,
            consecutive_test_fails=bead.consecutive_test_fails,
            last_error_summary=last_error or "N/A",
            forensic_notes="Terminación forzada ejecutada por The Witness. Worktree congelado para análisis de seguridad."
        )

        # Actualizar ledger
        ledger.update_status(
            bead_id=bead.bead_id,
            status=BeadStatus.KILLED,
            kill_reason=reason
        )

        # Guardar autopsia en disco
        out_file = os.path.join(self.autopsy_dir, f"{bead.bead_id}_autopsy.json")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(report.model_dump(), indent=2, ensure_ascii=False))

        return report

    def list_autopsies(self) -> list[AutopsyReport]:
        reports = []
        if not os.path.exists(self.autopsy_dir):
            return reports
        for fname in os.listdir(self.autopsy_dir):
            if fname.endswith("_autopsy.json"):
                fpath = os.path.join(self.autopsy_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.loads(f.read())
                        reports.append(AutopsyReport.model_validate(data))
                except Exception:
                    pass
        return reports
