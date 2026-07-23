from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "source_intake" / "capture.py"
SPEC = importlib.util.spec_from_file_location("si_capture", MODULE_PATH)
assert SPEC and SPEC.loader
capture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capture)

MODULE_REGISTRY_PATH = REPO_ROOT / "docs" / "catalog" / "MODULE_REGISTRY.json"


def _run(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _build_fixture_source_repo(root: Path) -> str:
    """A tiny, hermetic Shift-shaped repo: enough surface to exercise every
    F0 dataset without depending on the real (much larger) source repo."""
    _run(["init", "-q"], root)
    _run(["config", "user.email", "f0-test@example.com"], root)
    _run(["config", "user.name", "F0 Test"], root)

    router_dir = root / "apps" / "fixture-api" / "src" / "widgets"
    router_dir.mkdir(parents=True)
    (router_dir / "router.py").write_text(
        'from fastapi import APIRouter\n\nrouter = APIRouter(prefix="/widgets")\n\n\n'
        '@router.get("/")\nasync def list_widgets():\n    return []\n',
        encoding="utf-8",
    )

    migrations_dir = root / "database" / "migrations"
    migrations_dir.mkdir(parents=True)
    (migrations_dir / "001_foundation.sql").write_text("CREATE TABLE widgets (id int);\n", encoding="utf-8")

    catalog_dir = root / "docs" / "catalog"
    catalog_dir.mkdir(parents=True)
    (catalog_dir / "MODULE_REGISTRY.json").write_text(
        json.dumps({"schemaVersion": "1.0", "modules": []}, indent=2) + "\n", encoding="utf-8"
    )

    (root / ".env").write_text("SECRET=do-not-capture\n", encoding="utf-8")
    (root / "README.md").write_text("Fixture source repository for F0 tests.\n", encoding="utf-8")

    _run(["add", "-A"], root)
    _run(["commit", "-q", "-m", "fixture baseline"], root)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True
    ).stdout.strip()


class RunCaptureIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.source_repo = self.root / "source-repo"
        self.source_repo.mkdir()
        self.commit = _build_fixture_source_repo(self.source_repo)
        self.output_dir = self.root / "provenance-out"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _run(self, **overrides):
        kwargs = dict(
            source_repo_primary=self.source_repo,
            source_commit=self.commit,
            output_dir=self.output_dir,
            tmp_worktree_parent=self.root,
            skip_tests=True,
            keep_worktree=False,
        )
        kwargs.update(overrides)
        return capture.run_capture(**kwargs)

    def test_capture_produces_every_dataset(self) -> None:
        datasets = self._run()
        for key in (
            "file_inventory", "exclusions", "routes", "migrations",
            "dependency_graph", "module_registry_snapshot", "test_outcomes",
            "import_ledger", "capture_receipt",
        ):
            self.assertIn(key, datasets)

        source_paths = {r["source_path"] for r in datasets["file_inventory"]}
        self.assertIn("apps/fixture-api/src/widgets/router.py", source_paths)
        self.assertNotIn(".env", source_paths)
        excluded_paths = {r["source_path"] for r in datasets["exclusions"]}
        self.assertIn(".env", excluded_paths)

        self.assertEqual(len(datasets["routes"]), 1)
        self.assertEqual(datasets["routes"][0]["path"], "/widgets/")

        self.assertEqual(len(datasets["migrations"]), 1)
        self.assertTrue(datasets["capture_receipt"]["source_status_unchanged"])

    def test_no_secret_value_appears_in_any_written_output(self) -> None:
        datasets = self._run()
        capture.write_outputs(self.output_dir, datasets)
        for json_file in self.output_dir.glob("*.json"):
            text = json_file.read_text(encoding="utf-8")
            self.assertNotIn("do-not-capture", text)

    def test_source_repository_worktree_list_is_clean_after_capture(self) -> None:
        self._run()
        result = subprocess.run(
            ["git", "worktree", "list"], cwd=self.source_repo, capture_output=True, text=True, check=True
        )
        # Only the primary checkout should remain; the temporary detached
        # worktree must have been removed.
        self.assertEqual(len(result.stdout.strip().splitlines()), 1)

    def test_two_runs_at_the_same_pin_are_byte_identical_except_timing(self) -> None:
        datasets_a = self._run()
        capture.write_outputs(self.output_dir, datasets_a)
        first_pass = {p.name: p.read_bytes() for p in self.output_dir.glob("*.json")}

        second_output_dir = self.root / "provenance-out-2"
        datasets_b = self._run(output_dir=second_output_dir)
        capture.write_outputs(second_output_dir, datasets_b)
        second_pass = {p.name: p.read_bytes() for p in second_output_dir.glob("*.json")}

        self.assertEqual(set(first_pass), set(second_pass))
        for name in first_pass:
            if name == "capture_timing.json":
                continue
            self.assertEqual(first_pass[name], second_pass[name], f"{name} is not deterministic across runs")

    def test_every_written_json_file_parses(self) -> None:
        datasets = self._run()
        capture.write_outputs(self.output_dir, datasets)
        for json_file in self.output_dir.glob("*.json"):
            json.loads(json_file.read_text(encoding="utf-8"))  # must not raise

    def test_target_module_registry_is_untouched_by_a_full_capture(self) -> None:
        before = MODULE_REGISTRY_PATH.read_bytes()
        self._run()
        after = MODULE_REGISTRY_PATH.read_bytes()
        self.assertEqual(before, after, "F0 capture must never mutate this repository's Module Registry")

    def test_forbidden_target_path_is_rejected_before_any_worktree_is_created(self) -> None:
        forbidden_output = capture.TOOL_REPO_ROOT / "apps" / "should-not-exist"
        with self.assertRaises(capture.si_paths.PathEscapeError):
            self._run(output_dir=forbidden_output)
        self.assertFalse(forbidden_output.exists())
        result = subprocess.run(
            ["git", "worktree", "list"], cwd=self.source_repo, capture_output=True, text=True, check=True
        )
        self.assertEqual(len(result.stdout.strip().splitlines()), 1)

    def test_self_scan_of_tool_repository_is_rejected(self) -> None:
        with self.assertRaises(capture.si_paths.SelfScanError):
            self._run(source_repo_primary=capture.TOOL_REPO_ROOT)

    def test_abbreviated_pin_is_rejected(self) -> None:
        with self.assertRaises(capture.si_git_pin.SourcePinError):
            self._run(source_commit=self.commit[:7])

    def test_dirty_source_repo_primary_still_captures_but_records_status(self) -> None:
        # A dirty PRIMARY checkout (as opposed to a dirty temporary worktree)
        # is allowed to have local edits — F0 never reads its working tree,
        # only the pinned commit via a detached worktree — but the dirty
        # state must be faithfully recorded before and after, unchanged.
        (self.source_repo / "unrelated_local_edit.txt").write_text("wip\n", encoding="utf-8")
        datasets = self._run()
        self.assertIn("unrelated_local_edit.txt", datasets["capture_receipt"]["source_status_before"])
        self.assertEqual(
            datasets["capture_receipt"]["source_status_before"],
            datasets["capture_receipt"]["source_status_after"],
        )


if __name__ == "__main__":
    unittest.main()
