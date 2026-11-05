"""Root entry point for Bunker-Gateway."""

from pathlib import Path
import sys

_src_dir = str(Path(__file__).resolve().parent / "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from bunker_gateway.cli.runner import main

if __name__ == "__main__":
    main()
