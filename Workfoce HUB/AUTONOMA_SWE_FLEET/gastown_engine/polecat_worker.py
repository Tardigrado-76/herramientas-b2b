"""
Polecat Worker - Agente de Codificación Aislado en un Git Worktree.
Implementa el StepContract asignado, ejecuta pruebas locales y responde a The Witness.
"""

import os
import subprocess
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel
from core.step_contract import StepContract
from core.ast_seam_validator import ASTSeamValidator, ASTValidationResult
from gastown_engine.beads_ledger import BeadItem, BeadStatus, BeadsLedger
from gastown_engine.witness_watchdog import TheWitness


class PolecatExecutionResult(BaseModel):
    bead_id: str
    worktree_path: str
    target_file: str
    code_generated: str
    test_generated: str
    ast_result: ASTValidationResult
    pytest_passed: bool
    tests_count: int
    tokens_consumed: int
    consecutive_fails: int
    status: BeadStatus
    message: str


class PolecatWorker:
    """Obrero de codificación autónomo asignado a un worktree independiente."""

    def __init__(self, bead_id: str, worktree_path: str, contract: StepContract):
        self.bead_id = bead_id
        self.worktree_path = worktree_path
        self.contract = contract
        self.tokens_used = 0
        self.consecutive_fails = 0

    def execute_task(
        self,
        code_implementation: str,
        test_implementation: str,
        witness: TheWitness,
        ledger: BeadsLedger,
        simulate_loop_failure: bool = False,
        simulate_token_overdraft: bool = False
    ) -> PolecatExecutionResult:
        """Escribe el código y las pruebas en el worktree, corre pytest y valida AST."""
        # Contabilizar tokens consumidos
        self.tokens_used += 8500 if not simulate_token_overdraft else 52000
        
        bead = ledger.get_bead(self.bead_id)
        if not bead:
            bead = ledger.register_bead(
                bead_id=self.bead_id,
                contract_id=self.contract.contract_id,
                title=self.contract.title,
                target_file=self.contract.target_file,
                token_budget=self.contract.max_tokens_budget
            )

        bead.tokens_spent = self.tokens_used
        bead.worktree_path = self.worktree_path
        bead.status = BeadStatus.IN_WORKTREE
        ledger.update_status(self.bead_id, BeadStatus.IN_WORKTREE, tokens_spent=self.tokens_used)

        # 1. Supervisión temprana de The Witness por tokens
        should_kill, kill_reason = witness.evaluate_polecat(bead, ledger)
        if should_kill:
            return PolecatExecutionResult(
                bead_id=self.bead_id,
                worktree_path=self.worktree_path,
                target_file=self.contract.target_file,
                code_generated="",
                test_generated="",
                ast_result=ASTValidationResult(is_valid=False, score=0, violations=[kill_reason or ""]),
                pytest_passed=False,
                tests_count=0,
                tokens_consumed=self.tokens_used,
                consecutive_fails=self.consecutive_fails,
                status=BeadStatus.KILLED,
                message=kill_reason or "Agente eliminado por The Witness."
            )

        abs_target = os.path.join(self.worktree_path, self.contract.target_file)
        abs_test = os.path.join(self.worktree_path, self.contract.test_file)
        os.makedirs(os.path.dirname(abs_target), exist_ok=True)
        os.makedirs(os.path.dirname(abs_test), exist_ok=True)
        for d in [os.path.dirname(abs_target), os.path.dirname(abs_test)]:
            init_f = os.path.join(d, "__init__.py")
            if not os.path.exists(init_f):
                with open(init_f, "w", encoding="utf-8") as f:
                    f.write("# Package init\n")

        with open(abs_target, "w", encoding="utf-8") as f:
            f.write(code_implementation)
        with open(abs_test, "w", encoding="utf-8") as f:
            f.write(test_implementation)

        # 3. Validación de Costuras AST
        ast_res = ASTSeamValidator.validate_source(code_implementation, self.contract)

        # 4. Ejecución de Pytest en el worktree
        if simulate_loop_failure:
            self.consecutive_fails += 3  # Provocar disparo del circuit breaker
            bead.consecutive_test_fails = self.consecutive_fails
            pytest_passed = False
            tests_count = 1
            last_err = "AssertionError: Expected 200 OK, got 500 Internal Error (Infinite Loop Failure)"
        else:
            import sys
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.worktree_path) + os.pathsep + env.get("PYTHONPATH", "")
            pytest_res = subprocess.run(
                [sys.executable, "-m", "pytest", self.contract.test_file],
                cwd=self.worktree_path,
                env=env,
                capture_output=True,
                text=True
            )
            pytest_passed = (pytest_res.returncode == 0)
            tests_count = len(self.contract.scenarios) or 1
            last_err = pytest_res.stderr or pytest_res.stdout if not pytest_passed else ""
            if not pytest_passed:
                self.consecutive_fails += 1
            else:
                self.consecutive_fails = 0

        bead.consecutive_test_fails = self.consecutive_fails

        # 5. Supervisión de The Witness por fallos consecutivos
        should_kill, kill_reason = witness.evaluate_polecat(bead, ledger, last_error=last_err)
        if should_kill:
            return PolecatExecutionResult(
                bead_id=self.bead_id,
                worktree_path=self.worktree_path,
                target_file=self.contract.target_file,
                code_generated=code_implementation,
                test_generated=test_implementation,
                ast_result=ast_res,
                pytest_passed=False,
                tests_count=tests_count,
                tokens_consumed=self.tokens_used,
                consecutive_fails=self.consecutive_fails,
                status=BeadStatus.KILLED,
                message=kill_reason or "Agente eliminado por bucle infinito."
            )

        # 6. Evaluación de éxito de paso
        if ast_res.is_valid and pytest_passed:
            final_status = BeadStatus.DONE
            msg = "Completado con éxito: 100% Pytest superado y costura AST validada."
        else:
            final_status = BeadStatus.VALIDATING
            msg = f"Pendiente de corrección: AST Valid={ast_res.is_valid}, Pytest={pytest_passed}."

        ledger.update_status(
            self.bead_id,
            final_status,
            tokens_spent=self.tokens_used,
            consecutive_test_fails=self.consecutive_fails
        )

        return PolecatExecutionResult(
            bead_id=self.bead_id,
            worktree_path=self.worktree_path,
            target_file=self.contract.target_file,
            code_generated=code_implementation,
            test_generated=test_implementation,
            ast_result=ast_res,
            pytest_passed=pytest_passed,
            tests_count=tests_count,
            tokens_consumed=self.tokens_used,
            consecutive_fails=self.consecutive_fails,
            status=final_status,
            message=msg
        )
