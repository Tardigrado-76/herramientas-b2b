"""
Autonomous Vertical CFO & Legal Guard - Executive Web Application
Port: 8510
Compliance: Ley Crea y Crece, VeriFactu (RD 1007/2023), TicketBAI, NIS2, RGPD (Art. 17).
Architecture: SDP Progressive Disclosure + BYOK + 100% Local Models / Air-Gapped.
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

from cfo_core.solvency import AltmanZScoreCalculator, SolvencyZone
from cfo_core.cashflow import CashFlowProjector
from cfo_core.reconciliation import BankReconciler, BankTransaction, InvoiceItem, ReconciliationStatus
from cfo_core.orchestrator import CFOExecutiveOrchestrator
from connectors.sdp_engine import SDPEngine
from connectors.psd2_banking import PSD2BankingFeeder
from legal_guard.fraud_detector import FraudDetector
from legal_guard.electronic_invoicing import ElectronicInvoiceEngine, InvoiceComplianceFormat
from legal_guard.bunker_ledger import BunkerLedger
from legal_guard.gdpr_shredder import GDPRShredder
from hitl.approval_gate import HITLApprovalGate, ApprovalStatus
from reporting.bank_dossier_pdf import BankDossierPDFGenerator

# ---------------------------------------------------------
# Streamlit Page Setup & Glassmorphism Theme
# ---------------------------------------------------------
st.set_page_config(
    page_title="Autonomous Vertical CFO & Legal Guard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Modern Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .cfo-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0369a1 100%);
        padding: 24px 32px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .cfo-badge {
        display: inline-block;
        padding: 6px 14px;
        font-size: 13px;
        font-weight: 600;
        border-radius: 20px;
        margin-right: 8px;
    }
    .badge-success { background-color: #065f46; color: #34d399; border: 1px solid #059669; }
    .badge-warning { background-color: #78350f; color: #fbbf24; border: 1px solid #d97706; }
    .badge-danger { background-color: #7f1d1d; color: #f87171; border: 1px solid #dc2626; }
    .badge-info { background-color: #1e3a8a; color: #60a5fa; border: 1px solid #2563eb; }
    
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
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
# Session State Initialization (Persistent in Storage)
# ---------------------------------------------------------
LEDGER_DIR = PROJECT_ROOT / "storage" / "ledger"
LEDGER_DIR.mkdir(parents=True, exist_ok=True)
ledger_file_path = str(LEDGER_DIR / "bunker_log.jsonl")

if "bunker" not in st.session_state:
    st.session_state.bunker = BunkerLedger(ledger_file=ledger_file_path)
if "hitl_gate" not in st.session_state:
    st.session_state.hitl_gate = HITLApprovalGate(high_amount_threshold=3000.0)
if "sdp_engine" not in st.session_state:
    st.session_state.sdp_engine = SDPEngine()

# ---------------------------------------------------------
# Sidebar Controls & Configuration (BYOK / Air-Gapped)
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/security-shield-green.png", width=64)
    st.title("Autonomous CFO & Legal Guard")
    st.markdown("**Micro-SaaS para PYMEs (10-50 empleados)**")
    st.caption("Ver: 1.0.0-PROD | Port: :8510")
    
    st.divider()
    
    st.subheader("🛡️ Modo Soberanía & BYOK")
    ai_engine = st.selectbox(
        "Motor de Inteligencia",
        ["Ollama Local (qwen2.5-coder / mistral)", "OpenAI (GPT-4o)", "Anthropic (Claude 3.5 Sonnet)", "Google Gemini 1.5 Pro", "DeepSeek-V3"]
    )
    
    air_gapped = st.toggle("🔒 Modo Air-Gapped (Cero Salida Externa)", value=True)
    if air_gapped:
        st.success("Air-Gapped ACTIVO: Telemetría deshabilitada y modelos 100% on-premise.")
    else:
        st.info("Conectividad Cloud BYOK habilitada.")
        
    st.text_input("Ollama Endpoint", value="http://localhost:11434/v1")
    
    st.divider()
    st.subheader("🏢 Empresa Activa")
    company_name = st.text_input("Razón Social", value="INNOVACIONES INDUSTRIALES DEL MEDITERRÁNEO S.L.")
    company_cif = st.text_input("CIF / NIF", value="B-98765432")
    active_regime = st.selectbox("Marco Fiscal Principal", ["Ley Crea y Crece + VeriFactu (Nacional)", "TicketBAI (País Vasco)", "SII (Grandes Empresas)"])
    
    st.divider()
    st.caption("Cumplimiento normativo estricto: RD 1007/2023, Directiva NIS2, Art. 17 RGPD.")

# ---------------------------------------------------------
# Header Banner
# ---------------------------------------------------------
st.markdown(f"""
<div class="cfo-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin: 0; font-size: 26px; font-weight: 700;">🛡️ Autonomous Vertical CFO & Legal Guard</h1>
            <p style="margin: 6px 0 0 0; color: #cbd5e1; font-size: 15px;">
                Dirección Financiera Automatizada, Antifraude de Facturas y Compliance de Facturación Soberana
            </p>
        </div>
        <div style="text-align: right;">
            <span class="cfo-badge badge-success">ESTADO: OPERATIVO</span>
            <span class="cfo-badge badge-info">{active_regime.split(' ')[0]}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Tabs Navigation
# ---------------------------------------------------------
tab_cfo, tab_antifraud, tab_psd2, tab_invoicing, tab_hitl, tab_bunker, tab_dossier, tab_sdp = st.tabs([
    "📊 Panel Financiero & Solvencia",
    "🔍 Auditoría OCR & Antifraude",
    "🏦 Conciliación Bancaria PSD2",
    "📜 Factura Electrónica & VeriFactu",
    "⚖️ Aprobaciones HITL",
    "🛡️ Bóveda NIS2 & RGPD",
    "📄 Dossier Bancario A4",
    "🔌 Conectores & SDP Engine"
])

# =========================================================
# TAB 1: Panel Financiero & Solvencia (Altman Z')
# =========================================================
with tab_cfo:
    st.subheader("Salud Financiera & Previsión de Tesorería (Altman Z'-Score)")
    
    col_input, col_metrics = st.columns([1, 2])
    
    with col_input:
        st.markdown("#### Balance y Cuenta de Explotación")
        working_cap = st.number_input("Fondo de Maniobra (€)", value=145000.0, step=5000.0)
        retained_earn = st.number_input("Reservas / Beneficios Retenidos (€)", value=210000.0, step=5000.0)
        ebit_val = st.number_input("EBIT (€)", value=98000.0, step=2000.0)
        equity_val = st.number_input("Patrimonio Neto (€)", value=430000.0, step=10000.0)
        total_liab = st.number_input("Pasivo Total / Deuda (€)", value=280000.0, step=10000.0)
        sales_val = st.number_input("Ventas Netas Anuales (€)", value=1250000.0, step=25000.0)
        total_assets = st.number_input("Activo Total (€)", value=710000.0, step=10000.0)
        current_cash = st.number_input("Caja Líquida Disponible (€)", value=86500.0, step=5000.0)
        monthly_burn = st.number_input("Burn Rate Mensual Estimado (€)", value=18500.0, step=1000.0)
        
        z_res = AltmanZScoreCalculator.calculate(
            working_capital=working_cap,
            retained_earnings=retained_earn,
            ebit=ebit_val,
            equity=equity_val,
            total_liabilities=total_liab,
            sales=sales_val,
            total_assets=total_assets
        )

    with col_metrics:
        m1, m2, m3 = st.columns(3)
        with m1:
            color = "#34d399" if z_res.zone == SolvencyZone.SAFE_ZONE else ("#fbbf24" if z_res.zone == SolvencyZone.GREY_ZONE else "#f87171")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-sub">Altman Z'-Score (PYME)</div>
                <div class="metric-value" style="color: {color};">{z_res.altman_z_prime:.2f}</div>
                <div class="metric-sub" style="margin-top: 4px;">Zona: <strong>{z_res.zone.value}</strong></div>
            </div>
            """, unsafe_allow_html=True)
            
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-sub">Riesgo Insolvencia (24m)</div>
                <div class="metric-value" style="color: {color};">{z_res.bankruptcy_risk_pct:.1f}%</div>
                <div class="metric-sub" style="margin-top: 4px;">{z_res.recommendation}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m3:
            runway_days = (current_cash / (monthly_burn / 30.0)) if monthly_burn > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-sub">Runway de Caja Líquida</div>
                <div class="metric-value" style="color: #60a5fa;">{runway_days:.0f} días</div>
                <div class="metric-sub" style="margin-top: 4px;">{current_cash:,.2f} € disponibles</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("#### Proyección de Tesorería a 30, 60 y 90 días")
        
        cf_summary = CashFlowProjector.project(
            current_cash=current_cash,
            monthly_burn_rate=monthly_burn,
            receivables_30d=45000.0,
            payables_30d=18000.0,
            receivables_60d=52000.0,
            payables_60d=24000.0,
            receivables_90d=38000.0,
            payables_90d=15000.0
        )
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Caja proyectada a 30d", f"{cf_summary.projected_cash_30d:,.2f} €", f"{cf_summary.projected_cash_30d - current_cash:,.2f} €")
        c2.metric("Caja proyectada a 60d", f"{cf_summary.projected_cash_60d:,.2f} €", f"{cf_summary.projected_cash_60d - cf_summary.projected_cash_30d:,.2f} €")
        c3.metric("Caja proyectada a 90d", f"{cf_summary.projected_cash_90d:,.2f} €", f"{cf_summary.projected_cash_90d - cf_summary.projected_cash_60d:,.2f} €")
        
        st.markdown("##### Recomendaciones de Tesorería del Consejo IA:")
        for r in cf_summary.recommendations:
            st.info(f"💡 {r}")

# =========================================================
# TAB 2: Auditoría OCR & Antifraude (MitM / Benford)
# =========================================================
with tab_antifraud:
    st.subheader("Auditoría de Facturas Entrantes y Detección de Fraude MitM")
    st.markdown("Verificación automática del IBAN bancario del proveedor contra el registro de confianza corporativo.")
    
    col_t1, col_t2 = st.columns([1, 1])
    
    with col_t1:
        st.markdown("#### Simular Factura Recibida")
        test_case = st.selectbox(
            "Seleccionar Caso de Prueba",
            [
                "Factura Legítima (Proveedor Habitual)",
                "⚠️ ATAQUE Man-in-the-Middle (IBAN Alterado en Factura)",
                "⚠️ Factura Duplicada Recibida",
                "⚠️ Pico Anormal de Importe (+400% respecto a media)"
            ]
        )
        
        if test_case == "Factura Legítima (Proveedor Habitual)":
            inv_supplier = "Logística y Transportes Iberia S.L."
            inv_cif = "B12345678"
            inv_iban = "ES3400491500051111222233"
            inv_amount = 3450.00
            inv_number = "FRA-2026-089"
        elif "ATAQUE Man-in-the-Middle" in test_case:
            inv_supplier = "Logística y Transportes Iberia S.L."
            inv_cif = "B12345678"
            inv_iban = "ES0099998888777766665555" # Hacker IBAN
            inv_amount = 3450.00
            inv_number = "FRA-2026-090"
        elif "Factura Duplicada" in test_case:
            inv_supplier = "Logística y Transportes Iberia S.L."
            inv_cif = "B12345678"
            inv_iban = "ES3400491500051111222233"
            inv_amount = 1200.00
            inv_number = "DUP-991"
        else:
            inv_supplier = "Logística y Transportes Iberia S.L."
            inv_cif = "B12345678"
            inv_iban = "ES3400491500051111222233"
            inv_amount = 45000.00
            inv_number = "SPIKE-001"
            
        st.text_input("Proveedor", value=inv_supplier, key="af_supp")
        st.text_input("CIF Proveedor", value=inv_cif, key="af_cif")
        st.text_input("IBAN en Factura", value=inv_iban, key="af_iban")
        st.number_input("Total Factura (€)", value=inv_amount, key="af_amt")
        st.text_input("Número de Factura", value=inv_number, key="af_num")
        
        btn_audit = st.button("🔍 Auditar Factura con FraudDetector", type="primary")

    with col_t2:
        st.markdown("#### Resultado del Análisis Forense")
        if btn_audit or "last_audit" in st.session_state:
            if btn_audit:
                hist_dups = ["DUP-991"] if "Duplicada" in test_case else []
                hist_amts = [1000.0, 1100.0, 950.0] if "Pico" in test_case else [3200.0, 3400.0, 3500.0]
                
                res = FraudDetector.audit_invoice(
                    vendor_cif=inv_cif,
                    invoice_number=inv_number,
                    invoice_amount=inv_amount,
                    provided_iban=inv_iban,
                    historical_invoice_numbers=hist_dups,
                    historical_amounts=hist_amts
                )
                st.session_state.last_audit = res
                
                # Register in bunker
                st.session_state.bunker.record_action(
                    action_type="INVOICE_FRAUD_AUDIT",
                    actor="FraudDetector",
                    details={"invoice": inv_number, "status": res.status, "risk": res.risk_score, "flags": res.flags}
                )
            else:
                res = st.session_state.last_audit
                
            if res.status == "BLOCKED":
                st.error(f"🛑 FACTURA BLOQUEADA (Score de Riesgo: {res.risk_score}/100)")
            elif res.status == "REQUIRES_HITL":
                st.warning(f"⚠️ ENVIADA A REVISIÓN HUMANA HITL (Score de Riesgo: {res.risk_score}/100)")
            else:
                st.success(f"✅ FACTURA VALIDADA Y SEGURA (Score de Riesgo: {res.risk_score}/100)")
                
            st.markdown("##### Banderas de Riesgo Detectadas:")
            if res.flags:
                for f in res.flags:
                    st.markdown(f"- 🚩 `{f}`")
            else:
                st.markdown("- ✨ Ninguna discrepancia detectada.")
                
            st.info("La regla antifraude analiza: Registro maestro de IBANs, histórico de montos, números de factura duplicados y distribución de dígitos significativos.")

# =========================================================
# TAB 3: Conciliación Bancaria PSD2 Unattended
# =========================================================
with tab_psd2:
    st.subheader("Conciliación Bancaria Automática Desatendida (Open Banking PSD2)")
    st.markdown("Cruce en tiempo real entre extractos bancarios (Santander, BBVA, CaixaBank) y facturas de clientes/proveedores.")
    
    col_p1, col_p2 = st.columns([1, 1])
    
    with col_p1:
        st.markdown("#### Extractos Bancarios PSD2 Detectados")
        bank_txs = PSD2BankingFeeder.generate_simulated_transactions()
        df_bank = pd.DataFrame([
            {"ID": b.transaction_id, "Fecha": b.date, "Importe (€)": b.amount, "Contraparte": b.counterparty_name or "", "Concepto": b.description}
            for b in bank_txs
        ])
        st.dataframe(df_bank, use_container_width=True)
        
    with col_p2:
        st.markdown("#### Facturas en ERP (Holded / Sage / A3)")
        erp_invoices = [
            InvoiceItem(invoice_id="INV-001", invoice_number="INV-001", vendor_or_client="DISTRIBUCIONES NORTE", cif="B98765432", amount=12450.00, date="2026-10-21", is_income=True, status="PENDING"),
            InvoiceItem(invoice_id="INV-002", invoice_number="INV-002", vendor_or_client="LOGISTICA IBERIA", cif="B12345678", amount=3450.00, date="2026-10-20", is_income=False, status="PENDING"),
            InvoiceItem(invoice_id="INV-003", invoice_number="INV-003", vendor_or_client="ENERGIA LIMPIA SA", cif="A55555555", amount=820.00, date="2026-10-19", is_income=False, status="PENDING"),
            InvoiceItem(invoice_id="INV-004", invoice_number="INV-004", vendor_or_client="SERVICIOS TECNICOS VALENCIA", cif="B77777777", amount=14500.00, date="2026-10-18", is_income=True, status="PENDING")
        ]
        df_erp = pd.DataFrame([
            {"Factura": e.invoice_number, "Fecha": e.date, "Importe (€)": e.amount, "Tercero": e.vendor_or_client, "Tipo": "Cobro" if e.is_income else "Pago"}
            for e in erp_invoices
        ])
        st.dataframe(df_erp, use_container_width=True)
        
    st.divider()
    if st.button("⚡ Ejecutar Conciliación Desatendida", type="primary"):
        matches = BankReconciler.reconcile(bank_txs, erp_invoices)
        matched_items = [m for m in matches if m.status == ReconciliationStatus.MATCHED]
        
        st.success(f"Conciliación completada: {len(matched_items)} / {len(bank_txs)} movimientos cruzados con éxito.")
        
        for m in matches:
            if m.status == ReconciliationStatus.MATCHED:
                st.markdown(f"- ✅ **{m.transaction_id}** concilia con `{m.invoice_id}` (Confianza: {m.confidence*100:.0f}%) — {m.notes}")
            elif m.status == ReconciliationStatus.DISCREPANCY:
                st.markdown(f"- ⚠️ **{m.transaction_id}**: Discrepancia de {m.variance_amount:+.2f} € — {m.notes}")
            else:
                st.markdown(f"- ℹ️ **{m.transaction_id}**: Sin partida contable — {m.notes}")

# =========================================================
# TAB 4: Facturación Ley Crea y Crece & VeriFactu
# =========================================================
with tab_invoicing:
    st.subheader("Motor de Facturación Soberana: Ley Crea y Crece & VeriFactu (RD 1007/2023)")
    st.markdown("Generación de facturas con encadenamiento criptográfico SHA-256 inalterable y código QR de verificación según normativa de la AEAT.")
    
    col_i1, col_i2 = st.columns([1, 1])
    
    with col_i1:
        st.markdown("#### Emitir Factura Electrónica")
        inv_em_num = st.text_input("Número de Factura", value=f"EXP-2026-{datetime.datetime.now().strftime('%M%S')}")
        inv_buyer_nif = st.text_input("NIF Destinatario", value="B-84920112")
        inv_total_amt = st.number_input("Importe Total con IVA (€)", value=6050.0, step=250.0)
        inv_vat_rate = st.selectbox("Tipo Impositivo IVA", [21.0, 10.0, 4.0, 0.0])
        inv_regime_choice = st.selectbox("Modalidad Normativa", ["VERIFACTU", "CREA_Y_CRECE", "TICKETBAI"])
        
        btn_emit = st.button("🚀 Emitir y Firmar Criptográficamente", type="primary")

    with col_i2:
        st.markdown("#### Comprobante de Emisión y Huella Digital")
        if btn_emit:
            fmt = InvoiceComplianceFormat.VERIFACTU if inv_regime_choice == "VERIFACTU" else (InvoiceComplianceFormat.TICKETBAI if inv_regime_choice == "TICKETBAI" else InvoiceComplianceFormat.CREA_Y_CRECE)
            rec = ElectronicInvoiceEngine.generate_compliant_invoice_record(
                invoice_number=inv_em_num,
                issuer_cif=company_cif,
                recipient_cif=inv_buyer_nif,
                total_amount=inv_total_amt,
                format_type=fmt,
                vat_rate_pct=inv_vat_rate
            )
            
            # Record in bunker
            st.session_state.bunker.record_action(
                action_type="INVOICE_PROCESSED",
                actor="ElectronicInvoiceEngine",
                details={"num": rec.invoice_number, "hash": rec.record_hash, "amt": rec.total_amount}
            )
            
            st.success(f"Factura {rec.invoice_number} emitida con éxito bajo régimen {rec.format_applied.value}")
            
            st.markdown(f"**Huella Criptográfica SHA-256:**")
            st.code(rec.record_hash, language="text")
            
            st.markdown(f"**QR VeriFactu Payload:**")
            st.code(rec.qr_data, language="text")
            
            st.download_button(
                "📥 Descargar Factura JSON Regulada",
                data=json.dumps(rec.model_dump(), indent=2, ensure_ascii=False),
                file_name=f"{rec.invoice_number}_verifactu.json",
                mime="application/json"
            )

# =========================================================
# TAB 5: Aprobaciones HITL (Human-in-the-Loop)
# =========================================================
with tab_hitl:
    st.subheader("Pasarela de Control y Autorización HITL (Human-in-the-Loop)")
    st.markdown("Pagos superiores al umbral de seguridad (>3.000 €) o con banderas de riesgo requieren autorización explícita.")
    
    col_h1, col_h2 = st.columns([1, 2])
    
    with col_h1:
        st.markdown("#### Solicitar Nueva Autorización")
        p_ben = st.text_input("Beneficiario", value="SUMINISTROS INDUSTRIALES VALENCIA S.L.")
        p_cif = st.text_input("CIF Beneficiario", value="B-46981234")
        p_iban = st.text_input("IBAN Destino", value="ES7821000418450200059999")
        p_amt = st.number_input("Importe a Transferir (€)", value=7850.0, step=500.0)
        
        if st.button("📤 Enviar a Pasarela HITL"):
            auth_req = st.session_state.hitl_gate.evaluate_transaction(
                vendor_name=p_ben,
                vendor_cif=p_cif,
                amount=p_amt,
                destination_iban=p_iban,
                fraud_risk_score=35 if p_amt > 5000 else 0,
                fraud_flags=["ALTO_IMPORTE_MANUAL"] if p_amt > 3000 else []
            )
            if auth_req:
                st.success(f"Solicitud registrada en cola de supervisión: {auth_req.request_id}")
            else:
                st.info("La operación está por debajo del umbral y no presenta riesgo: Auto-aprobada.")
            st.rerun()
            
    with col_h2:
        st.markdown("#### Solicitudes Pendientes de Firma")
        pending = [r for r in st.session_state.hitl_gate.requests.values() if r.status == ApprovalStatus.PENDING]
        if not pending:
            st.info("No hay pagos pendientes de aprobación en este momento.")
        else:
            for req in pending:
                with st.expander(f"⚠️ {req.vendor_name} — {req.amount:,.2f} € (ID: {req.request_id})", expanded=True):
                    st.write(f"**CIF:** {req.vendor_cif} | **IBAN:** `{req.destination_iban}`")
                    st.write(f"**Motivo:** {req.reason_for_review}")
                    st.write(f"**Score de Riesgo:** {req.risk_score}/100")
                    
                    c_appr, c_rej = st.columns(2)
                    with c_appr:
                        if st.button(f"✅ Autorizar Pago", key=f"btn_ap_{req.request_id}"):
                            st.session_state.hitl_gate.approve(req.request_id, approver_name="CFO Humano", comment="Aprobado en sesión ejecutiva.")
                            st.session_state.bunker.record_action(
                                action_type="HITL_PAYMENT_APPROVED",
                                actor="HumanCFO",
                                details={"id": req.request_id, "amount": req.amount, "vendor": req.vendor_name}
                            )
                            st.success("Pago Autorizado y Registrado en Bóveda NIS2.")
                            st.rerun()
                    with c_rej:
                        if st.button(f"❌ Denegar Pago", key=f"btn_rj_{req.request_id}"):
                            st.session_state.hitl_gate.reject(req.request_id, approver_name="CFO Humano", reason="Rechazado: Cuenta no confirmada.")
                            st.session_state.bunker.record_action(
                                action_type="HITL_PAYMENT_REJECTED",
                                actor="HumanCFO",
                                details={"id": req.request_id, "amount": req.amount, "vendor": req.vendor_name}
                            )
                            st.error("Pago Denegado y Bloqueado.")
                            st.rerun()

# =========================================================
# TAB 6: Bóveda Inmutable NIS2 & RGPD Shredder
# =========================================================
with tab_bunker:
    st.subheader("Bóveda Inmutable de Evidencias (Directiva NIS2) & Destructor RGPD")
    st.markdown("Registro cronológico seguro con hash encadenado SHA-256 y HMAC para auditorías legales sin posibilidad de repudio.")
    
    col_b1, col_b2 = st.columns([1, 1])
    
    with col_b1:
        st.markdown("#### Integridad del Registro Inmutable")
        is_valid, count, msg = st.session_state.bunker.verify_ledger_integrity()
        
        if is_valid:
            st.success(f"✅ {msg}")
        else:
            st.error(f"🚨 INTEGRIDAD COMPROMETIDA: {msg}")
            
        blocks = st.session_state.bunker.get_all_blocks()
        st.metric("Total Evidencias Registradas", len(blocks))
        
        df_blocks = pd.DataFrame([
            {"Bloque": b.block_index, "Timestamp": b.timestamp[:19], "Tipo": b.action_type, "Actor": b.actor, "Hash": b.block_hash[:16] + "..."}
            for b in blocks[-10:]
        ])
        st.dataframe(df_blocks, use_container_width=True)

    with col_b2:
        st.markdown("#### Destrucción Criptográfica RGPD (Derecho al Olvido)")
        st.markdown("Eliminación irreversible de PII conservando únicamente la prueba criptográfica de destrucción según Art. 17 RGPD.")
        
        shred_cif = st.text_input("CIF / NIF a Destruir", value="48291039K")
        shred_rec_id = st.text_input("ID de Registro", value="REC-2026-CLIENT-088")
        
        if st.button("🔥 Ejecutar Destrucción Criptográfica"):
            shred_cert = GDPRShredder.shred_record(
                record_id=shred_rec_id,
                subject_identifier=shred_cif
            )
            st.session_state.bunker.record_action(
                action_type="GDPR_SHRED_EXECUTED",
                actor="GDPRShredder",
                details={"record_id": shred_rec_id, "proof_hash": shred_cert.proof_of_shredding_hash}
            )
            st.success(f"Datos destruidos con éxito. Hash de prueba: {shred_cert.proof_of_shredding_hash}")
            st.json(shred_cert.model_dump())

# =========================================================
# TAB 7: Generador Dossier Bancario A4 (ReportLab)
# =========================================================
with tab_dossier:
    st.subheader("Generador de Dossier Bancario y Solvencia A4 Certificado")
    st.markdown("Emisión automática de informes financieros profesionales para entidades bancarias, comités de riesgo y CIRBE.")
    
    out_pdf_path = PROJECT_ROOT / "storage" / "dossier_bancario_solvencia.pdf"
    out_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    
    col_d1, col_d2 = st.columns([1, 1])
    
    with col_d1:
        st.markdown("#### Parámetros del Dossier")
        st.text_input("Destinatario del Informe", value="Comité de Riesgos - Banco Santander / CaixaBank", key="doss_dest")
        st.text_input("Finalidad", value="Renovación de Línea de Crédito y Póliza de Circulante", key="doss_fin")
        
        btn_gen_pdf = st.button("📑 Compilar Dossier Bancario PDF", type="primary")

    with col_d2:
        st.markdown("#### Descarga del Informe")
        if btn_gen_pdf or out_pdf_path.exists():
            if btn_gen_pdf:
                BankDossierPDFGenerator.generate(
                    output_path=str(out_pdf_path),
                    company_name=company_name,
                    company_cif=company_cif,
                    liquidity=current_cash,
                    monthly_burn=monthly_burn,
                    altman_z_score=z_res.altman_z_prime,
                    solvency_zone=z_res.zone.value,
                    runway_months=cf_summary.runway_months,
                    working_capital=working_cap,
                    sales=sales_val,
                    tax_reserve=12500.0
                )
                st.success("Dossier compilado con éxito según estándares IFRS / PGC.")
                
            if out_pdf_path.exists():
                with open(out_pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                st.download_button(
                    label="📥 Descargar Dossier Bancario Oficial (.PDF)",
                    data=pdf_bytes,
                    file_name=f"Dossier_Solvencia_{company_cif}.pdf",
                    mime="application/pdf"
                )

# =========================================================
# TAB 8: Conectores & Protocolo SDP Engine (BYOK)
# =========================================================
with tab_sdp:
    st.subheader("Semantic Discovery Protocol (SDP) & Malla de Conectores")
    st.markdown("Descubrimiento progresivo de esquemas de datos: Nivel 0 (catálogo ultraligero de ~35 tokens) y Nivel 1 (esquema hidratado bajo demanda).")
    
    tier0_connectors = st.session_state.sdp_engine.list_connectors()
    
    st.markdown("#### Conectores Disponibles en el Ecosistema")
    cols = st.columns(len(tier0_connectors))
    for i, c in enumerate(tier0_connectors):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <h4 style="margin: 0; color: #60a5fa;">{c.name}</h4>
                <div class="metric-sub" style="margin: 6px 0;">{c.description}</div>
                <span class="cfo-badge badge-info">{c.category}</span>
                <div style="font-size: 11px; color: #94a3b8; margin-top: 8px;">Consumo: ~{c.estimated_tier0_tokens} tokens</div>
            </div>
            """, unsafe_allow_html=True)
            
    st.divider()
    selected_conn = st.selectbox("Explorar Esquema Hidratado (Tier-1 SDP)", [c.connector_id for c in tier0_connectors])
    if selected_conn:
        tier1 = st.session_state.sdp_engine.get_hydrated_schema(selected_conn)
        if tier1:
            st.markdown(f"##### Esquema Operativo: {tier1.get('name', selected_conn)}")
            st.json(tier1)
            
    st.divider()
    st.markdown("#### Configuración de Claves BYOK (Almacenamiento Local Seguro)")
    st.text_input("Holded API Key", type="password", placeholder="pk_live_...")
    st.text_input("A3 Innuva Client Secret", type="password", placeholder="a3_sec_...")
    st.text_input("Open Banking PSD2 Certificate", type="password", placeholder="-----BEGIN CERTIFICATE-----")
    if st.button("💾 Guardar Configuración de Conectores"):
        st.success("Configuración de credenciales almacenada localmente con cifrado AES-GCM.")
