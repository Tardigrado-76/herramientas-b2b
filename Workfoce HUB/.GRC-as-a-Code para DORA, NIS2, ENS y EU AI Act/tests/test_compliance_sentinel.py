"""Comprehensive Unit and Integration Test Suite for COMPLIANCE SENTINEL.
Verifies Merkle Tree Evidence Sealing, NIS2 Risk Auditing, RGPD TOMs/DPIA, CRA SBOM, and Multi-Agent GRC Council.
"""

from __future__ import annotations

import sys
from pathlib import Path
package_root = Path(__file__).resolve().parent.parent
if str(package_root) not in sys.path:
    sys.path.insert(0, str(package_root))

import tempfile
import unittest
from fastapi.testclient import TestClient

from agents.council_engine import ComplianceSentinelEngine
from api.server import API_KEY_SECRET, app
from compliance.cra_engine import CRAComplianceEngine
from compliance.nis2_engine import NIS2ComplianceEngine
from compliance.rgpd_engine import RGPDComplianceEngine
from reporting.executive_dictamen import ExecutiveDictamenGenerator
from sealer.merkle_bunker import EvidenceSeal, MerkleBunkerSealer
from tools.cra_sbom_tool import CRASBOMTool
from tools.nis2_audit_tool import NIS2AuditTool
from tools.remediation_planner_tool import RemediationPlannerTool
from tools.rgpd_audit_tool import RGPDAuditTool


class TestComplianceSentinel(unittest.TestCase):
    def setUp(self):
        self.sealer = MerkleBunkerSealer(secret_key="test-sentinel-key")
        self.engine = ComplianceSentinelEngine(
            tenant_id="test_grc_tenant",
            company_name="Empresa Piloto S.L.",
            sealer=self.sealer,
        )

    # --- 1. Merkle Tree & Evidence Bunker Sealer Tests ---
    def test_merkle_tree_construction_and_sealing(self):
        """Verifies binary Merkle Tree root calculation, sealing, and tamper verification."""
        evidence = {
            "policy_access.json": '{"mfa": true, "tls": "1.3"}',
            "incident_log.json": '{"incidents_reported_24h": 0}',
            "sbom_manifest.json": '{"format": "CycloneDX", "version": "1.5"}',
        }
        root, leaves = self.sealer.build_merkle_root(evidence)
        self.assertEqual(len(leaves), 3)
        self.assertEqual(len(root), 64)  # Valid SHA-256 hex string

        seal = self.sealer.issue_seal("Empresa Piloto S.L.", evidence, frameworks=["NIS2", "RGPD", "CRA"])
        self.assertEqual(seal.merkle_root, root)
        self.assertTrue(self.sealer.verify_seal(seal))

        # Tampering detection: modify seal merkle root
        tampered_seal = EvidenceSeal(
            seal_id=seal.seal_id,
            company_name=seal.company_name,
            timestamp_utc=seal.timestamp_utc,
            merkle_root="0000000000000000000000000000000000000000000000000000000000000000",
            leaf_count=seal.leaf_count,
            leaf_hashes=seal.leaf_hashes,
            frameworks=seal.frameworks,
            hmac_signature=seal.hmac_signature,
        )
        self.assertFalse(self.sealer.verify_seal(tampered_seal))

    # --- 2. NIS2 Compliance Engine Tests ---
    def test_nis2_evaluation_green_and_red(self):
        eng = NIS2ComplianceEngine()

        # All controls active -> GREEN
        telemetry_green = {
            "mfa_enforced": True,
            "tls_enforced": True,
            "automated_backups": True,
            "supply_chain_sbom_present": True,
            "incident_playbook_tested": True,
            "vulnerability_patching_active": True,
            "employee_cyber_training": True,
        }
        res_green = eng.evaluate_environment(telemetry_green)
        self.assertEqual(res_green.status, "GREEN")
        self.assertEqual(res_green.compliance_score, 100.0)
        self.assertTrue(res_green.incident_triggers_ready)

        # Poor controls -> RED
        telemetry_red = {
            "mfa_enforced": False,
            "tls_enforced": False,
            "automated_backups": False,
        }
        res_red = eng.evaluate_environment(telemetry_red)
        self.assertEqual(res_red.status, "RED")
        self.assertLess(res_red.compliance_score, 50.0)

    # --- 3. RGPD Compliance Engine Tests ---
    def test_rgpd_evaluation(self):
        eng = RGPDComplianceEngine()
        telemetry = {
            "pii_encryption_at_rest": True,
            "pii_anonymization_in_transit": True,
            "dpia_performed_for_ai": True,
            "breach_response_protocol_72h": True,
            "right_to_erasure_crypto_shredding": True,
            "records_of_processing_rat": True,
        }
        res = eng.evaluate_privacy_posture(telemetry)
        self.assertEqual(res.status, "GREEN")
        self.assertEqual(res.compliance_score, 100.0)
        self.assertEqual(res.breach_notification_sla_seconds, 259200)  # 72 hours

    # --- 4. CRA Compliance Engine Tests ---
    def test_cra_evaluation_and_sbom(self):
        eng = CRAComplianceEngine()
        telemetry = {
            "sbom_cyclonedx_generated": True,
            "vex_vulnerability_disclosed": True,
            "zero_default_credentials": True,
            "automated_security_updates": True,
            "input_sanitization_shield": True,
        }
        res = eng.audit_software_supply_chain(telemetry)
        self.assertEqual(res["status"], "GREEN")
        self.assertEqual(res["compliance_score"], 100.0)

        sbom = CRAComplianceEngine.generate_cyclonedx_sbom()
        self.assertEqual(sbom["bomFormat"], "CycloneDX")
        self.assertEqual(sbom["specVersion"], "1.5")
        self.assertGreater(len(sbom["components"]), 2)

    # --- 5. Tool Tests ---
    def test_remediation_planner_tool(self):
        findings = [
            {"rule_id": "F-01", "severity": "LOW", "passed": False, "remediation_guidance": "Fix doc"},
            {"rule_id": "F-02", "severity": "CRITICAL", "passed": False, "remediation_guidance": "Enable MFA"},
            {"rule_id": "F-03", "severity": "HIGH", "passed": False, "remediation_guidance": "Generate SBOM"},
            {"rule_id": "F-04", "severity": "CRITICAL", "passed": True, "remediation_guidance": "N/A"},
        ]
        tool = RemediationPlannerTool(findings=findings)
        res = tool.run()
        self.assertEqual(res["total_gaps_identified"], 3)
        self.assertEqual(res["critical_blockers"], 1)
        # CRITICAL should be sorted first (priority rank 1)
        self.assertEqual(res["remediation_roadmap"][0]["rule_id"], "F-02")

    # --- 6. End-to-End Council Engine Tests ---
    def test_council_engine_full_scan(self):
        telemetry = {
            "mfa_enforced": True,
            "tls_enforced": True,
            "automated_backups": True,
            "supply_chain_sbom_present": True,
            "incident_playbook_tested": True,
            "vulnerability_patching_active": True,
            "employee_cyber_training": True,
            "pii_encryption_at_rest": True,
            "pii_anonymization_in_transit": True,
            "dpia_performed_for_ai": True,
            "breach_response_protocol_72h": True,
            "right_to_erasure_crypto_shredding": True,
            "records_of_processing_rat": True,
            "sbom_cyclonedx_generated": True,
            "vex_vulnerability_disclosed": True,
            "zero_default_credentials": True,
            "automated_security_updates": True,
            "input_sanitization_shield": True,
        }
        res = self.engine.run_full_compliance_audit(
            company_name="Innovación Mediterránea S.L.",
            telemetry=telemetry,
        )
        self.assertEqual(res["global_status"], "GREEN")
        self.assertEqual(res["global_score"], 100.0)
        self.assertIn("DICTAMEN EJECUTIVO", res["markdown_dictamen"])
        self.assertIn("SELLO CRIPTOGRÁFICO", res["markdown_dictamen"])
        self.assertIn("evidence_seal", res)

    # --- 7. FastAPI Endpoints Tests ---
    def test_fastapi_server(self):
        client = TestClient(app)

        # Health
        r_health = client.get("/health")
        self.assertEqual(r_health.status_code, 200)
        self.assertEqual(r_health.json()["status"], "HEALTHY")

        # SBOM
        r_sbom = client.get("/sbom")
        self.assertEqual(r_sbom.status_code, 200)
        self.assertEqual(r_sbom.json()["bomFormat"], "CycloneDX")

        # Full Scan
        r_scan = client.post(
            "/audit/full-scan",
            headers={"X-API-KEY": API_KEY_SECRET},
            json={"company_name": "Test Enterprise"},
        )
        self.assertEqual(r_scan.status_code, 200)
        scan_data = r_scan.json()
        self.assertIn("global_score", scan_data)
        self.assertIn("evidence_seal", scan_data)

        # Seal Verification
        seal_payload = scan_data["evidence_seal"]
        r_verify = client.post(
            "/seal/verify",
            headers={"X-API-KEY": API_KEY_SECRET},
            json=seal_payload,
        )
        self.assertEqual(r_verify.status_code, 200)
        self.assertTrue(r_verify.json()["is_valid"])


if __name__ == "__main__":
    unittest.main()
