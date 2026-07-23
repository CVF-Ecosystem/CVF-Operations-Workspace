"""Application/package roots and import edges for F0 source intake (FR-07).

Local module ownership is discovered from the worktree itself (src-layout
or bare top-level package directories under apps/*/ and packages/*/),
never hardcoded, so the graph stays correct even if source packages are
renamed or added between pins.
"""

from __future__ import annotations

import ast
from pathlib import Path

_EXCLUDED_DIR_PARTS = {
    ".git", ".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__",
    "node_modules", "dist", "build", "coverage", ".venv", "venv",
}


def discover_roots(worktree: Path, group: str) -> list[str]:
    base = worktree / group
    if not base.is_dir():
        return []
    return sorted(child.name for child in base.iterdir() if child.is_dir())


def _discover_local_module_names(worktree: Path) -> dict[str, str]:
    """Map an importable top-level module name to its owning 'group/name'."""
    mapping: dict[str, str] = {}
    for group in ("apps", "packages"):
        base = worktree / group
        if not base.is_dir():
            continue
        for child in sorted(p for p in base.iterdir() if p.is_dir()):
            owner = f"{group}/{child.name}"
            src_dir = child / "src"
            search_roots = [src_dir] if src_dir.is_dir() else [child]
            for root in search_roots:
                if not root.is_dir():
                    continue
                for entry in sorted(p for p in root.iterdir() if p.is_dir()):
                    if (entry / "__init__.py").is_file():
                        mapping[entry.name] = owner
    return mapping


def _module_roots(node: ast.Import | ast.ImportFrom) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name.split(".")[0] for alias in node.names]
    if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
        return [node.module.split(".")[0]]
    return []


def discover_import_edges(worktree: Path) -> list[dict]:
    """Return de-duplicated, sorted {"from": owner, "to": owner} edges.

    Only edges between locally-owned apps/packages are recorded (imports of
    third-party libraries are not part of the local dependency graph). Self
    edges (a package importing its own module) are dropped.
    """
    module_owner = _discover_local_module_names(worktree)
    edges: set[tuple[str, str]] = set()
    for group in ("apps", "packages"):
        base = worktree / group
        if not base.is_dir():
            continue
        for py_file in base.rglob("*.py"):
            rel_parts = py_file.relative_to(worktree).parts
            if any(part in _EXCLUDED_DIR_PARTS for part in rel_parts):
                continue
            owner = f"{rel_parts[0]}/{rel_parts[1]}"
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue
            for node in ast.walk(tree):
                if not isinstance(node, (ast.Import, ast.ImportFrom)):
                    continue
                for root_name in _module_roots(node):
                    target_owner = module_owner.get(root_name)
                    if target_owner and target_owner != owner:
                        edges.add((owner, target_owner))
    return [{"from": frm, "to": to} for frm, to in sorted(edges)]


def build_dependency_graph(worktree: Path) -> dict:
    return {
        "application_roots": discover_roots(worktree, "apps"),
        "package_roots": discover_roots(worktree, "packages"),
        "import_edges": discover_import_edges(worktree),
    }
