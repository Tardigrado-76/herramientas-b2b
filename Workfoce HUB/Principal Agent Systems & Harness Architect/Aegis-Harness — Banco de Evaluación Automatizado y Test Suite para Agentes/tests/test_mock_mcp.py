import pytest
from aegis.mock_mcp import MockMCPServer

def test_mock_mcp_server_listing():
    server = MockMCPServer()
    servers = server.list_servers()
    assert "sqlite" in servers
    assert "github" in servers
    assert "filesystem" in servers
    assert "jira" in servers

def test_mock_mcp_tool_execution_success():
    server = MockMCPServer()
    result = server.call_tool("sqlite", "query", {"sql": "SELECT 1;"})
    assert "content" in result
    assert len(result["content"]) > 0
    assert "admin" in result["content"][0]["text"]

    history = server.get_history()
    assert len(history) == 1
    assert history[0]["server"] == "sqlite"
    assert history[0]["tool"] == "query"
    assert history[0]["success"] is True

def test_mock_mcp_missing_arguments():
    server = MockMCPServer()
    # 'query' requires 'sql' parameter
    result = server.call_tool("sqlite", "query", {})
    assert "error" in result
    assert "Missing required arguments" in result["error"]

def test_mock_mcp_unknown_tool():
    server = MockMCPServer()
    result = server.call_tool("sqlite", "drop_all_tables", {})
    assert "error" in result
    assert "Unknown tool" in result["error"]
