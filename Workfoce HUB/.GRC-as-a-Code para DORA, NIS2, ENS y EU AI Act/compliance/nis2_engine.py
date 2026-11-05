"""NIS2 Compliance Evaluation and Incident Alerting Engine — Directive (EU) 2022/2555.

Evaluates Article 21 Technical and Operational Cybersecurity Risk Management measures
and enforces Article 23 Incident Notification SLAs.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Finding:
    rule_id: str
    framework: str
    title: str
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    passed: bool
    evidence: str
    remediation_guidance: str
    iso27001_mapping: List[str] = field(default_factory=list)


@dataclass
class NIS2AuditResult:
    framework: str
    total_checks: int
    passed_checks: int
    compliance_score: float  # 0.0 - 100.0
    status: str  # GREEN (>=85%), AMBER (60-84%), RED (<60%)
    findings: List[Finding]
    incident_triggers_ready: bool


class NIS2ComplianceEngine:
    """Evaluates organization or infrastructure state against NIS2 Art. 21 controls."""

    def evaluate_environment(self, telemetry: Dict[str, Any]) -> NIS2AuditResult:
        """Evaluates infrastructure telemetry against NIS2 Art. 21 baseline controls.

        Expected telemetry keys (boolean/metadata):
        - mfa_enforced (bool)
        - tls_enforced (bool)
        - automated_backups (bool)
        - supply_chain_sbom_present (bool)
        - incident_playbook_tested (bool)
        - vulnerability_patching_active (bool)
        - employee_cyber_training (bool)
        """
        findings: List[Finding] = []

        # 1. Art. 21.2(j) MFA and Secure Communications
        mfa = telemetry.get("mfa_enforced", False)
        tls = telemetry.get("tls_enforced", False)
        mfa_ok = mfa and tls
        findings.append(
            Finding(
                rule_id="NIS2-MFA-001",
                framework="NIS2",
                title="NIS2 Art. 21.2(j) Multi-Factor Authentication & Encrypted Transport",
                description="Enforce MFA on all administrative interfaces and TLS 1.3 / mTLS on endpoints.",
                severity="CRITICAL",
                passed=mfa_ok,
                evidence=f"MFA Enforced: {mfa}, TLS Enforced: {tls}",
                remediation_guidance="Mandate MFA across all identity providers and enforce TLS 1.3.",
                iso27001_mapping=["A.8.5", "A.8.24"],
            )
        )

        # 2. Art. 21.2(c) Business Continuity & Disaster Recovery
        backups = telemetry.get("automated_backups", False)
        findings.append(
            Finding(
                rule_id="NIS2-RESIL-002",
                framework="NIS2",
                title="NIS2 Art. 21.2(c) Business Continuity, Backup Management & DR",
                description="Maintain automated, air-gapped, or immutable backup systems with tested RTO/RPO.",
                severity="CRITICAL",
                passed=backups,
                evidence=f"Automated backups active: {backups}",
                remediation_guidance="Implement immutable daily snapshots and perform quarterly disaster restore drills.",
                iso27001_mapping=["A.8.14", "A.8.13"],
            )
        )

        # 3. Art. 21.2(d) Supply Chain Risk & SBOM Handling
        sbom = telemetry.get("supply_chain_sbom_present", False)
        findings.append(
            Finding(
                rule_id="NIS2-SUPPLY-003",
                framework="NIS2",
                title="NIS2 Art. 21.2(d) Supply Chain Security & Software Component Transparency",
                description="Maintain verifiable Software Bill of Materials (SBOM) for all third-party software components.",
                severity="HIGH",
                passed=sbom,
                evidence=f"CycloneDX SBOM verified: {sbom}",
                remediation_guidance="Integrate automated CycloneDX SBOM generation into the CI/CD pipeline.",
                iso27001_mapping=["A.5.19", "A.5.20"],
            )
        )

        # 4. Art. 21.2(b) Incident Handling & Notification Preparedness
        incident_plan = telemetry.get("incident_playbook_tested", False)
        findings.append(
            Finding(
                rule_id="NIS2-INCIDENT-004",
                framework="NIS2",
                title="NIS2 Art. 21.2(b) Incident Handling & Art. 23 Notification Timelines",
                description="Maintain verified incident notification triggers (24h early warning, 72h full report).",
                severity="HIGH",
                passed=incident_plan,
                evidence=f"Incident playbook verified: {incident_plan}",
                remediation_guidance="Establish 24h CSIRT notification protocol and automated incident webhook.",
                iso27001_mapping=["A.5.24", "A.5.25"],
            )
        )

        # 5. Art. 21.2(e) Vulnerability Patching & Hygiene
        patching = telemetry.get("vulnerability_patching_active", False)
        findings.append(
            Finding(
                rule_id="NIS2-PATCH-005",
                framework="NIS2",
                title="NIS2 Art. 21.2(e) Vulnerability Handling and Security Patching",
                description="Regular vulnerability scans and automated patching of high/critical CVEs within 14 days.",
                severity="MEDIUM",
                passed=patching,
                evidence=f"Active vulnerability patch management: {patching}",
                remediation_guidance="Deploy automated patch management and CISA KEV monitoring.",
                iso27001_mapping=["A.8.8"],
            )
        )

        # 6. Art. 21.2(g) Cyber Hygiene & Training
        training = telemetry.get("employee_cyber_training", False)
        findings.append(
            Finding(
                rule_id="NIS2-HYGIENE-006",
                framework="NIS2",
                title="NIS2 Art. 21.2(g) Cybersecurity Training & Cyber Hygiene",
                description="Periodic employee cybersecurity training, phishing simulations, and credential hygiene.",
                severity="LOW",
                passed=training,
                evidence=f"Staff cybersecurity training logged: {training}",
                remediation_guidance="Schedule mandatory annual security refresher training for all employees.",
                iso27001_mapping=["A.6.3"],
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

        return NIS2AuditResult(
            framework="NIS2",
            total_checks=total,
            passed_checks=passed,
            compliance_score=score,
            status=status,
            findings=findings,
            incident_triggers_ready=incident_plan,
        )
