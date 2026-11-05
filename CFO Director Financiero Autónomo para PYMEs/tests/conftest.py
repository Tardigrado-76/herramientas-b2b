import sys
import types
from pathlib import Path

_pkg_root = Path(__file__).resolve().parent.parent
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

if "autonomo_cfo" not in sys.modules:
    _mod = types.ModuleType("autonomo_cfo")
    _mod.__path__ = [str(_pkg_root)]
    sys.modules["autonomo_cfo"] = _mod
