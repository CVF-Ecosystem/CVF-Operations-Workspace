"""Source-pin and worktree-cleanliness verification for F0 source intake.

FR-01/FR-02/FR-14: F0 must capture from a detached temporary worktree at an
exact, full, reachable commit SHA, and must never mutate the source
repository or its checked-out commit. Every guard here fails loudly rather
than silently degrading to a best-effort capture.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

_FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class SourcePinError(ValueError):
    """Raised when a source commit pin is missing, abbreviated or unreachable."""


class DirtyWorktreeError(ValueError):
    """Raised when a worktree that must be clean has local modifications."""


def is_full_sha(value: str) -> bool:
    """Return True only for a well-formed, unabbreviated 40-hex-char SHA-1."""
    return bool(_FULL_SHA_RE.fullmatch(value or ""))


def _run_git(args: list[str], cwd: Path, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def verify_pin_reachable(repo: Path, commit: str) -> str:
    """Verify ``commit`` is a full SHA that resolves to a real commit in ``repo``.

    Returns the canonical full SHA on success. Raises SourcePinError for a
    missing, empty, abbreviated, or unreachable pin.
    """
    if not commit:
        raise SourcePinError("source commit pin is missing")
    if not is_full_sha(commit):
        raise SourcePinError(
            f"source commit pin must be a full 40-character SHA-1, got: {commit!r}"
        )
    type_result = _run_git(["cat-file", "-t", commit], cwd=repo)
    if type_result.returncode != 0 or type_result.stdout.strip() != "commit":
        raise SourcePinError(f"source commit pin is not reachable in {repo}: {commit}")
    verify_result = _run_git(["rev-parse", "--verify", f"{commit}^{{commit}}"], cwd=repo)
    if verify_result.returncode != 0:
        raise SourcePinError(f"source commit pin failed rev-parse verification: {commit}")
    resolved = verify_result.stdout.strip()
    if resolved != commit:
        raise SourcePinError(
            f"source commit pin resolved to an unexpected SHA (possible ambiguity): "
            f"requested {commit}, resolved {resolved}"
        )
    return resolved


def get_status_porcelain(repo: Path) -> str:
    """Return raw 'git status --porcelain' output for ``repo`` (read-only)."""
    result = _run_git(["status", "--porcelain"], cwd=repo)
    if result.returncode != 0:
        raise SourcePinError(f"unable to read git status for {repo}: {result.stderr.strip()}")
    return result.stdout


def assert_worktree_clean(worktree: Path) -> None:
    """Raise DirtyWorktreeError if ``worktree`` has any local modification."""
    status = get_status_porcelain(worktree)
    if status.strip():
        raise DirtyWorktreeError(
            f"detached source worktree is not clean, refusing to capture: {worktree}\n{status}"
        )


def create_detached_worktree(repo: Path, commit: str, worktree_path: Path) -> None:
    """Create a detached worktree for ``repo`` at the exact ``commit``.

    Does not modify ``repo``'s own checked-out branch, index or working
    tree; ``git worktree add`` only creates a new linked checkout.
    """
    if worktree_path.exists():
        raise DirtyWorktreeError(
            f"refusing to reuse an existing path for a temporary worktree: {worktree_path}"
        )
    result = _run_git(
        ["worktree", "add", "--detach", str(worktree_path), commit],
        cwd=repo,
        timeout=120,
    )
    if result.returncode != 0:
        raise SourcePinError(
            f"failed to create detached worktree at {commit}: {result.stderr.strip()}"
        )


def remove_worktree(repo: Path, worktree_path: Path) -> None:
    """Remove a temporary worktree previously created with create_detached_worktree."""
    _run_git(["worktree", "remove", "--force", str(worktree_path)], cwd=repo, timeout=60)
    _run_git(["worktree", "prune"], cwd=repo, timeout=30)
