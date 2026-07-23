"""Module Registry snapshot for F0 source intake (FR-08).

Records the source repository's own Module Registry status verbatim, as
evidence, without writing to or promoting anything in this repository's
Module Registry. The target's docs/catalog/MODULE_REGISTRY.json is never
opened by this module.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import paths as si_paths  # noqa: E402
import inventory as si_inventory  # noqa: E402

SOURCE_REGISTRY_RELATIVE = "docs/catalog/MODULE_REGISTRY.json"


def snapshot_module_registry(worktree: Path, source_commit: str) -> dict[str, Any]:
    """Return a read-only snapshot of the source's Module Registry.

    If the file is absent at this pin, the snapshot says so explicitly
    rather than being omitted, so the absence itself is recorded evidence.
    """
    registry_path = worktree / SOURCE_REGISTRY_RELATIVE
    if not registry_path.is_file():
        return {
            "source_path": SOURCE_REGISTRY_RELATIVE,
            "present_at_pin": False,
            "source_commit": source_commit,
            "content": None,
            "sha256": None,
            "claim_boundary": (
                "Module Registry not present in the source repository at this "
                "pin. This is a snapshot only and asserts nothing about "
                "CVF-Operations-Workspace's own Module Registry, which remains "
                "empty and unmodified by F0."
            ),
        }
    rel_posix = si_paths.to_posix_relative(worktree, registry_path)
    data = si_inventory.read_tracked_blob(worktree, rel_posix)
    content = json.loads(data.decode("utf-8"))
    return {
        "source_path": rel_posix,
        "present_at_pin": True,
        "source_commit": source_commit,
        "content": content,
        "sha256": hashlib.sha256(data).hexdigest(),
        "claim_boundary": (
            "Snapshot of the source repository's Module Registry, captured "
            "read-only from the pinned commit. Not authoritative for "
            "CVF-Operations-Workspace; this repository's own Module Registry "
            "remains empty and unmodified by F0. No module is created or "
            "promoted here."
        ),
    }
