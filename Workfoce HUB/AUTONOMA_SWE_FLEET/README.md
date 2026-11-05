# 🛸 AUTONOMA SWE-FLEET — Enjambre de Ingeniería para Factorías de Software

> **Tagline:** *"Convierte una especificación de producto en 5 Pull Requests validadas en paralelo sin colisiones de Git ni bucles infinitos."*

**Producto Turnkey (Micro-SaaS Soberano)** que fusiona la arquitectura de **White Coding Harness**, **Gas Town** y **Skills-Manager** para orquestar flotas de agentes de codificación autónomos sobre repositorios compartidos con garantías matemáticas de no colisión.

---

## 💥 El Dolor Crítico del Mercado

Los equipos de ingeniería de software que despliegan múltiples agentes de codificación (Claude Code, Cursor, Copilot, Gemini CLI) sufren rápidamente cuatro problemas letales:
1. **Colisiones de Git:** Múltiples agentes trabajando sobre la misma rama principal generan conflictos de fusión destructivos y bloqueos de archivos (*lock contention*).
2. **Quiebra de Presupuestos de Tokens (Bucles Infinitos):** Agentes que entran en ciclos de reintentos ciegos sobre el mismo error de compilación, agotando presupuestos en minutos.
3. **Pérdida de Trazabilidad con Jira/Linear:** El código generado pierde la correspondencia con las historias de usuario y criterios de aceptación originales.
4. **Degradación Arquitectónica ("Vibe Coding"):** Agentes que crean módulos superficiales (*shallow modules*), violan las costuras (*seams*) y añaden dependencias prohibidas.

---

## 🏛️ Cómo Funciona la Solución: Los 3 Pilares

```
[PM / Jira / Linear Epic]
           │
           ▼
[1. StepContract Inmutable]  ──► Fija superficie pública, dependencias prohibidas y criterios Gherkin
           │
           ▼
[2. Gas Town (The Mayor)]    ──► Descompone en 5 Beads ('bd') y asigna a 5 Polecats en Git Worktrees
           │
           ├── [The Witness] ──► Watchdog: Mata al agente si falla 3 veces el mismo test o supera tokens
           │
           ▼
[3. Puerta de Fusión]        ──► 100% Pytest + Validador AST (Matt Pocock: Módulos Profundos)
           │
           ▼
[5 Pull Requests en Paralelo] ──► Zero Git Collisions, listas para merge
```

### 1. White Coding (StepContracts & Costuras AST)
Cada micro-tarea se formaliza en un `StepContract` inmutable:
- **Interface is the Test Surface:** Prohibido acoplar pruebas a variables o métodos privados `_`.
- **Validador AST:** Inspección estática de árboles de sintaxis abstracta para garantizar que no existan dependencias no autorizadas y que el ratio LOC/interfaz cumpla con el estándar de *módulos profundos*.

### 2. Gas Town & Git Worktrees Aislados
Inspirado en el framework creado por Steve Yegge:
- **The Mayor:** Director de orquesta que descompone épicas en unidades atómicas (*Beads*).
- **Beads Ledger (`bd`):** Libro mayor de tareas persistido en archivo/Git que resiste caídas y compactaciones de contexto.
- **Polecats en Git Worktrees:** Cada obrero opera en un subdirectorio físico independiente (`git worktree add -b polecat/<bead_id>`). Múltiples agentes modifican el repositorio simultáneamente **sin ninguna colisión de Git**.

### 3. The Witness (Circuit Breaker Anti-Bucles)
- **Regla de 3 Fallos:** Si un agente falla 3 veces consecutivas el mismo test unitario, The Witness ejecuta un `KILL` forzado inmediato.
- **Presupuesto Máximo de Tokens:** Si un agente supera el presupuesto asignado (ej. 40.000 tokens), el proceso se detiene en seco.
- **Autopsia Forense:** Registro detallado de cada eliminación en `storage/autopsy_reports/` para auditoría y mejora continua.

---

## 🚀 Inicio Rápido en Windows

### 1. Lanzador Principal (Doble Click)
Haga doble click sobre cualquiera de los siguientes accesos directos:
- **Acceso Directo:** `SWE_FLEET.lnk`
- **Script Batch:** [INICIAR_SWE_FLEET.bat](file:///E:/PROYECTOS%20IA/NEW%20TOOLS/AUTONOMA_SWE_FLEET/INICIAR_SWE_FLEET.bat)
- **Lanzador Raíz:** [E:\PROYECTOS IA\NEW TOOLS\INICIAR_SWE_FLEET.bat](file:///E:/PROYECTOS%20IA/NEW%20TOOLS/INICIAR_SWE_FLEET.bat)

El servidor iniciará automáticamente en:
👉 **`http://localhost:8512`**

---

## 🐳 Despliegue Secundario en Contenedor (Opcional)

Para entornos aislados o servidores Linux/Docker:
```bash
docker-compose up -d --build
```
El contenedor se ejecuta en modo no-root con puerto expuesto `8512:8512` y persistencia en `./storage` y `./sandbox`.

---

## 🔒 Soberanía, BYOK y Modo Air-Gapped

- **Air-Gapped Activo (Por defecto):** Los repositorios y código fuente no abandonan la infraestructura local. Funciona de manera nativa con modelos locales vía **Ollama** (`http://localhost:11434/v1` con `qwen2.5-coder:latest` o `mistral`).
- **BYOK (Bring Your Own Key):** Soporte opcional para conectar modelos de Claude 3.5 Sonnet, GPT-4o, DeepSeek-V3 o Gemini 1.5 Pro.

---

## 🧪 Pruebas Unitarias Automatizadas

Para ejecutar la suite de pruebas completa:
```bash
python -m pytest tests/ -v
```
100% de cobertura en:
- `test_step_contract.py`: Conformidad de contratos e invariantes.
- `test_ast_validator.py`: Detección de importaciones prohibidas y módulos superficiales.
- `test_worktree_isolation.py`: Validación de aislamiento físico de worktrees y ausencia de colisiones.
- `test_witness_circuit_breaker.py`: Liquidación exacta al 3er fallo consecutivo y por límite de tokens.
- `test_mayor_orchestration.py`: Orquestación paralela de 5 Pull Requests completas y contención de agentes rebeldes.
