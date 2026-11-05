# 🛡️ Aegis-Harness

## Banco de Evaluación Automatizado y Test Suite para Agentes de IA
> **Proyecto 1 del Roadmap de Nivel 5: Principal Agent Systems & Harness Architect**  
> **Directiva Mandatoria:** 100% Native Host (Cero Dependencias de Docker).  
> **Cumplimiento Normativo:** EU AI Act (Arts. 12, 14, 15), NIS2 (Art. 21), DORA (Art. 9) y ENS Nivel Alto.

---

## 1. Visión y Propósito
**Aegis-Harness** es un banco de pruebas determinista, evaluador de seguridad y gate de calidad para agentes autónomos basados en LLMs y servidores MCP (`MINI-AGENT LANGGRAPH`, `ai-employees`).

Permite detectar regresiones, validar precisión en selección de herramientas, certificar la resistencia ante ataques de *Prompt Injection* y emitir atestados de auditoría firmados criptográficamente sin necesidad de contenedores Docker.

---

## 2. Modos de Evaluación Soportados

Configurable en `aegis.config.yaml`:

1. **Evaluación Heurística Determinista (Coste $0 / Ultrarrápida):**
   - Validación de precisión de enrutamiento (`server` y `tool` exactos).
   - Validación de esquema de argumentos (`ArgumentSchemaEvaluator`).
   - Verificación de límites de latencia (`LatencyEvaluator`).
   - Verificación de restricciones y no-fuga de datos (`ConstraintEvaluator`).
   - Detección de brechas adversariales y jailbreaks (`SecurityEvaluator`).
   - *0 tokens LLM consumidos. 100% determinista y reproducible.*

2. **Juez Semántico Local con Ollama (Coste $0 / Soberanía de Datos):**
   - Conexión con instancia local de Ollama (`http://localhost:11434`).
   - Modelos recomendados: `llama3.2`, `mistral`, `qwen2.5`.
   - **Fallback automático transparente:** Si el daemon de Ollama no está activo, el sistema conmuta automáticamente a métricas deterministas sin interrumpir la suite.

---

## 3. Arquitectura del Sistema

```text
aegis-harness/
├── aegis.config.yaml                  # Configuración central (modos, pesos, umbrales)
├── pyproject.toml                     # Dependencias y configuración de pytest
├── datasets/                          # 120 Casos de Prueba
│   ├── functional/                    # 40 casos: Enrutamiento MCP (sqlite, github, filesystem, jira)
│   ├── adversarial/                   # 30 casos: Prompt injection, DAN, evasión y exfiltración
│   ├── edge_cases/                    # 20 casos: Cargas vacías, unicode, errores de sintaxis
│   └── regression/                    # 30 casos: Regresiones de bugs históricos y edge cases
├── src/aegis/
│   ├── models.py                      # Modelos Pydantic v2 (TestCase, TestResult, SuiteSummary)
│   ├── mock_mcp.py                    # Mock MCP Server (emulación determinista sin red)
│   ├── metrics.py                     # Agregador de métricas y puntuaciones
│   ├── gate.py                        # Quality Gate (bloqueo ante brechas o notas < 85%)
│   ├── ledger.py                      # Audit Ledger append-only con hash SHA-256 (NIS2 / SLSA)
│   ├── report.py                      # Generador de reportes Markdown y PDF ejecutivos
│   ├── runner.py                      # CLI Runner interactivo con Rich
│   ├── evaluators/
│   │   ├── deterministic.py           # Evaluadores deterministas (Tool, Schema, Latency, Constraints)
│   │   └── ollama_judge.py            # Evaluador juez local en Ollama
│   └── agents/
│       ├── langgraph_adapter.py       # Conector con LangGraph MCP Agent (assistant_graph.py)
│       └── ai_employees_adapter.py    # Conector con los 8 AI Employees
├── tests/                             # 29 Pruebas Unitarias del propio Harness
└── reports/                           # Salida de artefactos (PDF, MD, JSONL)
```

---

## 4. Instalación y Uso Rápido

### Requisitos Previos
- Python 3.11+
- Directiva Cero Docker: No requiere contenedores.

### Comandos de Ejecución

```bash
# 1. Ejecutar las pruebas unitarias e internas del Harness
pytest tests -v

# 2. Ejecutar la batería completa de evaluación de agentes (CLI Rich)
python -m aegis.runner

# 3. Ejecutar el script automatizado del Quality Gate (Windows PowerShell)
powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1
```

---

## 5. Batería de 120 Casos de Prueba

| Dataset | Fichero | Casos | Foco de Evaluación |
|:---|:---|:---:|:---|
| **Funcional** | `datasets/functional/routing_tests.yaml` | 40 | Precisión de selección de servidores SQLite, GitHub, Filesystem, Jira y respuestas directas. |
| **Adversarial** | `datasets/adversarial/prompt_injection.yaml` | 30 | Ataques DAN, Developer Mode, inyecciones en delimitadores, Base64 y robo de tokens. |
| **Edge Cases** | `datasets/edge_cases/mcp_edge_cases.yaml` | 20 | Payloads vacíos, caracteres Unicode especiales, tablas inexistentes y límites numéricos. |
| **Regresión** | `datasets/regression/known_bugs.yaml` | 30 | Verificación de corrección permanente de bugs históricos y estabilidad de sesión. |

---

## 6. Audit Ledger NIS2 y Trazabilidad Criptográfica

Cada evaluación genera un registro append-only en `reports/aegis_audit_ledger.jsonl`.
Cada bloque incluye:
- `previous_block_hash`: Hash SHA-256 del bloque anterior (encadenamiento tipo blockchain).
- `block_hash`: Hash SHA-256 del contenido actual.
- `slsa_provenance`: Declaración de procedencia SLSA v1.0 Level 3+.

Para verificar la integridad criptográfica del historial de auditoría:
```bash
python -c "from aegis.ledger import AuditLedger; valid, count, err = AuditLedger().verify_integrity(); print('Válido:', valid, 'Bloques:', count)"
```
