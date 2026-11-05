"""Pytest configuration and common fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def sandbox_scratch(tmp_path):
    scratch_dir = tmp_path / "harness_scratch"
    scratch_dir.mkdir(parents=True, exist_ok=True)
    return scratch_dir
