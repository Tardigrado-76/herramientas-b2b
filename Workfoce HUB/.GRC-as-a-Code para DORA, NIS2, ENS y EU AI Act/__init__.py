"""COMPLIANCE SENTINEL — Autonomous GRC-as-a-Code Engine.
Continuous Multi-Agent Compliance for EU NIS2, RGPD, and Cyber Resilience Act (CRA).
"""

import sys
from pathlib import Path

# Ensure self-contained resolution regardless of parent directory names with spaces
_pkg_root = str(Path(__file__).resolve().parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

__version__ = "1.0.0"
