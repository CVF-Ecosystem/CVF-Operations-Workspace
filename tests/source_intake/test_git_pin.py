from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "source_intake" / "git_pin.py"
SPEC = importlib.util.spec_from_file_location("si_git_pin", MODULE_PATH)
assert SPEC and SPEC.loader
git_pin = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(git_pin)


def _run(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _make_fixture_repo(root: Path) -> str:
    _run(["init", "-q"], root)
    _run(["config", "user.email", "f0-test@example.com"], root)
    _run(["config", "user.name", "F0 Test"], root)
    (root / "README.md").write_text("fixture\n", encoding="utf-8")
    _run(["add", "README.md"], root)
    _run(["commit", "-q", "-m", "initial"], root)
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True)
    return result.stdout.strip()


class IsFullShaTests(unittest.TestCase):
    def test_accepts_full_forty_char_sha(self) -> None:
        self.assertTrue(git_pin.is_full_sha("a" * 40))

    def test_rejects_abbreviated_sha(self) -> None:
        self.assertFalse(git_pin.is_full_sha("f98f29e"))

    def test_rejects_empty_string(self) -> None:
        self.assertFalse(git_pin.is_full_sha(""))

    def test_rejects_none(self) -> None:
        self.assertFalse(git_pin.is_full_sha(None))  # type: ignore[arg-type]

    def test_rejects_non_hex_characters(self) -> None:
        self.assertFalse(git_pin.is_full_sha("g" * 40))


class VerifyPinReachableTests(unittest.TestCase):
    def test_missing_pin_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _make_fixture_repo(repo)
            with self.assertRaises(git_pin.SourcePinError):
                git_pin.verify_pin_reachable(repo, "")

    def test_abbreviated_pin_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            full_sha = _make_fixture_repo(repo)
            with self.assertRaises(git_pin.SourcePinError):
                git_pin.verify_pin_reachable(repo, full_sha[:7])

    def test_unreachable_pin_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _make_fixture_repo(repo)
            fake_sha = "f" * 40
            with self.assertRaises(git_pin.SourcePinError):
                git_pin.verify_pin_reachable(repo, fake_sha)

    def test_valid_full_pin_resolves(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            full_sha = _make_fixture_repo(repo)
            resolved = git_pin.verify_pin_reachable(repo, full_sha)
            self.assertEqual(resolved, full_sha)


class DirtyWorktreeTests(unittest.TestCase):
    def test_clean_worktree_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _make_fixture_repo(repo)
            git_pin.assert_worktree_clean(repo)  # must not raise

    def test_dirty_worktree_with_untracked_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _make_fixture_repo(repo)
            (repo / "untracked.txt").write_text("surprise\n", encoding="utf-8")
            with self.assertRaises(git_pin.DirtyWorktreeError):
                git_pin.assert_worktree_clean(repo)

    def test_dirty_worktree_with_modified_tracked_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _make_fixture_repo(repo)
            (repo / "README.md").write_text("modified\n", encoding="utf-8")
            with self.assertRaises(git_pin.DirtyWorktreeError):
                git_pin.assert_worktree_clean(repo)


class WorktreeLifecycleTests(unittest.TestCase):
    def test_create_and_remove_detached_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            full_sha = _make_fixture_repo(repo)
            worktree = root / "worktree"
            git_pin.create_detached_worktree(repo, full_sha, worktree)
            try:
                self.assertTrue(worktree.is_dir())
                head = subprocess.run(
                    ["git", "rev-parse", "HEAD"], cwd=worktree, capture_output=True, text=True, check=True
                ).stdout.strip()
                self.assertEqual(head, full_sha)
                git_pin.assert_worktree_clean(worktree)
            finally:
                git_pin.remove_worktree(repo, worktree)
            self.assertFalse(worktree.exists())

    def test_refuses_to_reuse_existing_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            full_sha = _make_fixture_repo(repo)
            worktree = root / "occupied"
            worktree.mkdir()
            with self.assertRaises(git_pin.DirtyWorktreeError):
                git_pin.create_detached_worktree(repo, full_sha, worktree)


if __name__ == "__main__":
    unittest.main()
