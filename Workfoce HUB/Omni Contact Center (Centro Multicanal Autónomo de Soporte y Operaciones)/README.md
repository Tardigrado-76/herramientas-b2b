# OMNI CONTACT — Contact Center IA Multimodal

Production-ready implementation of **OMNI CONTACT** ("Contact Center IA Multimodal") conforming to **NIS2 (EU 2022/2555)**, **RGPD/GDPR (EU 2016/679)**, and **CRA (EU 2024/2847)**.

Built using the combination of:
- **`/ponytail`**: Extreme minimalism, standard library first, zero bloat, robust security.
- **`/gstack`**: Transparent builder metrics, exact file references, and verified test evidence.
- **`/agency-agents` & `/agency-swarm`**: Specialized contact center personas + Pydantic `BaseTool` OpenAI schemas.
- **`/swarms`**: Centralized multi-agent conversational orchestration via `OmniHubEngine`.

---

## 1. Architecture Overview

```
E:\PROYECTOS IA\NEW TOOLS\Contact Center IA Multimodal\
├── __init__.py                 # Root package & sys.path injection
├── compliance/                 # Regulatory compliance modules
│   ├── __init__.py
│   ├── nis2_call_audit.py      # Immutable SHA-256 call audit ledger & 24h CSIRT early warning
│   ├── rgpd_audio_vault.py     # Real-time multimodal PII redaction & Art. 17 cryptographic shredding
│   └── cra_telephony_security.py # CycloneDX v1.5 SBOM & telephony adversarial injection firewall
├── channels/                   # Inbound/Outbound Multichannel Adapters
│   ├── __init__.py
│   └── multichannel_adapter.py # Normalizes Voice SIP, WhatsApp, WebChat, and Email
├── tools/                      # Agency-Swarm BaseTool implementations
│   ├── __init__.py
│   ├── base.py                 # BaseTool with automated OpenAI JSON Schema generation
│   ├── crm_lookup_tool.py      # Customer profile, tier and knowledge base lookup
│   ├── sentiment_escalation_tool.py # Real-time frustration scoring & supervisor transfer
│   └── call_disposition_tool.py# Wrap-up summary, CRM tagging, and CSAT logging
├── agents/                     # Multi-Agent contact center hub
│   ├── __init__.py
│   ├── personas.py             # System prompts for 4 contact center roles
│   └── hub_engine.py           # Core conversational orchestrator
├── api/                        # Production REST API
│   ├── __init__.py
│   └── server.py               # FastAPI server with telephony and compliance endpoints
└── tests/
    └── test_omni_contact.py    # 14 unit and integration tests (100% passing)
```

---

## 2. Supported Multimodal Channels & Autonomous Personas

### Supported Channels
- **Voice SIP / WebRTC**: Audio event ingestion, barge-in detection, TTS output formatting.
- **WhatsApp Cloud API**: Webhook payload normalization and structured text/media replies.
- **Web Chat**: Real-time websocket events and customer session threading.
- **Email**: Inbound thread extraction and formatted ticketing responses.

### Specialized Agent Personas
1. **`Receptionist_Triage`**: Initial greeting, intent capture, RGPD recording consent registration.
2. **`Billing_Specialist`**: Invoice breakdowns, refund policy verification, payment adjustments.
3. **`Technical_Support_Tier1`**: Step-by-step connectivity diagnostics, SIP trunk checks, knowledge base retrieval.
4. **`Supervisor_Escalation`**: Immediate crisis de-escalation, managerial authority, empathetic concession.

---

## 3. Regulatory Compliance Implementation

| Regulation | Article / Requirement | Implementation in OMNI CONTACT |
|---|---|---|
| **NIS2** | Directive EU 2022/2555 Art. 21 | `NIS2ContactAuditLedger`: Cryptographically chained SHA-256 blocks for every call turn, transfer, and disposition. |
| **NIS2** | Directive EU 2022/2555 Art. 23 | Incident notification reporting formatted for CSIRT dispatch within 24h for telephony intrusion attempts. |
| **RGPD** | Regulation EU 2016/679 Art. 6 & 7 | Explicit customer consent recording before audio/text transcription processing. |
| **RGPD** | Regulation EU 2016/679 Art. 25 | Privacy by Design: Real-time redaction of emails, credit cards, DNI/NIE, IBAN, CVVs, and phone numbers. |
| **RGPD** | Regulation EU 2016/679 Art. 17 | Right to Erasure: `crypto_shred_call()` destroys call metadata, audio keys, and raw transcripts permanently. |
| **CRA** | Regulation EU 2024/2847 Art. 10 | Telephony Adversarial Firewall: Heuristic inspection blocking voice/chat prompt injection attacks. |
| **CRA** | Regulation EU 2024/2847 Art. 11 | `CRATelephonyGuard.generate_cyclonedx_sbom()`: Machine-readable CycloneDX v1.5 JSON SBOM. |

---

## 4. Running the Tests & API

### Run Test Suite
```powershell
python -m unittest discover -s "E:\PROYECTOS IA\NEW TOOLS\Contact Center IA Multimodal\tests" -p "test_*.py" -v
```

### Run FastAPI Production Server
```powershell
uvicorn api.server:app --app-dir "E:\PROYECTOS IA\NEW TOOLS\Contact Center IA Multimodal" --host 0.0.0.0 --port 8005 --reload
```
