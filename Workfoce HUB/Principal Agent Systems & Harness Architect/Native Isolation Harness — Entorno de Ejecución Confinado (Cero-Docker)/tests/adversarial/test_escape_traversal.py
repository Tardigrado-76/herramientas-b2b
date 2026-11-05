"""Adversarial test: Filesystem escape and path traversal attempts."""

from native_isolation_harness.core.harness_engine import HarnessEngine


def test_adversarial_escape_traversal_attempts(tmp_path):
    engine = HarnessEngine(base_scratch_dir=tmp_path)

    adversarial_attempts = [
        ["python", "../../Windows/System32/drivers/etc/hosts"],
        ["python", "..\\..\\..\\Windows\\win.ini"],
        ["python", "subdir/../../secrets.env"],
        ["python", "/etc/shadow"],
        ["python", "valid.py:hidden_stream.exe"],
    ]

    for attack in adversarial_attempts:
        res = engine.execute_command(attack, session_id="adv_escape_attempt")
        assert res.success is False
        assert res.security_violation in ("PATH_TRAVERSAL", "PROHIBITED_BINARY", "ARGUMENT_INJECTION")
        assert res.mitre_id in ("T1083", "T1059.003", "T1059.001")
