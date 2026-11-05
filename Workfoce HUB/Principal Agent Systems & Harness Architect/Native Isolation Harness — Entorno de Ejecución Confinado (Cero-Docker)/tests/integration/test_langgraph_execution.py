"""Integration tests for LangGraph Agent script execution via HarnessEngine."""

from native_isolation_harness.core.harness_engine import HarnessEngine


def test_langgraph_agent_executes_isolated_tool(tmp_path):
    engine = HarnessEngine(base_scratch_dir=tmp_path)

    # Simulated LangGraph Python tool code
    agent_task_script = (
        "import json\n"
        "data = {'summary': 'NIS2 Audit Completed', 'compliant_controls': 24}\n"
        "print(json.dumps(data))\n"
    )

    result = engine.execute_script(
        script_code=agent_task_script,
        language="python",
        session_id="langgraph_trace_492",
        agent_id="langgraph-assistant",
    )

    assert result.success is True
    assert result.exit_code == 0
    assert "NIS2 Audit Completed" in result.stdout
    assert result.security_violation is None
