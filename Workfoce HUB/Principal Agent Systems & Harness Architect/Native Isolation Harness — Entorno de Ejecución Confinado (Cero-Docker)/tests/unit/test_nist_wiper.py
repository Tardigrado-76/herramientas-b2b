"""Unit tests for NISTWiper."""

from pathlib import Path
from native_isolation_harness.jail.nist_wiper import NISTWiper
from native_isolation_harness.jail.fs_jailer import FSJailer


def test_nist_wiper_overwrites_and_deletes_file(tmp_path):
    target_file = tmp_path / "financial_data.csv"
    initial_content = "SALARY,BONUS,CREDIT_CARD\n100000,20000,4532123456789012"
    target_file.write_text(initial_content)

    assert target_file.exists()
    wiper = NISTWiper(default_passes=2)
    res = wiper.wipe_file(target_file, passes=2)

    assert res is True
    assert not target_file.exists()


def test_nist_wiper_wipes_entire_directory(tmp_path):
    jail_dir = tmp_path / "ephemeral_session_01"
    jail_dir.mkdir()
    f1 = jail_dir / "out1.txt"
    f1.write_text("SOME TEMP OUTPUT")
    sub = jail_dir / "nested"
    sub.mkdir()
    f2 = sub / "out2.json"
    f2.write_text('{"key": "value"}')

    wiper = NISTWiper(default_passes=1)
    res = wiper.wipe_directory(jail_dir)

    assert res is True
    assert not jail_dir.exists()


def test_fs_jailer_context_manager(tmp_path):
    jailer = FSJailer(base_scratch_dir=tmp_path)
    created_path = None

    with jailer.ephemeral_jail("test_session_abc") as jail:
        created_path = jail
        assert jail.exists()
        assert (jail / "notes.txt").write_text("Hello agent") > 0
        assert (jail / "notes.txt").exists()

    # Once context manager exits, directory must be wiped
    assert not created_path.exists()
