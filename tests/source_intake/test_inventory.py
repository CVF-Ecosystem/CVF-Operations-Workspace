from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "source_intake" / "inventory.py"
SPEC = importlib.util.spec_from_file_location("si_inventory", MODULE_PATH)
assert SPEC and SPEC.loader
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)


def _run(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


class ClassifyTests(unittest.TestCase):
    def test_database_migration(self) -> None:
        self.assertEqual(inventory.classify("database/migrations/001_foundation.sql"), "database_migration")

    def test_test_code_by_directory(self) -> None:
        self.assertEqual(inventory.classify("apps/workspace-api/tests/test_lifecycle.py"), "test_code")

    def test_test_code_by_filename_prefix(self) -> None:
        self.assertEqual(inventory.classify("tests/cvf/test_gates_unit.py"), "test_code")

    def test_ci_or_governance(self) -> None:
        self.assertEqual(inventory.classify(".github/workflows/ci.yml"), "ci_or_governance")

    def test_documentation(self) -> None:
        self.assertEqual(inventory.classify("docs/decisions/ADR_1.md"), "documentation")

    def test_contract_or_schema(self) -> None:
        self.assertEqual(
            inventory.classify("packages/workspace-contracts/event.schema.json"), "contract_or_schema"
        )

    def test_configuration(self) -> None:
        self.assertEqual(inventory.classify("pyproject.toml"), "configuration")

    def test_application_code(self) -> None:
        self.assertEqual(inventory.classify("apps/workspace-api/src/main.py"), "application_code")

    def test_package_code(self) -> None:
        self.assertEqual(inventory.classify("packages/cvf-runtime/src/gates.py"), "package_code")

    def test_lock_or_dependency_manifest(self) -> None:
        self.assertEqual(inventory.classify("pnpm-lock.yaml"), "lock_or_dependency_manifest")

    def test_root_markdown_file_is_documentation_regardless_of_location(self) -> None:
        for sample in ("AGENTS.md", "ARCHITECTURE.md", "CHANGELOG.md", "infrastructure/README.md"):
            self.assertEqual(inventory.classify(sample), "documentation")

    def test_license_and_codeowners_are_documentation(self) -> None:
        self.assertEqual(inventory.classify("LICENSE"), "documentation")
        self.assertEqual(inventory.classify("CODEOWNERS"), "documentation")

    def test_governance_and_session_directories_are_ci_or_governance(self) -> None:
        for sample in (
            ".githooks/pre-commit",
            ".cvf/manifest.json",
            "CVF_SESSION/ACTIVE_SESSION_STATE.json",
            "SESSION/handoffs/AGENT_HANDOFF_1.md",
        ):
            self.assertIn(inventory.classify(sample), {"ci_or_governance", "documentation"})
        # Directory membership must win for non-.md files in these trees.
        self.assertEqual(inventory.classify(".githooks/pre-commit"), "ci_or_governance")
        self.assertEqual(inventory.classify(".cvf/manifest.json"), "ci_or_governance")
        self.assertEqual(inventory.classify("CVF_SESSION/ACTIVE_SESSION_STATE.json"), "ci_or_governance")

    def test_root_dotfiles_and_makefile_are_configuration(self) -> None:
        for sample in (".gitignore", ".editorconfig", "Makefile", "conftest.py"):
            self.assertEqual(inventory.classify(sample), "configuration")

    def test_dockerfile_variants_are_configuration(self) -> None:
        self.assertEqual(inventory.classify("infrastructure/docker/Dockerfile.api"), "configuration")

    def test_top_level_scripts_directory_is_ci_or_governance(self) -> None:
        self.assertEqual(inventory.classify("scripts/generate_catalog.py"), "ci_or_governance")

    def test_database_non_migration_assets_are_configuration(self) -> None:
        self.assertEqual(inventory.classify("database/functions/freeze_shift.sql"), "configuration")
        self.assertEqual(inventory.classify("database/seeds/reference_data.sql"), "configuration")

    def test_root_level_json_metadata_is_documentation(self) -> None:
        self.assertEqual(inventory.classify("IMPLEMENTATION_STATUS.json"), "documentation")

    def test_nested_json_without_contract_keyword_is_not_forced_to_documentation(self) -> None:
        # The root-only rule must not swallow ordinary nested data files;
        # those still fall through to their normal path-based classification.
        self.assertEqual(inventory.classify("fixtures/events/sample.json"), "documentation")
        self.assertEqual(inventory.classify("apps/workspace-api/config/settings.json"), "application_code")

    def test_examples_and_fixtures_are_documentation(self) -> None:
        self.assertEqual(inventory.classify("examples/sample-shift/shift.json"), "documentation")
        self.assertEqual(inventory.classify("fixtures/messages/internal_message.json"), "documentation")

    def test_other_is_a_valid_catchall(self) -> None:
        result = inventory.classify("some_unexpected_top_level_file.xyz")
        self.assertEqual(result, "other")
        self.assertIn(result, inventory.CANDIDATE_CLASSES)

    def test_every_class_is_in_the_closed_vocabulary(self) -> None:
        samples = [
            "database/migrations/001_a.sql", "tests/test_x.py", ".github/workflows/ci.yml",
            "docs/readme.md", "packages/workspace-contracts/x.schema.json", "pyproject.toml",
            "apps/workspace-api/src/x.py", "packages/cvf-runtime/src/x.py", "pnpm-lock.yaml",
            "weird.bin",
        ]
        for sample in samples:
            self.assertIn(inventory.classify(sample), inventory.CANDIDATE_CLASSES)


class IsExcludedTests(unittest.TestCase):
    def test_env_file_excluded(self) -> None:
        excluded, reason = inventory.is_excluded(".env")
        self.assertTrue(excluded)
        self.assertEqual(reason, "env-file")

    def test_env_variant_excluded(self) -> None:
        excluded, _ = inventory.is_excluded(".env.production")
        self.assertTrue(excluded)

    def test_credential_like_name_excluded(self) -> None:
        excluded, reason = inventory.is_excluded("apps/workspace-api/provider_credentials.json")
        self.assertTrue(excluded)
        self.assertEqual(reason, "credential-like-name")

    def test_local_binding_excluded(self) -> None:
        excluded, reason = inventory.is_excluded(".cvf/local-binding.json")
        self.assertTrue(excluded)
        self.assertEqual(reason, "local-binding-file")

    def test_key_material_excluded(self) -> None:
        excluded, reason = inventory.is_excluded("certs/server.pem")
        self.assertTrue(excluded)
        self.assertEqual(reason, "key-material-suffix")

    def test_excluded_directory(self) -> None:
        excluded, reason = inventory.is_excluded("apps/workspace-api/__pycache__/x.pyc")
        self.assertTrue(excluded)
        self.assertEqual(reason, "excluded-directory")

    def test_ordinary_source_file_is_not_excluded(self) -> None:
        excluded, reason = inventory.is_excluded("apps/workspace-api/src/main.py")
        self.assertFalse(excluded)
        self.assertIsNone(reason)


class IsBinaryContentTests(unittest.TestCase):
    def test_text_is_not_binary(self) -> None:
        self.assertFalse(inventory.is_binary_content(b"hello world\n"))

    def test_null_byte_marks_binary(self) -> None:
        self.assertTrue(inventory.is_binary_content(b"\x00\x01\x02PNG"))


class BuildInventoryTests(unittest.TestCase):
    def test_excludes_secrets_and_hashes_the_rest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _run(["init", "-q"], repo)
            _run(["config", "user.email", "f0-test@example.com"], repo)
            _run(["config", "user.name", "F0 Test"], repo)

            (repo / "apps" / "demo-app" / "src").mkdir(parents=True)
            source_file = repo / "apps" / "demo-app" / "src" / "main.py"
            source_file.write_text("print('hello')\n", encoding="utf-8")

            env_file = repo / ".env"
            env_file.write_text("SECRET=do-not-capture\n", encoding="utf-8")

            _run(["add", "-A"], repo)
            _run(["commit", "-q", "-m", "fixture"], repo)

            records, exclusions = inventory.build_inventory(repo)

            captured_paths = {record["source_path"] for record in records}
            self.assertIn("apps/demo-app/src/main.py", captured_paths)
            self.assertNotIn(".env", captured_paths)

            excluded_paths = {item["source_path"]: item["reason"] for item in exclusions}
            self.assertEqual(excluded_paths.get(".env"), "env-file")

            main_record = next(r for r in records if r["source_path"] == "apps/demo-app/src/main.py")
            expected_blob = b"print('hello')\n"
            expected_hash = hashlib.sha256(expected_blob).hexdigest()
            self.assertEqual(main_record["sha256"], expected_hash)
            self.assertEqual(main_record["size_bytes"], len(expected_blob))
            self.assertEqual(main_record["candidate_class"], "application_code")
            self.assertFalse(main_record["is_binary"])

            # deterministic ordering
            self.assertEqual([r["source_path"] for r in records], sorted(r["source_path"] for r in records))

    def test_hashes_git_blob_not_eol_converted_worktree_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _run(["init", "-q"], repo)
            _run(["config", "user.email", "f0-test@example.com"], repo)
            _run(["config", "user.name", "F0 Test"], repo)

            tracked = repo / "README.md"
            blob_bytes = b"line one\nline two\n"
            tracked.write_bytes(blob_bytes)
            _run(["add", "README.md"], repo)
            _run(["commit", "-q", "-m", "fixture"], repo)

            # Simulate a Windows checkout after Git's LF-to-CRLF conversion.
            tracked.write_bytes(blob_bytes.replace(b"\n", b"\r\n"))
            records, _ = inventory.build_inventory(repo)
            record = next(r for r in records if r["source_path"] == "README.md")

            self.assertEqual(record["sha256"], hashlib.sha256(blob_bytes).hexdigest())
            self.assertEqual(record["size_bytes"], len(blob_bytes))
            self.assertNotEqual(record["sha256"], hashlib.sha256(tracked.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
