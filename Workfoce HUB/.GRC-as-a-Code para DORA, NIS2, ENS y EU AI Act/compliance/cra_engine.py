"""Cyber Resilience Act (CRA) Compliance & Supply Chain Security Engine — Regulation (EU) 2024/2847.

Audits Software Bill of Materials (SBOM Art. 11), Vulnerability Handling & VEX (Art. 13),
and Security by Design (Art. 10).
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from .nis2_engine import Finding


class CRAComplianceEngine:
    """Evaluates software security by design, vulnerability handling, and SBOM transparency."""

    PROMPT_INJECTION_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
        re.compile(r"system\s*prompt\s*override", re.IGNORECASE),
        re.compile(r"reveal\s+(api\s*key|secret|password|credentials)", re.IGNORECASE),
        re.compile(r"<script.*?>.*?</script>", re.IGNORECASE | re.DOTALL),
        re.compile(r"(base64|eval|exec)\s*\(", re.IGNORECASE),
    ]

    @classmethod
    def audit_software_supply_chain(cls, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Audits software assets against CRA Essential Requirements.

        Expected telemetry keys:
        - sbom_cyclonedx_generated (bool)
        - vex_vulnerability_disclosed (bool)
        - zero_default_credentials (bool)
        - automated_security_updates (bool)
        - input_sanitization_shield (bool)
        """
        findings: List[Finding] = []

        # 1. Art. 11 Machine-Readable Software Bill of Materials (SBOM)
        has_sbom = telemetry.get("sbom_cyclonedx_generated", False)
        findings.append(
            Finding(
                rule_id="CRA-SBOM-001",
                framework="CRA",
                title="CRA Art. 11 Software Bill of Materials in Machine-Readable Format (CycloneDX)",
                description="Maintain comprehensive, machine-readable inventory of software dependencies and hashes.",
                severity="CRITICAL",
                passed=has_sbom,
                evidence=f"CycloneDX v1.5 SBOM available: {has_sbom}",
                remediation_guidance="Generate CycloneDX v1.5 SBOM in build pipelines and sign with Cosign / Merkle proof.",
                iso27001_mapping=["A.8.28"],
            )
        )

        # 2. Art. 13 Vulnerability Handling & VEX Documentation
        has_vex = telemetry.get("vex_vulnerability_disclosed", False)
        findings.append(
            Finding(
                rule_id="CRA-VEX-002",
                framework="CRA",
                title="CRA Art. 13 Vulnerability Exploitability eXchange (VEX) & Disclosure",
                description="Publish actionable vulnerability advisories (VEX) confirming whether dependencies affect product.",
                severity="HIGH",
                passed=has_vex,
                evidence=f"VEX status tracking implemented: {has_vex}",
                remediation_guidance="Implement automated VEX generation mapping CVEs to actual execution paths.",
                iso27001_mapping=["A.8.8"],
            )
        )

        # 3. Art. 10 Security by Design & Elimination of Default Credentials
        no_defaults = telemetry.get("zero_default_credentials", False)
        findings.append(
            Finding(
                rule_id="CRA-SEC-003",
                framework="CRA",
                title="CRA Art. 10 Security by Default (No Default Passwords or Open Endpoints)",
                description="Deliver products with zero hardcoded credentials, randomized secrets, and authenticated APIs.",
                severity="CRITICAL",
                passed=no_defaults,
                evidence=f"Zero default credentials enforced: {no_defaults}",
                remediation_guidance="Enforce cryptographic API keys and remove all placeholder secrets.",
                iso27001_mapping=["A.5.15", "A.8.5"],
            )
        )

        # 4. Art. 10.4 Automated Secure Updates & Delivery
        updates = telemetry.get("automated_security_updates", False)
        findings.append(
            Finding(
                rule_id="CRA-UPDATE-004",
                framework="CRA",
                title="CRA Art. 10.4 Cryptographically Signed Updates & Secure Delivery",
                description="Provide digitally signed security updates that can be installed without user-side tampering.",
                severity="HIGH",
                passed=updates,
                evidence=f"Cryptographically verified update pipeline: {updates}",
                remediation_guidance="Sign all update payloads with HMAC or Ed25519 signatures before distribution.",
                iso27001_mapping=["A.8.19"],
            )
        )

        # 5. Art. 10.2 Defense against Injection & Input Exploitation
        injection_shield = telemetry.get("input_sanitization_shield", False)
        findings.append(
            Finding(
                rule_id="CRA-INPUT-005",
                framework="CRA",
                title="CRA Art. 10.2 Protection against Input Tampering & Prompt Injection",
                description="Strict input sanitization protecting LLM and API boundaries from adversarial payload injection.",
                severity="HIGH",
                passed=injection_shield,
                evidence=f"Input sanitization guard active: {injection_shield}",
                remediation_guidance="Deploy regex and semantic input filters across all public entry points.",
                iso27001_mapping=["A.8.26"],
            )
        )

        total = len(findings)
        passed = sum(1 for f in findings if f.passed)
        score = round((passed / total) * 100.0, 1) if total > 0 else 0.0

        if score >= 85.0:
            status = "GREEN"
        elif score >= 60.0:
            status = "AMBER"
        else:
            status = "RED"

        return {
            "framework": "CRA",
            "total_checks": total,
            "passed_checks": passed,
            "compliance_score": score,
            "status": status,
            "findings": findings,
        }

    @classmethod
    def generate_cyclonedx_sbom(cls, product_name: str = "compliance-sentinel", version: str = "1.0.0") -> Dict[str, Any]:
        """Generates CycloneDX v1.5 JSON Software Bill of Materials."""
        components = [
            {
                "type": "application",
                "name": product_name,
                "version": version,
                "description": "Autonomous GRC Multi-Agent Compliance Sentinel",
                "hashes": [{"alg": "SHA-256", "content": hashlib.sha256(product_name.encode()).hexdigest()}],
            },
            {
                "type": "library",
                "name": "swarms",
                "version": "14.0.0",
                "licenses": [{"license": {"id": "Apache-2.0"}}],
            },
            {
                "type": "library",
                "name": "pydantic",
                "version": "2.13.4",
                "licenses": [{"license": {"id": "MIT"}}],
            },
            {
                "type": "library",
                "name": "fastapi",
                "version": "0.115.0",
                "licenses": [{"license": {"id": "MIT"}}],
            },
        ]
        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": f"urn:uuid:compliance-sentinel-{hashlib.md5(datetime.now(timezone.utc).isoformat().encode()).hexdigest()}",
            "version": 1,
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tools": [{"vendor": "Antigravity DevSecOps", "name": "CRAComplianceEngine", "version": "1.0.0"}],
                "component": {"type": "application", "name": product_name, "version": version},
            },
            "components": components,
            "vulnerabilities": [],
        }
