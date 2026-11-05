"""Tests for SDP Dynamic Tool Dispatcher in Workforce AI Hub."""
from __future__ import annotations

import os
import sys

_pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from tools.sdp_workforce_dispatcher import SDPWorkforceDispatcher


def test_sdp_employee_tool_hydration() -> None:
    dispatcher = SDPWorkforceDispatcher()
    tools = dispatcher.hydrate_employee_tools("FullStack_WebDev")
    assert len(tools) >= 3
    assert all("schema" in t for t in tools)
    assert dispatcher.get_total_footprint(tools) < 500
    assert dispatcher.tenant_id == "quantigrade_workforce"
