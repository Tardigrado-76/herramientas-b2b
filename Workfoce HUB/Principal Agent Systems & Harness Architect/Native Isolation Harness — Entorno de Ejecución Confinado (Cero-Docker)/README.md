# 🛡️ Native Isolation Harness — Entorno de Ejecución Confinado (Cero-Docker)

> **Proyecto del Roadmap de Nivel 5: Principal Agent Systems & Harness Architect**  
> **Directiva Mandatoria:** 100% Native Host (Cero Dependencias de Docker).  
> **Normativas Target:** EU AI Act (Art. 15 Ciberseguridad & Robustez), NIS2 (Art. 21), DORA (Art. 9), ENS Nivel Alto, MITRE ATT&CK & CAPEC.

---

## 1. Visión General

**Native Isolation Harness** es un micro-sandbox nativo para Windows (con soporte multiplataforma) diseñado para permitir que agentes de IA autónomos (`MINI-AGENT LANGGRAPH`, `ai-employees`, servidores de herramientas MCP) ejecuten comandos del sistema, scripts en Python/Node y operaciones de terminal en un entorno **100% confinado, aislado y auditable en tiempo real sin requerir contenedores Docker**.

La contención se logra a nivel de kernel del sistema operativo mediante **Windows Job Objects** (`ctypes` sobre `kernel32.dll`), enjaulado estricto del sistema de ficheros en carpetas efímeras con borrado criptográfico **NIST SP 800-88 Rev 1**, control de binarios por whitelist y telemetría forense estructurada mapeada automáticamente a **MITRE ATT&CK** y **CAPEC**.

---

## 2. Directiva Mandatoria: 100% Native Host (Cero Docker)

⚠️ **REGLA ABSOLUTA:** Ningún componente, herramienta MCP o script depende ni utiliza contenedores Docker.
- **Node.js / JS:** Ejecución directa mediante `node` o `npx -y <paquete>`.
- **Python:** Ejecución directa mediante `python` o `uvx <paquete>` local.
- **Micro-Sandbox Nativo:** Inicio de sandbox en **< 8 milisegundos**, sin sobrecarga de virtualización.

---

## 3. Barreras de Seguridad y Hardware

| Capa de Seguridad | Primitiva / Tecnología | Control Implementado |
| :--- | :--- | :--- |
| **Capa 1: Kernel Job Object** | `kernel32.dll` (`CreateJobObjectW`, `SetInformationJobObject`) | Hard limits: RAM (512 MB máx), CPU Throttling (20% hard cap), Anti-Fork-Bomb (máx 4 procesos simultáneos), `KILL_ON_JOB_CLOSE`. |
| **Capa 2: Filesystem Jail** | `FSJailer` + `PathValidator` | Raíz virtualizada efímera `/scratch/{session_id}`. Detección de path traversal (`../../`), escape por symlinks/junctions y Alternate Data Streams (ADS). |
| **Capa 3: Borrado Seguro** | `NISTWiper` | Borrado según **NIST SP 800-88 Rev 1**: sobreescritura con bytes aleatorios (`os.urandom`) y sincronización forzada (`os.fsync`) antes de la desvinculación. |
| **Capa 4: Binary Whitelist** | `BinaryPolicyEngine` + `ArgSanitizer` | Whitelist de ejecutables autorizados (`python`, `node`, `git`, `uv`, `npx`). Bloqueo de shells (`cmd.exe`, `powershell.exe`) y sanitización estricta de argumentos. |
| **Capa 5: Telemetría Forense** | `SOCLogger` + `MITREMapper` | Registro estructurado JSONL con mapeo automático a técnicas MITRE ATT&CK (`T1083`, `T1059`, `T1499`) y patrones CAPEC (`CAPEC-126`, `CAPEC-248`, `CAPEC-130`). |

---

## 4. Matriz Regulatoria

- **EU AI Act (Art. 15):** Prevención activa contra explotación de vulnerabilidades en el entorno de ejecución agéntico.
- **NIS2 (Art. 21.2.c):** Continuidad operativa garantizada mediante cuotas de hardware que impiden ataques de denegación de servicio (DoS) al host.
- **DORA (Art. 9):** Aislamiento estricto de ejecuciones sin acceso a datos bancarios o secretos del servidor.
- **ENS Nivel Alto (Op.exp.8 / Op.pl.1):** Asignación de recursos infranqueables y mínimo privilegio con acceso exclusivo a directorio efímero.

---

## 5. Guía de Uso

### 5.1 Ejecución Directa mediante Python SDK

```python
from native_isolation_harness.core.harness_engine import HarnessEngine

engine = HarnessEngine()

# 1. Ejecutar un script Python de forma confinada
res = engine.execute_script(
    script_code="import sys\nprint('DATA_PROCESSED_SUCCESSFULLY')",
    session_id="agent_sess_01",
    agent_id="chief-of-staff"
)

print(f"Éxito: {res.success} | RAM Pico: {res.peak_memory_mb} MB | Tiempo: {res.duration_ms} ms")
print(res.stdout)

# 2. Ejecutar un comando validado
cmd_res = engine.execute_command(
    cmd=["python", "-c", "import os; print(os.getcwd())"],
    session_id="agent_sess_02"
)
```

### 5.2 Confinamiento de Servidores MCP Nativos (Stdio)

```python
from native_isolation_harness.mcp.mcp_sandbox_runner import MCPSandboxRunner

runner = MCPSandboxRunner()

# Lanza servidor nativo en Job Object con scratch efímero (Cero Docker)
with runner.start_isolated_mcp_server(["npx", "-y", "@modelcontextprotocol/server-postgres"]) as mcp:
    response = mcp.send_request({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    })
    print(response)
```

### 5.3 CLI del Harness y Monitor SOC

```powershell
# Ejecutar un comando o script bajo el sandbox
python src/native_isolation_harness/cli/harness_cli.py --cmd python -c "print('Harness Online')"

# Abrir el monitor de incidentes de seguridad SOC
python src/native_isolation_harness/cli/soc_monitor.py
```

---

## 6. Ejecución de Pruebas y Certificación

Para ejecutar la batería completa de pruebas unitarias, de integración y adversariales (29/29 tests):

```powershell
.\scripts\test_harness_isolation.ps1
```
