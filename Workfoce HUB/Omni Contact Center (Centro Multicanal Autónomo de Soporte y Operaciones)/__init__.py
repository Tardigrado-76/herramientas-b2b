"""
OMNI CONTACT - Root Package
Contact Center IA Multimodal conforming to NIS2, RGPD, and CRA.
"""
import sys
from pathlib import Path

_pkg_root = str(Path(__file__).resolve().parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

__version__ = "1.0.0"
__app_name__ = "OMNI CONTACT"
