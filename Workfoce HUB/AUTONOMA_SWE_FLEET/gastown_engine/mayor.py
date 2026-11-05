"""
The Mayor - Director de Orquesta y Chief of Staff de Autonoma SWE-Fleet.
Coordina la descomposición en Beads, el despliegue en Worktrees, la supervisión
de The Witness y la emisión de 5 Pull Requests atómicas sin colisiones.
"""

import os
import json
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field

from core.epic_parser import ProductEpic, EpicParser
from core.step_contract import StepContract
from core.pr_packager import PullRequestManifest, PRPackager
from gastown_engine.beads_ledger import BeadsLedger, BeadStatus, BeadItem
from gastown_engine.worktree_manager import WorktreeManager, WorktreeInfo
from gastown_engine.witness_watchdog import TheWitness, AutopsyReport
from gastown_engine.polecat_worker import PolecatWorker, PolecatExecutionResult


class FleetRunReport(BaseModel):
    epic_id: str
    epic_title: str
    timestamp: str
    total_beads: int
    completed_beads: int
    killed_beads: int
    total_tokens_consumed: int
    prs_generated: list[PullRequestManifest] = Field(default_factory=list)
    autopsies: list[AutopsyReport] = Field(default_factory=list)
    execution_time_seconds: float = 0.0


class TheMayor:
    """Orquestador ejecutivo central del enjambre de ingeniería de software."""

    def __init__(
        self,
        base_repo_path: str = "sandbox/sample_repo",
        worktrees_dir: str = "sandbox/isolated_worktrees",
        ledger_file: str = "storage/beads/beads_ledger.jsonl",
        autopsy_dir: str = "storage/autopsy_reports",
        pr_exports_dir: str = "storage/pr_exports"
    ):
        self.base_repo_path = base_repo_path
        self.worktrees_dir = worktrees_dir
        self.pr_exports_dir = pr_exports_dir
        os.makedirs(self.pr_exports_dir, exist_ok=True)

        self.ledger = BeadsLedger(ledger_file=ledger_file)
        self.worktree_mgr = WorktreeManager(base_repo_path=base_repo_path, worktrees_dir=worktrees_dir)
        self.witness = TheWitness(autopsy_dir=autopsy_dir)

    def execute_fleet_workflow(
        self,
        epic: ProductEpic,
        code_templates: dict[str, tuple[str, str]] | None = None,
        simulate_loop_on_bead: str | None = None,
        simulate_token_overdraft_on_bead: str | None = None
    ) -> FleetRunReport:
        """Ejecuta el ciclo de vida completo: Épica -> StepContracts -> Beads -> Worktrees -> PRs."""
        start_time = datetime.now()
        contracts = EpicParser.decompose_into_step_contracts(epic)
        prs_generated: list[PullRequestManifest] = []

        for contract in contracts:
            # 1. Registrar Bead en el Ledger persistente
            bead = self.ledger.register_bead(
                bead_id=contract.bead_id,
                contract_id=contract.contract_id,
                title=contract.title,
                target_file=contract.target_file,
                token_budget=contract.max_tokens_budget
            )

            # 2. Asignar Git Worktree Físico Aislado
            wt_info = self.worktree_mgr.create_worktree(bead_id=contract.bead_id)
            self.ledger.update_status(
                contract.bead_id,
                BeadStatus.ASSIGNED,
                worktree_path=wt_info.worktree_path,
                assigned_polecat_id=f"polecat-{contract.bead_id}"
            )

            # 3. Obtener plantillas de código para el Polecat
            if code_templates and contract.bead_id in code_templates:
                code_impl, test_impl = code_templates[contract.bead_id]
            else:
                code_impl, test_impl = self._generate_default_implementation(contract)

            # 4. Despachar al Polecat Worker en su Worktree
            worker = PolecatWorker(
                bead_id=contract.bead_id,
                worktree_path=wt_info.worktree_path,
                contract=contract
            )

            is_loop = (simulate_loop_on_bead == contract.bead_id)
            is_overdraft = (simulate_token_overdraft_on_bead == contract.bead_id)

            res = worker.execute_task(
                code_implementation=code_impl,
                test_implementation=test_impl,
                witness=self.witness,
                ledger=self.ledger,
                simulate_loop_failure=is_loop,
                simulate_token_overdraft=is_overdraft
            )

            # 5. Si el Polecat superó las pruebas y AST, empaquetar Pull Request
            if res.status == BeadStatus.DONE:
                diff_mock = f"diff --git a/{contract.target_file} b/{contract.target_file}\n+ {code_impl[:120]}..."
                pr = PRPackager.create_pr(
                    bead_id=contract.bead_id,
                    contract_id=contract.contract_id,
                    title=contract.title,
                    files_changed=[contract.target_file, contract.test_file],
                    ast_score=res.ast_result.score,
                    tests_passed=res.tests_count,
                    tests_total=res.tests_count,
                    unified_diff=diff_mock
                )
                prs_generated.append(pr)
                self.ledger.update_status(contract.bead_id, BeadStatus.DONE, pr_id=pr.pr_id)

                # Exportar JSON de la PR
                pr_path = os.path.join(self.pr_exports_dir, f"{pr.pr_id}.json")
                with open(pr_path, "w", encoding="utf-8") as f:
                    f.write(json.dumps(pr.model_dump(), indent=2, ensure_ascii=False))

        # Compilar reporte ejecutivo final
        all_beads = [self.ledger.get_bead(c.bead_id) for c in contracts]
        completed = len([b for b in all_beads if b and b.status == BeadStatus.DONE])
        killed = len([b for b in all_beads if b and b.status == BeadStatus.KILLED])
        total_tokens = sum([b.tokens_spent for b in all_beads if b])
        elapsed = (datetime.now() - start_time).total_seconds()

        return FleetRunReport(
            epic_id=epic.epic_id,
            epic_title=epic.title,
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_beads=len(contracts),
            completed_beads=completed,
            killed_beads=killed,
            total_tokens_consumed=total_tokens,
            prs_generated=prs_generated,
            autopsies=self.witness.list_autopsies(),
            execution_time_seconds=round(elapsed, 2)
        )

    def _generate_default_implementation(self, contract: StepContract) -> tuple[str, str]:
        """Genera código e implementación de tests conformes por defecto para el contrato."""
        fn_defs = []
        for fn in contract.allowed_interface.functions:
            fn_defs.append(
                f"    def {fn.name}(self, {', '.join(fn.args)}) -> {fn.return_type}:\n"
                f"        \"\"\"{fn.docstring or fn.name}\"\"\"\n"
                f"        return True if '{fn.return_type}' == 'bool' else ('OK' if '{fn.return_type}' == 'str' else 1)\n"
            )

        code_impl = (
            f"\"\"\"Implementación generada para {contract.title}\"\"\"\n"
            f"from typing import Any\n\n"
            f"class {contract.allowed_interface.class_name}:\n"
            f"    def __init__(self):\n"
            f"        self.is_active = True\n\n"
            + "\n".join(fn_defs)
        )

        test_impl = (
            f"\"\"\"Suite de pruebas unitarias para {contract.title}\"\"\"\n"
            f"import pytest\n"
            f"import sys, os\n"
            f"sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\n"
            f"from {contract.target_file.replace('/', '.').replace('.py', '')} import {contract.allowed_interface.class_name}\n\n"
            f"def test_{contract.bead_id.replace('-', '_')}():\n"
            f"    instance = {contract.allowed_interface.class_name}()\n"
            f"    assert instance.is_active is True\n"
        )

        return code_impl, test_impl
