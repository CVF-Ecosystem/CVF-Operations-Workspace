"""Database migration order and hashing for F0 source intake (FR-06).

Reads and hashes migration files only. Never executes SQL, never connects
to a database, never invokes a migration tool.
"""

from __future__ import annotations

import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import paths as si_paths  # noqa: E402
import inventory as si_inventory  # noqa: E402


def discover_migrations(worktree: Path) -> list[dict]:
    """Return every database/migrations/*.sql file, in filename order.

    Each record: order (0-based index in applied order), source_path,
    sha256, size_bytes. Filename order is used because the source
    repository's migrations are numerically prefixed (001_, 002_, ...),
    which is also the order a migration tool would apply them in — this
    tool never applies them, it only records the order it observes.
    """
    base = worktree / "database" / "migrations"
    if not base.is_dir():
        return []
    migration_files = sorted(base.glob("*.sql"), key=lambda path: path.name)
    records: list[dict] = []
    for index, migration_file in enumerate(migration_files):
        rel_posix = si_paths.to_posix_relative(worktree, migration_file)
        data = si_inventory.read_tracked_blob(worktree, rel_posix)
        records.append(
            {
                "order": index,
                "source_path": rel_posix,
                "sha256": si_inventory.sha256_bytes(data),
                "size_bytes": len(data),
            }
        )
    return records
