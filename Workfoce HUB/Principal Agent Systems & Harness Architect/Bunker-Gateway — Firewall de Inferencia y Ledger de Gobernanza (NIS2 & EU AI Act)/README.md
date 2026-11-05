# 🛡️ Bunker-Gateway

> **Reverse Proxy de Inferencia, Firewall Agéntico y Ledger Inmutable de Gobernanza**  
> **Cumplimiento Normativo:** EU AI Act (Arts. 12, 14, 15), NIS2 (Art. 21), DORA (Art. 9) y ENS Nivel Alto.  
> **Directiva:** 100% Native Host (Cero Dependencias de Docker).

---

## 1. Visión General

Bunker-Gateway es un proxy inverso local y firewall de inferencia que se coloca in-line entre los agentes autónomos (`MINI-AGENT LANGGRAPH`, `ai-employees`, etc.) y los proveedores LLM (OpenAI, Anthropic, Ollama local) o servidores MCP nativos (`stdio`/`SSE`).

### Capacidades Clave
1. **Sanitización Bidireccional de PII:** Redacta automáticamente DNI/NIE, IBAN español, números de tarjeta, emails y teléfonos antes de salir a la nube, y los rehidrata de forma transparente para el cliente autorizado.
2. **Escudo Anti-Prompt Injection & Jailbreak:** Detecta y bloquea intentos de manipulación de instrucciones (`DAN`, `system prompt override`, delimitadores falsos y payloads Base64 ofuscados).
3. **Detector de Fuga de Secretos (Outbound):** Intercepta en tiempo real claves API (`sk-...`, `AKIA...`, `ghp_...`), llaves criptográficas privadas y connection strings, bloqueando la exfiltración antes de llegar al usuario.
4. **Circuit Breaker Anti-Loops:** Interrumpe bucles infinitos agénticos cuando detecta 4 llamadas idénticas consecutivas (código HTTP 429), protegiendo la API key y evitando sobrecostes.
5. **Ledger Inmutable Hash-Chain NIS2:** Registra cada transacción en `data/audit_nis2_ledger.jsonl` encadenada criptográficamente con SHA-256 y sellada con firmas clásicas (ECDSA P-256) y post-cuánticas (ML-DSA-87 / FIPS 204).
6. **Interceptor Nativo MCP:** Inspecciona llamadas JSON-RPC a herramientas nativas en `stdio`/`SSE`, bloqueando operaciones destructivas según políticas declarativas ABAC (`config/abac_policies.yaml`).

---

## 2. Puesta en Marcha Rápida (Windows Native)

### 2.1 Iniciar el Gateway
```powershell
powershell -ExecutionPolicy Bypass -File "scripts/start_gateway.ps1"
```
O directamente con Python:
```powershell
$env:PYTHONPATH = "src"
python -m uvicorn bunker_gateway.main:app --host 127.0.0.1 --port 8080
```

### 2.2 Redirigir Clientes Agénticos (Drop-in Replacement)
Configura tu cliente OpenAI o LangGraph para apuntar al gateway local:
```python
from openai import OpenAI

# Redirección en 1 línea
client = OpenAI(
    base_url="http://127.0.0.1:8080/v1",
    api_key="tu-api-key",
    default_headers={"X-Agent-Id": "langgraph-agent", "X-Session-Id": "sess_001"}
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Consulta los datos de Juan Perez con DNI 12345678Z"}]
)
```

### 2.3 Inspección Forense del Ledger
```powershell
python -m bunker_gateway.cli.audit_cli
```
Para sellar la época actual con árbol Merkle y firmas PQC:
```powershell
python -m bunker_gateway.cli.audit_cli --seal
```

---

## 3. Matriz de Cumplimiento Normativo

| Regulación | Artículo | Mecanismo de Garantía |
| :--- | :--- | :--- |
| **EU AI Act** | **Art. 12 (Trazabilidad y Registros)** | Registro append-only inmutable SHA-256 de toda inferencia y tool call. |
| **EU AI Act** | **Art. 14 (Supervisión Humana)** | Circuit breaker con corte automático de bucles y paradas de emergencia. |
| **EU AI Act** | **Art. 15 (Ciberseguridad y Robustez)** | Escudo anti-jailbreak y neutralización de inyección de prompts. |
| **NIS2** | **Art. 21 (Gestión de Riesgos)** | Inspección in-line Zero-Trust del 100% del tráfico agéntico. |
| **DORA** | **Art. 9 (Protección de Integridad)** | Sanitización de PII bancaria (IBAN, tarjetas) y detección de secretos. |
| **ENS Nivel Alto** | **Op.pl.4 (Integridad)** | Encadenamiento SHA-256 tipo blockchain y manifiestos SLSA v1.0 Level 3+. |
