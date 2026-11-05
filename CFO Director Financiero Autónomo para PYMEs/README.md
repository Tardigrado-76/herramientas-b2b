# AUTONOMOUS CFO — Director Financiero para PYMEs
### *Caso de Estudio Práctico: Superando la Fricción del "PoC Purgatory" mediante Agentes Financieros Acotados y Control HITL*

---

## El Reto del "PoC Purgatory" en Procesos Financieros Críticos

> *"En las grandes consultoras y corporaciones, el 85% de las iniciativas de IA mueren en el 'PoC Purgatory': demos vistosas en Jupyter Notebooks que colapsan en cuanto tocan datos sucios, carecen de auditoría legal y requieren un batallón de ingenieros solo para mantenerlas vivas.*
>
> *Iwan van der Kleijn propuso la alternativa: el **AI Workbench bottom-up**. Diseñar herramientas locales, acotar estrictamente a los agentes, integrar el compliance desde la primera línea y congelar el resultado en ejecutables autónomos con cero fricción de despliegue.*
>
> *Este componente ilustra de forma práctica cómo aplicar esa disciplina arquitectónica a un dominio financiero real: conciliación bancaria PSD2, extracción contable y salvaguardas de solvencia auditables."*

---

## Arquitectura del Sistema

```mermaid
graph TD
 subgraph UI ["Consola Ejecutiva Streamlit (Port 8501)"]
 DASH["Dashboard Financiero & Altman Z'-Score"]
 HITL_UI["Centro de Aprobaciones 4-Ojos (Art. 14 EU AI Act)"]
 REP["Generador de Dossiers PDF (ReportLab)"]
 end

 subgraph Core ["Motor Orquestador AutonomoCFOEngine"]
 OCR["InvoiceOCRTool<br/><i>Lectura y Validación de Facturas</i>"]
 FRAUD["FraudDetectorTool<br/><i>Detección de IBANs y Desvíos</i>"]
 CASH["CashFlowForecasterTool<br/><i>Pasarela de Caja & Burn Rate</i>"]
 TAX["TaxLedgerTool<br/><i>Modelos 303/111 AEAT</i>"]
 end

 subgraph SDP ["Conectores SDP Dinámicos (Tier-0)"]
 A3["A3 Innuva ERP"]
 HOLDED["Holded Cloud"]
 SAGE["Sage 50 Cloud"]
 PSD2["Open Banking Gateway (Santander/BBVA)"]
 STRIPE["Stripe Billing"]
 end

 subgraph Governance ["Búnker Criptográfico & Cumplimiento"]
 LEDGER["Ledger SHA-256 Inmutable<br/><i>Directiva NIS2 (Art. 21/23)</i>"]
 VAULT["Bóveda Criptográfica RGPD<br/><i>Anonimización & Shredding</i>"]
 SBOM["SBOM CycloneDX v1.5<br/><i>Cyber Resilience Act (CRA)</i>"]
 end

 DASH --> Core
 Core --> SDP
 Core --> Governance
 Core --> HITL_UI
 HITL_UI -->|Firma Digital Interventor| LEDGER
 Governance --> REP
```

---

## Características Principales

1. **Gestión Financiera Integral:**
 - **Previsión de Tesorería:** Cálculo de runway, burn rate y flujo de caja proyectado a 30, 60 y 90 días.
 - **Índice de Solvencia:** Implementación exacta del modelo **Altman Z'-Score** para empresas no cotizadas, detectando riesgo de quiebra antes de que ocurra.
 - **Control Tributario:** Estimación en tiempo real de liquidaciones de IVA e IRPF (Modelos 303 y 111 de la AEAT).
 - **Detección de Fraude en Facturas:** Alertas tempranas ante suplantación de identidad en proveedores o cambios no autorizados en cuentas bancarias.

2. **Gobernanza Criptográfica Integrada (Compliance-by-Design):**
 - **Directiva NIS2 (Art. 21 y 23):** Cada factura procesada, conciliación bancaria y orden de pago queda sellada en una cadena inmutable de bloques SHA-256 (`audit_nis2_ledger.jsonl`).
 - **Supervisión Humana Obligatoria (HITL Gate):** Conforme al **Artículo 14 del EU AI Act**, cualquier pago que supere el umbral configurado requiere autorización explícita de un interventor humano.
 - **Privacidad RGPD (Art. 17):** Anonimización de datos sensibles y capacidad de borrado criptográfico no recuperable (*cryptographic shredding*).
 - **SBOM CycloneDX v1.5 (CRA):** Trazabilidad de dependencias y firewall contra prompt injections en documentos adjuntos.

3. **Conectores ERP & Bancarios mediante Semantic Discovery Protocol:**
 - Carga dinámica y bajo demanda de conectores a A3 Innuva, Holded, Sage 50, ContaSOL, Stripe Billing y APIs PSD2 Open Banking, ahorrando hasta un 94% de contexto en llamadas de inferencia.

## Documentación Técnica & Gobernanza
- [**Manual de Uso y Operación Detallado**](./MANUAL_DE_USO.md)
- [**Especificación y Gobernanza de Agentes (AGENTS.md)**](./AGENTS.md)
- [**Catálogo de Skills Asignadas (SKILLS_REGISTRY.md)**](./SKILLS_REGISTRY.md)
- [**Integración de Servidores MCP Nativos (MCP_INTEGRATION.md)**](./MCP_INTEGRATION.md)

---

## Guía de Inicio Rápido y Uso

### 1. Requisitos
- Python 3.10+ (probado exhaustivamente en Python 3.13 en Windows 11).
- Instalar dependencias:
 ```powershell
 pip install -r requirements.txt
 ```

### 2. Ejecución con Doble Clic
Ejecute el archivo batch en la raíz del módulo:
```bat
INICIAR_CFO_AUTONOMO.bat
```
El servidor Streamlit se iniciará en su puerto dedicado:
 **`http://localhost:8501`**

### 3. Operativa en la Interfaz
- **Pestaña 1 - Panel de Control:** Visualice el estado de tesorería, ratios de liquidez y gráfico de Altman Z'-Score.
- **Pestaña 2 - Carga de Facturas:** Suba facturas en PDF o imagen para su análisis OCR automático y escaneo antifraude.
- **Pestaña 3 - Aprobación HITL:** Revise y apruebe operaciones pendientes con firma de intervención.
- **Pestaña 4 - Auditoría NIS2:** Compruebe la integridad de la cadena de bloques con verificación matemática en un clic (`verify_chain`).
- **Pestaña 5 - Descarga de Informes:** Genere dossiers ejecutivos periciales en PDF compilados formalmente con ReportLab.

---

## Verificación de Pruebas Unitarias (26 / 26 PASS)

La suite completa consta de 26 pruebas unitarias sin fallos:
```powershell
python -m pytest -v
```

```
tests/test_cfo_engine.py::test_cash_flow_forecaster PASSED
tests/test_cfo_engine.py::test_fraud_detector PASSED
tests/test_cfo_engine.py::test_invoice_ocr PASSED
tests/test_cfo_engine.py::test_tax_ledger PASSED
tests/test_cfo_engine.py::test_altman_z_score PASSED
tests/test_cfo_engine.py::test_nis2_audit_ledger PASSED
tests/test_cfo_engine.py::test_rgpd_anonymizer PASSED
tests/test_cfo_engine.py::test_cra_sbom_validator PASSED
tests/test_cfo_engine.py::test_hitl_approval_gate PASSED
tests/test_sdp_accounting_connector.py::test_sdp_accounting_registry PASSED
tests/test_sdp_accounting_connector.py::test_sdp_a3_innuva_routing PASSED
tests/test_sdp_accounting_connector.py::test_sdp_psd2_banking_routing PASSED
tests/test_sdp_accounting_connector.py::test_sdp_accounting_token_efficiency PASSED
tests/test_cfo_ocr_and_ppt.py::test_paddleocr_invoice_parser PASSED
tests/test_cfo_ocr_and_ppt.py::test_cfo_ppt_deck_generation PASSED
tests/test_cfo_wave3.py::test_monthly_closing_agent PASSED
tests/test_cfo_wave3.py::test_multichannel_reconciliation PASSED
tests/test_cfo_wave3.py::test_m365_excel_ghost_scripts PASSED
...
============================== 26 passed in 7.42s ==============================
```

---

## Matriz Oficial de Cobertura Regulatoria

| Marco Normativo | Base Legal | Implementación Técnica en Autonomous CFO | Estado |
| :--- | :--- | :--- | :---: |
| **NIS2** | Directiva UE 2022/2555 | Art. 21 y 23: Trazabilidad inmutable de órdenes financieras en blockchain SHA-256 (`audit_nis2_ledger.jsonl`). | **Conforme** |
| **EU AI Act Art. 14** | Reglamento UE 2024/1689 | Supervisión humana obligatoria (HITL Gate): autorización explícita de interventor para transferencias > 50.000 EUR. | **Conforme** |
| **RGPD** | Reglamento UE 2016/679 | Art. 17: Anonimización de datos sensibles y borrado criptográfico no recuperable (*cryptographic shredding*). | **Conforme** |
| **DORA** | Reglamento UE 2022/2554 | Resiliencia de transacciones financieras, conciliación bancaria PSD2 y trazabilidad de pasarelas de pago. | **Conforme** |
| **CRA** | Cyber Resilience Act | SBOM CycloneDX v1.5, validación de integridad de dependencias y escaneo contra prompt injection en adjuntos. | **Conforme** |

```powershell
python -m ruff check . # 0 errors
python -m bandit -r . -ll # 0 issues
```

---

*Diseñado bajo la premisa de ingeniería de Iwan van der Kleijn: Si no se puede desplegar con doble clic y auditar criptográficamente, no es software empresarial.*
