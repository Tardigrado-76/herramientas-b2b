"""Integration tests for MCPSandboxRunner (Zero-Docker Native MCP)."""

import json
from pathlib import Path
import sys
import pytest
from native_isolation_harness.mcp.mcp_sandbox_runner import MCPSandboxRunner
from native_isolation_harness.core.exceptions import ProhibitedBinaryError


def test_mcp_sandbox_runner_blocks_docker_invocation():
    runner = MCPSandboxRunner()
    with pytest.raises(ProhibitedBinaryError, match="Docker/Podman is strictly forbidden"):
        runner.start_isolated_mcp_server(["docker", "run", "-i", "mcp-server"])


def test_mcp_sandbox_runner_native_stdio_server():
    runner = MCPSandboxRunner()
    # Inline Python script acting as a minimal native JSON-RPC 2.0 stdio server
    server_script = (
        "import sys, json\n"
        "for line in sys.stdin:\n"
        "    if not line.strip(): continue\n"
        "    req = json.loads(line.strip())\n"
        "    resp = {'jsonrpc': '2.0', 'id': req.get('id'), 'result': {'status': 'OK_NATIVE_CONTAINED'}}\n"
        "    sys.stdout.write(json.dumps(resp) + '\\n')\n"
        "    sys.stdout.flush()\n"
    )

    cmd = [sys.executable, "-c", server_script]

    with runner.start_isolated_mcp_server(cmd, session_id="test_mcp_session") as mcp_proc:
        assert mcp_proc.is_active is True
        req = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
        resp = mcp_proc.send_request(req, timeout=3.0)

        assert resp["jsonrpc"] == "2.0"
        assert resp["id"] == 1
        assert resp["result"]["status"] == "OK_NATIVE_CONTAINED"

    # Post-exit: scratch jail directory must be cleaned
    assert not mcp_proc.jail_path.exists()
