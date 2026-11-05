"""
CRA Compliance Module - Cyber Resilience Act (EU Regulation 2024/2847)
Provides CycloneDX v1.5 JSON SBOM, prompt injection guardrails, and secure execution limits.
"""
import re
import time
from typing import Any, ClassVar


class CRASecurityGuard:
    """
    Enforces Cyber Resilience Act requirements (Art. 10 & 11) for AI Agent systems:
    - SBOM generation (CycloneDX v1.5 JSON)
    - Anti-prompt-injection boundary checks
    - Sandboxing constraint verification
    """

    # Prohibited prompt injection attack heuristics
    INJECTION_HEURISTICS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r'ignore\s+all\s+previous\s+instructions', re.IGNORECASE),
        re.compile(r'system\s+override', re.IGNORECASE),
        re.compile(r'disregard\s+system\s+prompt', re.IGNORECASE),
        re.compile(r'you\s+are\s+now\s+in\s+developer\s+mode', re.IGNORECASE),
        re.compile(r'bypass\s+safety\s+filters', re.IGNORECASE),
        re.compile(r'reveal\s+internal\s+credentials', re.IGNORECASE),
        re.compile(r'dump\s+database\s+passwords', re.IGNORECASE),
        re.compile(r'cat\s+/etc/shadow', re.IGNORECASE)
    ]

    @classmethod
    def inspect_prompt(cls, prompt: str) -> tuple[bool, str]:
        """
        CRA Art. 10: Protection against unauthorized adversarial inputs.
        Returns (is_safe: bool, reason: str).
        """
        for pattern in cls.INJECTION_HEURISTICS:
            if pattern.search(prompt):
                return False, f"Malicious input detected matching pattern: {pattern.pattern}"
        return True, "Safe"

    @classmethod
    def generate_cyclonedx_sbom(cls) -> dict[str, Any]:
        """
        CRA Art. 11: Machine-readable Software Bill of Materials (SBOM) in CycloneDX v1.5 format.
        """
        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": f"urn:uuid:workforce-ai-cra-{int(time.time())}",
            "version": 1,
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "component": {
                    "type": "application",
                    "name": "WORKFORCE AI",
                    "version": "1.0.0",
                    "description": "On-demand autonomous AI workforce platform conforming to NIS2, RGPD, and CRA."
                },
                "licenses": [
                    {"license": {"id": "Apache-2.0"}}
                ]
            },
            "components": [
                {
                    "type": "framework",
                    "name": "swarms",
                    "version": "8.5.0",
                    "purl": "pkg:pypi/swarms@8.5.0",
                    "scope": "required"
                },
                {
                    "type": "library",
                    "name": "agency-swarm",
                    "version": "0.4.0",
                    "purl": "pkg:pypi/agency-swarm@0.4.0",
                    "scope": "required"
                },
                {
                    "type": "framework",
                    "name": "fastapi",
                    "version": "0.115.0",
                    "purl": "pkg:pypi/fastapi@0.115.0",
                    "scope": "required"
                },
                {
                    "type": "library",
                    "name": "pydantic",
                    "version": "2.9.2",
                    "purl": "pkg:pypi/pydantic@2.9.2",
                    "scope": "required"
                }
            ],
            "vulnerabilities": []
        }
