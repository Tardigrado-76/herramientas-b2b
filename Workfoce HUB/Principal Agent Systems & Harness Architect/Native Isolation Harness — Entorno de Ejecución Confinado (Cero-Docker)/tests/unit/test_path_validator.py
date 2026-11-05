"""Unit tests for PathValidator."""

import os
from pathlib import Path
import pytest
from native_isolation_harness.jail.path_validator import PathValidator
from native_isolation_harness.core.exceptions import PathTraversalError


def test_path_validator_allows_valid_contained_subpaths(tmp_path):
    root = tmp_path / "sandbox"
    root.mkdir()
    validator = PathValidator(root_jail=root)

    valid_file = root / "script.py"
    valid_file.write_text("print('test')")

    res = validator.assert_contained(valid_file)
    assert res == valid_file.resolve()

    res_rel = validator.assert_contained("script.py")
    assert res_rel == valid_file.resolve()

    nested = root / "subdir" / "data.json"
    nested.parent.mkdir()
    nested.write_text("{}")
    assert validator.assert_contained(nested) == nested.resolve()


def test_path_validator_blocks_parent_directory_traversal(tmp_path):
    root = tmp_path / "sandbox"
    root.mkdir()
    secret = tmp_path / "secrets.env"
    secret.write_text("API_KEY=ABC")

    validator = PathValidator(root_jail=root)

    # Various traversal patterns
    traversal_patterns = [
        "../secrets.env",
        "..\\secrets.env",
        "subdir/../../secrets.env",
        "a/b/../../../secrets.env",
        root / ".." / "secrets.env",
    ]

    for pattern in traversal_patterns:
        with pytest.raises(PathTraversalError):
            validator.assert_contained(pattern)


def test_path_validator_blocks_absolute_system_paths(tmp_path):
    root = tmp_path / "sandbox"
    root.mkdir()
    validator = PathValidator(root_jail=root)

    system_paths = [
        "C:\\Windows\\System32\\calc.exe",
        "C:\\Windows\\win.ini",
        "C:\\Users",
        "/etc/passwd",
        "/root/.ssh/id_rsa",
    ]

    for p in system_paths:
        with pytest.raises(PathTraversalError):
            validator.assert_contained(p)


def test_path_validator_blocks_alternate_data_streams(tmp_path):
    root = tmp_path / "sandbox"
    root.mkdir()
    validator = PathValidator(root_jail=root)

    ads_patterns = [
        "file.txt:hidden.exe",
        "script.py:$DATA",
        "test.py:secret_stream",
    ]

    for ads in ads_patterns:
        with pytest.raises(PathTraversalError, match="Alternate Data Stream"):
            validator.assert_contained(ads)


def test_path_validator_blocks_null_byte_injection(tmp_path):
    root = tmp_path / "sandbox"
    root.mkdir()
    validator = PathValidator(root_jail=root)

    with pytest.raises(PathTraversalError, match="Null byte"):
        validator.assert_contained("valid.py\x00../../secret.txt")


def test_path_validator_blocks_escaping_symlink(tmp_path):
    root = tmp_path / "sandbox"
    root.mkdir()
    external_secret = tmp_path / "external_token.txt"
    external_secret.write_text("SUPER_SECRET")

    symlink_path = root / "leaked_link.txt"
    try:
        os.symlink(external_secret, symlink_path)
        validator = PathValidator(root_jail=root)
        with pytest.raises(PathTraversalError):
            validator.assert_contained(symlink_path)
    except OSError:
        # On Windows, os.symlink might require SeCreateSymbolicLinkPrivilege unless Dev Mode is on
        pass
