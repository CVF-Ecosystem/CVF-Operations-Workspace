"""Git-object-level scan for the governed Operations/Shift link.

Claim boundary: scan produces deterministic discovery metadata only. It does
not authorize or perform source application, porting, runtime compatibility,
AI governance, or production-readiness decisions.

Output boundary: run_scan self-derives its only write target as:
  <operations_root>/provenance/shift-operations/<candidate_commit>/
No caller-supplied output_root is accepted. Test isolation must inject a
temporary operations_root; the provenance path is derived inside that root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import dispositions  # noqa: E402
import workspace_link  # noqa: E402


class ScanError(RuntimeError):
    pass


class CommitNotFoundError(ScanError):
    pass


class NonAncestorCandidateError(ScanError):
    pass


def _git_bytes(repo: Path, *args: str, check: bool = True) -> bytes:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if check and result.returncode:
        raise ScanError(result.stderr.decode("utf-8", "replace").strip() or f"git {' '.join(args)} failed")
    return result.stdout


def _git(repo: Path, *args: str, check: bool = True) -> str:
    return _git_bytes(repo, *args, check=check).decode("utf-8", "replace").strip()


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _tree(repo: Path, commit: str) -> dict[str, dict[str, Any]]:
    raw = _git_bytes(repo, "ls-tree", "-rlz", commit)
    result: dict[str, dict[str, Any]] = {}
    for item in raw.split(b"\0"):
        if not item:
            continue
        meta, path_raw = item.split(b"\t", 1)
        mode, object_type, git_hash, size_raw = meta.decode("ascii").split()
        path = path_raw.decode("utf-8", "surrogateescape").replace("\\", "/")
        result[path] = {
            "mode": mode,
            "type": object_type,
            "gitHash": git_hash,
            "size": 0 if size_raw == "-" else int(size_raw),
        }
    return result


def _blob(repo: Path, commit: str, path: str) -> bytes:
    return _git_bytes(repo, "show", f"{commit}:{path}")


def _diff_records(repo: Path, base: str, candidate: str) -> list[tuple[str, list[str]]]:
    tokens = _git_bytes(repo, "diff", "--name-status", "-z", "-M", base, candidate).split(b"\0")
    records: list[tuple[str, list[str]]] = []
    index = 0
    while index < len(tokens) and tokens[index]:
        status = tokens[index].decode("ascii")
        index += 1
        count = 2 if status.startswith(("R", "C")) else 1
        paths = [tokens[index + offset].decode("utf-8", "surrogateescape").replace("\\", "/") for offset in range(count)]
        index += count
        records.append((status, paths))
    return records


def build_dataset(peer_repo: Path, base: str, candidate: str) -> dict[str, Any]:
    for label, commit in (("base", base), ("candidate", candidate)):
        if len(commit) != 40 or subprocess.run(
            ["git", "-C", str(peer_repo), "cat-file", "-e", f"{commit}^{{commit}}"],
            capture_output=True,
        ).returncode:
            raise CommitNotFoundError(f"{label} commit does not resolve: {commit}")
    if subprocess.run(
        ["git", "-C", str(peer_repo), "merge-base", "--is-ancestor", base, candidate],
        capture_output=True,
    ).returncode:
        raise NonAncestorCandidateError("candidate must descend from sourcePin")

    base_tree = _tree(peer_repo, base)
    candidate_tree = _tree(peer_repo, candidate)
    changed: set[str] = set()
    records: list[dict[str, Any]] = []

    for status, paths in _diff_records(peer_repo, base, candidate):
        code = status[0]
        if code == "R":
            old_path, new_path = paths
            changed.update((old_path, new_path))
            old_blob = _blob(peer_repo, base, old_path)
            new_blob = _blob(peer_repo, candidate, new_path)
            record = {
                "changeType": "renamed",
                "oldPath": old_path,
                "newPath": new_path,
                "path": new_path,
                "baseGitObject": base_tree[old_path]["gitHash"],
                "candidateGitObject": candidate_tree[new_path]["gitHash"],
                "baseBlobSha256": _sha256(old_blob),
                "candidateBlobSha256": _sha256(new_blob),
                "baseMode": base_tree[old_path]["mode"],
                "candidateMode": candidate_tree[new_path]["mode"],
                "size": candidate_tree[new_path]["size"],
                "contentChanged": old_blob != new_blob,
                "binary": b"\0" in new_blob[:8192],
            }
            classification, reason = dispositions.classify(record, new_blob)
        elif code == "A":
            path = paths[0]
            changed.add(path)
            blob = _blob(peer_repo, candidate, path)
            record = {
                "changeType": "added",
                "path": path,
                "candidateGitObject": candidate_tree[path]["gitHash"],
                "candidateBlobSha256": _sha256(blob),
                "candidateMode": candidate_tree[path]["mode"],
                "size": candidate_tree[path]["size"],
                "binary": b"\0" in blob[:8192],
            }
            classification, reason = dispositions.classify(record, blob)
        elif code == "D":
            path = paths[0]
            changed.add(path)
            blob = _blob(peer_repo, base, path)
            record = {
                "changeType": "deleted",
                "path": path,
                "baseGitObject": base_tree[path]["gitHash"],
                "baseBlobSha256": _sha256(blob),
                "baseMode": base_tree[path]["mode"],
                "size": base_tree[path]["size"],
                "binary": b"\0" in blob[:8192],
            }
            # R5 fix: pass base blob content so secret-shaped deleted content is classified HARD_EXCLUDE
            classification, reason = dispositions.classify(record, blob)
        else:
            path = paths[-1]
            changed.add(path)
            blob = _blob(peer_repo, candidate, path)
            record = {
                "changeType": "modified",
                "path": path,
                "baseGitObject": base_tree[path]["gitHash"],
                "candidateGitObject": candidate_tree[path]["gitHash"],
                "baseBlobSha256": _sha256(_blob(peer_repo, base, path)),
                "candidateBlobSha256": _sha256(blob),
                "baseMode": base_tree[path]["mode"],
                "candidateMode": candidate_tree[path]["mode"],
                "size": candidate_tree[path]["size"],
                "binary": b"\0" in blob[:8192],
            }
            classification, reason = dispositions.classify(record, blob)
        record["classification"] = classification
        record["reason"] = reason
        records.append(record)

    for path in sorted(set(base_tree) & set(candidate_tree) - changed):
        blob = _blob(peer_repo, candidate, path)
        record = {
            "changeType": "unchanged",
            "path": path,
            "baseGitObject": base_tree[path]["gitHash"],
            "candidateGitObject": candidate_tree[path]["gitHash"],
            "baseBlobSha256": _sha256(blob),
            "candidateBlobSha256": _sha256(blob),
            "baseMode": base_tree[path]["mode"],
            "candidateMode": candidate_tree[path]["mode"],
            "size": candidate_tree[path]["size"],
            "binary": b"\0" in blob[:8192],
        }
        classification, reason = dispositions.classify(record, blob)
        record["classification"] = classification
        record["reason"] = reason
        records.append(record)

    records.sort(key=lambda row: (row.get("path", ""), row.get("oldPath", ""), row["changeType"]))
    accounting = {key: sum(1 for row in records if row["changeType"] == key) for key in ("unchanged", "modified", "added", "deleted", "renamed")}
    classifications = {key: sum(1 for row in records if row["classification"] == key) for key in dispositions.SCAN_CLASSIFICATIONS}
    expected = len(set(base_tree) | set(candidate_tree)) - accounting["renamed"]
    if sum(accounting.values()) != expected or sum(classifications.values()) != len(records):
        raise ScanError("exactly-once accounting invariant failed")
    return {
        "schemaVersion": "1.0",
        "baseCommit": base,
        "candidateCommit": candidate,
        "accounting": accounting,
        "classifications": classifications,
        "records": records,
    }


def run_scan(
    operations_root: Path,
    candidate_commit: str,
    *,
    descriptor_path: Path | None = None,
    clone_to: Path | None = None,
    fetch: bool = True,
    write_outputs: bool = True,
) -> dict[str, Any]:
    """Run scan and write outputs only to the self-derived provenance directory.

    Output boundary: outputs are always written to
      <operations_root>/provenance/shift-operations/<candidate_commit>/
    No caller-supplied output path is accepted. For test isolation, pass a
    temporary directory as operations_root; the provenance subpath is derived
    inside it and the boundary is enforced relative to that root.
    """
    operations_root = operations_root.resolve()
    descriptor_path = descriptor_path or operations_root / ".cvf" / "workspace-link.json"
    descriptor = workspace_link.load_descriptor(descriptor_path)
    peer = workspace_link.resolve_peer(operations_root, descriptor, clone_to=clone_to, fetch=fetch)
    dataset = build_dataset(peer, descriptor["sourcePin"], candidate_commit)
    dataset_sha = _sha256(_canonical_bytes(dataset))
    policy_bytes = (HERE / "filtering_policy.json").read_bytes()
    inventory = {"dataset": dataset, "datasetSha256": dataset_sha, "filteringPolicySha256": _sha256(policy_bytes)}
    report = {
        "schemaVersion": "1.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "claimBoundary": "Discovery metadata only; no source application or porting authorization.",
        **inventory,
    }
    if write_outputs:
        # Self-derived output — bounded to the declared provenance ceiling.
        target = operations_root / "provenance" / "shift-operations" / candidate_commit
        # Enforce: target must be inside operations_root
        try:
            target.resolve().relative_to(operations_root)
        except ValueError as exc:
            raise ScanError("derived output path escapes operations root") from exc
        target.mkdir(parents=True, exist_ok=True)
        (target / "linked_sources_inventory.json").write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (target / "linked_sources_scan_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--operations-root", type=Path, default=HERE.parents[1])
    parser.add_argument("--candidate-commit", required=True)
    parser.add_argument("--clone-to", type=Path)
    args = parser.parse_args()
    run_scan(args.operations_root, args.candidate_commit, clone_to=args.clone_to)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
