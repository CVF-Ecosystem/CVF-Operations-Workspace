#!/usr/bin/env python3
"""F0 source-intake capture orchestrator (OW-F0-WO-001 / OW-F0-SPEC-001).

Captures a reproducible, secret-safe baseline of a pinned Shift Operations
commit into provenance/shift-operations/<commit>/. Imports no runtime
source: every output is evidence (hashes, inventories, snapshots), never a
copy of application code.

Usage:
    python scripts/source_intake/capture.py \
        --source-repo-primary <path to shift-operations-workspace> \
        --source-commit <full 40-char SHA> \
        --output-dir provenance/shift-operations/<same SHA>

All datasets are built in memory and validated before anything is written,
so a failed run never leaves a partially-written provenance directory.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import dependency_graph as si_dependency_graph  # noqa: E402
import git_pin as si_git_pin  # noqa: E402
import inventory as si_inventory  # noqa: E402
import ledger as si_ledger  # noqa: E402
import migrations as si_migrations  # noqa: E402
import module_snapshot as si_module_snapshot  # noqa: E402
import paths as si_paths  # noqa: E402
import redact as si_redact  # noqa: E402
import routes as si_routes  # noqa: E402
import test_outcomes as si_test_outcomes  # noqa: E402

TOOL_REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_REPOSITORY_NAME = "shift-operations-workspace"
SCHEMA_VERSION = 1


class CaptureError(RuntimeError):
    """Raised for any F0 stop condition; always maps to a non-zero exit."""


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=False) + "\n", encoding="utf-8")


def run_capture(
    source_repo_primary: Path,
    source_commit: str,
    output_dir: Path,
    tmp_worktree_parent: Path,
    skip_tests: bool,
    keep_worktree: bool,
) -> dict:
    si_paths.assert_not_forbidden_target(output_dir, TOOL_REPO_ROOT)
    si_paths.assert_not_self_scan(source_repo_primary, TOOL_REPO_ROOT)

    canonical_commit = si_git_pin.verify_pin_reachable(source_repo_primary, source_commit)
    source_status_before = si_git_pin.get_status_porcelain(source_repo_primary)

    tmp_worktree = tmp_worktree_parent / f".tmp-f0-source-capture-{canonical_commit[:12]}"
    si_paths.assert_not_self_scan(tmp_worktree, TOOL_REPO_ROOT)

    datasets: dict[str, Any] = {}
    try:
        si_git_pin.create_detached_worktree(source_repo_primary, canonical_commit, tmp_worktree)
        si_git_pin.assert_worktree_clean(tmp_worktree)
        worktree_head = si_git_pin.verify_pin_reachable(tmp_worktree, canonical_commit)
        if worktree_head != canonical_commit:  # pragma: no cover - defensive
            raise CaptureError("temporary worktree HEAD does not match the requested pin")

        file_inventory, exclusions = si_inventory.build_inventory(tmp_worktree)
        routes = si_routes.discover_routes(tmp_worktree)
        migrations = si_migrations.discover_migrations(tmp_worktree)
        dep_graph = si_dependency_graph.build_dependency_graph(tmp_worktree)
        module_snap = si_module_snapshot.snapshot_module_registry(tmp_worktree, canonical_commit)
        test_outcomes = [] if skip_tests else si_test_outcomes.run_all(tmp_worktree)

        ledger_rows = si_ledger.build_ledger(file_inventory, SOURCE_REPOSITORY_NAME, canonical_commit)
        ledger_problems = si_ledger.validate_ledger(ledger_rows)
        if ledger_problems:
            raise CaptureError("import ledger failed validation:\n  " + "\n  ".join(ledger_problems))

        datasets = {
            "file_inventory": file_inventory,
            "exclusions": exclusions,
            "routes": routes,
            "migrations": migrations,
            "dependency_graph": dep_graph,
            "module_registry_snapshot": module_snap,
            "test_outcomes": test_outcomes,
            "import_ledger": ledger_rows,
        }
    finally:
        if not keep_worktree:
            si_git_pin.remove_worktree(source_repo_primary, tmp_worktree)

    source_status_after = si_git_pin.get_status_porcelain(source_repo_primary)
    if source_status_before != source_status_after:
        raise CaptureError(
            "source repository status changed during capture; this must never "
            "happen and the run is rejected:\n"
            f"before:\n{source_status_before}\nafter:\n{source_status_after}"
        )

    receipt = {
        "schema_version": SCHEMA_VERSION,
        "source_repository": SOURCE_REPOSITORY_NAME,
        "source_commit": canonical_commit,
        "source_status_before": si_redact.redact_credential_urls(source_status_before),
        "source_status_after": si_redact.redact_credential_urls(source_status_after),
        "source_status_unchanged": True,
        "counts": {
            "tracked_files_inventoried": len(datasets["file_inventory"]),
            "tracked_files_excluded": len(datasets["exclusions"]),
            "routes_discovered": len(datasets["routes"]),
            "migrations_discovered": len(datasets["migrations"]),
            "import_edges_discovered": len(datasets["dependency_graph"]["import_edges"]),
            "test_commands_attempted": len(datasets["test_outcomes"]),
            "ledger_rows": len(datasets["import_ledger"]),
        },
        "claim_boundary": (
            "This receipt proves a reproducible read-only baseline was captured "
            "at the pinned commit. It does not import runtime source, does not "
            "claim any module status, and does not authorize any asset for "
            "porting."
        ),
    }
    datasets["capture_receipt"] = receipt
    return datasets


def write_outputs(output_dir: Path, datasets: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "capture_receipt.json", datasets["capture_receipt"])
    _write_json(
        output_dir / "capture_timing.json",
        {"captured_at_utc": datetime.now(timezone.utc).isoformat()},
    )
    _write_json(output_dir / "file_inventory.json", datasets["file_inventory"])
    _write_json(output_dir / "exclusions.json", datasets["exclusions"])
    _write_json(output_dir / "routes.json", datasets["routes"])
    _write_json(output_dir / "migrations.json", datasets["migrations"])
    _write_json(output_dir / "dependency_graph.json", datasets["dependency_graph"])
    _write_json(output_dir / "module_registry_snapshot.json", datasets["module_registry_snapshot"])
    _write_json(output_dir / "test_outcomes.json", datasets["test_outcomes"])
    _write_json(output_dir / "import_ledger.json", datasets["import_ledger"])


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repo-primary", required=True, type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--tmp-worktree-parent", type=Path, default=None)
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--keep-worktree", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source_repo_primary = args.source_repo_primary.resolve()
    output_dir = args.output_dir if args.output_dir.is_absolute() else (TOOL_REPO_ROOT / args.output_dir)
    tmp_worktree_parent = (
        args.tmp_worktree_parent.resolve() if args.tmp_worktree_parent else source_repo_primary.parent
    )
    try:
        datasets = run_capture(
            source_repo_primary=source_repo_primary,
            source_commit=args.source_commit,
            output_dir=output_dir,
            tmp_worktree_parent=tmp_worktree_parent,
            skip_tests=args.skip_tests,
            keep_worktree=args.keep_worktree,
        )
        write_outputs(output_dir, datasets)
    except (
        si_paths.PathEscapeError,
        si_paths.SelfScanError,
        si_git_pin.SourcePinError,
        si_git_pin.DirtyWorktreeError,
        CaptureError,
    ) as exc:
        print(f"F0 CAPTURE: FAIL — {exc}", file=sys.stderr)
        return 1
    print(f"F0 CAPTURE: PASS — wrote evidence to {output_dir}")
    for key, value in datasets["capture_receipt"]["counts"].items():
        print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
