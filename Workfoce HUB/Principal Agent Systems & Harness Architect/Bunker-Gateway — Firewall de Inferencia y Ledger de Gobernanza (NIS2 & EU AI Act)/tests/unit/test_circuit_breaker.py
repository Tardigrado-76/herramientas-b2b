"""Unit tests for CircuitBreaker."""

from bunker_gateway.resilience.circuit_breaker import CircuitBreaker


def test_circuit_breaker_trips_on_cyclical_tool_calls():
    cb = CircuitBreaker(max_consecutive_duplicates=3)
    agent = "gtm-engineer"
    tool = "search_web"
    args = {"query": "tech companies in madrid"}

    # Three consecutive calls are allowed (threshold is 3)
    assert cb.evaluate_call(agent, tool, args).allowed is True
    assert cb.evaluate_call(agent, tool, args).allowed is True
    assert cb.evaluate_call(agent, tool, args).allowed is True

    # 4th identical call trips the breaker
    decision = cb.evaluate_call(agent, tool, args)
    assert decision.allowed is False
    assert decision.tripped is True
    assert decision.reason == "CYCLE_DETECTED_MAX_REPEATS_EXCEEDED"

    # Different tool or args is permitted
    other_call = cb.evaluate_call(agent, "search_web", {"query": "different query"})
    assert other_call.allowed is True
