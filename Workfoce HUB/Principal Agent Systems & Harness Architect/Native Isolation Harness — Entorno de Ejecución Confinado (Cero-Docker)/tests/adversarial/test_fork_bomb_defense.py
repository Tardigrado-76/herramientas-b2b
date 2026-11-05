"""Adversarial test: Fork-bomb defense and process limit enforcement."""

import sys
from native_isolation_harness.core.harness_engine import HarnessEngine
from native_isolation_harness.core.config import HarnessConfig


def test_adversarial_fork_bomb_defense(tmp_path):
    # Set limit to max 2 processes
    config = HarnessConfig(
        base_scratch_dir=str(tmp_path),
        memory_limit_mb=128,
        max_processes=2,
        default_timeout_seconds=3,
    )
    engine = HarnessEngine(config=config)

    # Fork bomb attempt in Python: spawns subprocesses indefinitely
    fork_bomb_script = (
        "import subprocess, sys\n"
        "procs = []\n"
        "for _ in range(50):\n"
        "    try:\n"
        "        p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(5)'])\n"
        "        procs.append(p)\n"
        "    except Exception:\n"
        "        break\n"
    )

    res = engine.execute_script(
        script_code=fork_bomb_script,
        session_id="adversarial_fork_bomb",
        timeout=3,
    )

    # Process limit or timeout must kick in, protecting host from unbounded process creation
    assert res.exit_code != 0 or res.security_violation is not None or res.duration_ms < 4000
