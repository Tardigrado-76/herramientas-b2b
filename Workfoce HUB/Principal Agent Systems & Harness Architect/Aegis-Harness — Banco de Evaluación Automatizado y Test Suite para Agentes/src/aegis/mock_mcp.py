"""
Mock MCP Server for deterministic agent evaluation.
Emulates MCP servers without external network calls or Docker dependencies.
"""

from typing import Dict, List, Any, Optional
import time

class MockMCPServer:
    """
    Simulates real MCP tools (sqlite, github, filesystem, jira, analytics)
    and captures tool call interactions.
    """
    
    SERVER_REGISTRY: Dict[str, Dict[str, Dict[str, Any]]] = {
        "sqlite": {
            "query": {
                "description": "Execute a read-only SQL query on the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql": {"type": "string"}
                    },
                    "required": ["sql"]
                },
                "mock_response": [{"id": 1, "username": "admin", "role": "sysadmin"}]
            },
            "describe_table": {
                "description": "Describe schema of a table",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string"}
                    },
                    "required": ["table_name"]
                },
                "mock_response": {"columns": ["id INTEGER PRIMARY KEY", "username TEXT", "created_at TIMESTAMP"]}
            }
        },
        "github": {
            "search_repositories": {
                "description": "Search for repositories on GitHub",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    },
                    "required": ["query"]
                },
                "mock_response": [{"name": "enterprise-agent", "stars": 142, "url": "https://github.com/org/enterprise-agent"}]
            },
            "get_issue": {
                "description": "Get issue details by repo and issue number",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "issue_number": {"type": "integer"}
                    },
                    "required": ["owner", "repo", "issue_number"]
                },
                "mock_response": {"title": "Fix memory leak in agent session", "state": "open"}
            }
        },
        "filesystem": {
            "read_file": {
                "description": "Read content of a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"}
                    },
                    "required": ["path"]
                },
                "mock_response": "CONTENT: Enterprise configuration settings verified."
            },
            "list_directory": {
                "description": "List files in directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"}
                    },
                    "required": ["path"]
                },
                "mock_response": ["config.yaml", "main.py", "audit.log"]
            }
        },
        "jira": {
            "search_issues": {
                "description": "Search Jira issues with JQL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "jql": {"type": "string"}
                    },
                    "required": ["jql"]
                },
                "mock_response": [{"key": "SEC-101", "summary": "Audit NIS2 compliance", "status": "In Progress"}]
            }
        }
    }

    def __init__(self):
        self.call_history: List[Dict[str, Any]] = []

    def list_servers(self) -> List[str]:
        return list(self.SERVER_REGISTRY.keys())

    def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        server = self.SERVER_REGISTRY.get(server_name, {})
        return [{"name": name, **meta} for name, meta in server.items()]

    def has_tool(self, server_name: str, tool_name: str) -> bool:
        return server_name in self.SERVER_REGISTRY and tool_name in self.SERVER_REGISTRY[server_name]

    def call_tool(self, server_name: str, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        arguments = arguments or {}
        call_record = {
            "timestamp": time.time(),
            "server": server_name,
            "tool": tool_name,
            "arguments": arguments,
            "success": False,
            "result": None,
            "error": None
        }

        if server_name not in self.SERVER_REGISTRY:
            call_record["error"] = f"Unknown server: {server_name}"
            self.call_history.append(call_record)
            return {"error": call_record["error"]}

        server_tools = self.SERVER_REGISTRY[server_name]
        if tool_name not in server_tools:
            call_record["error"] = f"Unknown tool '{tool_name}' on server '{server_name}'"
            self.call_history.append(call_record)
            return {"error": call_record["error"]}

        tool_spec = server_tools[tool_name]
        required_params = tool_spec.get("parameters", {}).get("required", [])
        missing = [p for p in required_params if p not in arguments]
        if missing:
            call_record["error"] = f"Missing required arguments: {missing}"
            self.call_history.append(call_record)
            return {"error": call_record["error"]}

        # Success
        call_record["success"] = True
        call_record["result"] = tool_spec.get("mock_response", {"status": "ok"})
        self.call_history.append(call_record)
        return {"content": [{"type": "text", "text": str(call_record["result"])}]}

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self.call_history)

    def clear_history(self) -> None:
        self.call_history.clear()
