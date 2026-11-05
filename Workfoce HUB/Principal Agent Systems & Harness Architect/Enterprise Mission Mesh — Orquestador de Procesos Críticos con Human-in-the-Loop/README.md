# 🛡️ Enterprise Mission Mesh

> **Deterministic HITL Orchestration Gateway with Idempotent Sagas and 1-Click Rollback**  
> **100% Native Host Architecture — Cero Dependencias de Docker.**  
> **Cumplimiento Normativo:** EU AI Act (Art. 14 Human Oversight), Estatuto de los Trabajadores (Art. 34.9 Registro de Jornada), NIS2 (Art. 21) y DORA (Art. 9).

---

## 1. Visión General y Propósito

Enterprise Mission Mesh resuelve el principal obstáculo para el despliegue de agentes autónomos en entornos empresariales regulados: **la responsabilidad legal, laboral y financiera ante alucinaciones o errores agénticos**.

Si un agente modifica un fichaje en `Kronos`, aprueba un reembolso o altera una base de datos crítica:
1. **Clasificación de Riesgo & Puerta de Confianza:** Si el impacto es bajo y la confianza > 95%, auto-ejecuta. Si incide en el registro de jornada laboral (> 15 min / horas extra) o exposición financiera, congela la acción y escala a supervisión humana.
2. **Human-in-the-Loop (HITL) Omnicanal:** Despacho interactivo con tokens HMAC anti-manipulación a **Slack Block Kit**, **Teams Adaptive Cards**, **Telegram Inline Bot**, **Webhooks / n8n**, **Email**, **Discord**, **WhatsApp** y un **Portal Web Local**.
3. **Arquitectura Saga con 1-Click Rollback:** Cada acción almacena su imagen previa (*Before-Image*) y transacción compensatoria. Cualquier supervisor o auditor puede revertir el estado al punto exacto anterior con un solo clic.
4. **Cadena Criptográfica Inmutable:** Registro SQLite en modo WAL con encadenamiento SHA-256 y firmas HMAC para auditorías no repudiables.

---

## 2. Acceso a Canales de Supervisión (Q1: Opciones A, B, C, D)

El sistema provee soporte nativo y botones de acceso directo en el **Local Portal UI**:

- **Opción A:** Mensajes interactivos de **Slack** con Block Kit y botones de aprobación unívocos.
- **Opción B:** Tarjetas adaptativas de **Microsoft Teams** (Adaptive Cards v1.4).
- **Opción C:** Bot interactivo de **Telegram** con teclado inline (`InlineKeyboardMarkup`).
- **Opción D:** **Portal Web Local en FastAPI** (`http://127.0.0.1:8765`) + CLI interactivo **Rich TUI** (`python -m enterprise_mission_mesh.cli.mesh_cli`).
- **Canales Adicionales:** Webhooks hacia **n8n** (Zero Docker), **Email Ejecutivo**, **Discord** y **WhatsApp Business API**.

---

## 3. Emisores Agénticos Soportados (Q2)

Incluye adaptadores nativos y conectores transaccionales para:
- `ai-employees`:
  - `chief-of-staff`: Circuit breaker de emergencia y aprobaciones ejecutivas.
  - `hr-operations-specialist`: Ajustes de fichaje y horas extra en `Kronos`.
  - `sales-employee` / `gtm-engineer`: Descuentos comerciales y contratos.
  - `customer-satisfaction`: Reembolsos y créditos de servicio.
  - `ad-manager`: Límites presupuestarios de campañas.
  - `web-dev-employee`: Despliegues y cambios de esquema.
- Multi-Agent Frameworks:
  - `subagent-driven-development`
  - `agency-agents`
  - `agency-swarm`
  - `swarms`

---

## 4. Guía de Puesta en Marcha (Windows Native)

### 4.1 Ejecución del Servidor y Portal Web
```powershell
$env:PYTHONPATH = "e:\PROYECTOS IA\enterprise-mission-mesh\src"
python -m uvicorn enterprise_mission_mesh.server:app --host 127.0.0.1 --port 8765
```
Accede al portal interactivo en: `http://127.0.0.1:8765`

### 4.2 Simulación de Incidencia Kronos y 1-Click Rollback
```powershell
$env:PYTHONPATH = "e:\PROYECTOS IA\enterprise-mission-mesh\src"
python "e:\PROYECTOS IA\enterprise-mission-mesh\scripts\simulate_kronos_incident.py"
```

### 4.3 Inspección de Auditoría Forense y Cadena SHA-256
```powershell
$env:PYTHONPATH = "e:\PROYECTOS IA\enterprise-mission-mesh\src"
python -m enterprise_mission_mesh.cli.audit_trail
```

### 4.4 Ejecución de la Batería de Pruebas
```powershell
$env:PYTHONPATH = "e:\PROYECTOS IA\enterprise-mission-mesh\src"
pytest "e:\PROYECTOS IA\enterprise-mission-mesh\tests" -v
```

---

## 5. Cumplimiento Normativo Auditado

| Regulación | Artículo | Mecanismo de Garantía |
| :--- | :--- | :--- |
| **EU AI Act** | **Art. 14 (Human Oversight)** | Ninguna acción crítica se aplica sin visto bueno humano físico. |
| **EU AI Act** | **Art. 14.4.d (Parada e Intervención)** | Botón de 1-Click Rollback para revertir estados en cualquier momento. |
| **Estatuto Trabajadores** | **Art. 34.9 (Registro de Jornada)** | Inmutabilidad de los fichajes en Kronos; trazabilidad con Before-Image. |
| **NIS2** | **Art. 21 (Continuidad de Negocio)** | Transacciones idempotentes Saga con recuperación automática. |
| **DORA** | **Art. 9 (Protección de Integridad)** | Cadena de bloques local SHA-256 + HMAC resistente a manipulaciones. |
