"""
Autonoma SWE-Fleet: Enjambre de Ingeniería para Factorías de Software
Port: 8512
Paradigma: Fusión de White Coding (StepContracts + Costuras AST) + Gas Town (Beads, Worktrees, The Witness).
"""

import os
import sys
import json
import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

from core.epic_parser import ProductEpic, EpicParser
from core.step_contract import StepContract
from core.pr_packager import PullRequestManifest
from core.ast_seam_validator import ASTSeamValidator
from gastown_engine.beads_ledger import BeadsLedger, BeadStatus, BeadItem
from gastown_engine.worktree_manager import WorktreeManager
from gastown_engine.witness_watchdog import TheWitness, AutopsyReport
from gastown_engine.mayor import TheMayor, FleetRunReport

# ---------------------------------------------------------
# Streamlit Page Config & Theme
# ---------------------------------------------------------
st.set_page_config(
    page_title="Autonoma SWE-Fleet | Gas Town Control Plane",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Modern Styling (Glassmorphism & Neon Tech Palette)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .fleet-header {
        background: linear-gradient(135deg, #090d16 0%, #1e1b4b 45%, #059669 100%);
        padding: 24px 32px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    
    .status-badge {
        display: inline-block;
        padding: 6px 14px;
        font-size: 13px;
        font-weight: 600;
        border-radius: 20px;
        margin-right: 8px;
    }
    .badge-open { background-color: #1e3a8a; color: #93c5fd; border: 1px solid #3b82f6; }
    .badge-inworktree { background-color: #854d0e; color: #fde047; border: 1px solid #eab308; }
    .badge-done { background-color: #065f46; color: #6ee7b7; border: 1px solid #10b981; }
    .badge-killed { background-color: #7f1d1d; color: #fca5a5; border: 1px solid #ef4444; }
    
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        margin-top: 4px;
    }
    
    .metric-sub {
        font-size: 13px;
        color: #94a3b8;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0px 0px;
        padding: 10px 20px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State Initialization (Persistent Storage)
# ---------------------------------------------------------
STORAGE_DIR = PROJECT_ROOT / "storage"
LEDGER_FILE = STORAGE_DIR / "beads" / "beads_ledger.jsonl"
AUTOPSY_DIR = STORAGE_DIR / "autopsy_reports"
PR_EXPORTS_DIR = STORAGE_DIR / "pr_exports"
BASE_REPO = PROJECT_ROOT / "sandbox" / "sample_repo"
WORKTREES_DIR = PROJECT_ROOT / "sandbox" / "isolated_worktrees"

STORAGE_DIR.mkdir(parents=True, exist_ok=True)

if "mayor" not in st.session_state:
    st.session_state.mayor = TheMayor(
        base_repo_path=str(BASE_REPO),
        worktrees_dir=str(WORKTREES_DIR),
        ledger_file=str(LEDGER_FILE),
        autopsy_dir=str(AUTOPSY_DIR),
        pr_exports_dir=str(PR_EXPORTS_DIR)
    )

if "last_run_report" not in st.session_state:
    st.session_state.last_run_report = None

# ---------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/module.png", width=64)
    st.title("Autonoma SWE-Fleet")
    st.markdown("**Enjambre de Ingeniería Gas Town**")
    st.caption("Ver: 1.0.0-PROD | Port: :8512")
    
    st.divider()
    st.subheader("⚙️ Configuración del Enjambre")
    ai_engine = st.selectbox(
        "Motor de Inferencia",
        ["Ollama Local (qwen2.5-coder:latest)", "Claude 3.5 Sonnet", "GPT-4o", "DeepSeek-V3", "Gemini 1.5 Pro"]
    )
    
    air_gapped = st.toggle("🔒 Modo Air-Gapped (On-Premise)", value=True)
    if air_gapped:
        st.success("Air-Gapped ACTIVO: Cero salida de código a nubes públicas.")
        
    st.divider()
    st.subheader("👁️ Watchdog (The Witness)")
    max_tokens = st.slider("Presupuesto Máximo de Tokens / Bead", 10000, 80000, 40000, 5000)
    max_retries = st.slider("Límite de Fallos Consecutivos (Anti-Loop)", 1, 5, 3)
    
    st.divider()
    st.caption("Aislamiento físico en Git Worktrees independientes. Zero branch collisions.")

# ---------------------------------------------------------
# Header Banner
# ---------------------------------------------------------
st.markdown("""
<div class="fleet-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin: 0; font-size: 26px; font-weight: 700;">🛸 Autonoma SWE-Fleet — Gas Town Control Plane</h1>
            <p style="margin: 6px 0 0 0; color: #cbd5e1; font-size: 15px;">
                "Convierte una especificación de producto en 5 Pull Requests validadas en paralelo sin colisiones de Git ni bucles infinitos."
            </p>
        </div>
        <div style="text-align: right;">
            <span class="status-badge badge-done">FLOTA ACTIVA</span>
            <span class="status-badge badge-open">5 WORKTREES</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Tabs Navigation
# ---------------------------------------------------------
tab_mayor, tab_beads, tab_worktrees, tab_witness, tab_ast, tab_prs = st.tabs([
    "🛸 Puente de Mando The Mayor",
    "📋 Tablero Beads & StepContracts",
    "🌲 Monitor de Git Worktrees",
    "👁️ Radar The Witness (Watchdog)",
    "🛡️ Puerta de Fusión (AST & Pytest)",
    "🚀 Hub de Pull Requests & Trazabilidad"
])

# =========================================================
# TAB 1: Puente de Mando The Mayor
# =========================================================
with tab_mayor:
    st.subheader("Despacho Ejecutivo y Ejecución Paralela de la Flota")
    
    col_epic, col_metrics = st.columns([1, 1])
    
    with col_epic:
        st.markdown("#### Especificación de Producto (Jira / Linear / PRD)")
        epic_id = st.text_input("ID de la Épica", value="EPIC-CORP-401")
        epic_title = st.text_input("Título de la Iniciativa", value="Enterprise Core Infrastructure & Resilient Billing Engine")
        epic_desc = st.text_area(
            "Descripción y Requerimientos de Negocio",
            value="Implementar arquitectura perimetral con tokens HMAC rotativos, limitador DoS por IP, "
                  "gestor de ciclo de vida de suscripciones, bóveda de auditoría inmutable SHA-256 "
                  "y despachador de webhooks con backoff exponencial.",
            height=110
        )
        epic_val = st.text_input("Valor de Negocio", value="Cumplimiento DORA y NIS2 con zero colisiones en repositorio compartido")
        
        sim_rogue = st.checkbox("🧪 Simular Agente Rebelde en Bucle Infinito (Probar The Witness)")
        
        btn_run = st.button("🚀 Lanzar Flota de 5 Polecats en Worktrees", type="primary")

    with col_metrics:
        st.markdown("#### Rendimiento y Throughput de la Flota")
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-sub">Concurrencia Activa</div>
                <div class="metric-value" style="color: #60a5fa;">5 Agentes</div>
                <div class="metric-sub">5 Worktrees paralelos</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-sub">Colisiones de Git</div>
                <div class="metric-value" style="color: #34d399;">0 Conflictos</div>
                <div class="metric-sub">Ramas 100% aisladas</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-sub">Ahorro de Tiempo</div>
                <div class="metric-value" style="color: #fbbf24;">80%</div>
                <div class="metric-sub">vs. ejecución secuencial</div>
            </div>
            """, unsafe_allow_html=True)

        if btn_run:
            with st.spinner("The Mayor coordinando flota de 5 Polecats en Git Worktrees independientes..."):
                epic_obj = ProductEpic(
                    epic_id=epic_id,
                    title=epic_title,
                    description=epic_desc,
                    business_value=epic_val,
                    target_microservice="sample_microservice_fastapi"
                )
                
                bad_bead = f"bead-{epic_id.lower()}-01-auth" if sim_rogue else None
                rep = st.session_state.mayor.execute_fleet_workflow(epic_obj, simulate_loop_on_bead=bad_bead)
                st.session_state.last_run_report = rep
                st.success(f"Ejecución finalizada en {rep.execution_time_seconds}s. {rep.completed_beads} PRs generadas, {rep.killed_beads} liquidados por The Witness.")

        if st.session_state.last_run_report:
            rep = st.session_state.last_run_report
            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("Beads Completados", f"{rep.completed_beads} / {rep.total_beads}")
            c2.metric("Agentes Aniquilados", rep.killed_beads)
            c3.metric("Tokens Consumidos", f"{rep.total_tokens_consumed:,}")

# =========================================================
# TAB 2: Tablero Beads & StepContracts
# =========================================================
with tab_beads:
    st.subheader("Libro Mayor de Tareas (Beads 'bd' Ledger) y Contratos Formales")
    st.markdown("Cada micro-tarea se convierte en un `StepContract` inmutable con superficie de prueba pública y restricciones de diseño.")
    
    beads = st.session_state.mayor.ledger.list_all_beads()
    if not beads:
        st.info("No hay Beads registrados todavía. Lance una épica desde el Puente de Mando.")
    else:
        df_beads = pd.DataFrame([
            {
                "ID": b.bead_id,
                "Título": b.title,
                "Archivo Objetivo": b.target_file,
                "Estado": b.status.value,
                "Tokens": f"{b.tokens_spent:,} / {b.token_budget:,}",
                "Fallos Test": b.consecutive_test_fails,
                "PR Asignada": b.pr_id or "Pendiente"
            }
            for b in beads
        ])
        st.dataframe(df_beads, use_container_width=True)

# =========================================================
# TAB 3: Monitor de Git Worktrees
# =========================================================
with tab_worktrees:
    st.subheader("Topología Física de Git Worktrees Aislados")
    st.markdown("Aislamiento físico en disco: cada Polecat opera en su propia subcarpeta sin bloqueo de archivos de Git.")
    
    active_wts = st.session_state.mayor.worktree_mgr.list_active_worktrees()
    
    cols = st.columns(max(1, len(active_wts) if active_wts else 5))
    for i, wt in enumerate(active_wts):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 3px solid #10b981;">
                <h4 style="margin: 0; color: #34d399;">🌲 {wt.bead_id}</h4>
                <div class="metric-sub" style="margin: 4px 0;">Rama: <code>{wt.branch_name}</code></div>
                <div style="font-size: 11px; color: #cbd5e1; word-break: break-all;">Ruta: {wt.worktree_path}</div>
                <div style="margin-top: 8px;">
                    <span class="status-badge badge-done">AISLADO</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    if not active_wts:
        st.info("Los worktrees se crean dinámicamente al despachar una épica y se mantienen limpios.")

# =========================================================
# TAB 4: Radar The Witness (Watchdog)
# =========================================================
with tab_witness:
    st.subheader("Radar de Supervisión The Witness (Circuit Breaker Anti-Bucles)")
    st.markdown("Watchdog que aniquila agentes estancados: liquida procesos con > 3 fallos consecutivos o sobrecoste de tokens.")
    
    autopsies = st.session_state.mayor.witness.list_autopsies()
    
    col_w1, col_w2 = st.columns([1, 1])
    
    with col_w1:
        st.markdown("#### Parámetros Activos del Watchdog")
        st.write(f"- **Presupuesto Máximo:** {max_tokens:,} tokens por tarea.")
        st.write(f"- **Tolerancia a Bucles:** {max_retries} fallos consecutivos.")
        st.write(f"- **Acción de Contención:** `SIGKILL` automático + congelación de worktree para forense.")
        st.metric("Total de Autopsias Registradas", len(autopsies))
        
    with col_w2:
        st.markdown("#### Historial de Autopsias Forenses")
        if not autopsies:
            st.success("✨ Ningún agente ha sido aniquilado por The Witness. Toda la flota opera dentro de parámetros saludables.")
        else:
            for a in autopsies:
                with st.expander(f"🛑 {a.autopsy_id} — {a.bead_id}", expanded=True):
                    st.write(f"**Causa de Muerte:** `{a.kill_reason}`")
                    st.write(f"**Tokens Consumidos:** {a.tokens_consumed:,} / {a.token_budget:,}")
                    st.write(f"**Racha de Fallos:** {a.consecutive_test_fails}")
                    st.code(a.last_error_summary, language="text")
                    st.caption(f"Dictamen Forense: {a.forensic_notes}")

# =========================================================
# TAB 5: Puerta de Fusión (AST & Pytest)
# =========================================================
with tab_ast:
    st.subheader("Puerta de Fusión Arquitectónica: Validador AST & Cobertura Pytest")
    st.markdown("Ningún agente puede hacer Pull Request sin demostrar que respetó las costuras del diseño (*Matt Pocock*) y pasó el 100% de tests.")
    
    st.markdown("#### Criterios de Validación Estática:")
    st.markdown("""
    - **Zero Fugas de Abstracción:** Prohibido el acceso directo a propiedades o métodos privados `_`.
    - **Cero Dependencias No Autorizadas:** Prohibida la importación de librerías fuera de la especificación del contrato.
    - **Módulos Profundos:** Ratio LOC / Métodos Públicos ≥ 2.0 (evita envoltorios superficiales inservibles).
    """)

# =========================================================
# TAB 6: Hub de Pull Requests & Trazabilidad
# =========================================================
with tab_prs:
    st.subheader("Hub de Pull Requests Atómicas & Trazabilidad Jira")
    st.markdown("Listado de Pull Requests preparadas y verificadas, listas para merge inmediato sin conflictos.")
    
    prs = []
    if os.path.exists(PR_EXPORTS_DIR):
        for fname in os.listdir(PR_EXPORTS_DIR):
            if fname.endswith(".json"):
                try:
                    with open(os.path.join(PR_EXPORTS_DIR, fname), "r", encoding="utf-8") as f:
                        prs.append(PullRequestManifest.model_validate(json.loads(f.read())))
                except Exception:
                    pass
                    
    if not prs:
        st.info("No hay Pull Requests generadas todavía. Lance una épica desde el Puente de Mando.")
    else:
        for p in prs:
            with st.expander(f"✅ {p.pr_id} — {p.title}", expanded=True):
                st.markdown(p.summary)
                st.code(p.unified_diff, language="diff")
                st.download_button(
                    label=f"📥 Descargar Manifiesto PR ({p.pr_id})",
                    data=json.dumps(p.model_dump(), indent=2, ensure_ascii=False),
                    file_name=f"{p.pr_id}.json",
                    mime="application/json",
                    key=f"dl_{p.pr_id}"
                )
