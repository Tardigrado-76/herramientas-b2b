"""Root entry point for Enterprise Mission Mesh."""

from pathlib import Path
import sys

_src_dir = str(Path(__file__).resolve().parent / "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from enterprise_mission_mesh.server import run_server

if __name__ == "__main__":
    run_server()
