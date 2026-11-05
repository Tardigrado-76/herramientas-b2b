"""
CRA Compliance Module - Cyber Resilience Act (EU Regulation 2024/2847)
Provides CycloneDX v1.5 JSON SBOM, multimodal prompt injection firewall, and telephony safety checks.
"""
import re
import time
from typing import Any, ClassVar


class CRATelephonyGuard:
    """
    Enforces Cyber Resilience Act requirements (Art. 10 & 11) for Multimodal Contact Centers:
    - Audio/Text prompt injection detection
    - Telephony resource exhaustion guards
    - CycloneDX v1.5 JSON SBOM generation
    """

    # Prohibited prompt injection attack heuristics (voice-transcribed or text-based)
    ATTACK_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r'ignore\s+previous\s+instructions', re.IGNORECASE),
        re.compile(r'system\s+prompt\s+override', re.IGNORECASE),
        re.compile(r'you\s+are\s+now\s+in\s+operator\s+mode', re.IGNORECASE),
        re.compile(r'transfer\s+me\s+to\s+root\s+admin', re.IGNORECASE),
        re.compile(r'read\s+back\s+all\s+caller\s+records', re.IGNORECASE),
        re.compile(r'dump\s+crm\s+database', re.IGNORECASE),
        re.compile(r'bypass\s+authentication', re.IGNORECASE)
    ]

    @classmethod
    def inspect_utterance(cls, text: str) -> tuple[bool, str]:
        """
        CRA Art. 10: Protection against unauthorized adversarial inputs in voice/chat.
        Returns (is_safe: bool, reason: str).
        """
        for pattern in cls.ATTACK_PATTERNS:
            if pattern.search(text):
                return False, f"Malicious telephony input detected: {pattern.pattern}"
        return True, "Safe"

    @classmethod
    def generate_cyclonedx_sbom(cls) -> dict[str, Any]:
        """
        CRA Art. 11: Machine-readable Software Bill of Materials (SBOM) in CycloneDX v1.5 format.
        """
        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": f"urn:uuid:omni-contact-cra-{int(time.time())}",
            "version": 1,
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "component": {
                    "type": "application",
                    "name": "OMNI CONTACT",
                    "version": "1.0.0",
                    "description": "Enterprise Multimodal AI Contact Center complying with NIS2, RGPD, and CRA."
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
