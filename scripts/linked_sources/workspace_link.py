"""Portable descriptor handling for the Operations/Shift repository link.

Claim boundary: this module validates relationship identity and local clone
resolution only. It does not authorize porting, application, runtime
compatibility, AI governance, or production readiness.

Local binding schema (gitignored .cvf/local-workspace-link.json):
  {
    "schemaVersion": "1.0",
    "workspaceId": "<workspaceId>",
    "peerRepoId": "<peerRepo.repoId>",
    "peerLocalPath": "<absolute or repo-relative path>"
  }

Fallback resolution order (no filesystem search):
  1. Validated local binding (peerLocalPath, absolute or sibling-topology relative)
  2. Exact expected sibling: <operations_root.parent>/<peerRepo.repoId>
  3. Explicit --clone-to or deterministic default clone (sibling)
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


class WorkspaceLinkError(RuntimeError):
    """Base class for named, fail-closed descriptor errors."""


class DescriptorSchemaError(WorkspaceLinkError):
    pass


class WorkspaceIdMismatchError(WorkspaceLinkError):
    pass


class RepositoryIdentityMismatchError(WorkspaceLinkError):
    pass


class RemoteMismatchError(WorkspaceLinkError):
    pass


class RoleMismatchError(WorkspaceLinkError):
    pass


class DirectionMismatchError(WorkspaceLinkError):
    pass


class SourcePinError(WorkspaceLinkError):
    pass


class UnsafeCloneDestinationError(WorkspaceLinkError):
    pass


DESCRIPTOR_KEYS = {
    "schemaVersion",
    "workspaceId",
    "thisRepo",
    "peerRepo",
    "relationshipDirection",
    "sourcePin",
    "pinUpdatePolicy",
}
REPO_KEYS = {"repoId", "role", "remote"}
COMPLEMENTARY_ROLES = {("PRIMARY_PLATFORM", "PROFILE_SOURCE"), ("PROFILE_SOURCE", "PRIMARY_PLATFORM")}

# Expected canonical identities for this operations repository.
_EXPECTED_WORKSPACE_ID = "cvf-operations-workspace"
_EXPECTED_THIS_REPO_ID = "cvf-operations-workspace"
_EXPECTED_PEER_REPO_ID = "shift-operations-workspace"
_EXPECTED_THIS_ROLE = "PRIMARY_PLATFORM"
_EXPECTED_PEER_ROLE = "PROFILE_SOURCE"
_EXPECTED_DIRECTION = "SHIFT_TO_OPERATIONS_GOVERNED_INTAKE"
_EXPECTED_PIN_POLICY = "REVIEWED_SCAN_APPLY_CYCLE_ONLY"
_EXPECTED_THIS_REMOTE = "https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git"
_EXPECTED_PEER_REMOTE = "https://github.com/CVF-Ecosystem/shift-operations-workspace.git"

# Local binding field names (ADR schema)
_LOCAL_BINDING_KEYS = {"schemaVersion", "workspaceId", "peerRepoId", "peerLocalPath"}


def _git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and result.returncode:
        raise WorkspaceLinkError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def load_descriptor(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DescriptorSchemaError(f"descriptor unreadable: {path}") from exc
    if not isinstance(data, dict) or set(data) != DESCRIPTOR_KEYS:
        raise DescriptorSchemaError("descriptor must contain exactly the contracted top-level fields")
    if data.get("schemaVersion") != "1.0" or data.get("workspaceId") != _EXPECTED_WORKSPACE_ID:
        raise WorkspaceIdMismatchError("workspaceId/schemaVersion mismatch")
    if data.get("relationshipDirection") != _EXPECTED_DIRECTION:
        raise DirectionMismatchError("relationshipDirection mismatch")
    if data.get("pinUpdatePolicy") != _EXPECTED_PIN_POLICY:
        raise DescriptorSchemaError("pinUpdatePolicy mismatch")
    for key in ("thisRepo", "peerRepo"):
        if not isinstance(data.get(key), dict) or set(data[key]) != REPO_KEYS:
            raise DescriptorSchemaError(f"{key} must contain exactly repoId, role and remote")
        if not all(isinstance(data[key][field], str) and data[key][field] for field in REPO_KEYS):
            raise DescriptorSchemaError(f"{key} fields must be non-empty strings")
    # Validate canonical identities for this Operations repository
    if data["thisRepo"]["repoId"] != _EXPECTED_THIS_REPO_ID:
        raise RepositoryIdentityMismatchError("thisRepo.repoId does not match expected operations workspace id")
    if data["peerRepo"]["repoId"] != _EXPECTED_PEER_REPO_ID:
        raise RepositoryIdentityMismatchError("peerRepo.repoId does not match expected shift operations workspace id")
    if data["thisRepo"]["role"] != _EXPECTED_THIS_ROLE:
        raise RoleMismatchError(f"thisRepo.role must be {_EXPECTED_THIS_ROLE}")
    if data["peerRepo"]["role"] != _EXPECTED_PEER_ROLE:
        raise RoleMismatchError(f"peerRepo.role must be {_EXPECTED_PEER_ROLE}")
    if data["thisRepo"]["remote"] != _EXPECTED_THIS_REMOTE:
        raise RemoteMismatchError("thisRepo.remote does not match canonical remote URL")
    if data["peerRepo"]["remote"] != _EXPECTED_PEER_REMOTE:
        raise RemoteMismatchError("peerRepo.remote does not match canonical remote URL")
    if (data["thisRepo"]["role"], data["peerRepo"]["role"]) not in COMPLEMENTARY_ROLES:
        raise RoleMismatchError("repository roles are not complementary")
    pin = data.get("sourcePin")
    if not isinstance(pin, str) or len(pin) != 40 or any(c not in "0123456789abcdef" for c in pin):
        raise SourcePinError("sourcePin must be a full lowercase 40-character commit id")
    return data


def validate_reciprocal(local: dict[str, Any], peer: dict[str, Any]) -> None:
    """Validate that the peer descriptor is the exact mirror of the local one.

    Checks both role records: peer.thisRepo must match local.peerRepo and
    peer.peerRepo must match local.thisRepo, including roles on both sides.
    """
    if local["workspaceId"] != peer.get("workspaceId"):
        raise WorkspaceIdMismatchError("peer workspaceId mismatch")
    if local["thisRepo"]["repoId"] != peer.get("peerRepo", {}).get("repoId"):
        raise RepositoryIdentityMismatchError("local thisRepo does not match peer peerRepo")
    if local["peerRepo"]["repoId"] != peer.get("thisRepo", {}).get("repoId"):
        raise RepositoryIdentityMismatchError("local peerRepo does not match peer thisRepo")
    if local["thisRepo"]["remote"] != peer.get("peerRepo", {}).get("remote"):
        raise RemoteMismatchError("local remote does not match peer record")
    if local["peerRepo"]["remote"] != peer.get("thisRepo", {}).get("remote"):
        raise RemoteMismatchError("peer remote does not match local record")
    # Both role pairs must be complementary
    if (local["thisRepo"]["role"], peer.get("thisRepo", {}).get("role")) not in COMPLEMENTARY_ROLES:
        raise RoleMismatchError("reciprocal roles are not complementary")
    # peer.peerRepo.role must mirror local.thisRepo.role
    if peer.get("peerRepo", {}).get("role") != local["thisRepo"]["role"]:
        raise RoleMismatchError("peer peerRepo.role contradicts local thisRepo.role")
    if local["relationshipDirection"] != peer.get("relationshipDirection"):
        raise DirectionMismatchError("reciprocal relationshipDirection mismatch")


def validate_peer_repository(peer_path: Path, descriptor: dict[str, Any]) -> None:
    if _git(peer_path, "remote", "get-url", "origin") != descriptor["peerRepo"]["remote"]:
        raise RemoteMismatchError("resolved peer origin does not match descriptor")
    if subprocess.run(
        ["git", "-C", str(peer_path), "cat-file", "-e", f"{descriptor['sourcePin']}^{{commit}}"],
        capture_output=True,
    ).returncode:
        raise SourcePinError("sourcePin does not resolve in peer history")
    if subprocess.run(
        ["git", "-C", str(peer_path), "merge-base", "--is-ancestor", descriptor["sourcePin"], "HEAD"],
        capture_output=True,
    ).returncode:
        raise SourcePinError("sourcePin is not reachable from peer HEAD")
    reciprocal_path = peer_path / ".cvf" / "workspace-link.json"
    if reciprocal_path.exists():
        peer = json.loads(reciprocal_path.read_text(encoding="utf-8"))
        validate_reciprocal(descriptor, peer)


def _try_local_binding(binding_path: Path, operations_root: Path, descriptor: dict[str, Any]) -> Path | None:
    """Return a valid peer path from the local binding, or None if invalid/stale.

    The binding is silently discarded (not an error) if it has wrong schema,
    wrong workspaceId/peerRepoId, a path that does not exist, or a remote that
    does not match the descriptor. This preserves the fail-safe fallback order.
    """
    if not binding_path.exists():
        return None
    try:
        binding = json.loads(binding_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    # Validate ADR binding schema
    if not isinstance(binding, dict) or set(binding) != _LOCAL_BINDING_KEYS:
        return None
    if binding.get("schemaVersion") != "1.0":
        return None
    if binding.get("workspaceId") != descriptor.get("workspaceId"):
        return None
    if binding.get("peerRepoId") != descriptor["peerRepo"]["repoId"]:
        return None
    raw_path = binding.get("peerLocalPath", "")
    if not isinstance(raw_path, str) or not raw_path:
        return None

    operations_root = operations_root.resolve()
    workspace_container = operations_root.parent
    candidate_path = Path(raw_path)
    if not candidate_path.is_absolute():
        # Relative path: resolve within bounded workspace topology (sibling of operations_root)
        resolved_candidate = (workspace_container / raw_path).resolve()
        try:
            resolved_candidate.relative_to(workspace_container)
        except ValueError:
            return None  # Escapes workspace container (e.g. ../outside)
        expected_sibling = (workspace_container / descriptor["peerRepo"]["repoId"]).resolve()
        if resolved_candidate != expected_sibling:
            return None
        candidate = resolved_candidate
    else:
        candidate = candidate_path.resolve()

    if not candidate.is_dir():
        return None
    # Validate that the remote matches before trusting this binding
    try:
        actual_remote = _git(candidate, "remote", "get-url", "origin")
        if actual_remote != descriptor["peerRepo"]["remote"]:
            return None
    except WorkspaceLinkError:
        return None
    return candidate


def resolve_peer(
    operations_root: Path,
    descriptor: dict[str, Any],
    *,
    clone_to: Path | None = None,
    fetch: bool = True,
) -> Path:
    """Resolve peer via: validated local binding -> exact sibling -> clone.

    No filesystem search is performed. Each step is either deterministic or
    an explicit decision (clone). Stale/invalid/wrong-remote bindings are
    silently skipped and the next fallback is tried.
    """
    operations_root = operations_root.resolve()
    binding_path = operations_root / ".cvf" / "local-workspace-link.json"

    # 1. Validated local binding
    candidate = _try_local_binding(binding_path, operations_root, descriptor)

    # 2. Exact expected sibling
    exact_sibling = operations_root.parent / descriptor["peerRepo"]["repoId"]
    if candidate is None and exact_sibling.is_dir():
        candidate = exact_sibling

    # 3. Clone to explicit or deterministic default
    if candidate is None:
        destination = (clone_to or exact_sibling).resolve()
        if destination.exists() and any(destination.iterdir()):
            raise UnsafeCloneDestinationError("refusing non-empty clone destination")
        destination.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["git", "clone", "--no-checkout", descriptor["peerRepo"]["remote"], str(destination)],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise UnsafeCloneDestinationError(result.stderr.strip() or "peer clone failed")
        candidate = destination

    validate_peer_repository(candidate, descriptor)
    if fetch:
        _git(candidate, "fetch", "origin", "--prune")

    # Write binding with ADR-correct schema
    binding_path.write_text(
        json.dumps(
            {
                "schemaVersion": "1.0",
                "workspaceId": descriptor["workspaceId"],
                "peerRepoId": descriptor["peerRepo"]["repoId"],
                "peerLocalPath": str(candidate.resolve()),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return candidate
