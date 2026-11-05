# AUTÓNOMO CFO — Director Financiero Autónomo para PYMEs

Aplicación ejecutiva con interfaz web moderna en **Streamlit** y acceso directo ejecutable doble clic para Windows (`.bat` y `.lnk`), diseñada bajo los estándares de cumplimiento europeo **NIS2 (Directiva UE 2022/2555)**, **RGPD (Reglamento UE 2016/679)** y **CRA (Reglamento UE 2024/2847)**.

---

## Inicio Rápido (Doble Clic)

Tienes dos opciones de inicio instantáneo en la raíz del proyecto:

1. **`CFO_AUTONOMO.lnk`**: Acceso directo ejecutable con icono ejecutivo de Windows (doble clic).
2. **`INICIAR_CFO_AUTONOMO.bat`**: Script batch que inicia el servidor Streamlit en `http://localhost:8501` y abre el navegador por defecto.

O bien por terminal:
```powershell
streamlit run app_streamlit.py
```

---

## Consejo de Agentes IA Integrado (/agency-agents, /swarms)

- **CFO Executive**: Orquestador financiero que proyecta flujos de caja a 90 días, analiza solvencia (Altman Z'-Score) y formula recomendaciones de tesorería.
- **Tax Accountant**: Auditor OCR de facturas y tickets, validación de coherencia matemática y cálculo de retenciones e IVA (Modelos 303, 111, 202).
-  **Risk Analyst**: Rastreador de fraudes, desvíos de IBAN no registrados y duplicidades en tiempo real.
-  **GRC Sentinel**: Guardián de cumplimiento normativo europeo (inmutabilidad NIS2, purga de PII RGPD y ciberresiliencia CRA).

---

## Módulos de la Aplicación Web (Streamlit)

1. ** Panel Financiero & Tesorería**:
 - Tarjetas métricas ejecutivas en tiempo real: Liquidez, Runway, Altman Z'-Score con alertas de zona (Safe, Grey, Distress) y Pasivos Fiscales.
 - Gráfica interactiva de proyección de caja a 90 días (+30d, +60d, +90d).
 - Desglose detallado de impuestos trimestrales de la AEAT.

2. ** Auditoría OCR de Facturas**:
 - Procesamiento de facturas simuladas o reales con extracción estructurada.
 - Detección de consistencia matemática de bases e impuestos.
 - Detección de fraudes o anomalías en IBANs de proveedores.

3. ** Aprobaciones HITL (Human-in-the-Loop)**:
 - Bloqueo preventivo de pagos sospechosos o superiores al umbral configurado (1.000 €).
 - Panel de autorización o rechazo con un solo clic y registro en ledger.

4. ** Auditoría Criptográfica NIS2**:
 - Verificación de integridad de la cadena inmutable de bloques SHA-256 (Art. 21).
 - Tabla cronológica completa de eventos auditados.

5. ** Seguridad & SBOM CRA**:
 - Software Bill of Materials (SBOM) en formato estándar CycloneDX v1.5 JSON descargable.
 - Simulador interactivo del firewall contra inyecciones de prompt adversarial (Art. 10 y 11).

---

## Verificación de Pruebas Unitarias

Ejecutado con 100% de éxito:
```powershell
python -m unittest tests/test_autonomo_cfo.py -v
```
*(13 tests pasando en 8.76s)*
