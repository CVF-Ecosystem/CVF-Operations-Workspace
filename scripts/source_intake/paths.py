"""Path normalization and safety guards for F0 source-intake tooling.

Every artifact this tool writes must reference repository-relative paths
using ``/`` separators, regardless of host platform, and must never point
outside the declared root. This module is the single place those two
invariants are enforced.
"""

from __future__ import annotations

from pathlib import Path


class PathEscapeError(ValueError):
    """Raised when a resolved path would escape its declared root."""


class SelfScanError(ValueError):
    """Raised when a scan target resolves inside this tool's own repository."""


def to_posix_relative(root: Path, target: Path) -> str:
    """Return ``target`` relative to ``root`` using ``/`` separators.

    Raises PathEscapeError if ``target`` does not resolve inside ``root``.
    This is the only sanctioned way to turn a filesystem path into a value
    that goes into a captured artifact.
    """
    root_resolved = root.resolve()
    target_resolved = target.resolve()
    try:
        relative = target_resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise PathEscapeError(
            f"path escapes declared root: {target_resolved} is not inside {root_resolved}"
        ) from exc
    return relative.as_posix()


def contains_backslash(value: str) -> bool:
    """Return True if a supposedly repository-relative path uses '\\'.

    Used as a defense-in-depth guard on records that did not necessarily
    pass through to_posix_relative (e.g. records rebuilt from a fixture in
    a test, or read back from a written artifact).
    """
    return "\\" in value


def assert_not_self_scan(candidate_root: Path, tool_root: Path) -> None:
    """Refuse to treat this tool's own repository as a scan target.

    F0 must only ever capture the detached Shift worktree. Pointing the
    scanner at the CVF-Operations-Workspace repository (this tool's own
    home) — whether exactly or via a subdirectory — would silently mix
    target-repository content into what is supposed to be a Shift-only
    baseline, defeating the whole purpose of provenance tracking.
    """
    candidate_resolved = candidate_root.resolve()
    tool_resolved = tool_root.resolve()
    if candidate_resolved == tool_resolved:
        raise SelfScanError(
            f"refusing to scan the tool's own repository as a source worktree: {candidate_resolved}"
        )
    try:
        candidate_resolved.relative_to(tool_resolved)
    except ValueError:
        return
    raise SelfScanError(
        f"refusing to scan a path inside the tool's own repository: {candidate_resolved}"
    )


def assert_not_forbidden_target(output_dir: Path, repo_root: Path) -> None:
    """Refuse to write F0 output under apps/, packages/ or database/.

    FR-15 forbids F0 from creating those trees in the target repository.
    This guard makes that a hard failure rather than a documentation-only
    rule, independent of what the caller passed on the command line.
    """
    forbidden_roots = ("apps", "packages", "database")
    output_resolved = output_dir.resolve()
    repo_resolved = repo_root.resolve()
    try:
        relative = output_resolved.relative_to(repo_resolved)
    except ValueError:
        # Output outside the repository entirely is not a forbidden-target
        # violation; other guards (e.g. changed-set ceiling review) cover it.
        return
    if relative.parts and relative.parts[0] in forbidden_roots:
        raise PathEscapeError(
            f"refusing to write F0 output under forbidden target tree: {relative.as_posix()}"
        )
