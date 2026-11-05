import sys
from pathlib import Path

# Add src to sys.path so aegis package can be imported directly in tests
src_path = Path(__file__).resolve().parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
