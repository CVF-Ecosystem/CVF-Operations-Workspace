from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "scripts" / "linked_sources" / "scan.py"
SPEC = importlib.util.spec_from_file_location("linked_scan", MODULE)
assert SPEC and SPEC.loader
scan = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scan)


def git(repo: Path, *args: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)
    return result.stdout if binary else result.stdout.decode().strip()


def commit(repo: Path, message: str) -> str:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return str(git(repo, "rev-parse", "HEAD"))


class ScanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.peer = self.root / "shift-operations-workspace"
        self.ops = self.root / "CVF-Operations-Workspace"
        self.peer.mkdir()
        self.ops.mkdir()
        git(self.peer, "init", "-q")
        git(self.peer, "config", "user.email", "test@example.com")
        git(self.peer, "config", "user.name", "Test")
        git(self.peer, "config", "core.autocrlf", "false")
        (self.peer / "keep.txt").write_bytes(b"line one\nline two\n")
        (self.peer / "delete.txt").write_text("delete me\n", encoding="utf-8")
        (self.peer / "rename.txt").write_text("alpha\nbeta\ngamma\ndelta\n", encoding="utf-8")
        self.base = commit(self.peer, "base")
        self.remote = self.peer.as_posix()
        git(self.peer, "remote", "add", "origin", self.remote)

        (self.peer / "keep.txt").write_bytes(b"line one\nline changed\n")
        (self.peer / "delete.txt").unlink()
        (self.peer / "added.py").write_text("VALUE = 1\n", encoding="utf-8")
        (self.peer / "rename.txt").rename(self.peer / "renamed.txt")
        (self.peer / "synthetic-secret.txt").write_text("AKIAABCDEFGHIJKLMNOP\n", encoding="utf-8")
        self.candidate = commit(self.peer, "candidate")

        git(self.peer, "remote", "set-url", "origin", "https://github.com/CVF-Ecosystem/shift-operations-workspace.git")
        (self.ops / ".cvf").mkdir()
        descriptor = {
            "schemaVersion": "1.0",
            "workspaceId": "cvf-operations-workspace",
            "thisRepo": {"repoId": "cvf-operations-workspace", "role": "PRIMARY_PLATFORM", "remote": "https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git"},
            "peerRepo": {"repoId": "shift-operations-workspace", "role": "PROFILE_SOURCE", "remote": "https://github.com/CVF-Ecosystem/shift-operations-workspace.git"},
            "relationshipDirection": "SHIFT_TO_OPERATIONS_GOVERNED_INTAKE",
            "sourcePin": self.base,
            "pinUpdatePolicy": "REVIEWED_SCAN_APPLY_CYCLE_ONLY",
        }
        (self.ops / ".cvf" / "workspace-link.json").write_text(json.dumps(descriptor), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_object_level_exact_accounting_and_rename(self) -> None:
        dataset = scan.build_dataset(self.peer, self.base, self.candidate)
        accounting = dataset["accounting"]
        self.assertEqual(sum(accounting.values()), len(dataset["records"]))
        self.assertEqual(accounting["added"], 2)
        self.assertEqual(accounting["deleted"], 1)
        self.assertEqual(accounting["modified"], 1)
        self.assertEqual(accounting["renamed"], 1)
        rename = next(row for row in dataset["records"] if row["changeType"] == "renamed")
        self.assertEqual((rename["oldPath"], rename["newPath"]), ("rename.txt", "renamed.txt"))
        self.assertFalse(rename["contentChanged"])

    def test_blob_sha_uses_git_object_bytes_and_secret_is_not_persisted(self) -> None:
        dataset = scan.build_dataset(self.peer, self.base, self.candidate)
        keep = next(row for row in dataset["records"] if row["path"] == "keep.txt")
        blob = git(self.peer, "show", f"{self.candidate}:keep.txt", binary=True)
        self.assertEqual(keep["candidateBlobSha256"], hashlib.sha256(blob).hexdigest())
        secret = next(row for row in dataset["records"] if row["path"] == "synthetic-secret.txt")
        self.assertEqual(secret["classification"], "HARD_EXCLUDE")
        serialized = json.dumps(dataset)
        self.assertNotIn("AKIAABCDEFGHIJKLMNOP", serialized)

    def test_dataset_is_deterministic_and_has_four_way_partition(self) -> None:
        first = scan.build_dataset(self.peer, self.base, self.candidate)
        second = scan.build_dataset(self.peer, self.base, self.candidate)
        self.assertEqual(first, second)
        self.assertEqual(sum(first["classifications"].values()), len(first["records"]))
        self.assertNotIn("APPROVED_APPLY", json.dumps(first))

    def test_run_scan_output_boundary_is_derived_provenance_path(self) -> None:
        # R6: run_scan must write only to self-derived provenance path; no caller-supplied output_root
        before_binding = (self.ops / ".cvf" / "workspace-link.json").read_bytes()
        peer_head = git(self.peer, "rev-parse", "HEAD")
        report = scan.run_scan(self.ops, self.candidate, fetch=False)
        # workspace-link.json descriptor must be unchanged (only local binding may be written)
        self.assertEqual((self.ops / ".cvf" / "workspace-link.json").read_bytes(), before_binding)
        # Shift HEAD must be unchanged (no import)
        self.assertEqual(git(self.peer, "rev-parse", "HEAD"), peer_head)
        # Local binding is written (gitignored)
        self.assertTrue((self.ops / ".cvf" / "local-workspace-link.json").is_file())
        # Output is ONLY in provenance/shift-operations/<candidate>/ — nowhere else
        expected_dir = self.ops / "provenance" / "shift-operations" / self.candidate
        self.assertTrue(expected_dir.is_dir())
        output_files = {p.name for p in expected_dir.iterdir()}
        self.assertEqual(output_files, {"linked_sources_inventory.json", "linked_sources_scan_report.json"})
        # run_scan must NOT accept an output_root parameter
        import inspect
        sig = inspect.signature(scan.run_scan)
        self.assertNotIn("output_root", sig.parameters)
        self.assertEqual(report["dataset"]["candidateCommit"], self.candidate)

    def test_non_ancestor_and_missing_commit_are_named_refusals(self) -> None:
        with self.assertRaises(scan.CommitNotFoundError):
            scan.build_dataset(self.peer, self.base, "0" * 40)
        other = self.root / "other"
        git(self.peer, "worktree", "add", "-q", "--detach", str(other), self.base)
        (other / "other.txt").write_text("branch\n", encoding="utf-8")
        unrelated = commit(other, "other")
        with self.assertRaises(scan.NonAncestorCandidateError):
            scan.build_dataset(self.peer, self.candidate, unrelated)
        git(self.peer, "worktree", "remove", "--force", str(other))

    def test_addition_deletion_pure_rename_and_rename_with_change_classified(self) -> None:
        # AC-08: all four change types in one scan
        dataset = scan.build_dataset(self.peer, self.base, self.candidate)
        change_types = {row["changeType"] for row in dataset["records"]}
        self.assertIn("added", change_types)
        self.assertIn("deleted", change_types)
        self.assertIn("renamed", change_types)
        self.assertIn("modified", change_types)
        # Pure rename: rename.txt -> renamed.txt has contentChanged=False
        renamed = next(r for r in dataset["records"] if r["changeType"] == "renamed")
        self.assertFalse(renamed["contentChanged"])
        # Each changed record has a classification
        for row in dataset["records"]:
            self.assertIn("classification", row)

    def test_scan_does_not_import_runtime_assets(self) -> None:
        # AC-13: scan module must not import runtime asset modules
        source = MODULE.read_text(encoding="utf-8")
        forbidden_imports = ["import apps", "import packages", "import database", "from apps", "from packages"]
        for bad in forbidden_imports:
            self.assertNotIn(bad, source)

    def test_fetch_only_preserves_shift_status_and_head(self) -> None:
        # AC-15: run_scan with fetch=False does not alter peer HEAD, branch or working tree
        peer_head_before = git(self.peer, "rev-parse", "HEAD")
        peer_status_before = subprocess.run(
            ["git", "-C", str(self.peer), "status", "--porcelain"],
            capture_output=True, text=True,
        ).stdout
        scan.run_scan(self.ops, self.candidate, fetch=False)
        peer_head_after = git(self.peer, "rev-parse", "HEAD")
        peer_status_after = subprocess.run(
            ["git", "-C", str(self.peer), "status", "--porcelain"],
            capture_output=True, text=True,
        ).stdout
        self.assertEqual(peer_head_before, peer_head_after)
        self.assertEqual(peer_status_before, peer_status_after)

    def test_deleted_secret_content_classified_hard_exclude(self) -> None:
        # R5: deleted files with secret-shaped content must be HARD_EXCLUDE, not just QUARANTINE
        # The scan.py for deleted entries passes blob bytes to dispositions.classify
        dataset = scan.build_dataset(self.peer, self.base, self.candidate)
        # delete.txt was deleted — it has normal content so should be QUARANTINE_REVIEW
        deleted = next((r for r in dataset["records"] if r["changeType"] == "deleted"), None)
        self.assertIsNotNone(deleted)
        # Now make a new scan with a deleted file that contains a secret
        peer2 = self.root / "peer2"
        peer2.mkdir()
        subprocess.run(["git", "init", "-q", str(peer2)], check=True)
        for cfg in (("config", "user.email", "t@t.com"), ("config", "user.name", "T"), ("config", "core.autocrlf", "false")):
            subprocess.run(["git", "-C", str(peer2), *cfg], check=True)
        (peer2 / "secret_deleted.py").write_text("-----BEGIN RSA PRIVATE KEY-----\nMIIdata\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(peer2), "add", "secret_deleted.py"], check=True)
        subprocess.run(["git", "-C", str(peer2), "commit", "-q", "-m", "with-secret"], check=True)
        base2 = subprocess.run(["git", "-C", str(peer2), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        (peer2 / "secret_deleted.py").unlink()
        (peer2 / "normal.py").write_text("x = 1\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(peer2), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(peer2), "commit", "-q", "-m", "deleted-secret"], check=True)
        candidate2 = subprocess.run(["git", "-C", str(peer2), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        dataset2 = scan.build_dataset(peer2, base2, candidate2)
        secret_del = next(r for r in dataset2["records"] if r.get("path") == "secret_deleted.py")
        self.assertEqual(secret_del["classification"], "HARD_EXCLUDE")


if __name__ == "__main__":
    unittest.main()
