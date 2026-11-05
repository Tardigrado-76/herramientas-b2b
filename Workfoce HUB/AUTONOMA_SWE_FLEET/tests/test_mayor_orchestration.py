import pytest
import os
import tempfile
from core.epic_parser import ProductEpic
from gastown_engine.mayor import TheMayor

def test_mayor_orchestrates_5_prs_in_parallel():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_repo = os.path.abspath("sandbox/sample_repo")
        wt_dir = os.path.join(tmpdir, "worktrees")
        ledger_file = os.path.join(tmpdir, "ledger.jsonl")
        autopsy_dir = os.path.join(tmpdir, "autopsies")
        pr_dir = os.path.join(tmpdir, "prs")

        mayor = TheMayor(
            base_repo_path=base_repo,
            worktrees_dir=wt_dir,
            ledger_file=ledger_file,
            autopsy_dir=autopsy_dir,
            pr_exports_dir=pr_dir
        )

        epic = ProductEpic(
            epic_id="EPIC-101",
            title="Enterprise Cloud Security & Resilient Billing Suite",
            description="Módulo de seguridad perimetral, suscripciones recurrentes y trazabilidad inmutable.",
            business_value="Cumplimiento DORA y NIS2 con zero churn en pasarelas",
            target_microservice="sample_microservice_fastapi"
        )

        report = mayor.execute_fleet_workflow(epic)

        assert report.total_beads == 5
        assert report.completed_beads == 5
        assert report.killed_beads == 0
        assert len(report.prs_generated) == 5
        for pr in report.prs_generated:
            assert pr.merge_ready is True
            assert pr.ast_score >= 80

def test_mayor_handles_witness_circuit_breaker_on_rogue_agent():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_repo = os.path.abspath("sandbox/sample_repo")
        wt_dir = os.path.join(tmpdir, "worktrees")
        ledger_file = os.path.join(tmpdir, "ledger.jsonl")
        autopsy_dir = os.path.join(tmpdir, "autopsies")
        pr_dir = os.path.join(tmpdir, "prs")

        mayor = TheMayor(
            base_repo_path=base_repo,
            worktrees_dir=wt_dir,
            ledger_file=ledger_file,
            autopsy_dir=autopsy_dir,
            pr_exports_dir=pr_dir
        )

        epic = ProductEpic(
            epic_id="EPIC-102",
            title="Simulated Rogue Agent Test",
            description="Prueba de contención de The Witness",
            business_value="Protección de presupuesto",
            target_microservice="sample_microservice_fastapi"
        )

        # Trigger simulated loop on the first bead
        first_bead_id = "bead-epic-102-01-auth"
        report = mayor.execute_fleet_workflow(epic, simulate_loop_on_bead=first_bead_id)

        assert report.total_beads == 5
        assert report.completed_beads == 4
        assert report.killed_beads == 1
        assert len(report.autopsies) >= 1
