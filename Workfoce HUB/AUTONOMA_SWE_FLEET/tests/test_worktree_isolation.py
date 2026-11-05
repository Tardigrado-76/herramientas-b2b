import pytest
import os
import tempfile
from gastown_engine.worktree_manager import WorktreeManager

def test_worktree_isolation_no_collision():
    # Use the sample_repo as base
    base_repo = os.path.abspath("sandbox/sample_repo")
    with tempfile.TemporaryDirectory() as tmp_worktrees_dir:
        wt_mgr = WorktreeManager(base_repo_path=base_repo, worktrees_dir=tmp_worktrees_dir)

        wt1 = wt_mgr.create_worktree("bead-alpha")
        wt2 = wt_mgr.create_worktree("bead-beta")

        assert os.path.exists(wt1.worktree_path)
        assert os.path.exists(wt2.worktree_path)
        assert wt1.worktree_path != wt2.worktree_path

        # Modify same file in both worktrees
        f1 = os.path.join(wt1.worktree_path, "local_change.txt")
        f2 = os.path.join(wt2.worktree_path, "local_change.txt")

        with open(f1, "w") as f:
            f.write("Alpha worktree content")
        with open(f2, "w") as f:
            f.write("Beta worktree content")

        # Verify completely independent content without git collision
        with open(f1, "r") as f:
            assert f.read() == "Alpha worktree content"
        with open(f2, "r") as f:
            assert f.read() == "Beta worktree content"

        # Cleanup
        wt_mgr.remove_worktree("bead-alpha")
        wt_mgr.remove_worktree("bead-beta")
        assert not os.path.exists(wt1.worktree_path)
        assert not os.path.exists(wt2.worktree_path)
