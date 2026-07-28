"""Manifest-gated application for reviewed linked-source changes.

Claim boundary: this module enforces a reviewed manifest and all-or-restore
mechanics. It does not decide PORT_AS_IS/ADAPT/REIMPLEMENT, validate Shift
runtime behavior, prove AI governance, or establish production readiness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import uuid
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import scan  # noqa: E402
import workspace_link  # noqa: E402


class ApplyRefusal(RuntimeError):
    pass


class ManifestSchemaError(ApplyRefusal):
    pass


class AuthorizationError(ApplyRefusal):
    pass


class DestinationPathError(ApplyRefusal):
    pass


class DestinationDriftError(ApplyRefusal):
    pass


TOP_KEYS = {
    "schemaVersion",
    "workspaceId",
    "baseCommit",
    "candidateCommit",
    "scanDatasetSha256",
    "filteringPolicyVersion",
    "filteringPolicySha256",
    "entries",
    "authorizationReceiptPath",
    "manifestSha256",
}
# Fields that would indicate a circular or self-declared authorization model
# are explicitly disallowed at the top level.
_FORBIDDEN_TOP_FIELDS = {"authorizationCommit", "status", "approval", "approvalStatus", "reviewPass"}

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
PROTECTED_PREFIXES = (
    ".git/",
    ".cvf/",
    "cvf_session/",
    "docs/catalog/",
    "docs/decisions/",
    "docs/specs/",
    "docs/work_orders/",
    "docs/reviews/",
    "docs/roadmaps/",
    "provenance/",
)
PROTECTED_EXACT = {
    "agents.md",
    "implementation_status.json",
    "cvf_session_memory.md",
    "docs/index.md",
}


def canonical_manifest_sha256(manifest: dict[str, Any]) -> str:
    value = dict(manifest)
    value.pop("manifestSha256", None)
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git(repo: Path, *args: str, binary: bool = False, check: bool = True) -> bytes | str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if check and result.returncode:
        raise AuthorizationError(result.stderr.decode("utf-8", "replace").strip() or f"git {' '.join(args)} failed")
    return result.stdout if binary else result.stdout.decode("utf-8", "replace").strip()


def _require_hash(value: Any, field: str, pattern: re.Pattern[str] = HEX64) -> None:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ManifestSchemaError(f"{field} is not a canonical hash")


def _validate_precondition(value: Any, expected: str) -> None:
    if not isinstance(value, dict) or value.get("state") != expected:
        raise ManifestSchemaError(f"precondition must be {expected}")
    if expected == "ABSENT" and set(value) != {"state"}:
        raise ManifestSchemaError("ABSENT precondition has unknown fields")
    if expected == "PRESENT":
        if set(value) != {"state", "sha256"}:
            raise ManifestSchemaError("PRESENT precondition requires only state and sha256")
        _require_hash(value["sha256"], "precondition.sha256")


def _safe_relative(path_text: str, operations_root: Path) -> Path:
    if not isinstance(path_text, str) or not path_text:
        raise DestinationPathError("destinationPath must be a non-empty string")
    if "\0" in path_text or ":" in path_text:
        raise DestinationPathError("destinationPath contains invalid characters")
    if path_text.startswith(("/", "\\", "//", "\\\\")) or re.match(r"^[A-Za-z]:", path_text):
        raise DestinationPathError("destinationPath must not be an absolute, drive, or UNC path")
    if "\\" in path_text:
        raise DestinationPathError("destinationPath must be POSIX (slash-separated)")

    posix = path_text
    parts = posix.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise DestinationPathError("destinationPath contains empty, dot, or traversal components")
    if any(part.split(".")[0].upper() in RESERVED for part in parts):
        raise DestinationPathError("destinationPath contains a reserved device name")

    folded = posix.lower()
    if folded.startswith(PROTECTED_PREFIXES) or folded in PROTECTED_EXACT:
        raise DestinationPathError(f"destinationPath '{path_text}' falls within protected root boundary")

    root = operations_root.resolve()
    target = (root / posix).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise DestinationPathError(f"destinationPath '{path_text}' escapes operations root") from exc

    # Symlink/reparse point check on target and all parent ancestors relative to operations_root
    current = target
    while current != root and current.parent != current:
        is_j = getattr(current, "is_junction", lambda: False)()
        if current.is_symlink() or is_j or os.path.islink(current):
            raise DestinationPathError(f"destinationPath component '{current}' is a symlink/reparse ancestor")
        current = current.parent

    return target


def _check(path: Path, precondition: dict[str, Any]) -> None:
    expected_state = precondition["state"]
    if expected_state == "ABSENT":
        if path.exists():
            raise DestinationDriftError(f"destination '{path}' unexpectedly exists")
        return
    if not path.is_file():
        raise DestinationDriftError(f"destination '{path}' does not exist as a regular file")
    data = path.read_bytes()
    if _sha(data) != precondition["sha256"]:
        raise DestinationDriftError(f"destination '{path}' content hash mismatch")


def _destinations(manifest: dict[str, Any], operations_root: Path) -> dict[int, list[Path]]:
    mapping: dict[int, list[Path]] = {}
    normalized_seen: dict[str, str] = {}
    for index, entry in enumerate(manifest["entries"]):
        operation = entry["operation"]
        paths: list[Path] = []
        raw_paths: list[str] = []
        if operation == "renamed":
            raw_paths = [entry["oldDestinationPath"], entry["newDestinationPath"]]
        else:
            raw_paths = [entry["destinationPath"]]
        for raw in raw_paths:
            target = _safe_relative(raw, operations_root)
            norm = unicodedata.normalize("NFC", raw).lower()
            if norm in normalized_seen:
                raise DestinationPathError(f"duplicate destination detected for '{raw}'")
            normalized_seen[norm] = raw
            paths.append(target)
        mapping[index] = paths
    return mapping


def _validate_canonical_receipt_path(path_text: str) -> str:
    """Validate that path_text is a strictly canonical repository-relative POSIX path.
    Fail-closed rejection for absolute, drive, UNC, leading slash/backslash, empty component,
    dot, parent traversal, mixed-separator traversal, NUL, ADS/colon, empty string.
    """
    if not isinstance(path_text, str) or not path_text:
        raise ManifestSchemaError("authorizationReceiptPath must be a non-empty string")
    if "\0" in path_text:
        raise ManifestSchemaError("authorizationReceiptPath must not contain NUL byte")
    if ":" in path_text:
        raise ManifestSchemaError("authorizationReceiptPath must not contain colon or ADS")
    if path_text.startswith(("/", "\\", "//", "\\\\")) or re.match(r"^[A-Za-z]:", path_text):
        raise ManifestSchemaError("authorizationReceiptPath must not be absolute, drive, or UNC path")
    if "\\" in path_text and "/" in path_text:
        raise ManifestSchemaError("authorizationReceiptPath must not use mixed separators")
    if "\\" in path_text:
        raise ManifestSchemaError("authorizationReceiptPath must be POSIX (slash-separated)")
    parts = path_text.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ManifestSchemaError("authorizationReceiptPath must not contain empty, dot, or traversal components")
    return path_text


def validate_manifest(manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ManifestSchemaError("manifest must be an object")
    # Non-circular model: reject any self-declared authorization/status/approval field
    forbidden = set(manifest) & _FORBIDDEN_TOP_FIELDS
    if forbidden:
        raise ManifestSchemaError(f"manifest must not contain self-declared authorization fields: {sorted(forbidden)}")
    if set(manifest) != TOP_KEYS:
        raise ManifestSchemaError("manifest has missing or unknown top-level fields")
    if manifest["schemaVersion"] != "1.0" or manifest["workspaceId"] != "cvf-operations-workspace":
        raise ManifestSchemaError("manifest identity mismatch")
    _require_hash(manifest["baseCommit"], "baseCommit", HEX40)
    _require_hash(manifest["candidateCommit"], "candidateCommit", HEX40)
    for field in ("scanDatasetSha256", "filteringPolicySha256", "manifestSha256"):
        _require_hash(manifest[field], field)
    if manifest["filteringPolicyVersion"] != "1.0":
        raise ManifestSchemaError("filteringPolicyVersion mismatch")
    _validate_canonical_receipt_path(manifest.get("authorizationReceiptPath", ""))
    if not isinstance(manifest["entries"], list) or not manifest["entries"]:
        raise ManifestSchemaError("entries must be a non-empty array")
    for entry in manifest["entries"]:
        if not isinstance(entry, dict):
            raise ManifestSchemaError("entry must be an object")
        operation = entry.get("operation")
        if operation in {"new", "modified"}:
            expected = {"operation", "candidateSourcePath", "candidateSourceBlobSha256", "candidateSourceGitMode", "destinationPath", "destinationPrecondition"}
            if set(entry) != expected:
                raise ManifestSchemaError(f"{operation} entry shape mismatch")
            _require_hash(entry["candidateSourceBlobSha256"], "candidateSourceBlobSha256")
            if entry["candidateSourceGitMode"] not in {"100644", "100755"}:
                raise ManifestSchemaError("unsafe candidateSourceGitMode")
            _validate_precondition(entry["destinationPrecondition"], "ABSENT" if operation == "new" else "PRESENT")
        elif operation == "deleted":
            expected = {"operation", "baseSourcePath", "baseBlobSha256", "destinationPath", "destinationPrecondition"}
            if set(entry) != expected:
                raise ManifestSchemaError("deleted entry shape mismatch")
            _require_hash(entry["baseBlobSha256"], "baseBlobSha256")
            _validate_precondition(entry["destinationPrecondition"], "PRESENT")
        elif operation == "renamed":
            expected = {
                "operation", "oldSourcePath", "newSourcePath", "baseBlobSha256",
                "candidateBlobSha256", "candidateSourceGitMode", "oldDestinationPath",
                "newDestinationPath", "contentChanged", "oldDestinationPrecondition",
                "newDestinationPrecondition",
            }
            if set(entry) != expected:
                raise ManifestSchemaError("renamed entry shape mismatch")
            _require_hash(entry["baseBlobSha256"], "baseBlobSha256")
            _require_hash(entry["candidateBlobSha256"], "candidateBlobSha256")
            if entry["candidateSourceGitMode"] not in {"100644", "100755"} or not isinstance(entry["contentChanged"], bool):
                raise ManifestSchemaError("renamed entry mode/contentChanged mismatch")
            _validate_precondition(entry["oldDestinationPrecondition"], "PRESENT")
            _validate_precondition(entry["newDestinationPrecondition"], "ABSENT")
        else:
            raise ManifestSchemaError("unknown operation")
    if canonical_manifest_sha256(manifest) != manifest["manifestSha256"]:
        raise ManifestSchemaError("manifestSha256 mismatch")
    return manifest



def verify_authorization(
    operations_root: Path,
    manifest_path: Path,
    authorization_commit: str,
    receipt_path: Path,
) -> dict[str, Any]:
    # R1: authorization_commit must be a lowercase full SHA-40 — reject symbolic refs,
    # abbreviated hashes, uppercase letters, and any non-hex character.
    if not isinstance(authorization_commit, str) or not HEX40.fullmatch(authorization_commit):
        raise AuthorizationError(
            "authorization_commit must be a lowercase full 40-character hex SHA; "
            "symbolic refs (e.g. 'origin/main'), abbreviated hashes and uppercase are not accepted"
        )
    if subprocess.run(
        ["git", "-C", str(operations_root), "merge-base", "--is-ancestor", authorization_commit, "origin/main"],
        capture_output=True,
    ).returncode:
        raise AuthorizationError("authorization commit is not reachable from origin/main")

    try:
        receipt_rel = receipt_path.resolve().relative_to(operations_root.resolve()).as_posix()
    except ValueError as exc:
        raise AuthorizationError("receipt_path resolves outside Operations repository root") from exc

    try:
        _validate_canonical_receipt_path(receipt_rel)
    except ManifestSchemaError as exc:
        raise AuthorizationError(f"CLI --authorization-receipt path is invalid: {exc}") from exc

    try:
        manifest_rel = manifest_path.resolve().relative_to(operations_root.resolve()).as_posix()
    except ValueError as exc:
        raise AuthorizationError("manifest_path resolves outside Operations repository root") from exc

    committed_manifest = _git(operations_root, "show", f"{authorization_commit}:{manifest_rel}", binary=True)
    committed_receipt = _git(operations_root, "show", f"{authorization_commit}:{receipt_rel}", binary=True)
    if committed_manifest != manifest_path.read_bytes() or committed_receipt != receipt_path.read_bytes():
        raise AuthorizationError("working manifest/receipt differs from authorization commit")

    committed_parsed = validate_manifest(json.loads(committed_manifest.decode("utf-8")))

    # R1: validate receipt schema completely
    receipt = json.loads(committed_receipt.decode("utf-8"))
    required_receipt_keys = {
        "receiptSchemaVersion", "decision", "manifestPath", "manifestSha256",
        "baseCommit", "candidateCommit", "scanDatasetSha256",
        "filteringPolicySha256", "reviewerRole", "reviewEvidence",
    }
    if not isinstance(receipt, dict) or set(receipt) != required_receipt_keys:
        raise AuthorizationError("independent review receipt has missing or unknown fields")
    if receipt.get("receiptSchemaVersion") != "1.0":
        raise AuthorizationError("receipt receiptSchemaVersion must be '1.0'")
    if receipt.get("decision") != "REVIEW_PASS":
        raise AuthorizationError("receipt decision must be REVIEW_PASS")
    if receipt.get("reviewerRole") != "REVIEWER":
        raise AuthorizationError("receipt reviewerRole must be 'REVIEWER'")
    if not isinstance(receipt.get("reviewEvidence"), str) or not receipt["reviewEvidence"].strip():
        raise AuthorizationError("receipt reviewEvidence must be a non-empty string")

    manifest = validate_manifest(json.loads(manifest_path.read_text(encoding="utf-8")))

    # R1A: CLI receipt path must match manifest.authorizationReceiptPath exactly after canonical validation
    manifest_auth_path = _validate_canonical_receipt_path(manifest["authorizationReceiptPath"])
    if receipt_rel != manifest_auth_path:
        raise AuthorizationError(
            f"--authorization-receipt path '{receipt_rel}' does not match "
            f"manifest.authorizationReceiptPath '{manifest_auth_path}'"
        )

    pairs = (
        ("manifestPath", manifest_rel),
        ("manifestSha256", manifest["manifestSha256"]),
        ("baseCommit", manifest["baseCommit"]),
        ("candidateCommit", manifest["candidateCommit"]),
        ("scanDatasetSha256", manifest["scanDatasetSha256"]),
        ("filteringPolicySha256", manifest["filteringPolicySha256"]),
    )
    if any(receipt.get(field) != expected for field, expected in pairs):
        raise AuthorizationError("receipt does not bind the exact manifest")
    if canonical_manifest_sha256(committed_parsed) != receipt["manifestSha256"]:
        raise AuthorizationError("committed manifest canonical digest mismatch")
    return manifest


def _source_bytes(peer: Path, commit: str, path: str) -> bytes:
    return _git(peer, "show", f"{commit}:{path}", binary=True)  # type: ignore[return-value]


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".cvf-apply-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def _check_entry_against_fresh_scan(entry: dict[str, Any], record: dict[str, Any]) -> None:
    """R2: per-field binding between manifest entry and fresh scan record.

    Rejects each field mismatch individually with a specific error message.
    """
    operation = entry["operation"]
    change_type_map = {"new": "added", "modified": "modified", "deleted": "deleted", "renamed": "renamed"}
    expected_change = change_type_map[operation]
    if record.get("changeType") != expected_change:
        raise ApplyRefusal(
            f"scan record changeType '{record.get('changeType')}' does not match manifest operation '{operation}' (expected '{expected_change}')"
        )

    if operation in {"new", "modified"}:
        if record.get("candidateBlobSha256") != entry["candidateSourceBlobSha256"]:
            raise ApplyRefusal("fresh scan candidateBlobSha256 does not match manifest candidateSourceBlobSha256")
        if record.get("candidateMode") != entry["candidateSourceGitMode"]:
            raise ApplyRefusal(
                f"fresh scan candidateMode '{record.get('candidateMode')}' does not match "
                f"manifest candidateSourceGitMode '{entry['candidateSourceGitMode']}'"
            )
        if record.get("path") != entry["candidateSourcePath"]:
            raise ApplyRefusal("fresh scan path does not match manifest candidateSourcePath")
    elif operation == "deleted":
        if record.get("baseBlobSha256") != entry["baseBlobSha256"]:
            raise ApplyRefusal("fresh scan baseBlobSha256 does not match manifest baseBlobSha256")
        if record.get("path") != entry["baseSourcePath"]:
            raise ApplyRefusal("fresh scan path does not match manifest baseSourcePath")
        # Deleted entries must NOT have a candidate blob in the manifest
        if "candidateSourceBlobSha256" in entry:
            raise ApplyRefusal("deleted manifest entry must not contain candidateSourceBlobSha256")
    elif operation == "renamed":
        if record.get("oldPath") != entry["oldSourcePath"]:
            raise ApplyRefusal("fresh scan oldPath does not match manifest oldSourcePath")
        if record.get("newPath") != entry["newSourcePath"]:
            raise ApplyRefusal("fresh scan newPath does not match manifest newSourcePath")
        if record.get("baseBlobSha256") != entry["baseBlobSha256"]:
            raise ApplyRefusal("fresh scan baseBlobSha256 does not match manifest baseBlobSha256")
        if record.get("candidateBlobSha256") != entry["candidateBlobSha256"]:
            raise ApplyRefusal("fresh scan candidateBlobSha256 does not match manifest candidateBlobSha256")
        if record.get("candidateMode") != entry["candidateSourceGitMode"]:
            raise ApplyRefusal(
                f"fresh scan candidateMode '{record.get('candidateMode')}' does not match "
                f"manifest candidateSourceGitMode '{entry['candidateSourceGitMode']}'"
            )
        if record.get("contentChanged") != entry["contentChanged"]:
            raise ApplyRefusal("fresh scan contentChanged does not match manifest contentChanged")

    # Classification must permit application
    if record.get("classification") in {"HARD_EXCLUDE", "PROTECTED_SOURCE_ONLY"}:
        raise ApplyRefusal(
            f"manifest entry is classified '{record.get('classification')}' and cannot be applied"
        )


def apply_manifest(
    operations_root: Path,
    manifest_path: Path,
    authorization_commit: str,
    authorization_receipt: Path,
    *,
    failure_hook: Callable[[int], None] | None = None,
) -> dict[str, Any]:
    operations_root = operations_root.resolve()
    if not manifest_path.is_file() or not authorization_receipt.is_file():
        raise ApplyRefusal("tracked manifest and independent receipt are required")
    manifest = verify_authorization(operations_root, manifest_path, authorization_commit, authorization_receipt)
    descriptor = workspace_link.load_descriptor(operations_root / ".cvf" / "workspace-link.json")
    peer = workspace_link.resolve_peer(operations_root, descriptor, fetch=True)
    fresh = scan.build_dataset(peer, manifest["baseCommit"], manifest["candidateCommit"])
    if _sha(json.dumps(fresh, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")) != manifest["scanDatasetSha256"]:
        raise ApplyRefusal("fresh scan dataset does not match manifest")
    if _sha((HERE / "filtering_policy.json").read_bytes()) != manifest["filteringPolicySha256"]:
        raise ApplyRefusal("filtering policy drift")

    records = fresh["records"]
    # Build lookup by (changeType, path/oldPath/newPath tuple)
    by_key: dict[tuple[str, str | None, str | None, str | None], dict[str, Any]] = {
        (row["changeType"], row.get("path"), row.get("oldPath"), row.get("newPath")): row
        for row in records
    }
    destinations = _destinations(manifest, operations_root)

    # R2 + R3: full per-field binding check AND immediate pre-mutation checks
    for index, entry in enumerate(manifest["entries"]):
        operation = entry["operation"]
        if operation == "new":
            record = by_key.get(("added", entry["candidateSourcePath"], None, None))
        elif operation == "modified":
            record = by_key.get(("modified", entry["candidateSourcePath"], None, None))
        elif operation == "deleted":
            record = by_key.get(("deleted", entry["baseSourcePath"], None, None))
        else:  # renamed
            record = by_key.get(("renamed", entry["newSourcePath"], entry["oldSourcePath"], entry["newSourcePath"]))

        if record is None:
            raise ApplyRefusal(f"manifest entry '{operation}' is absent from fresh scan")

        # R2: full per-field binding
        _check_entry_against_fresh_scan(entry, record)

        # Pre-loop precondition check
        paths = destinations[index]
        if operation == "renamed":
            _check(paths[0], entry["oldDestinationPrecondition"])
            _check(paths[1], entry["newDestinationPrecondition"])
        else:
            _check(paths[0], entry["destinationPrecondition"])

    run_id = uuid.uuid4().hex
    recovery_root = operations_root / ".cvf" / "local-linked-source-recovery" / run_id
    recovery_root.mkdir(parents=True, exist_ok=False)
    preimages: list[dict[str, Any]] = []
    all_paths = [path for paths in destinations.values() for path in paths]
    for index, path in enumerate(all_paths):
        exists = path.is_file()
        data = path.read_bytes() if exists else b""
        recovery_file = recovery_root / f"{index:04d}.bin"
        recovery_file.write_bytes(data)
        if _sha(recovery_file.read_bytes()) != _sha(data):
            raise ApplyRefusal("recovery bundle verification failed before mutation")
        preimages.append({"path": path, "existed": exists, "sha256": _sha(data), "recovery": recovery_file})

    mutated: list[Path] = []
    receipt_rows: list[dict[str, str]] = []
    manifest_sha = manifest["manifestSha256"]
    receipt_root = operations_root / "provenance" / "shift-operations" / manifest["candidateCommit"] / "apply" / manifest_sha
    try:
        for index, entry in enumerate(manifest["entries"]):
            if failure_hook:
                failure_hook(index)
            paths = destinations[index]
            operation = entry["operation"]

            # R3: immediate pre-mutation recheck — full path safety + precondition
            if operation == "renamed":
                # Re-run full path safety (catches TOCTOU reparse on ancestors)
                _safe_relative(entry["oldDestinationPath"], operations_root)
                _safe_relative(entry["newDestinationPath"], operations_root)
                _check(paths[0], entry["oldDestinationPrecondition"])
                _check(paths[1], entry["newDestinationPrecondition"])
                data = _source_bytes(peer, manifest["candidateCommit"], entry["newSourcePath"])
                _atomic_write(paths[1], data)
                mutated.append(paths[1])
                paths[0].unlink()
                mutated.append(paths[0])
                receipt_rows.extend([
                    {"path": entry["oldDestinationPath"], "disposition": "APPROVED_APPLY", "beforeSha256": entry["oldDestinationPrecondition"]["sha256"], "afterSha256": _sha(b"")},
                    {"path": entry["newDestinationPath"], "disposition": "APPROVED_APPLY", "beforeSha256": _sha(b""), "afterSha256": _sha(data)},
                ])
            elif operation == "deleted":
                _safe_relative(entry["destinationPath"], operations_root)
                _check(paths[0], entry["destinationPrecondition"])
                before = paths[0].read_bytes()
                paths[0].unlink()
                mutated.append(paths[0])
                receipt_rows.append({"path": entry["destinationPath"], "disposition": "APPROVED_APPLY", "beforeSha256": _sha(before), "afterSha256": _sha(b"")})
            else:
                _safe_relative(entry["destinationPath"], operations_root)
                _check(paths[0], entry["destinationPrecondition"])
                before = paths[0].read_bytes() if paths[0].is_file() else b""
                data = _source_bytes(peer, manifest["candidateCommit"], entry["candidateSourcePath"])
                _atomic_write(paths[0], data)
                mutated.append(paths[0])
                receipt_rows.append({"path": entry["destinationPath"], "disposition": "APPROVED_APPLY", "beforeSha256": _sha(before), "afterSha256": _sha(data)})
        # Receipt: path/disposition/hash/outcome only — no raw bytes, no secret substrings,
        # no absolute paths (paths are repository-relative strings from the manifest).
        receipt = {"outcome": "APPLIED", "entries": receipt_rows}
        receipt_root.mkdir(parents=True, exist_ok=True)
        (receipt_root / "apply_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        return receipt
    except Exception:
        restored: list[dict[str, str]] = []
        for item in preimages:
            path = item["path"]
            if item["existed"]:
                _atomic_write(path, item["recovery"].read_bytes())
            elif path.exists() or path.is_symlink():
                path.unlink()
            restored.append({
                "path": path.relative_to(operations_root).as_posix(),
                "disposition": "APPROVED_APPLY",
                "beforeSha256": item["sha256"],
                "afterSha256": item["sha256"],
            })
        failure = {
            "outcome": "FAILED_RESTORED",
            "entries": restored,
        }
        receipt_root.mkdir(parents=True, exist_ok=True)
        (receipt_root / "failure_recovery_receipt.json").write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--operations-root", type=Path, default=HERE.parents[1])
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--authorization-commit", required=True)
    parser.add_argument("--authorization-receipt", type=Path, required=True)
    args = parser.parse_args()
    apply_manifest(args.operations_root, args.manifest, args.authorization_commit, args.authorization_receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
