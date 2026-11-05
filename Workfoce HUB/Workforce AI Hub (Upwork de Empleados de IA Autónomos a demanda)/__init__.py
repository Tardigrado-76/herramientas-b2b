"""
WORKFORCE AI - Root Package
Autonomous on-demand AI employee workforce conforming to NIS2, RGPD, and CRA.
"""
import sys
from pathlib import Path

_pkg_root = str(Path(__file__).resolve().parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

__version__ = "1.0.0"
__app_name__ = "WORKFORCE AI"
