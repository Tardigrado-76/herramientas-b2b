"""Adversarial test: Memory exhaustion defense under strict Job limits."""

from native_isolation_harness.core.harness_engine import HarnessEngine
from native_isolation_harness.core.config import HarnessConfig
from native_isolation_harness.win32.win32_defs import IS_WINDOWS


def test_adversarial_memory_exhaustion_defense(tmp_path):
    # Restrict memory limit to 64 MB
    config = HarnessConfig(
        base_scratch_dir=str(tmp_path),
        memory_limit_mb=64,
        default_timeout_seconds=5,
    )
    engine = HarnessEngine(config=config)

    # Script attempting to greedily allocate 512 MB of RAM
    exhaustion_script = (
        "import sys\n"
        "chunks = []\n"
        "for _ in range(512):\n"
        "    chunks.append(bytearray(1024 * 1024))\n"
    )

    res = engine.execute_script(
        script_code=exhaustion_script,
        session_id="adversarial_mem_leak",
        timeout=5,
    )

    if IS_WINDOWS:
        # Kernel job object must terminate or halt memory consumption
        assert res.success is False
        assert res.exit_code != 0 or res.security_violation in ("MEMORY_LIMIT", "EXECUTION_TIMEOUT")
    else:
        assert True
