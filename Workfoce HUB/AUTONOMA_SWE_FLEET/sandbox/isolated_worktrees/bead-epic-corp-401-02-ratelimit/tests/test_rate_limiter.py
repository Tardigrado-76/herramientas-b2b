"""Suite de pruebas unitarias para Implementar SlidingWindowRateLimiter contra ataques DoS"""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from middleware.rate_limiter import SlidingWindowRateLimiter

def test_bead_epic_corp_401_02_ratelimit():
    instance = SlidingWindowRateLimiter()
    assert instance.is_active is True
