"""
Agent Under Test (AUT) Adapters for Aegis-Harness.
Connects Aegis-Harness directly with:
- LangGraph MCP Agent (assistant_graph.py)
- AI Employees (8 business agents)
"""

from aegis.agents.langgraph_adapter import LangGraphAgentAdapter
from aegis.agents.ai_employees_adapter import AIEmployeesAdapter

__all__ = ["LangGraphAgentAdapter", "AIEmployeesAdapter"]
