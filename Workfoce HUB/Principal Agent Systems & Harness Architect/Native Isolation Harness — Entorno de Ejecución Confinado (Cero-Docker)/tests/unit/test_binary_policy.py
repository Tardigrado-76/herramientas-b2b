"""Unit tests for BinaryPolicyEngine and ArgSanitizer."""

import sys
import pytest
from native_isolation_harness.policy.binary_policy import BinaryPolicyEngine
from native_isolation_harness.core.exceptions import ProhibitedBinaryError, ArgumentInjectionError


def test_binary_policy_allows_python_and_valid_args():
    engine = BinaryPolicyEngine()
    cmd = [sys.executable, "-c", "print('HELLO')"]
    validated = engine.validate_command(cmd)

    assert validated.executable_name == "python"
    assert validated.args == ["-c", "print('HELLO')"]


def test_binary_policy_blocks_prohibited_binaries():
    engine = BinaryPolicyEngine()
    prohibited_cmds = [
        ["cmd.exe", "/c", "dir"],
        ["cmd", "/c", "calc.exe"],
        ["powershell.exe", "-Command", "Get-Process"],
        ["pwsh", "-c", "ls"],
        ["certutil.exe", "-urlcache", "-split", "-f"],
        ["whoami.exe"],
        ["whoami"],
        ["net.exe", "user"],
        ["vssadmin.exe", "delete", "shadows"],
    ]

    for p_cmd in prohibited_cmds:
        with pytest.raises(ProhibitedBinaryError):
            engine.validate_command(p_cmd)


def test_binary_policy_blocks_shell_chaining_and_injection():
    engine = BinaryPolicyEngine()
    malicious_cmds = [
        ["python", "script.py", "&", "powershell", "-enc", "abc"],
        ["python", "script.py;whoami"],
        ["python", "script.py", "|", "net", "user"],
        ["python", "script.py", ">", "out.txt"],
        ["python", "script.py", "`calc`"],
        ["python", "script.py", "$(whoami)"],
        "python script.py -enc 123",
        "python script.py downloadstring",
    ]

    for m_cmd in malicious_cmds:
        with pytest.raises(ArgumentInjectionError):
            engine.validate_command(m_cmd)


def test_binary_policy_git_subcommand_restriction():
    engine = BinaryPolicyEngine()
    # Allowed git subcommand
    val = engine.validate_command(["git", "status"])
    assert val.executable_name == "git"

    # Prohibited git subcommands
    with pytest.raises(ProhibitedBinaryError):
        engine.validate_command(["git", "push", "origin", "main"])

    with pytest.raises(ProhibitedBinaryError):
        engine.validate_command(["git", "commit", "-m", "msg"])
