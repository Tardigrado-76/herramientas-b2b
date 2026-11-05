"""Unit tests for ToolGuard ABAC policy enforcer."""

from bunker_gateway.firewall.tool_guard import ToolGuard


def test_tool_guard_allows_permitted_tool():
    guard = ToolGuard()
    eval_res = guard.evaluate_tool_call(
        agent_id="chief-of-staff",
        tool_name="freeze_service",
        parameters={"service": "auth"},
    )
    assert eval_res.allowed is True


def test_tool_guard_blocks_unauthorized_tool():
    guard = ToolGuard()
    # gtm-engineer is not authorized to call kronos_adjust_entry
    eval_res = guard.evaluate_tool_call(
        agent_id="gtm-engineer",
        tool_name="kronos_adjust_entry",
        parameters={"delta": 30},
    )
    assert eval_res.allowed is False
    assert "TOOL_NOT_PERMITTED_FOR_AGENT" in eval_res.reason or "DISALLOWED_TOOL_BY_POLICY" in eval_res.reason


def test_tool_guard_blocks_destructive_params():
    guard = ToolGuard()
    # Even if tool name looks harmless, destructive SQL inside params is blocked
    eval_res = guard.evaluate_tool_call(
        agent_id="chief-of-staff",
        tool_name="read_kpi_dashboard",
        parameters={"query": "DROP TABLE users;"},
    )
    assert eval_res.allowed is False
    assert "DESTRUCTIVE_OPERATION_BLOCKED" in eval_res.reason
