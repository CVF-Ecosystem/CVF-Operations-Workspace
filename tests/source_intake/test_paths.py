from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "source_intake" / "paths.py"
SPEC = importlib.util.spec_from_file_location("si_paths", MODULE_PATH)
assert SPEC and SPEC.loader
paths = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(paths)


class ToPosixRelativeTests(unittest.TestCase):
    def test_relative_path_uses_forward_slashes(self) -> None:
        root = REPO_ROOT
        target = REPO_ROOT / "docs" / "catalog" / "README.md"
        result = paths.to_posix_relative(root, target)
        self.assertEqual(result, "docs/catalog/README.md")
        self.assertNotIn("\\", result)

    def test_path_escape_is_rejected(self) -> None:
        root = REPO_ROOT / "docs"
        escaping_target = REPO_ROOT.parent / "outside-the-repo.txt"
        with self.assertRaises(paths.PathEscapeError):
            paths.to_posix_relative(root, escaping_target)

    def test_parent_traversal_escape_is_rejected(self) -> None:
        root = REPO_ROOT / "docs" / "catalog"
        escaping_target = root / ".." / ".." / ".." / "etc" / "passwd"
        with self.assertRaises(paths.PathEscapeError):
            paths.to_posix_relative(root, escaping_target)


class ContainsBackslashTests(unittest.TestCase):
    def test_detects_windows_separator(self) -> None:
        self.assertTrue(paths.contains_backslash("docs\\decisions\\HIST.md"))

    def test_posix_path_is_clean(self) -> None:
        self.assertFalse(paths.contains_backslash("docs/decisions/HIST.md"))


class SelfScanGuardTests(unittest.TestCase):
    def test_refuses_exact_tool_root(self) -> None:
        with self.assertRaises(paths.SelfScanError):
            paths.assert_not_self_scan(REPO_ROOT, REPO_ROOT)

    def test_refuses_subdirectory_of_tool_root(self) -> None:
        with self.assertRaises(paths.SelfScanError):
            paths.assert_not_self_scan(REPO_ROOT / "scripts", REPO_ROOT)

    def test_allows_unrelated_directory(self) -> None:
        # A sibling directory (not inside the tool's own repo) must pass.
        paths.assert_not_self_scan(REPO_ROOT.parent, REPO_ROOT)


class ForbiddenTargetGuardTests(unittest.TestCase):
    def test_refuses_apps_target(self) -> None:
        with self.assertRaises(paths.PathEscapeError):
            paths.assert_not_forbidden_target(REPO_ROOT / "apps" / "whatever", REPO_ROOT)

    def test_refuses_packages_target(self) -> None:
        with self.assertRaises(paths.PathEscapeError):
            paths.assert_not_forbidden_target(REPO_ROOT / "packages" / "whatever", REPO_ROOT)

    def test_refuses_database_target(self) -> None:
        with self.assertRaises(paths.PathEscapeError):
            paths.assert_not_forbidden_target(REPO_ROOT / "database", REPO_ROOT)

    def test_allows_provenance_target(self) -> None:
        paths.assert_not_forbidden_target(REPO_ROOT / "provenance" / "shift-operations", REPO_ROOT)


if __name__ == "__main__":
    unittest.main()
