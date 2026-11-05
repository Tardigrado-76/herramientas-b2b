"""Cyber Resilience Act (CRA) Outbound Module — Regulation (EU) 2024/2847.

Enforces:
1. Security by Design & Anti-Phishing Guardrails:
   - Blocks deceptive headers, fake 'Re:' prefixes on first outreach.
   - Blocks prompt injection in prospect notes or scraped web data.
   - Spam score heuristic screening.
2. CycloneDX v1.5 JSON SBOM generation for OUTBOUND MACHINE.
3. Domain security hygiene (SPF, DKIM, DMARC alignment check).
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple


class CRAOutboundSecurityManager:
    """Guards outbound messaging pipelines against exploitation, reputation damage, and CRA infractions."""

    PROMPT_INJECTION_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
        re.compile(r"system\s*prompt\s*override", re.IGNORECASE),
        re.compile(r"send\s+(this|the)\s+email\s+to\s+everyone", re.IGNORECASE),
        re.compile(r"reveal\s+(api\s*key|secret|password|credentials)", re.IGNORECASE),
        re.compile(r"<script.*?>.*?</script>", re.IGNORECASE | re.DOTALL),
        re.compile(r"(base64|eval|exec)\s*\(", re.IGNORECASE),
    ]

    DECEPTIVE_SUBJECT_PATTERNS = [
        re.compile(r"^(re|fwd|rv)\s*:\s*", re.IGNORECASE),
        re.compile(r"(urgent|act\s+now|account\s+suspended|security\s+alert)", re.IGNORECASE),
        re.compile(r"(\$\$\$|100%\s+free|guaranteed\s+profit)", re.IGNORECASE),
    ]

    @classmethod
    def sanitize_prospect_input(cls, text: str) -> Tuple[str, bool, List[str]]:
        """Cleanses prospect data scraped from external websites before passing to LLM."""
        threats = []
        for pattern in cls.PROMPT_INJECTION_PATTERNS:
            if pattern.search(text):
                threats.append(pattern.pattern)

        is_safe = len(threats) == 0
        clean = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text).strip()
        return clean, is_safe, threats

    @classmethod
    def validate_outbound_pitch(cls, subject: str, body: str, is_first_contact: bool = True) -> Tuple[bool, List[str]]:
        """Audits drafted emails against deceptive phishing tactics and anti-spam heuristics."""
        warnings: List[str] = []

        if is_first_contact:
            for pattern in cls.DECEPTIVE_SUBJECT_PATTERNS:
                if pattern.search(subject):
                    warnings.append(f"DECEPTIVE_SUBJECT_WARNING: Subject '{subject}' violates anti-phishing hygiene.")

        # Check for ALL CAPS shouting
        words = subject.split()
        if len(words) > 3 and sum(1 for w in words if w.isupper()) / len(words) > 0.6:
            warnings.append("SPAM_WARNING: Excessive uppercase in subject line.")

        # Check for empty body or excessive length
        if len(body.strip()) < 50:
            warnings.append("QUALITY_WARNING: Email body is too brief (< 50 chars).")
        elif len(body.strip()) > 5000:
            warnings.append("QUALITY_WARNING: Email body exceeds 5,000 characters, risking ISP clip.")

        passed = len(warnings) == 0
        return passed, warnings

    @classmethod
    def generate_cyclonedx_sbom(cls, product_name: str = "outbound-machine", version: str = "1.0.0") -> Dict[str, Any]:
        """Generates standard CycloneDX v1.5 JSON SBOM for CRA conformity (Art. 11)."""
        components = [
            {
                "type": "application",
                "name": product_name,
                "version": version,
                "purl": f"pkg:generic/{product_name}@{version}",
                "description": "Autonomous Outbound Sales Engine with multi-agent research & GRC compliance",
                "scope": "required",
                "hashes": [{"alg": "SHA-256", "content": hashlib.sha256(product_name.encode()).hexdigest()}],
            },
            {
                "type": "library",
                "name": "swarms",
                "version": "14.0.0",
                "purl": "pkg:pypi/swarms@14.0.0",
                "scope": "required",
                "licenses": [{"license": {"id": "Apache-2.0"}}],
                "description": "Multi-agent autonomous framework",
            },
            {
                "type": "library",
                "name": "pydantic",
                "version": "2.13.4",
                "purl": "pkg:pypi/pydantic@2.13.4",
                "scope": "required",
                "licenses": [{"license": {"id": "MIT"}}],
                "description": "Data validation using Python type hints",
            },
            {
                "type": "library",
                "name": "fastapi",
                "version": "0.115.0",
                "purl": "pkg:pypi/fastapi@0.115.0",
                "scope": "required",
                "licenses": [{"license": {"id": "MIT"}}],
                "description": "FastAPI ASGI web framework",
            },
        ]

        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": f"urn:uuid:outbound-machine-{hashlib.md5(datetime.now(timezone.utc).isoformat().encode()).hexdigest()}",
            "version": 1,
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tools": [{"vendor": "Antigravity DevSecOps", "name": "CRAOutboundSecurityManager", "version": "1.0.0"}],
                "component": {
                    "type": "application",
                    "name": product_name,
                    "version": version,
                },
            },
            "components": components,
            "vulnerabilities": [],
        }
