"""OUTBOUND MACHINE — Autonomous B2B Outbound Sales & Demand Generation Engine.
Compliant with EU NIS2, RGPD (GDPR), and Cyber Resilience Act (CRA).
"""

import sys
from pathlib import Path

# Ensure self-contained resolution regardless of parent directory names with spaces
_pkg_root = str(Path(__file__).resolve().parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

__version__ = "1.0.0"
