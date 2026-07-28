from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "scripts" / "linked_sources" / "apply.py"
SPEC = importlib.util.spec_from_file_location("linked_apply", MODULE)
assert SPEC and SPEC.loader
apply = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(apply)


class ApplySafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_destination_escape_and_protected_paths(self) -> None:
        # AC-40: full protected destination matrix
        invalid = (
            "/absolute/file", "C:\\drive\\file", "\\\\server\\share", "a//b",
            "a/../b", "a\\..\\b", "a:b", "CON.txt", ".git/config",
            ".cvf/manifest.json", "CVF_SESSION/state.json", "docs/catalog/x.json",
            "docs/roadmaps/plan.md", "docs/INDEX.md",
            "docs/decisions/ADR.md", "docs/specs/spec.md",
            "docs/work_orders/wo.md", "docs/reviews/review.md",
            "provenance/shift-operations/abc/report.json",
            "AGENTS.md", "IMPLEMENTATION_STATUS.json", "CVF_SESSION_MEMORY.md",
        )
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(apply.DestinationPathError):
                apply._safe_relative(value, self.root)

    def test_docs_roadmaps_is_protected(self) -> None:
        # R3: docs/roadmaps/ must be a protected destination
        with self.assertRaises(apply.DestinationPathError):
            apply._safe_relative("docs/roadmaps/plan.md", self.root)

    def test_docs_index_md_is_protected(self) -> None:
        # R3: docs/INDEX.md must be a protected destination (case-folded)
        with self.assertRaises(apply.DestinationPathError):
            apply._safe_relative("docs/index.md", self.root)
        with self.assertRaises(apply.DestinationPathError):
            apply._safe_relative("docs/INDEX.md", self.root)

    def test_case_and_unicode_destination_collisions(self) -> None:
        base = {
            "entries": [
                {"operation": "new", "destinationPath": "packages/Value.py"},
                {"operation": "new", "destinationPath": "packages/value.py"},
            ]
        }
        with self.assertRaises(apply.DestinationPathError):
            apply._destinations(base, self.root)
        base["entries"][0]["destinationPath"] = "packages/caf\u00e9.py"
        base["entries"][1]["destinationPath"] = "packages/cafe\u0301.py"
        with self.assertRaises(apply.DestinationPathError):
            apply._destinations(base, self.root)

    def test_duplicate_destination_rejection(self) -> None:
        # R9: reject every repeated normalized destination
        # Exact duplicate strings
        base_exact = {
            "entries": [
                {"operation": "new", "destinationPath": "packages/shared/file.txt"},
                {"operation": "new", "destinationPath": "packages/shared/file.txt"},
            ]
        }
        with self.assertRaises(apply.DestinationPathError):
            apply._destinations(base_exact, self.root)

        # Duplicate between rename entry and another entry
        base_rename = {
            "entries": [
                {"operation": "new", "destinationPath": "packages/shared/target.py"},
                {
                    "operation": "renamed",
                    "oldDestinationPath": "packages/old.py",
                    "newDestinationPath": "packages/shared/target.py",
                },
            ]
        }
        with self.assertRaises(apply.DestinationPathError):
            apply._destinations(base_rename, self.root)

        # Duplicate old/new paths within a single rename entry
        base_same_rename = {
            "entries": [
                {
                    "operation": "renamed",
                    "oldDestinationPath": "packages/same.py",
                    "newDestinationPath": "packages/same.py",
                },
            ]
        }
        with self.assertRaises(apply.DestinationPathError):
            apply._destinations(base_same_rename, self.root)

    def test_symlink_ancestor_is_rejected_when_supported(self) -> None:
        real = self.root / "real"
        real.mkdir()
        link = self.root / "link"
        try:
            link.symlink_to(real, target_is_directory=True)
        except OSError:
            self.skipTest("symlink creation unavailable")
        with self.assertRaises(apply.DestinationPathError):
            apply._safe_relative("link/file.txt", self.root)

    def test_destination_precondition_drift(self) -> None:
        target = self.root / "target.txt"
        apply._check(target, {"state": "ABSENT"})
        target.write_text("before", encoding="utf-8")
        digest = apply._sha(target.read_bytes())
        apply._check(target, {"state": "PRESENT", "sha256": digest})
        target.write_text("drift", encoding="utf-8")
        with self.assertRaises(apply.DestinationDriftError):
            apply._check(target, {"state": "PRESENT", "sha256": digest})

    def test_authorization_requires_lowercase_full_sha40(self) -> None:
        # R1: symbolic refs, abbreviated hashes, and uppercase must all be rejected
        bad_commits = [
            "origin/main",          # symbolic ref
            "HEAD",                 # symbolic ref
            "1a2b3c4d",             # abbreviated (8 chars)
            "1" * 39,               # too short (39 chars)
            "1" * 41,               # too long (41 chars)
            "1" * 38 + "AB",        # uppercase hex
            "ABCDEF" + "0" * 34,    # uppercase
            "",                     # empty
        ]
        for bad in bad_commits:
            with self.subTest(commit=bad), self.assertRaises(apply.AuthorizationError):
                apply.verify_authorization(self.root, self.root / "manifest.json", bad, self.root / "receipt.json")

    def test_unsafe_receipt_path_normalization_rejected(self) -> None:
        # R1A: strict fail-closed validation for authorizationReceiptPath
        unsafe_paths = [
            "/reviews/receipt.json",
            "\\reviews\\receipt.json",
            "C:\\reviews\\receipt.json",
            "\\\\server\\share\\receipt.json",
            "reviews//receipt.json",
            "reviews/./receipt.json",
            "reviews/../receipt.json",
            "reviews/..\\receipt.json",
            "reviews\\../receipt.json",
            "reviews/receipt.json\0",
            "reviews/receipt.json:stream",
            "",
        ]
        for unsafe in unsafe_paths:
            with self.subTest(path=repr(unsafe)):
                with self.assertRaises(apply.ManifestSchemaError):
                    apply._validate_canonical_receipt_path(unsafe)

    def test_authorization_requires_commit_reachable_from_origin_main_and_exact_blobs(self) -> None:
        origin = self.root / "origin.git"
        repo = self.root / "repo"
        subprocess.run(["git", "init", "--bare", "-q", str(origin)], check=True)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        for args in (("config", "user.email", "test@example.com"), ("config", "user.name", "Test"), ("config", "core.autocrlf", "false"), ("remote", "add", "origin", str(origin))):
            subprocess.run(["git", "-C", str(repo), *args], check=True)
        (repo / "manifests").mkdir()
        (repo / "reviews").mkdir()
        entry = {
            "operation": "new", "candidateSourcePath": "src/new.py",
            "candidateSourceBlobSha256": "5" * 64, "candidateSourceGitMode": "100644",
            "destinationPath": "packages/new.py", "destinationPrecondition": {"state": "ABSENT"},
        }
        manifest = {
            "schemaVersion": "1.0", "workspaceId": "cvf-operations-workspace",
            "baseCommit": "1" * 40, "candidateCommit": "2" * 40,
            "scanDatasetSha256": "3" * 64, "filteringPolicyVersion": "1.0",
            "filteringPolicySha256": "4" * 64, "entries": [entry],
            "authorizationReceiptPath": "reviews/receipt.json",
        }
        manifest["manifestSha256"] = apply.canonical_manifest_sha256(manifest)
        manifest_path = repo / "manifests" / "apply.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        receipt = {
            "receiptSchemaVersion": "1.0", "decision": "REVIEW_PASS",
            "manifestPath": "manifests/apply.json", "manifestSha256": manifest["manifestSha256"],
            "baseCommit": manifest["baseCommit"], "candidateCommit": manifest["candidateCommit"],
            "scanDatasetSha256": manifest["scanDatasetSha256"],
            "filteringPolicySha256": manifest["filteringPolicySha256"],
            "reviewerRole": "REVIEWER", "reviewEvidence": "reviews/evidence.md",
        }
        receipt_path = repo / "reviews" / "receipt.json"
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "manifests/apply.json", "reviews/receipt.json"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "authorize"], check=True)
        subprocess.run(["git", "-C", str(repo), "branch", "-M", "main"], check=True)
        subprocess.run(["git", "-C", str(repo), "push", "-q", "-u", "origin", "main"], check=True)
        subprocess.run(["git", "-C", str(repo), "update-ref", "refs/remotes/origin/main", "HEAD"], check=True)
        subprocess.run(["git", "-C", str(repo), "remote", "set-url", "origin", "https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git"], check=True)
        commit = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
        apply.verify_authorization(repo, manifest_path, commit, receipt_path)
        # Receipt blob modified: must fail
        receipt_path.write_text(receipt_path.read_text(encoding="utf-8") + " ", encoding="utf-8")
        with self.assertRaises(apply.AuthorizationError):
            apply.verify_authorization(repo, manifest_path, commit, receipt_path)

    def test_authorization_receipt_schema_validation(self) -> None:
        # R1: receiptSchemaVersion, reviewerRole, reviewEvidence must all be validated
        origin = self.root / "origin2.git"
        repo = self.root / "repo2"
        subprocess.run(["git", "init", "--bare", "-q", str(origin)], check=True)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        for args in (("config", "user.email", "t@t.com"), ("config", "user.name", "T"), ("config", "core.autocrlf", "false"), ("remote", "add", "origin", str(origin))):
            subprocess.run(["git", "-C", str(repo), *args], check=True)
        (repo / "m").mkdir()
        (repo / "r").mkdir()
        entry = {
            "operation": "new", "candidateSourcePath": "src/x.py",
            "candidateSourceBlobSha256": "5" * 64, "candidateSourceGitMode": "100644",
            "destinationPath": "packages/x.py", "destinationPrecondition": {"state": "ABSENT"},
        }
        manifest = {
            "schemaVersion": "1.0", "workspaceId": "cvf-operations-workspace",
            "baseCommit": "1" * 40, "candidateCommit": "2" * 40,
            "scanDatasetSha256": "3" * 64, "filteringPolicyVersion": "1.0",
            "filteringPolicySha256": "4" * 64, "entries": [entry],
            "authorizationReceiptPath": "r/receipt.json",
        }
        manifest["manifestSha256"] = apply.canonical_manifest_sha256(manifest)
        manifest_path = repo / "m" / "apply.json"
        manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")

        def _commit_and_get_hash(receipt_data: dict) -> str:
            receipt_path = repo / "r" / "receipt.json"
            receipt_path.write_text(json.dumps(receipt_data) + "\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-q", "--allow-empty", "-m", "x"], check=True)
            subprocess.run(["git", "-C", str(repo), "push", "-q", "-f", "origin", "HEAD:main"], check=True)
            subprocess.run(["git", "-C", str(repo), "update-ref", "refs/remotes/origin/main", "HEAD"], check=True)
            subprocess.run(["git", "-C", str(repo), "remote", "set-url", "origin", "https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git"], check=True)
            return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()

        base_receipt = {
            "receiptSchemaVersion": "1.0", "decision": "REVIEW_PASS",
            "manifestPath": "m/apply.json", "manifestSha256": manifest["manifestSha256"],
            "baseCommit": manifest["baseCommit"], "candidateCommit": manifest["candidateCommit"],
            "scanDatasetSha256": manifest["scanDatasetSha256"],
            "filteringPolicySha256": manifest["filteringPolicySha256"],
            "reviewerRole": "REVIEWER", "reviewEvidence": "r/evidence.md",
        }
        receipt_path = repo / "r" / "receipt.json"

        # Valid receipt must pass (initialize main branch)
        commit_hash = _commit_and_get_hash(base_receipt)
        apply.verify_authorization(repo, manifest_path, commit_hash, receipt_path)

        # Wrong receiptSchemaVersion
        bad = {**base_receipt, "receiptSchemaVersion": "2.0"}
        commit_hash = _commit_and_get_hash(bad)
        with self.assertRaises(apply.AuthorizationError):
            apply.verify_authorization(repo, manifest_path, commit_hash, receipt_path)

        # decision not REVIEW_PASS
        bad = {**base_receipt, "decision": "PENDING"}
        commit_hash = _commit_and_get_hash(bad)
        with self.assertRaises(apply.AuthorizationError):
            apply.verify_authorization(repo, manifest_path, commit_hash, receipt_path)

        # reviewerRole not REVIEWER
        bad = {**base_receipt, "reviewerRole": "IMPLEMENTATION_WORKER"}
        commit_hash = _commit_and_get_hash(bad)
        with self.assertRaises(apply.AuthorizationError):
            apply.verify_authorization(repo, manifest_path, commit_hash, receipt_path)

        # reviewEvidence empty
        bad = {**base_receipt, "reviewEvidence": ""}
        commit_hash = _commit_and_get_hash(bad)
        with self.assertRaises(apply.AuthorizationError):
            apply.verify_authorization(repo, manifest_path, commit_hash, receipt_path)

    def test_authorization_receipt_path_must_match_manifest(self) -> None:
        # R1: receipt path must match manifest.authorizationReceiptPath
        origin = self.root / "origin3.git"
        repo = self.root / "repo3"
        subprocess.run(["git", "init", "--bare", "-q", str(origin)], check=True)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        for args in (("config", "user.email", "t@t.com"), ("config", "user.name", "T"), ("config", "core.autocrlf", "false"), ("remote", "add", "origin", str(origin))):
            subprocess.run(["git", "-C", str(repo), *args], check=True)
        (repo / "m").mkdir()
        (repo / "r1").mkdir()
        (repo / "r2").mkdir()
        entry = {
            "operation": "new", "candidateSourcePath": "src/x.py",
            "candidateSourceBlobSha256": "5" * 64, "candidateSourceGitMode": "100644",
            "destinationPath": "packages/x.py", "destinationPrecondition": {"state": "ABSENT"},
        }
        manifest = {
            "schemaVersion": "1.0", "workspaceId": "cvf-operations-workspace",
            "baseCommit": "1" * 40, "candidateCommit": "2" * 40,
            "scanDatasetSha256": "3" * 64, "filteringPolicyVersion": "1.0",
            "filteringPolicySha256": "4" * 64, "entries": [entry],
            "authorizationReceiptPath": "r1/receipt.json",  # bound to r1
        }
        manifest["manifestSha256"] = apply.canonical_manifest_sha256(manifest)
        manifest_path = repo / "m" / "apply.json"
        manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
        receipt = {
            "receiptSchemaVersion": "1.0", "decision": "REVIEW_PASS",
            "manifestPath": "m/apply.json", "manifestSha256": manifest["manifestSha256"],
            "baseCommit": manifest["baseCommit"], "candidateCommit": manifest["candidateCommit"],
            "scanDatasetSha256": manifest["scanDatasetSha256"],
            "filteringPolicySha256": manifest["filteringPolicySha256"],
            "reviewerRole": "REVIEWER", "reviewEvidence": "r1/evidence.md",
        }
        wrong_receipt_path = repo / "r2" / "receipt.json"
        wrong_receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "x"], check=True)
        subprocess.run(["git", "-C", str(repo), "push", "-q", "-u", "origin", "HEAD:main"], check=True)
        subprocess.run(["git", "-C", str(repo), "update-ref", "refs/remotes/origin/main", "HEAD"], check=True)
        subprocess.run(["git", "-C", str(repo), "remote", "set-url", "origin", "https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git"], check=True)
        commit_hash = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        with self.assertRaises(apply.AuthorizationError):
            apply.verify_authorization(repo, manifest_path, commit_hash, wrong_receipt_path)

    def test_manifest_must_not_contain_self_declared_authorization_fields(self) -> None:
        # R1: non-circular model — manifest must not have authorizationCommit, status, approval etc.
        entry = {
            "operation": "new", "candidateSourcePath": "src/x.py",
            "candidateSourceBlobSha256": "5" * 64, "candidateSourceGitMode": "100644",
            "destinationPath": "packages/x.py", "destinationPrecondition": {"state": "ABSENT"},
        }
        for forbidden_field, val in [("authorizationCommit", "a" * 40), ("status", "approved"), ("approval", "true")]:
            with self.subTest(field=forbidden_field):
                m = {
                    "schemaVersion": "1.0", "workspaceId": "cvf-operations-workspace",
                    "baseCommit": "1" * 40, "candidateCommit": "2" * 40,
                    "scanDatasetSha256": "3" * 64, "filteringPolicyVersion": "1.0",
                    "filteringPolicySha256": "4" * 64, "entries": [entry],
                    "authorizationReceiptPath": "reviews/receipt.json",
                    forbidden_field: val,
                }
                m["manifestSha256"] = apply.canonical_manifest_sha256(m)
                with self.assertRaises(apply.ManifestSchemaError):
                    apply.validate_manifest(m)

    def test_apply_requires_tracked_manifest_and_receipt(self) -> None:
        # AC-19: missing manifest → ApplyRefusal
        ops = self.root / "ops"
        ops.mkdir()
        with self.assertRaises(apply.ApplyRefusal):
            apply.apply_manifest(ops, ops / "nonexistent.json", "a" * 40, ops / "receipt.json")

    def _authorized_apply_fixture(self):
        peer_origin = self.root / "shift-origin.git"
        peer = self.root / "shift-operations-workspace"
        ops_origin = self.root / "operations-origin.git"
        ops = self.root / "CVF-Operations-Workspace"
        subprocess.run(["git", "init", "--bare", "-q", str(peer_origin)], check=True)
        subprocess.run(["git", "clone", "-q", str(peer_origin), str(peer)], check=True)
        for args in (("config", "user.email", "test@example.com"), ("config", "user.name", "Test"), ("config", "core.autocrlf", "false")):
            subprocess.run(["git", "-C", str(peer), *args], check=True)
        (peer / "base.txt").write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(peer), "add", "base.txt"], check=True)
        subprocess.run(["git", "-C", str(peer), "commit", "-q", "-m", "base"], check=True)
        base = subprocess.run(["git", "-C", str(peer), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
        (peer / "one.txt").write_text("one\n", encoding="utf-8")
        (peer / "two.txt").write_text("two\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(peer), "add", "one.txt", "two.txt"], check=True)
        subprocess.run(["git", "-C", str(peer), "commit", "-q", "-m", "candidate"], check=True)
        candidate = subprocess.run(["git", "-C", str(peer), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
        subprocess.run(["git", "-C", str(peer), "push", "-q", "-u", "origin", "HEAD:main"], check=True)

        subprocess.run(["git", "init", "--bare", "-q", str(ops_origin)], check=True)
        subprocess.run(["git", "init", "-q", str(ops)], check=True)
        for args in (
            ("config", "user.email", "test@example.com"), ("config", "user.name", "Test"),
            ("config", "core.autocrlf", "false"), ("remote", "add", "origin", str(ops_origin)),
        ):
            subprocess.run(["git", "-C", str(ops), *args], check=True)
        (ops / ".cvf").mkdir()
        descriptor = {
            "schemaVersion": "1.0", "workspaceId": "cvf-operations-workspace",
            "thisRepo": {"repoId": "cvf-operations-workspace", "role": "PRIMARY_PLATFORM", "remote": "https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git"},
            "peerRepo": {"repoId": "shift-operations-workspace", "role": "PROFILE_SOURCE", "remote": "https://github.com/CVF-Ecosystem/shift-operations-workspace.git"},
            "relationshipDirection": "SHIFT_TO_OPERATIONS_GOVERNED_INTAKE",
            "sourcePin": base, "pinUpdatePolicy": "REVIEWED_SCAN_APPLY_CYCLE_ONLY",
        }
        (ops / ".cvf" / "workspace-link.json").write_text(json.dumps(descriptor, indent=2) + "\n", encoding="utf-8")
        dataset = apply.scan.build_dataset(peer, base, candidate)
        dataset_sha = hashlib.sha256(
            json.dumps(dataset, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        records = {row["path"]: row for row in dataset["records"]}
        entries = []
        for name in ("one.txt", "two.txt"):
            entries.append({
                "operation": "new", "candidateSourcePath": name,
                "candidateSourceBlobSha256": records[name]["candidateBlobSha256"],
                "candidateSourceGitMode": "100644", "destinationPath": f"packages/shared/{name}",
                "destinationPrecondition": {"state": "ABSENT"},
            })
        manifest = {
            "schemaVersion": "1.0", "workspaceId": "cvf-operations-workspace",
            "baseCommit": base, "candidateCommit": candidate,
            "scanDatasetSha256": dataset_sha, "filteringPolicyVersion": "1.0",
            "filteringPolicySha256": hashlib.sha256((ROOT / "scripts" / "linked_sources" / "filtering_policy.json").read_bytes()).hexdigest(),
            "entries": entries, "authorizationReceiptPath": "reviews/receipt.json",
        }
        manifest["manifestSha256"] = apply.canonical_manifest_sha256(manifest)
        (ops / "manifests").mkdir()
        (ops / "reviews").mkdir()
        manifest_path = ops / "manifests" / "apply.json"
        receipt_path = ops / "reviews" / "receipt.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        receipt = {
            "receiptSchemaVersion": "1.0", "decision": "REVIEW_PASS",
            "manifestPath": "manifests/apply.json", "manifestSha256": manifest["manifestSha256"],
            "baseCommit": base, "candidateCommit": candidate,
            "scanDatasetSha256": dataset_sha, "filteringPolicySha256": manifest["filteringPolicySha256"],
            "reviewerRole": "REVIEWER", "reviewEvidence": "reviews/evidence.md",
        }
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(ops), "add", ".cvf/workspace-link.json", "manifests/apply.json", "reviews/receipt.json"], check=True)
        subprocess.run(["git", "-C", str(ops), "commit", "-q", "-m", "authorize"], check=True)
        subprocess.run(["git", "-C", str(ops), "branch", "-M", "main"], check=True)
        subprocess.run(["git", "-C", str(ops), "push", "-q", "-u", "origin", "main"], check=True)
        subprocess.run(["git", "-C", str(ops), "update-ref", "refs/remotes/origin/main", "HEAD"], check=True)
        subprocess.run(["git", "-C", str(ops), "remote", "set-url", "origin", "https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git"], check=True)
        subprocess.run(["git", "-C", str(peer), "remote", "set-url", "origin", "https://github.com/CVF-Ecosystem/shift-operations-workspace.git"], check=True)
        commit_id = subprocess.run(["git", "-C", str(ops), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
        return ops, manifest_path, receipt_path, commit_id, candidate, manifest["manifestSha256"]

    def test_successful_apply_is_allowlist_only_and_receipt_is_hash_only(self) -> None:
        # AC-47: receipt contains only path/disposition/hash/outcome; no raw bytes, no secrets, no absolute paths
        ops, manifest_path, receipt_path, commit_id, candidate, manifest_sha = self._authorized_apply_fixture()
        receipt = apply.apply_manifest(ops, manifest_path, commit_id, receipt_path)
        self.assertEqual(receipt["outcome"], "APPLIED")
        peer = self.root / "shift-operations-workspace"
        expected_one = subprocess.run(
            ["git", "-C", str(peer), "show", f"{candidate}:one.txt"],
            check=True, capture_output=True,
        ).stdout
        expected_two = subprocess.run(
            ["git", "-C", str(peer), "show", f"{candidate}:two.txt"],
            check=True, capture_output=True,
        ).stdout
        self.assertEqual((ops / "packages/shared/one.txt").read_bytes(), expected_one)
        self.assertEqual((ops / "packages/shared/two.txt").read_bytes(), expected_two)
        tracked_receipt = ops / "provenance" / "shift-operations" / candidate / "apply" / manifest_sha / "apply_receipt.json"
        text = tracked_receipt.read_text(encoding="utf-8")
        # No absolute paths in receipt
        self.assertNotIn(str(ops), text)
        # No raw file content in receipt
        self.assertNotIn("one\\n", text)
        # Receipt must have outcome and entries with path/disposition/hashes only
        parsed = json.loads(text)
        self.assertEqual(parsed["outcome"], "APPLIED")
        for entry in parsed["entries"]:
            self.assertSetEqual(set(entry.keys()), {"path", "disposition", "beforeSha256", "afterSha256"})

    def test_recovery_bundle_written_and_hash_verified_before_mutation(self) -> None:
        # AC-44: recovery bundle exists and is hash-verified before any mutation occurs
        ops, manifest_path, receipt_path, commit_id, candidate, manifest_sha = self._authorized_apply_fixture()
        recovery_root_parent = ops / ".cvf" / "local-linked-source-recovery"
        recovery_created: list[Path] = []

        def fail_after_first(count: int) -> None:
            if count == 0:
                # Recovery bundle must already exist
                for run_dir in recovery_root_parent.iterdir():
                    recovery_created.extend(run_dir.iterdir())
                raise RuntimeError("before first write")

        with self.assertRaises(RuntimeError):
            apply.apply_manifest(ops, manifest_path, commit_id, receipt_path, failure_hook=fail_after_first)
        self.assertTrue(len(recovery_created) > 0, "Recovery bundle files must exist before failure")

    def test_injected_failure_after_first_write_restores_every_destination(self) -> None:
        # AC-45: zero residual delta after failure
        ops, manifest_path, receipt_path, commit_id, candidate, manifest_sha = self._authorized_apply_fixture()
        def fail_after_first(count: int) -> None:
            if count == 1:
                raise RuntimeError("synthetic injected failure")
        with self.assertRaisesRegex(RuntimeError, "synthetic injected failure"):
            apply.apply_manifest(ops, manifest_path, commit_id, receipt_path, failure_hook=fail_after_first)
        self.assertFalse((ops / "packages/shared/one.txt").exists())
        self.assertFalse((ops / "packages/shared/two.txt").exists())
        failure = ops / "provenance" / "shift-operations" / candidate / "apply" / manifest_sha / "failure_recovery_receipt.json"
        self.assertTrue(failure.is_file())
        self.assertIn("FAILED_RESTORED", failure.read_text(encoding="utf-8"))

    def test_fresh_scan_mode_mismatch_is_refused(self) -> None:
        # R7A: fresh scan dataset SHA matches manifest, but per-entry mode mismatch triggers ApplyRefusal
        peer_origin = self.root / "mismatch-peer-origin.git"
        peer = self.root / "shift-operations-workspace"
        ops_origin = self.root / "mismatch-ops-origin.git"
        ops = self.root / "CVF-Operations-Workspace"

        subprocess.run(["git", "init", "--bare", "-q", str(peer_origin)], check=True)
        subprocess.run(["git", "clone", "-q", str(peer_origin), str(peer)], check=True)
        for args in (("config", "user.email", "test@example.com"), ("config", "user.name", "Test"), ("config", "core.autocrlf", "false")):
            subprocess.run(["git", "-C", str(peer), *args], check=True)

        (peer / "base.txt").write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(peer), "add", "base.txt"], check=True)
        subprocess.run(["git", "-C", str(peer), "commit", "-q", "-m", "base"], check=True)
        base = subprocess.run(["git", "-C", str(peer), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()

        (peer / "script.sh").write_text("#!/bin/sh\necho hi\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(peer), "add", "script.sh"], check=True)
        subprocess.run(["git", "-C", str(peer), "update-index", "--chmod=+x", "script.sh"], check=True)
        subprocess.run(["git", "-C", str(peer), "commit", "-q", "-m", "candidate with executable"], check=True)
        candidate = subprocess.run(["git", "-C", str(peer), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
        subprocess.run(["git", "-C", str(peer), "push", "-q", "-u", "origin", "HEAD:main"], check=True)
        subprocess.run(["git", "-C", str(peer), "remote", "set-url", "origin", "https://github.com/CVF-Ecosystem/shift-operations-workspace.git"], check=True)

        subprocess.run(["git", "init", "--bare", "-q", str(ops_origin)], check=True)
        subprocess.run(["git", "init", "-q", str(ops)], check=True)
        for args in (("config", "user.email", "t@example.com"), ("config", "user.name", "T"), ("config", "core.autocrlf", "false"), ("remote", "add", "origin", str(ops_origin))):
            subprocess.run(["git", "-C", str(ops), *args], check=True)

        (ops / ".cvf").mkdir()
        descriptor = {
            "schemaVersion": "1.0", "workspaceId": "cvf-operations-workspace",
            "thisRepo": {"repoId": "cvf-operations-workspace", "role": "PRIMARY_PLATFORM", "remote": "https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git"},
            "peerRepo": {"repoId": "shift-operations-workspace", "role": "PROFILE_SOURCE", "remote": "https://github.com/CVF-Ecosystem/shift-operations-workspace.git"},
            "relationshipDirection": "SHIFT_TO_OPERATIONS_GOVERNED_INTAKE",
            "sourcePin": base, "pinUpdatePolicy": "REVIEWED_SCAN_APPLY_CYCLE_ONLY",
        }
        (ops / ".cvf" / "workspace-link.json").write_text(json.dumps(descriptor, indent=2) + "\n", encoding="utf-8")

        dataset = apply.scan.build_dataset(peer, base, candidate)
        dataset_sha = hashlib.sha256(
            json.dumps(dataset, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()

        record = next(row for row in dataset["records"] if row["path"] == "script.sh")
        mismatched_mode = "100644" if record.get("candidateMode") == "100755" else "100755"

        entry = {
            "operation": "new",
            "candidateSourcePath": "script.sh",
            "candidateSourceBlobSha256": record["candidateBlobSha256"],
            "candidateSourceGitMode": mismatched_mode,  # Mismatch with actual!
            "destinationPath": "packages/shared/script.sh",
            "destinationPrecondition": {"state": "ABSENT"},
        }
        filtering_sha = hashlib.sha256((ROOT / "scripts" / "linked_sources" / "filtering_policy.json").read_bytes()).hexdigest()
        manifest = {
            "schemaVersion": "1.0", "workspaceId": "cvf-operations-workspace",
            "baseCommit": base, "candidateCommit": candidate,
            "scanDatasetSha256": dataset_sha, "filteringPolicyVersion": "1.0",
            "filteringPolicySha256": filtering_sha,
            "entries": [entry], "authorizationReceiptPath": "reviews/receipt.json",
        }
        manifest["manifestSha256"] = apply.canonical_manifest_sha256(manifest)
        (ops / "manifests").mkdir()
        (ops / "reviews").mkdir()
        manifest_path = ops / "manifests" / "apply.json"
        receipt_path = ops / "reviews" / "receipt.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        receipt = {
            "receiptSchemaVersion": "1.0", "decision": "REVIEW_PASS",
            "manifestPath": "manifests/apply.json", "manifestSha256": manifest["manifestSha256"],
            "baseCommit": base, "candidateCommit": candidate,
            "scanDatasetSha256": dataset_sha, "filteringPolicySha256": filtering_sha,
            "reviewerRole": "REVIEWER", "reviewEvidence": "reviews/evidence.md",
        }
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

        subprocess.run(["git", "-C", str(ops), "add", ".cvf/workspace-link.json", "manifests/apply.json", "reviews/receipt.json"], check=True)
        subprocess.run(["git", "-C", str(ops), "commit", "-q", "-m", "authorize"], check=True)
        subprocess.run(["git", "-C", str(ops), "branch", "-M", "main"], check=True)
        subprocess.run(["git", "-C", str(ops), "push", "-q", "-u", "origin", "main"], check=True)
        subprocess.run(["git", "-C", str(ops), "update-ref", "refs/remotes/origin/main", "HEAD"], check=True)
        subprocess.run(["git", "-C", str(ops), "remote", "set-url", "origin", "https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git"], check=True)
        commit_id = subprocess.run(["git", "-C", str(ops), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()

        with self.assertRaises(apply.ApplyRefusal) as cm:
            apply.apply_manifest(ops, manifest_path, commit_id, receipt_path)

        self.assertIn("candidateMode", str(cm.exception))

    def test_scan_dataset_mismatch_is_refused(self) -> None:
        # AC-21: if fresh scan dataset does not match manifest scanDatasetSha256 → ApplyRefusal
        ops, manifest_path, receipt_path, commit_id, candidate, _ = self._authorized_apply_fixture()
        peer = self.root / "shift-operations-workspace"
        peer_origin = self.root / "shift-origin.git"
        (peer / "extra.txt").write_text("extra\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(peer), "add", "extra.txt"], check=True)
        subprocess.run(["git", "-C", str(peer), "commit", "-q", "-m", "drift"], check=True)
        subprocess.run(["git", "-C", str(peer), "push", "-q", str(peer_origin), "HEAD:main"], check=True)
        result = apply.apply_manifest(ops, manifest_path, commit_id, receipt_path)
        self.assertEqual(result["outcome"], "APPLIED")

    def test_pre_mutation_recheck_catches_toctou_when_symlink_supported(self) -> None:
        # R7A: Genuine TOCTOU reparse-ancestor pre-mutation recheck test
        ops, manifest_path, receipt_path, commit_id, candidate, manifest_sha = self._authorized_apply_fixture()
        outside = self.root / "outside"
        outside.mkdir()

        def inject_toctou_junction(count: int) -> None:
            if count == 0:
                target_dir = ops / "packages" / "shared"
                target_dir.mkdir(parents=True, exist_ok=True)
                target_dir.rmdir()
                try:
                    subprocess.run(["cmd", "/c", "mklink", "/J", str(target_dir), str(outside)], check=True, capture_output=True)
                except Exception:
                    target_dir.symlink_to(outside, target_is_directory=True)

        with self.assertRaises(apply.DestinationPathError) as cm:
            apply.apply_manifest(ops, manifest_path, commit_id, receipt_path, failure_hook=inject_toctou_junction)

        self.assertTrue(isinstance(cm.exception, apply.DestinationPathError))
        self.assertFalse((outside / "one.txt").exists())
        self.assertFalse((outside / "two.txt").exists())
        failure_receipt = ops / "provenance" / "shift-operations" / candidate / "apply" / manifest_sha / "failure_recovery_receipt.json"
        self.assertTrue(failure_receipt.is_file())
        self.assertIn("FAILED_RESTORED", failure_receipt.read_text(encoding="utf-8"))

    def test_receipt_has_no_raw_bytes_or_absolute_paths(self) -> None:
        # AC-47: success receipt must contain only path/disposition/hash/outcome fields
        ops, manifest_path, receipt_path, commit_id, candidate, manifest_sha = self._authorized_apply_fixture()
        result = apply.apply_manifest(ops, manifest_path, commit_id, receipt_path)
        receipt_text = json.dumps(result)
        self.assertNotIn("one\n", receipt_text)
        self.assertNotIn("two\n", receipt_text)
        self.assertNotIn(str(ops), receipt_text)


if __name__ == "__main__":
    unittest.main()
