"""Tests for SDP Omnichannel CRM & Billing Connector in Omni Contact Center."""
from __future__ import annotations

import os
import sys

_pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from tools.sdp_omni_connector import SDPOmniConnector


def test_sdp_omni_customer_query() -> None:
    connector = SDPOmniConnector()
    res = connector.query_customer_context("CUST-001")
    assert res["status"] == "SUCCESS"
    assert "crm_tier0" in res
    assert res["tokens_consumed"] < 150
    assert res["customer_id"] == "CUST-001"
    assert res["provenance_signature"] is not None
