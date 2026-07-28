from __future__ import annotations

import importlib.util
import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "scripts" / "linked_sources" / "workspace_link.py"
SPEC = importlib.util.spec_from_file_location("workspace_link", MODULE)
assert SPEC and SPEC.loader
workspace_link = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workspace_link)


def _make_git_repo(path: Path, remote_url: str | None = None) -> None:
    """Initialize a minimal git repo with an initial commit."""
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "Test"], check=True)
    subprocess.run(["git", "-C", str(path), "config", "core.autocrlf", "false"], check=True)
    if remote_url:
        subprocess.run(["git", "-C", str(path), "remote", "add", "origin", remote_url], check=True)
    (path / "init.txt").write_text("init\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(path), "add", "init.txt"], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-q", "-m", "init"], check=True)


class WorkspaceLinkTests(unittest.TestCase):
    def test_tracked_descriptor_is_exact_and_portable(self) -> None:
        data = workspace_link.load_descriptor(ROOT / ".cvf" / "workspace-link.json")
        self.assertEqual(data["workspaceId"], "cvf-operations-workspace")
        self.assertEqual(data["thisRepo"]["role"], "PRIMARY_PLATFORM")
        self.assertEqual(data["peerRepo"]["role"], "PROFILE_SOURCE")
        text = json.dumps(data)
        for marker in ("C:\\", "/home/", "/Users/"):
            self.assertNotIn(marker, text)

    def test_named_descriptor_failures(self) -> None:
        original = json.loads((ROOT / ".cvf" / "workspace-link.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "descriptor.json"
            # Wrong workspaceId
            broken = dict(original)
            broken["workspaceId"] = "wrong"
            path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaises(workspace_link.WorkspaceIdMismatchError):
                workspace_link.load_descriptor(path)
            # Wrong peerRepo role
            broken = json.loads(json.dumps(original))
            broken["peerRepo"]["role"] = "PRIMARY_PLATFORM"
            path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaises(workspace_link.RoleMismatchError):
                workspace_link.load_descriptor(path)
            # Wrong thisRepo role
            broken = json.loads(json.dumps(original))
            broken["thisRepo"]["role"] = "PROFILE_SOURCE"
            path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaises(workspace_link.RoleMismatchError):
                workspace_link.load_descriptor(path)
            # Wrong thisRepo.repoId
            broken = json.loads(json.dumps(original))
            broken["thisRepo"]["repoId"] = "wrong-workspace"
            path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaises(workspace_link.RepositoryIdentityMismatchError):
                workspace_link.load_descriptor(path)
            # Wrong peerRepo.repoId (R4A)
            broken = json.loads(json.dumps(original))
            broken["peerRepo"]["repoId"] = "evil-source"
            path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaises(workspace_link.RepositoryIdentityMismatchError):
                workspace_link.load_descriptor(path)
            # Fake Operations remote (R4A)
            broken = json.loads(json.dumps(original))
            broken["thisRepo"]["remote"] = "https://fake.invalid/CVF-Operations-Workspace.git"
            path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaises(workspace_link.RemoteMismatchError):
                workspace_link.load_descriptor(path)
            # Fake Shift remote (R4A)
            broken = json.loads(json.dumps(original))
            broken["peerRepo"]["remote"] = "https://fake.invalid/shift-operations-workspace.git"
            path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaises(workspace_link.RemoteMismatchError):
                workspace_link.load_descriptor(path)
            # Wrong direction
            broken = json.loads(json.dumps(original))
            broken["relationshipDirection"] = "WRONG_DIRECTION"
            path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaises(workspace_link.DirectionMismatchError):
                workspace_link.load_descriptor(path)
            # sourcePin uppercase
            broken = json.loads(json.dumps(original))
            broken["sourcePin"] = broken["sourcePin"].upper()
            path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaises(workspace_link.SourcePinError):
                workspace_link.load_descriptor(path)
            # sourcePin abbreviated
            broken = json.loads(json.dumps(original))
            broken["sourcePin"] = broken["sourcePin"][:8]
            path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaises(workspace_link.SourcePinError):
                workspace_link.load_descriptor(path)

    def test_reciprocal_mismatch_detection(self) -> None:
        # AC-07: reciprocal validation checks both role records
        local = json.loads((ROOT / ".cvf" / "workspace-link.json").read_text(encoding="utf-8"))
        peer = {
            "schemaVersion": "1.0",
            "workspaceId": local["workspaceId"],
            "thisRepo": copy.deepcopy(local["peerRepo"]),
            "peerRepo": copy.deepcopy(local["thisRepo"]),
            "relationshipDirection": local["relationshipDirection"],
        }
        workspace_link.validate_reciprocal(local, peer)
        # Wrong remote on peer's peerRepo
        bad_peer = copy.deepcopy(peer)
        bad_peer["peerRepo"]["remote"] = "https://example.invalid/wrong.git"
        with self.assertRaises(workspace_link.RemoteMismatchError):
            workspace_link.validate_reciprocal(local, bad_peer)
        # Repo-ID mismatch: peer's peerRepo doesn't match local's thisRepo
        bad_peer = copy.deepcopy(peer)
        bad_peer["peerRepo"]["repoId"] = "wrong-id"
        with self.assertRaises(workspace_link.RepositoryIdentityMismatchError):
            workspace_link.validate_reciprocal(local, bad_peer)
        # Direction mismatch
        bad_peer = copy.deepcopy(peer)
        bad_peer["relationshipDirection"] = "WRONG"
        with self.assertRaises(workspace_link.DirectionMismatchError):
            workspace_link.validate_reciprocal(local, bad_peer)
        # Role mismatch: peer's peerRepo.role contradicts local's thisRepo.role
        bad_peer = copy.deepcopy(peer)
        bad_peer["peerRepo"]["role"] = "PROFILE_SOURCE"  # should be PRIMARY_PLATFORM
        with self.assertRaises(workspace_link.RoleMismatchError):
            workspace_link.validate_reciprocal(local, bad_peer)

    def test_local_binding_and_recovery_are_gitignored(self) -> None:
        for path in (".cvf/local-workspace-link.json", ".cvf/local-linked-source-recovery/example.bin"):
            result = subprocess.run(["git", "check-ignore", "-q", path], cwd=ROOT)
            self.assertEqual(result.returncode, 0, path)

    def test_stale_binding_falls_back_to_sibling(self) -> None:
        # AC-04: stale/invalid local binding is silently skipped; sibling is used instead
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            ops = workspace / "CVF-Operations-Workspace"
            peer_origin = workspace / "shift-origin.git"
            peer = workspace / "shift-operations-workspace"
            ops.mkdir(parents=True)
            (ops / ".cvf").mkdir()
            subprocess.run(["git", "init", "--bare", "-q", str(peer_origin)], check=True)
            _make_git_repo(peer, remote_url=str(peer_origin))
            subprocess.run(["git", "-C", str(peer), "push", "-q", "-u", "origin", "HEAD:main"], check=True)
            head = subprocess.run(["git", "-C", str(peer), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
            descriptor = {
                "schemaVersion": "1.0", "workspaceId": "cvf-operations-workspace",
                "thisRepo": {"repoId": "cvf-operations-workspace", "role": "PRIMARY_PLATFORM", "remote": str(ops)},
                "peerRepo": {"repoId": "shift-operations-workspace", "role": "PROFILE_SOURCE", "remote": str(peer_origin)},
                "relationshipDirection": "SHIFT_TO_OPERATIONS_GOVERNED_INTAKE",
                "sourcePin": head, "pinUpdatePolicy": "REVIEWED_SCAN_APPLY_CYCLE_ONLY",
            }
            (ops / ".cvf" / "workspace-link.json").write_text(json.dumps(descriptor), encoding="utf-8")
            # Write a stale binding with wrong workspaceId — must be silently ignored
            stale_binding = {
                "schemaVersion": "1.0",
                "workspaceId": "wrong-workspace",
                "peerRepoId": "shift-operations-workspace",
                "peerLocalPath": "/nonexistent/path",
            }
            (ops / ".cvf" / "local-workspace-link.json").write_text(json.dumps(stale_binding), encoding="utf-8")
            # Should fall back to exact sibling at workspace/shift-operations-workspace
            resolved = workspace_link.resolve_peer(ops, descriptor, fetch=False)
            self.assertEqual(resolved.resolve(), peer.resolve())

    def test_wrong_remote_binding_falls_back(self) -> None:
        # AC-05: local binding pointing to a repo with wrong remote is discarded
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            ops = workspace / "CVF-Operations-Workspace"
            peer_origin = workspace / "shift-origin.git"
            peer = workspace / "shift-operations-workspace"
            wrong_peer = workspace / "wrong-peer"
            ops.mkdir(parents=True)
            (ops / ".cvf").mkdir()
            subprocess.run(["git", "init", "--bare", "-q", str(peer_origin)], check=True)
            _make_git_repo(peer, remote_url=str(peer_origin))
            subprocess.run(["git", "-C", str(peer), "push", "-q", "-u", "origin", "HEAD:main"], check=True)
            head = subprocess.run(["git", "-C", str(peer), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
            # Wrong peer: uses a different remote URL
            wrong_origin = workspace / "wrong-origin.git"
            subprocess.run(["git", "init", "--bare", "-q", str(wrong_origin)], check=True)
            _make_git_repo(wrong_peer, remote_url=str(wrong_origin))
            descriptor = {
                "schemaVersion": "1.0", "workspaceId": "cvf-operations-workspace",
                "thisRepo": {"repoId": "cvf-operations-workspace", "role": "PRIMARY_PLATFORM", "remote": str(ops)},
                "peerRepo": {"repoId": "shift-operations-workspace", "role": "PROFILE_SOURCE", "remote": str(peer_origin)},
                "relationshipDirection": "SHIFT_TO_OPERATIONS_GOVERNED_INTAKE",
                "sourcePin": head, "pinUpdatePolicy": "REVIEWED_SCAN_APPLY_CYCLE_ONLY",
            }
            (ops / ".cvf" / "workspace-link.json").write_text(json.dumps(descriptor), encoding="utf-8")
            # Binding points to wrong_peer (different remote) — should be discarded
            wrong_binding = {
                "schemaVersion": "1.0",
                "workspaceId": "cvf-operations-workspace",
                "peerRepoId": "shift-operations-workspace",
                "peerLocalPath": str(wrong_peer),
            }
            (ops / ".cvf" / "local-workspace-link.json").write_text(json.dumps(wrong_binding), encoding="utf-8")
            # Should fall back to exact sibling
            resolved = workspace_link.resolve_peer(ops, descriptor, fetch=False)
            self.assertEqual(resolved.resolve(), peer.resolve())

    def test_relative_binding_resolves_within_sibling_topology(self) -> None:
        # AC-03: relative peerLocalPath is resolved within workspace topology (sibling of ops)
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            ops = workspace / "CVF-Operations-Workspace"
            peer_origin = workspace / "shift-origin.git"
            peer = workspace / "shift-operations-workspace"
            ops.mkdir(parents=True)
            (ops / ".cvf").mkdir()
            subprocess.run(["git", "init", "--bare", "-q", str(peer_origin)], check=True)
            _make_git_repo(peer, remote_url=str(peer_origin))
            subprocess.run(["git", "-C", str(peer), "push", "-q", "-u", "origin", "HEAD:main"], check=True)
            head = subprocess.run(["git", "-C", str(peer), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
            descriptor = {
                "schemaVersion": "1.0", "workspaceId": "cvf-operations-workspace",
                "thisRepo": {"repoId": "cvf-operations-workspace", "role": "PRIMARY_PLATFORM", "remote": str(ops)},
                "peerRepo": {"repoId": "shift-operations-workspace", "role": "PROFILE_SOURCE", "remote": str(peer_origin)},
                "relationshipDirection": "SHIFT_TO_OPERATIONS_GOVERNED_INTAKE",
                "sourcePin": head, "pinUpdatePolicy": "REVIEWED_SCAN_APPLY_CYCLE_ONLY",
            }
            (ops / ".cvf" / "workspace-link.json").write_text(json.dumps(descriptor), encoding="utf-8")
            # Relative path "shift-operations-workspace" — relative to workspace (parent of ops)
            relative_binding = {
                "schemaVersion": "1.0",
                "workspaceId": "cvf-operations-workspace",
                "peerRepoId": "shift-operations-workspace",
                "peerLocalPath": "shift-operations-workspace",  # relative
            }
            (ops / ".cvf" / "local-workspace-link.json").write_text(json.dumps(relative_binding), encoding="utf-8")
            resolved = workspace_link.resolve_peer(ops, descriptor, fetch=False)
            self.assertEqual(resolved.resolve(), peer.resolve())

    def test_relative_binding_outside_workspace_rejected(self) -> None:
        # R4A: peerLocalPath escaping workspace topology (e.g. ../outside) must return None (discarded)
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            ops = workspace / "CVF-Operations-Workspace"
            peer_origin = workspace / "shift-origin.git"
            peer = workspace / "shift-operations-workspace"
            outside = Path(tmp) / "outside"
            ops.mkdir(parents=True)
            (ops / ".cvf").mkdir()
            subprocess.run(["git", "init", "--bare", "-q", str(peer_origin)], check=True)
            _make_git_repo(peer, remote_url=str(peer_origin))
            _make_git_repo(outside, remote_url=str(peer_origin))
            head = subprocess.run(["git", "-C", str(peer), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
            descriptor = {
                "schemaVersion": "1.0", "workspaceId": "cvf-operations-workspace",
                "thisRepo": {"repoId": "cvf-operations-workspace", "role": "PRIMARY_PLATFORM", "remote": str(ops)},
                "peerRepo": {"repoId": "shift-operations-workspace", "role": "PROFILE_SOURCE", "remote": str(peer_origin)},
                "relationshipDirection": "SHIFT_TO_OPERATIONS_GOVERNED_INTAKE",
                "sourcePin": head, "pinUpdatePolicy": "REVIEWED_SCAN_APPLY_CYCLE_ONLY",
            }
            # Binding trying to escape sibling topology
            for bad_rel in ("../outside", "../../outside", "shift-operations-workspace/subfolder", "wrong-sibling"):
                binding_path = ops / ".cvf" / "local-workspace-link.json"
                binding_data = {
                    "schemaVersion": "1.0",
                    "workspaceId": "cvf-operations-workspace",
                    "peerRepoId": "shift-operations-workspace",
                    "peerLocalPath": bad_rel,
                }
                binding_path.write_text(json.dumps(binding_data), encoding="utf-8")
                res = workspace_link._try_local_binding(binding_path, ops, descriptor)
                self.assertIsNone(res, f"peerLocalPath {bad_rel} must be discarded")

    def test_clone_destination_safety(self) -> None:
        # AC-42: non-empty clone destination is refused
        with tempfile.TemporaryDirectory() as tmp:
            non_empty = Path(tmp) / "non-empty"
            non_empty.mkdir()
            (non_empty / "existing.txt").write_text("existing\n", encoding="utf-8")
            descriptor = {
                "schemaVersion": "1.0", "workspaceId": "cvf-operations-workspace",
                "thisRepo": {"repoId": "cvf-operations-workspace", "role": "PRIMARY_PLATFORM", "remote": "https://example.invalid/ops.git"},
                "peerRepo": {"repoId": "shift-operations-workspace", "role": "PROFILE_SOURCE", "remote": "https://example.invalid/peer.git"},
                "relationshipDirection": "SHIFT_TO_OPERATIONS_GOVERNED_INTAKE",
                "sourcePin": "a" * 40, "pinUpdatePolicy": "REVIEWED_SCAN_APPLY_CYCLE_ONLY",
            }
            ops = Path(tmp) / "ops"
            ops.mkdir()
            with self.assertRaises(workspace_link.UnsafeCloneDestinationError):
                workspace_link.resolve_peer(ops, descriptor, clone_to=non_empty, fetch=False)

    def test_binding_recreated_with_adr_schema(self) -> None:
        # AC-03: after resolve_peer, local binding uses ADR schema (peerLocalPath not peerPath)
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            ops = workspace / "CVF-Operations-Workspace"
            peer_origin = workspace / "shift-origin.git"
            peer = workspace / "shift-operations-workspace"
            ops.mkdir(parents=True)
            (ops / ".cvf").mkdir()
            subprocess.run(["git", "init", "--bare", "-q", str(peer_origin)], check=True)
            _make_git_repo(peer, remote_url=str(peer_origin))
            subprocess.run(["git", "-C", str(peer), "push", "-q", "-u", "origin", "HEAD:main"], check=True)
            head = subprocess.run(["git", "-C", str(peer), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
            descriptor = {
                "schemaVersion": "1.0", "workspaceId": "cvf-operations-workspace",
                "thisRepo": {"repoId": "cvf-operations-workspace", "role": "PRIMARY_PLATFORM", "remote": str(ops)},
                "peerRepo": {"repoId": "shift-operations-workspace", "role": "PROFILE_SOURCE", "remote": str(peer_origin)},
                "relationshipDirection": "SHIFT_TO_OPERATIONS_GOVERNED_INTAKE",
                "sourcePin": head, "pinUpdatePolicy": "REVIEWED_SCAN_APPLY_CYCLE_ONLY",
            }
            (ops / ".cvf" / "workspace-link.json").write_text(json.dumps(descriptor), encoding="utf-8")
            workspace_link.resolve_peer(ops, descriptor, fetch=False)
            binding_path = ops / ".cvf" / "local-workspace-link.json"
            self.assertTrue(binding_path.is_file())
            binding = json.loads(binding_path.read_text(encoding="utf-8"))
            # Must use ADR schema: peerLocalPath not peerPath
            self.assertIn("peerLocalPath", binding)
            self.assertNotIn("peerPath", binding)
            self.assertIn("peerRepoId", binding)
            self.assertEqual(binding["schemaVersion"], "1.0")
            self.assertEqual(binding["workspaceId"], "cvf-operations-workspace")
            self.assertEqual(binding["peerRepoId"], "shift-operations-workspace")

    def test_source_pin_head_reachability_enforced(self) -> None:
        # R10: sourcePin must resolve AND be ancestor-or-equal to peer HEAD
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            ops = workspace / "CVF-Operations-Workspace"
            peer = workspace / "shift-operations-workspace"
            ops.mkdir(parents=True)
            (ops / ".cvf").mkdir()
            (peer / ".cvf").mkdir(parents=True)

            _make_git_repo(peer, remote_url="https://github.com/CVF-Ecosystem/shift-operations-workspace.git")
            commit_a = subprocess.run(
                ["git", "-C", str(peer), "rev-parse", "HEAD"],
                capture_output=True, text=True, check=True,
            ).stdout.strip()

            ops_descriptor = {
                "schemaVersion": "1.0",
                "workspaceId": "cvf-operations-workspace",
                "thisRepo": {"repoId": "cvf-operations-workspace", "role": "PRIMARY_PLATFORM", "remote": "https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git"},
                "peerRepo": {"repoId": "shift-operations-workspace", "role": "PROFILE_SOURCE", "remote": "https://github.com/CVF-Ecosystem/shift-operations-workspace.git"},
                "relationshipDirection": "SHIFT_TO_OPERATIONS_GOVERNED_INTAKE",
                "sourcePin": commit_a,
                "pinUpdatePolicy": "REVIEWED_SCAN_APPLY_CYCLE_ONLY",
            }
            reciprocal_descriptor = {
                "schemaVersion": "1.0",
                "workspaceId": "cvf-operations-workspace",
                "thisRepo": {"repoId": "shift-operations-workspace", "role": "PROFILE_SOURCE", "remote": "https://github.com/CVF-Ecosystem/shift-operations-workspace.git"},
                "peerRepo": {"repoId": "cvf-operations-workspace", "role": "PRIMARY_PLATFORM", "remote": "https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git"},
                "relationshipDirection": "SHIFT_TO_OPERATIONS_GOVERNED_INTAKE",
            }
            (peer / ".cvf" / "workspace-link.json").write_text(json.dumps(reciprocal_descriptor), encoding="utf-8")

            # Positive test: sourcePin == HEAD (commit_a is HEAD)
            workspace_link.validate_peer_repository(peer, ops_descriptor)

            # Positive test: commit_a is ancestor of new HEAD commit_b
            (peer / "second.txt").write_text("second\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(peer), "add", "second.txt"], check=True)
            subprocess.run(["git", "-C", str(peer), "commit", "-q", "-m", "second"], check=True)
            workspace_link.validate_peer_repository(peer, ops_descriptor)

            # Negative test: orphan/unrelated current HEAD
            subprocess.run(["git", "-C", str(peer), "checkout", "-q", "--orphan", "unrelated_branch"], check=True)
            (peer / "orphan.txt").write_text("orphan\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(peer), "add", "orphan.txt"], check=True)
            subprocess.run(["git", "-C", str(peer), "commit", "-q", "-m", "orphan commit"], check=True)

            with self.assertRaises(workspace_link.SourcePinError):
                workspace_link.validate_peer_repository(peer, ops_descriptor)


if __name__ == "__main__":
    unittest.main()
