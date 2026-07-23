"""Tracked-file inventory and candidate classification for F0 source intake.

FR-03/FR-04/FR-13: inventory only Git-tracked files (never the working
directory blindly, which would pick up ignored/untracked local state), hash
every retained file with SHA-256, classify it into a closed vocabulary, and
exclude secret-like, generated, or local-state paths before they are ever
read for content.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import paths as si_paths  # noqa: E402

CANDIDATE_CLASSES = (
    "database_migration",
    "test_code",
    "ci_or_governance",
    "documentation",
    "contract_or_schema",
    "configuration",
    "application_code",
    "package_code",
    "lock_or_dependency_manifest",
    "other",
)

_EXCLUDED_DIR_PARTS = {
    ".git", ".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__",
    "node_modules", ".pnpm-store", "dist", "build", "coverage", ".venv", "venv",
}

_EXCLUDED_NAME_SUBSTRINGS = ("secret", "credential", "credentials")
_EXCLUDED_NAME_PREFIXES = (".env",)
_EXCLUDED_EXACT_RELATIVE_PATHS = {".cvf/local-binding.json"}
_EXCLUDED_SUFFIXES = (".pem", ".key")


def is_excluded(rel_posix_path: str) -> tuple[bool, str | None]:
    """Return (excluded, reason). Excluded files are never hashed or read."""
    parts = rel_posix_path.split("/")
    if any(part in _EXCLUDED_DIR_PARTS for part in parts[:-1]):
        return True, "excluded-directory"
    name = parts[-1]
    lower_name = name.lower()
    if rel_posix_path in _EXCLUDED_EXACT_RELATIVE_PATHS:
        return True, "local-binding-file"
    if lower_name.startswith(_EXCLUDED_NAME_PREFIXES):
        return True, "env-file"
    if any(token in lower_name for token in _EXCLUDED_NAME_SUBSTRINGS):
        return True, "credential-like-name"
    if lower_name.endswith(_EXCLUDED_SUFFIXES):
        return True, "key-material-suffix"
    return False, None


_GOVERNANCE_DIR_PREFIXES = (".github/", ".githooks/", ".cvf/", "cvf_session/", "session/")
_NAMED_DOCUMENTATION_FILES = {"license", "codeowners", ".mailmap", ".gitattributes"}
_NAMED_CONFIGURATION_FILES = {
    "package.json", "pyproject.toml", "pnpm-workspace.yaml",
    "docker-compose.yml", "docker-compose.yaml",
    ".gitignore", ".editorconfig", ".dockerignore", "makefile", "conftest.py",
}
_REFERENCE_DATA_DIR_PREFIXES = ("examples/", "fixtures/", "knowledge/")


def classify(rel_posix_path: str) -> str:
    """Classify a tracked, non-excluded path into a closed vocabulary.

    'other' is itself a valid, explicit classification (the catch-all), so
    no tracked file is ever left unclassified by this function; the failure
    mode this guards against is a code defect that returns something
    outside CANDIDATE_CLASSES, which callers must treat as fatal.

    Order matters: extension/name-based signals (a file named *.md, or a
    well-known root file) are checked before path-prefix signals, so e.g.
    a README.md living under infrastructure/ is still 'documentation' and
    not swallowed by a broader directory rule.
    """
    lower_full = rel_posix_path.lower()
    segments = rel_posix_path.split("/")
    name = segments[-1]
    lower_name = name.lower()

    if rel_posix_path.startswith("database/migrations/") and name.endswith(".sql"):
        return "database_migration"
    if (
        "tests" in segments[:-1]
        or name.startswith("test_")
        or name.endswith("_test.py")
        or name.endswith(".test.ts")
        or name.endswith(".spec.ts")
    ):
        return "test_code"
    if lower_full.startswith(_GOVERNANCE_DIR_PREFIXES) or (
        len(segments) >= 2 and segments[0].lower() in {"cvf_session", "session"}
    ):
        return "ci_or_governance"
    if lower_name.endswith(".md") or lower_name in _NAMED_DOCUMENTATION_FILES:
        return "documentation"
    if rel_posix_path.startswith("docs/"):
        return "documentation"
    if name.endswith((".json", ".yaml", ".yml")) and any(
        token in lower_full for token in ("contract", "schema", "policy")
    ):
        return "contract_or_schema"
    if (
        lower_name in _NAMED_CONFIGURATION_FILES
        or lower_name.startswith("dockerfile")
        or lower_name.endswith((".cfg", ".ini", ".toml", ".conf"))
    ):
        return "configuration"
    if name.endswith((".lock",)) or lower_name in {"pnpm-lock.yaml", "package-lock.json"}:
        return "lock_or_dependency_manifest"
    if len(segments) == 1 and lower_name.endswith((".json", ".yaml", ".yml")):
        # Root-level machine-readable metadata (e.g. IMPLEMENTATION_STATUS.json)
        # is project status/documentation, not application or package code,
        # once the more specific named-config and lock-file rules above have
        # already had first refusal.
        return "documentation"
    if rel_posix_path.startswith("apps/"):
        return "application_code"
    if rel_posix_path.startswith("packages/"):
        return "package_code"
    if rel_posix_path.startswith("scripts/"):
        return "ci_or_governance"
    if rel_posix_path.startswith("infrastructure/") or rel_posix_path.startswith("database/"):
        return "configuration"
    if lower_full.startswith(_REFERENCE_DATA_DIR_PREFIXES):
        return "documentation"
    return "other"


def is_binary_content(data: bytes) -> bool:
    """Cheap, dependency-free binary sniff: a NUL byte in a leading sample."""
    return b"\x00" in data[:8000]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def list_tracked_files(worktree: Path) -> list[str]:
    """Return every Git-tracked path in ``worktree``, repository-relative posix.

    Uses 'git ls-files' rather than a filesystem walk so the inventory is
    exactly the tracked-object surface Git itself considers authoritative,
    independent of local .gitignore quirks or accidental untracked files.
    """
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=worktree,
        capture_output=True,
        timeout=60,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git ls-files failed in {worktree}: {result.stderr.decode(errors='replace')}")
    raw = result.stdout.decode("utf-8", errors="surrogateescape")
    return sorted(entry for entry in raw.split("\x00") if entry)


def read_tracked_blobs(worktree: Path, rel_posix_paths: list[str]) -> dict[str, bytes]:
    """Read exact Git-blob bytes for paths at detached HEAD in one batch.

    Reading the checked-out file is not equivalent on platforms where Git
    applies working-tree filters such as LF-to-CRLF conversion. F0 records
    source-object hashes, so hashes and sizes must come from Git objects.
    """
    if not rel_posix_paths:
        return {}
    for rel_posix_path in rel_posix_paths:
        if si_paths.contains_backslash(rel_posix_path) or "\n" in rel_posix_path or "\r" in rel_posix_path:
            raise RuntimeError(f"unsupported Git blob path: {rel_posix_path!r}")
    request = b"".join(f"HEAD:{path}\n".encode("utf-8") for path in rel_posix_paths)
    result = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=worktree,
        input=request,
        capture_output=True,
        timeout=60,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "unable to read tracked Git blobs: "
            f"{result.stderr.decode(errors='replace').strip()}"
        )
    records: dict[str, bytes] = {}
    offset = 0
    for rel_posix_path in rel_posix_paths:
        header_end = result.stdout.find(b"\n", offset)
        if header_end < 0:
            raise RuntimeError(f"truncated Git cat-file header for {rel_posix_path!r}")
        fields = result.stdout[offset:header_end].split()
        if len(fields) != 3 or fields[1] != b"blob":
            raise RuntimeError(
                f"tracked path did not resolve to a Git blob: {rel_posix_path!r}"
            )
        size = int(fields[2])
        content_start = header_end + 1
        content_end = content_start + size
        if content_end >= len(result.stdout) or result.stdout[content_end:content_end + 1] != b"\n":
            raise RuntimeError(f"truncated Git blob payload for {rel_posix_path!r}")
        records[rel_posix_path] = result.stdout[content_start:content_end]
        offset = content_end + 1
    if offset != len(result.stdout):
        raise RuntimeError("unexpected trailing bytes from Git cat-file batch")
    return records


def read_tracked_blob(worktree: Path, rel_posix_path: str) -> bytes:
    """Read one exact Git blob; shared by migration and registry snapshots."""
    return read_tracked_blobs(worktree, [rel_posix_path])[rel_posix_path]


def build_inventory(worktree: Path) -> tuple[list[dict], list[dict]]:
    """Build (inventory_records, exclusion_records) for every tracked file.

    Each inventory record: source_path, sha256, size_bytes, candidate_class,
    is_binary. Each exclusion record: source_path, reason. No excluded
    file's bytes are ever read for hashing.
    """
    inventory: list[dict] = []
    exclusions: list[dict] = []
    included_paths: list[str] = []
    for rel_path in list_tracked_files(worktree):
        rel_posix = rel_path.replace("\\", "/")
        excluded, reason = is_excluded(rel_posix)
        if excluded:
            exclusions.append({"source_path": rel_posix, "reason": reason})
            continue
        included_paths.append(rel_posix)

    blobs = read_tracked_blobs(worktree, included_paths)
    for rel_posix in included_paths:
        data = blobs[rel_posix]
        candidate_class = classify(rel_posix)
        if candidate_class not in CANDIDATE_CLASSES:  # pragma: no cover - defensive
            raise RuntimeError(f"classifier produced an out-of-vocabulary class for {rel_posix}")
        if si_paths.contains_backslash(rel_posix):  # pragma: no cover - defensive
            raise RuntimeError(f"inventory path retained a backslash separator: {rel_posix}")
        inventory.append(
            {
                "source_path": rel_posix,
                "sha256": sha256_bytes(data),
                "size_bytes": len(data),
                "candidate_class": candidate_class,
                "is_binary": is_binary_content(data),
            }
        )
    inventory.sort(key=lambda record: record["source_path"])
    exclusions.sort(key=lambda record: record["source_path"])
    return inventory, exclusions
