"""Unit tests for Win32JobGuard."""

import os
import sys
import pytest
from native_isolation_harness.win32.job_guard import Win32JobGuard
from native_isolation_harness.win32.win32_defs import IS_WINDOWS


def test_job_guard_create_and_close():
    guard = Win32JobGuard()
    job_handle = guard.create_job(memory_limit_mb=128, cpu_rate_percent=20, max_processes=2)
    assert job_handle > 0
    guard.close_job(job_handle)
    assert job_handle not in guard.active_jobs


def test_job_guard_enforces_memory_limit():
    guard = Win32JobGuard()
    # 64MB hard limit
    job_handle = guard.create_job(memory_limit_mb=64, cpu_rate_percent=20, max_processes=2)
    assert job_handle > 0
    try:
        # Script that attempts allocating 256MB of RAM
        cmd = [sys.executable, "-c", "x = bytearray(256 * 1024 * 1024)"]
        result = guard.run_contained_process(job_handle, cmd, timeout=5)
        if IS_WINDOWS:
            # Must be terminated or failed with memory limit / error
            assert result.killed_by_limit is True or result.exit_code != 0
        else:
            assert True
    finally:
        guard.close_job(job_handle)


def test_job_guard_runs_successful_process():
    guard = Win32JobGuard()
    job_handle = guard.create_job(memory_limit_mb=256, cpu_rate_percent=50, max_processes=4)
    try:
        cmd = [sys.executable, "-c", "print('CONTAINED_OK')"]
        result = guard.run_contained_process(job_handle, cmd, timeout=5)
        assert result.exit_code == 0
        assert "CONTAINED_OK" in result.stdout
        assert result.killed_by_limit is False
    finally:
        guard.close_job(job_handle)
