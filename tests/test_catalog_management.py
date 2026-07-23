"""Regression tests for the Golden Downstream Catalog Kit 1.1 manager.

These tests replace the retired Python catalog manager
(`scripts/manage_catalog.py`) and its prior test suite. They exercise the
real, byte-identical-to-CVF-core PowerShell manager
(`scripts/manage_cvf_downstream_catalog.ps1` +
`scripts/lib/downstream_catalog/CvfDownstreamCatalogLib.ps1`) as an external
process, never re-implementing or mocking its validation logic. Every
guarantee the retired Python suite proved has an equivalent case here:
schema closure, path existence, duplicate id/path rejection, path-escape
rejection, and generated-view drift detection. Golden's closed schema adds
guarantees the old open-ended schema never had (unknown-field rejection,
mandatory-baseline-entry enforcement, module status/evidence/control/
dependency rules), which are covered as new cases, not carried over from the
old suite's `related`/`type` fields that no longer exist in the Golden
schema.
"""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANAGER_RELATIVE = Path("scripts") / "manage_cvf_downstream_catalog.ps1"
ARTIFACT_REGISTRY_RELATIVE = Path("docs") / "catalog" / "ARTIFACT_REGISTRY.json"
MODULE_REGISTRY_RELATIVE = Path("docs") / "catalog" / "MODULE_REGISTRY.json"
INDEX_RELATIVE = Path("docs") / "INDEX.md"
MODULE_CATALOG_RELATIVE = Path("docs") / "catalog" / "MODULE_CATALOG.md"


def _run_manager(project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    manager_path = project_root / MANAGER_RELATIVE
    return subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(manager_path), *args],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )


class GoldenCatalogManagerRegressionTests(unittest.TestCase):
    """Runs the real Golden manager against a disposable copy of this repo."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmpdir = tempfile.TemporaryDirectory()
        cls.project_root = Path(cls.tmpdir.name) / "repo"
        shutil.copytree(
            REPO_ROOT,
            cls.project_root,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"),
        )
        cls.artifact_registry_path = cls.project_root / ARTIFACT_REGISTRY_RELATIVE
        cls.module_registry_path = cls.project_root / MODULE_REGISTRY_RELATIVE
        cls.index_path = cls.project_root / INDEX_RELATIVE
        cls.module_catalog_path = cls.project_root / MODULE_CATALOG_RELATIVE
        cls.base_artifact_registry = json.loads(
            cls.artifact_registry_path.read_text(encoding="utf-8")
        )
        cls.base_module_registry = json.loads(
            cls.module_registry_path.read_text(encoding="utf-8")
        )
        cls.base_index_text = cls.index_path.read_text(encoding="utf-8")
        cls.base_module_catalog_text = cls.module_catalog_path.read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmpdir.cleanup()

    def setUp(self) -> None:
        # Every test starts from the real, currently-valid registries and
        # generated views so a mutation in one test (including a hand-edit)
        # can never leak into another.
        self._write_artifact_registry(self.base_artifact_registry)
        self._write_module_registry(self.base_module_registry)
        self.index_path.write_text(self.base_index_text, encoding="utf-8")
        self.module_catalog_path.write_text(self.base_module_catalog_text, encoding="utf-8")

    def _write_artifact_registry(self, registry: dict) -> None:
        self.artifact_registry_path.write_text(
            json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    def _write_module_registry(self, registry: dict) -> None:
        self.module_registry_path.write_text(
            json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    def _check(self) -> subprocess.CompletedProcess[str]:
        return _run_manager(self.project_root, "-Check")

    # -- positive baseline -------------------------------------------------

    def test_real_repository_registries_pass_check(self) -> None:
        result = self._check()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("[PASS]", result.stdout)

    def test_cli_check_passes_without_writing(self) -> None:
        before_index = (self.project_root / INDEX_RELATIVE).read_text(encoding="utf-8")
        result = self._check()
        after_index = (self.project_root / INDEX_RELATIVE).read_text(encoding="utf-8")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(before_index, after_index)

    def test_write_then_check_has_no_drift(self) -> None:
        write_result = _run_manager(self.project_root, "-Write")
        self.assertEqual(0, write_result.returncode, write_result.stdout + write_result.stderr)
        check_result = self._check()
        self.assertEqual(0, check_result.returncode, check_result.stdout + check_result.stderr)

    # -- artifact registry: closed-schema shape -----------------------------

    def test_unknown_top_level_field_fails(self) -> None:
        registry = copy.deepcopy(self.base_artifact_registry)
        registry["unexpectedTopLevelField"] = "not allowed"
        self._write_artifact_registry(registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("additional property not allowed", result.stdout)

    def test_unknown_entry_field_fails(self) -> None:
        registry = copy.deepcopy(self.base_artifact_registry)
        registry["artifacts"][0]["title"] = "old-schema field, not in Golden schema"
        self._write_artifact_registry(registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("additional property not allowed", result.stdout)

    def test_invalid_family_fails(self) -> None:
        registry = copy.deepcopy(self.base_artifact_registry)
        registry["artifacts"][0]["family"] = "not-a-real-family"
        self._write_artifact_registry(registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("invalid family", result.stdout)

    def test_invalid_status_fails(self) -> None:
        registry = copy.deepcopy(self.base_artifact_registry)
        registry["artifacts"][0]["status"] = "imaginary"
        self._write_artifact_registry(registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("invalid lifecycle status", result.stdout)

    def test_duplicate_artifact_id_fails(self) -> None:
        registry = copy.deepcopy(self.base_artifact_registry)
        duplicate = copy.deepcopy(registry["artifacts"][0])
        duplicate["path"] = "docs/catalog/README.md"  # avoid also tripping duplicate-path
        registry["artifacts"].append(duplicate)
        self._write_artifact_registry(registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("duplicate id", result.stdout)

    def test_duplicate_artifact_path_fails(self) -> None:
        registry = copy.deepcopy(self.base_artifact_registry)
        registry["artifacts"][1]["path"] = registry["artifacts"][0]["path"]
        self._write_artifact_registry(registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("duplicate path", result.stdout)

    def test_missing_artifact_path_fails(self) -> None:
        registry = copy.deepcopy(self.base_artifact_registry)
        registry["artifacts"][0]["path"] = "docs/catalog/schemas/DOES_NOT_EXIST.json"
        self._write_artifact_registry(registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("registered path does not exist", result.stdout)

    def test_windows_backslash_path_fails(self) -> None:
        registry = copy.deepcopy(self.base_artifact_registry)
        registry["artifacts"][0]["path"] = "docs\\catalog\\schemas\\ARTIFACT_REGISTRY.schema.json"
        self._write_artifact_registry(registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("path escape or non-portable path", result.stdout)

    def test_path_traversal_escape_fails(self) -> None:
        registry = copy.deepcopy(self.base_artifact_registry)
        registry["artifacts"][0]["path"] = "../WORKSPACE_RULES.md"
        self._write_artifact_registry(registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("path escape or non-portable path", result.stdout)

    def test_leading_slash_path_fails(self) -> None:
        registry = copy.deepcopy(self.base_artifact_registry)
        registry["artifacts"][0]["path"] = "/etc/passwd"
        self._write_artifact_registry(registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("path escape or non-portable path", result.stdout)

    def test_drive_letter_path_fails(self) -> None:
        registry = copy.deepcopy(self.base_artifact_registry)
        registry["artifacts"][0]["path"] = "C:/Windows/System32/config"
        self._write_artifact_registry(registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("path escape or non-portable path", result.stdout)

    def test_missing_mandatory_baseline_entry_fails(self) -> None:
        registry = copy.deepcopy(self.base_artifact_registry)
        registry["artifacts"] = [
            a for a in registry["artifacts"] if a["id"] != "manifest-cvf"
        ]
        self._write_artifact_registry(registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing mandatory authority surface", result.stdout)

    def test_mandatory_baseline_entry_wrong_path_fails(self) -> None:
        registry = copy.deepcopy(self.base_artifact_registry)
        for artifact in registry["artifacts"]:
            if artifact["id"] == "policy-cvf":
                artifact["path"] = "docs/catalog/README.md"
        self._write_artifact_registry(registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("has unexpected path", result.stdout)

    # -- module registry: source-backed vocabulary --------------------------

    def _module_registry_with(self, module: dict) -> dict:
        registry = copy.deepcopy(self.base_module_registry)
        registry["modules"] = [module]
        return registry

    def test_module_plan_only_status_fails(self) -> None:
        registry = self._module_registry_with(
            {
                "id": "future-module",
                "name": "Future Module",
                "path": "scripts",
                "status": "PLANNED",
                "description": "Negative test fixture.",
                "evidence": "None yet.",
            }
        )
        self._write_module_registry(registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("invalid status", result.stdout)
        self.assertIn("plan-only", result.stdout)

    def test_module_missing_evidence_fails(self) -> None:
        registry = self._module_registry_with(
            {
                "id": "unevidenced-module",
                "name": "Unevidenced Module",
                "path": "scripts",
                "status": "ENFORCED",
                "description": "Negative test fixture.",
                "evidence": "",
            }
        )
        self._write_module_registry(registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("evidence", result.stdout)

    def test_module_unknown_control_token_fails(self) -> None:
        registry = self._module_registry_with(
            {
                "id": "bad-control-module",
                "name": "Bad Control Module",
                "path": "scripts",
                "status": "STUB",
                "description": "Negative test fixture.",
                "evidence": "scripts/manage_cvf_downstream_catalog.ps1",
                "controls": ["identity"],
            }
        )
        self._write_module_registry(registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("unknown CVF control token", result.stdout)

    def test_module_unknown_dependency_fails(self) -> None:
        registry = self._module_registry_with(
            {
                "id": "dependent-module",
                "name": "Dependent Module",
                "path": "scripts",
                "status": "STUB",
                "description": "Negative test fixture.",
                "evidence": "scripts/manage_cvf_downstream_catalog.ps1",
                "dependencies": ["nonexistent-module"],
            }
        )
        self._write_module_registry(registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("unknown module dependency", result.stdout)

    # -- generated-view drift -----------------------------------------------

    def test_hand_edited_generated_index_fails_closed(self) -> None:
        index_path = self.project_root / INDEX_RELATIVE
        index_path.write_text(
            index_path.read_text(encoding="utf-8") + "HAND EDIT\n", encoding="utf-8"
        )
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("hand-edited or stale", result.stdout)

    def test_hand_edited_module_catalog_fails_closed(self) -> None:
        module_catalog_path = self.project_root / "docs" / "catalog" / "MODULE_CATALOG.md"
        module_catalog_path.write_text(
            module_catalog_path.read_text(encoding="utf-8") + "HAND EDIT\n", encoding="utf-8"
        )
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("hand-edited or stale", result.stdout)

    def test_registry_project_identity_mismatch_fails(self) -> None:
        artifact_registry = copy.deepcopy(self.base_artifact_registry)
        module_registry = copy.deepcopy(self.base_module_registry)
        module_registry["projectName"] = "Some-Other-Project"
        self._write_artifact_registry(artifact_registry)
        self._write_module_registry(module_registry)
        result = self._check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("registry project identity mismatch", result.stdout)


if __name__ == "__main__":
    unittest.main()
