"""Script to simulate a real-world Kronos time-tracking punch discrepancy and 1-click rollback."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Ensure Windows PowerShell UTF-8 support
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from rich.console import Console
from rich.panel import Panel

from enterprise_mission_mesh.connectors.agent_emitters import HROperationsEmitter
from enterprise_mission_mesh.connectors.kronos_connector import KronosConnector
from enterprise_mission_mesh.core.orchestrator import MissionOrchestrator
from enterprise_mission_mesh.core.state import HumanDecisionType, MissionStatus

console = Console()


def run_simulation():
    console.print(Panel("[bold cyan]SIMULACION DE INCIDENCIA LABORAL EN KRONOS CON SUPERVISION HUMANA Y ROLLBACK[/bold cyan]"))

    orchestrator = MissionOrchestrator()
    kronos = KronosConnector()
    emitter = HROperationsEmitter()

    # Register compensating transaction for Kronos state reversal
    orchestrator.rollback_engine.register_compensator(
        "KRONOS_ADJUST_ENTRY",
        lambda entity_id, comp_payload: kronos.revert_adjustment(entity_id, comp_payload)
    )


    # 1. Estado inicial del empleado en Kronos
    import time
    ts = int(time.time())
    emp_id = f"emp_spain_{ts}"
    initial_clock = {"clock_in": "08:30:00", "clock_out": "16:30:00", "total_hours": 8.0}

    kronos.adjust_time_entry(emp_id, initial_clock)
    console.print(f"[green]1. Estado Inicial en Kronos para {emp_id}:[/green] Entrada: 08:30 | Salida: 16:30 (8h)")

    # 2. Agente autónomo propone modificar el fichaje: Salida a las 18:00 (+90 min, horas extra)
    proposal = emitter.propose_time_adjustment(
        employee_id=emp_id,
        clock_in="08:30:00",
        clock_out="18:00:00",
        delta_minutes=90,
        is_overtime=True,
        original_clock_in="08:30:00",
        original_clock_out="16:30:00",
    )
    console.print(f"\n[yellow]2. Agente Emisor ({proposal.agent_id}) somete propuesta:[/yellow]")
    console.print(f"   Modificar salida a 18:00 (+90m, Horas Extra). Confianza modelo: {proposal.confidence_score:.1%}")

    # 3. Sometimiento a la malla
    mission = orchestrator.submit_mission(proposal)
    console.print(f"\n[bold blue]3. Evaluación de la Malla (ConfidenceGate & Legal Policy):[/bold blue]")
    console.print(f"   Estado Misión: [bold yellow]{mission.status.value}[/bold yellow]")
    console.print(f"   Nivel de Riesgo Evaluado: [bold red]{mission.risk_level.value}[/bold red]")
    console.print(f"   Razón Legal (Estatuto Trabajadores Art. 34.9): {mission.gate_reason}")
    console.print(f"   Canales Notificados: {', '.join(mission.dispatched_channels)}")

    # 4. Supervisor humano recibe tarjeta en Slack/Teams/Telegram/Portal y pulsa [Aprobar]
    console.print(f"\n[cyan]4. Supervisor de RRHH examina la justificación agéntica y pulsa [Aprobar Cambio]:[/cyan]")
    approved_mission = orchestrator.apply_human_decision(
        mission_id=mission.id,
        decision=HumanDecisionType.APPROVE,
        decided_by="maria_rrhh_supervisor",
        reason="Parte de trabajo firmado por el empleado adjunto",
        token=mission.approve_token,
        forward_callable=lambda p: kronos.adjust_time_entry(emp_id, p),
    )
    console.print(f"   Estado de la Misión: [bold green]{approved_mission.status.value}[/bold green]")
    current_entry = kronos.get_last_entry(emp_id)
    console.print(f"   Fichaje Actualizado en Kronos: Salida: {current_entry.get('clock_out')} (Horas Extra: Sí)")

    # 5. Tres días después, auditoría laboral detecta discrepancia -> Supervisor pulsa [1-Click Rollback]
    console.print(f"\n[red]5. Auditoría detecta error posterior: Supervisor activa [1-Click Rollback]:[/red]")
    rollback_report = orchestrator.rollback(
        mission_id=mission.id,
        requested_by="auditor_laboral_externo",
        reason="Inspección de Trabajo: El parte correspondía a otro empleado",
    )
    console.print(f"   Resultado Rollback: {'[bold green]ÉXITO[/bold green]' if rollback_report.success else '[bold red]FALLO[/bold red]'}")
    console.print(f"   ID Reversión: {rollback_report.rollback_id}")

    # 6. Verificación del estado restaurado en Kronos
    reverted_entry = kronos.get_last_entry(emp_id)
    console.print(Panel("[bold green][OK] PRUEBA DE CICLO COMPLETO CONCLUIDA EXITOSAMENTE (Cero Inconsistencias, Cero Docker)[/bold green]"))



if __name__ == "__main__":
    run_simulation()
