# WORKFORCE AI - Autonomous On-Demand AI Employee Platform

Production-ready implementation of **App #4: WORKFORCE AI** ("Upwork de Agentes IA Autónomos Bajo Demanda") conforming to **NIS2 (EU 2022/2555)**, **RGPD/GDPR (EU 2016/679)**, and **CRA (EU 2024/2847)**.

Built using the combination of:
- **`/ponytail`**: Extreme minimalism, standard library first, zero bloat, robust security.
- **`/gstack`**: Transparent builder metrics, exact file references, and verified test evidence.
- **`/agency-agents` & `/agency-swarm`**: 8 autonomous specialized employee personas + Chief of Staff with Pydantic `BaseTool` OpenAI schemas and dynamic routing.
- **`/swarms`**: Centralized multi-agent orchestration via `WorkforceHubEngine`.

---

## 1. Architecture Overview

```
E:\PROYECTOS IA\NEW TOOLS\WORKFORCE AI\
├── __init__.py                 # Root package & sys.path injection
├── compliance/                 # Regulatory compliance modules
│   ├── __init__.py
│   ├── nis2_worker_audit.py    # Immutable SHA-256 execution ledger & early incident warnings
│   ├── rgpd_tenant_vault.py    # PII scrubber & Art. 17 cryptographic shredding
│   └── cra_agent_security.py   # CycloneDX v1.5 SBOM & prompt injection firewall
├── tools/                      # Agency-Swarm BaseTool implementations
│   ├── __init__.py
│   ├── base.py                 # BaseTool with automated OpenAI JSON Schema generation
│   ├── agent_hiring_tool.py    # Contract binding & SLA allocation per role
│   ├── task_router_tool.py     # Dynamic intent & capability matching
│   ├── token_budget_tool.py    # Real-time token consumption & spending limits
│   └── quality_gate_tool.py    # Automated editorial and technical deliverable judge
├── agents/                     # Multi-Agent workforce hub
│   ├── __init__.py
│   ├── personas.py             # System prompts for 8 employee roles + Chief of Staff
│   └── hub_engine.py           # Core orchestrator coordinating security, routing & audit
├── api/                        # Production REST API
│   ├── __init__.py
│   └── server.py               # FastAPI server with regulatory and operational endpoints
└── tests/
    └── test_workforce_ai.py    # 14 unit and integration tests (100% passing)
```

---

## 2. Supported Autonomous Workforce Personas

1. **`Chief_of_Staff`**: Cross-agent orchestrator, executive briefing, task decomposition.
2. **`GTM_Engineer`**: Inbound/outbound pipeline automation, CRM sync, conversion telemetry.
3. **`SEO_AEO_Specialist`**: Perplexity/Claude AEO citation optimization, Schema.org markup, SERP audits.
4. **`FullStack_WebDev`**: FastAPI endpoints, responsive frontend, clean JS, landing pages.
5. **`Social_Media_Manager`**: Multi-channel content calendars, viral hooks, X/LinkedIn threads.
6. **`Ad_Manager`**: High-ROAS ad copywriting, multi-variant testing, budget modeling.
7. **`Sales_Representative`**: B2B cold email sequences, ICP scoring, objection handling.
8. **`Customer_Satisfaction`**: Empathetic ticket triage, customer de-escalation, issue resolution.

---

## 3. Regulatory Compliance Implementation

| Regulation | Article / Requirement | Implementation in WORKFORCE AI |
|---|---|---|
| **NIS2** | Directive EU 2022/2555 Art. 21 | `NIS2WorkerLedger`: Cryptographically chained SHA-256 blocks for every employee execution. Non-repudiation and tamper detection. |
| **NIS2** | Directive EU 2022/2555 Art. 23 | Incident notification reporting formatted for CSIRT dispatch within 24h for security anomalies. |
| **RGPD** | Regulation EU 2016/679 Art. 25 | Privacy by Design: Regex-driven sanitization of email, phone, IBAN, DNI/NIE, credit cards before tool processing. |
| **RGPD** | Regulation EU 2016/679 Art. 17 | Right to Erasure: `crypto_shred_tenant()` destroys keys and wipes tenant memory permanently. |
| **CRA** | Regulation EU 2024/2847 Art. 10 | Prompt Injection Firewall: Heuristic pattern inspection intercepting adversarial overrides. |
| **CRA** | Regulation EU 2024/2847 Art. 11 | `CRASecurityGuard.generate_cyclonedx_sbom()`: Machine-readable CycloneDX v1.5 JSON SBOM. |

---

## 4. Running the Tests & API

### Run Test Suite
```powershell
python -m unittest discover -s "E:\PROYECTOS IA\NEW TOOLS\WORKFORCE AI\tests" -p "test_*.py" -v
```

### Run FastAPI Production Server
```powershell
uvicorn api.server:app --app-dir "E:\PROYECTOS IA\NEW TOOLS\WORKFORCE AI" --host 0.0.0.0 --port 8004 --reload
```
