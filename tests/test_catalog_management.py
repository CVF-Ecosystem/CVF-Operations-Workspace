from __future__ import annotations

import copy
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "manage_catalog.py"
SPEC = importlib.util.spec_from_file_location("manage_catalog", SCRIPT_PATH)
assert SPEC and SPEC.loader
manage_catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manage_catalog)


class CatalogManagementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.artifacts = manage_catalog.load_json(
            REPO_ROOT / "docs" / "catalog" / "ARTIFACT_REGISTRY.json"
        )
        cls.modules = manage_catalog.load_json(
            REPO_ROOT / "docs" / "catalog" / "MODULE_REGISTRY.json"
        )

    def test_repository_baseline_is_valid(self) -> None:
        self.assertEqual([], manage_catalog.verify_artifacts(self.artifacts, REPO_ROOT))
        self.assertEqual([], manage_catalog.verify_modules(self.modules, REPO_ROOT))

    def test_duplicate_artifact_id_fails(self) -> None:
        registry = copy.deepcopy(self.artifacts)
        registry["artifacts"].append(copy.deepcopy(registry["artifacts"][0]))
        problems = manage_catalog.verify_artifacts(registry, REPO_ROOT)
        self.assertTrue(any("duplicate artifact id" in item for item in problems))

    def test_missing_artifact_path_fails(self) -> None:
        registry = copy.deepcopy(self.artifacts)
        registry["artifacts"][0]["path"] = "docs/does-not-exist.md"
        problems = manage_catalog.verify_artifacts(registry, REPO_ROOT)
        self.assertTrue(any("does not exist" in item for item in problems))

    def test_unknown_relationship_fails(self) -> None:
        registry = copy.deepcopy(self.artifacts)
        registry["artifacts"][0]["related"] = ["missing-id"]
        problems = manage_catalog.verify_artifacts(registry, REPO_ROOT)
        self.assertTrue(any("related unknown artifact" in item for item in problems))

    def test_unknown_artifact_status_and_duplicate_path_fail(self) -> None:
        registry = copy.deepcopy(self.artifacts)
        registry["artifacts"][0]["status"] = "imaginary"
        registry["artifacts"][1]["path"] = registry["artifacts"][0]["path"]
        problems = manage_catalog.verify_artifacts(registry, REPO_ROOT)
        self.assertTrue(any("unknown artifact status" in item for item in problems))
        self.assertTrue(any("duplicate artifact path" in item for item in problems))

    def test_empty_required_artifact_field_fails(self) -> None:
        registry = copy.deepcopy(self.artifacts)
        registry["artifacts"][0]["authority"] = ""
        problems = manage_catalog.verify_artifacts(registry, REPO_ROOT)
        self.assertTrue(any("authority must be a non-empty string" in item for item in problems))

    def test_windows_separator_and_path_escape_fail(self) -> None:
        registry = copy.deepcopy(self.artifacts)
        registry["artifacts"][0]["path"] = "docs\\INDEX.md"
        problems = manage_catalog.verify_artifacts(registry, REPO_ROOT)
        self.assertTrue(any("must use '/'" in item for item in problems))
        registry["artifacts"][0]["path"] = "../WORKSPACE_RULES.md"
        problems = manage_catalog.verify_artifacts(registry, REPO_ROOT)
        self.assertTrue(any("escapes repository" in item for item in problems))

    def test_unknown_module_status_and_dependency_fail(self) -> None:
        registry = copy.deepcopy(self.modules)
        registry["modules"] = [
            {
                "id": "bad-module",
                "path": "scripts",
                "kind": "tool",
                "purpose": "Negative test fixture.",
                "status": "imaginary",
                "cvfControls": ["imaginary-control"],
                "enforcement": "None.",
                "dependsOn": ["missing-module"],
                "tests": [],
                "nextStep": "Remove fixture.",
                "metrics": {"codeLoc": 0, "codeFiles": 0, "nonemptyCodeFiles": 0},
            }
        ]
        problems = manage_catalog.verify_modules(registry, REPO_ROOT)
        self.assertTrue(any("unknown module status" in item for item in problems))
        self.assertTrue(any("unknown CVF control" in item for item in problems))
        self.assertTrue(any("dependsOn unknown module" in item for item in problems))

    def test_generated_views_and_metrics_have_no_drift(self) -> None:
        self.assertEqual([], manage_catalog.run(write=False, root=REPO_ROOT))

    def test_hand_edited_generated_index_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            clone = Path(temporary) / "repo"
            shutil.copytree(
                REPO_ROOT,
                clone,
                ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"),
            )
            index = clone / "docs" / "INDEX.md"
            index.write_text(index.read_text(encoding="utf-8") + "HAND EDIT\n", encoding="utf-8")
            problems = manage_catalog.run(write=False, root=clone)
            self.assertTrue(any("docs/INDEX.md has drifted" in item for item in problems))

    def test_cli_check_passes_without_writing(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--check"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("INDEX/CATALOG: PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
