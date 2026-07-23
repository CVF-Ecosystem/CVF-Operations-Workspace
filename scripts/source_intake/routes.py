"""Public HTTP ingress discovery for F0 source intake (FR-05).

Scans every *.py file under apps/ generically (no hardcoded app allowlist),
so any FastAPI ingress — including apps/integration-edge, not just the main
API — is captured. An earlier review bundle's public-API map only covered
one app and silently missed a live webhook route; this scanner is
deliberately app-agnostic to avoid repeating that gap.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import paths as si_paths  # noqa: E402

_HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"}
_EXCLUDED_DIR_PARTS = {
    ".git", ".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__",
    "node_modules", "dist", "build", "coverage", ".venv", "venv",
}


def _literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _app_owner(rel_posix_path: str) -> str | None:
    parts = rel_posix_path.split("/")
    if len(parts) >= 2 and parts[0] == "apps":
        return parts[1]
    return None


def _scan_file(worktree: Path, py_file: Path) -> list[dict]:
    rel_posix = si_paths.to_posix_relative(worktree, py_file)
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return []

    prefixes: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            if getattr(node.value.func, "id", None) == "APIRouter":
                prefix = ""
                for keyword in node.value.keywords:
                    if keyword.arg == "prefix":
                        prefix = _literal_string(keyword.value) or ""
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        prefixes[target.id] = prefix

    routes: list[dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                continue
            method = decorator.func.attr.upper()
            if method not in _HTTP_METHODS:
                continue
            router_name = getattr(decorator.func.value, "id", "router")
            route_path = _literal_string(decorator.args[0]) if decorator.args else None
            if route_path is None:
                continue
            routes.append(
                {
                    "app": _app_owner(rel_posix) or "unknown",
                    "method": method,
                    "path": f"{prefixes.get(router_name, '')}{route_path}" or "/",
                    "function": node.name,
                    "source_path": rel_posix,
                }
            )
    return routes


def discover_routes(worktree: Path) -> list[dict]:
    """Discover every FastAPI-decorated route under worktree/apps/**.

    Returns records sorted by (app, path, method, source_path) for
    determinism. Discovery is purely AST-based: no application import, no
    dependency installation, no runtime execution.
    """
    apps_dir = worktree / "apps"
    if not apps_dir.is_dir():
        return []
    routes: list[dict] = []
    for py_file in apps_dir.rglob("*.py"):
        if any(part in _EXCLUDED_DIR_PARTS for part in py_file.relative_to(worktree).parts):
            continue
        routes.extend(_scan_file(worktree, py_file))
    routes.sort(key=lambda item: (item["app"], item["path"], item["method"], item["source_path"]))
    return routes
