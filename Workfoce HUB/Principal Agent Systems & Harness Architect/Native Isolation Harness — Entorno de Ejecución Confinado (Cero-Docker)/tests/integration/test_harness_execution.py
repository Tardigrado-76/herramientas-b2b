"""Integration tests for HarnessEngine."""

from pathlib import Path
import sys
import pytest
from native_isolation_harness.core.harness_engine import HarnessEngine


def test_harness_engine_executes_python_script(tmp_path):
    engine = HarnessEngine(base_scratch_dir=tmp_path)
    script_code = "import sys\nprint('NATIVE_SANDBOX_SUCCESS')\nsys.exit(0)"

    res = engine.execute_script(script_code, language="python")
    assert res.success is True
    assert res.exit_code == 0
    assert "NATIVE_SANDBOX_SUCCESS" in res.stdout
    assert res.security_violation is None
    # Check that execution latency is small
    assert res.duration_ms < 1500


def test_harness_engine_blocks_prohibited_cmd_exe(tmp_path):
    engine = HarnessEngine(base_scratch_dir=tmp_path)
    res = engine.execute_command(["cmd.exe", "/c", "echo hacked"])

    assert res.success is False
    assert res.exit_code == 126
    assert res.security_violation == "PROHIBITED_BINARY"
    assert res.mitre_id == "T1059.003"


def test_harness_engine_blocks_argument_injection(tmp_path):
    engine = HarnessEngine(base_scratch_dir=tmp_path)
    res = engine.execute_command(["python", "script.py", "&", "powershell", "-enc", "abc"])

    assert res.success is False
    assert res.exit_code == 127
    assert res.security_violation == "ARGUMENT_INJECTION"
    assert res.mitre_id == "T1059.001"


def test_harness_engine_blocks_path_traversal(tmp_path):
    engine = HarnessEngine(base_scratch_dir=tmp_path)
    res = engine.execute_command(["python", "../../external_secrets.py"])

    assert res.success is False
    assert res.security_violation == "PATH_TRAVERSAL"
    assert res.mitre_id == "T1083"
