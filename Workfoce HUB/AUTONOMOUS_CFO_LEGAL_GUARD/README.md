# 🛡️ AUTONOMOUS VERTICAL CFO & LEGAL GUARD

> **Tagline:** *"El director financiero y oficial de cumplimiento autónomo para empresas que no pueden pagar uno a tiempo completo."*

**Producto Turnkey (Micro-SaaS Soberano)** orientado a PYMEs de 10 a 50 empleados en España y la Unión Europea. Proporciona dirección financiera cuantitativa, detección forense de fraude en pagos a proveedores y garantía de facturación inalterable bajo las normativas **Ley Crea y Crece**, **VeriFactu (RD 1007/2023)**, **Directiva NIS2** y **RGPD Art. 17**.

---

## 🏛️ Arquitectura del Consejo de Agentes IA

El sistema opera bajo un consejo colegiado de 4 agentes especializados:
1. **CFO Executive Agent:** Diagnóstico de solvencia matemática mediante el modelo Altman Z'-Score para PYMEs privadas, cálculo de runway en días y asignación de capital.
2. **Tax & Ledger Accountant:** Conciliación bancaria desatendida multicuenta (Open Banking PSD2) y proyección de reservas fiscales trimestrales (IVA e Impuesto sobre Sociedades).
3. **Risk & Fraud Sentinel:** Auditoría algorítmica de facturas entrantes con verificación estricta de IBAN contra registro maestro histórico (Anti Man-in-the-Middle) y heurística de Benford.
4. **GRC & Sovereign Keeper:** Encadenamiento criptográfico SHA-256 de facturas con código QR reglamentario, búnker inmutable local bajo estándar NIS2 y triturador criptográfico de datos personales (RGPD Art. 17).

---

## 🚀 Inicio Rápido en Windows

### 1. Lanzador Principal (Doble Click)
Haga doble click sobre cualquiera de los siguientes accesos directos:
- **Acceso Directo:** `CFO_LEGAL_GUARD.lnk`
- **Script Batch:** [INICIAR_CFO_LEGAL_GUARD.bat](file:///E:/PROYECTOS%20IA/NEW%20TOOLS/AUTONOMOUS_CFO_LEGAL_GUARD/INICIAR_CFO_LEGAL_GUARD.bat)
- **Lanzador Raíz:** [E:\PROYECTOS IA\NEW TOOLS\INICIAR_CFO_LEGAL_GUARD.bat](file:///E:/PROYECTOS%20IA/NEW%20TOOLS/INICIAR_CFO_LEGAL_GUARD.bat)

El servidor iniciará automáticamente en:
👉 **`http://localhost:8510`**

---

## 🐳 Despliegue Secundario en Contenedor (Opcional)

Para entornos aislados o servidores Linux/Docker:
```bash
docker-compose up -d --build
```
El contenedor se ejecuta en modo no-root con puerto expuesto `8510:8510` y almacenamiento persistente en `./storage`.

---

## 🔒 Soberanía, BYOK y Modo Air-Gapped

- **Air-Gapped Activo (Por defecto):** Los datos financieros y extractos bancarios no abandonan la infraestructura local. Funciona de manera nativa con modelos locales vía **Ollama** (`http://localhost:11434/v1`).
- **BYOK (Bring Your Own Key):** Soporte opcional para conectar modelos de OpenAI, Anthropic, Google Gemini o DeepSeek con claves API almacenadas localmente.
- **Protocolo SDP (Semantic Discovery Protocol):** Conexión con ERPs y contabilidad (Holded, A3 Innuva, Sage 50, Stripe, PSD2) con consumo ultrabajo de tokens (~35 tokens por descubrimiento).

---

## 🧪 Pruebas Unitarias y Verificación

Para ejecutar la suite de tests automatizada:
```bash
python -m pytest tests/
```
100% de cobertura en:
- `test_solvency.py`: Validación de zonas de riesgo Altman Z'.
- `test_fraud_detector.py`: Detección de ataques MitM y facturas duplicadas.
- `test_reconciliation.py`: Cruce exacto y difuso de movimientos PSD2.
- `test_bunker.py`: Integridad y sellado SHA-256 / HMAC bajo NIS2.
- `test_invoicing.py`: Encadenamiento VeriFactu y generación de QR.
