"""Root entry point for Native Isolation Harness."""

from pathlib import Path
import sys

_src_dir = str(Path(__file__).resolve().parent / "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from native_isolation_harness.cli.harness_cli import main

if __name__ == "__main__":
    main()
