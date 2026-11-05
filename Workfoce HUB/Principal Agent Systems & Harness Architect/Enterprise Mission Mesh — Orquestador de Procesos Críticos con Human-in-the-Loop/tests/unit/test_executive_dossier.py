"""Unit tests for ExecutiveDossierGenerator (HTML & PDF)."""

from pathlib import Path
from enterprise_mission_mesh.core.state import (
    AgentEmitterType,
    Mission,
    MissionStatus,
    RiskLevel,
)
from enterprise_mission_mesh.reporting.executive_dossier import ExecutiveDossierGenerator
from enterprise_mission_mesh.saga.action_ledger import ActionLedger


def test_executive_dossier_html_generation(tmp_path: Path):
    ledger = ActionLedger(db_path=str(tmp_path / "dossier_test.db"))
    for i in range(5):
        m = Mission(
            idempotency_key=f"dossier_m_{i}",
            agent_id="hr-specialist",
            agent_type=AgentEmitterType.HR_OPERATIONS,
            action_type="KRONOS_ADJUST_ENTRY",
            target_entity_id=f"emp_{i}",
            confidence_score=0.98,
            risk_level=RiskLevel.HIGH,
            status=MissionStatus.COMPLETED,
            decided_by="supervisor_rrhh",
        )
        ledger.record_mission(m)

    generator = ExecutiveDossierGenerator(ledger, output_dir=str(tmp_path / "out"))
    html_path = generator.generate_html_dossier("test_dossier.html")

    assert html_path.exists()
    content = html_path.read_text(encoding="utf-8")
    assert "Dossier Ejecutivo de Auditoría" in content
    assert "hr-specialist" in content


def test_executive_dossier_pdf_generation(tmp_path: Path):
    ledger = ActionLedger(db_path=str(tmp_path / "pdf_test.db"))
    generator = ExecutiveDossierGenerator(ledger, output_dir=str(tmp_path / "out"))
    pdf_path = generator.generate_pdf_dossier("test_dossier.pdf")
    if pdf_path:
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
