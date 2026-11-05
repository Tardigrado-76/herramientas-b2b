"""Adversarial test: Complex command injection and shell smuggling."""

from native_isolation_harness.core.harness_engine import HarnessEngine


def test_adversarial_command_injection_attempts(tmp_path):
    engine = HarnessEngine(base_scratch_dir=tmp_path)

    injection_attacks = [
        ["python", "script.py", "&", "powershell", "-enc", "SQBFAFgA"],
        ["python", "script.py", "|", "whoami"],
        ["python", "script.py;calc.exe"],
        ["python", "script.py", "`certutil -urlcache`"],
        ["python", "script.py", "$(cat /etc/passwd)"],
        ["python", "script.py", ">", "overwrite.dll"],
        ["python", "script.py", "<", "input.bin"],
        ["cmd.exe", "/c", "dir"],
        ["powershell.exe", "-Command", "Invoke-WebRequest"],
    ]

    for attack in injection_attacks:
        res = engine.execute_command(attack, session_id="adv_injection_attempt")
        assert res.success is False
        assert res.security_violation in ("ARGUMENT_INJECTION", "PROHIBITED_BINARY", "PATH_TRAVERSAL")
        assert res.mitre_id in ("T1059.001", "T1059.003", "T1083")
