#!/usr/bin/env python3
"""Validate and generate the project documentation index and module catalog."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = REPO_ROOT / "docs" / "catalog"
ARTIFACT_REGISTRY_PATH = CATALOG_DIR / "ARTIFACT_REGISTRY.json"
MODULE_REGISTRY_PATH = CATALOG_DIR / "MODULE_REGISTRY.json"
INDEX_PATH = REPO_ROOT / "docs" / "INDEX.md"
MODULE_CATALOG_PATH = CATALOG_DIR / "MODULE_CATALOG.md"

ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CODE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx"}
SKIP_DIRS = {".git", ".pytest_cache", "__pycache__", "build", "dist", "node_modules"}
TYPE_ORDER = [
    "continuity",
    "implementation_truth",
    "catalog",
    "decision",
    "roadmap",
    "specification",
    "work_order",
    "review",
    "guide",
]
STATUS_ORDER = {"enforced": 0, "partial": 1, "contract-only": 2, "stub": 3}
CANONICAL_CVF_CONTROLS = {
    "identity", "permission", "domain_lock", "data_scope", "risk", "approval",
    "evidence", "audit", "cost", "refusal", "termination", "freeze",
}
MODULE_KINDS = {"app", "package", "service", "tool"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _safe_repo_path(root: Path, relative: object, label: str, problems: list[str]) -> Path | None:
    if not isinstance(relative, str) or not relative:
        problems.append(f"{label}: path must be a non-empty string")
        return None
    if "\\" in relative:
        problems.append(f"{label}: path must use '/' separators: {relative!r}")
        return None
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        problems.append(f"{label}: path escapes repository: {relative!r}")
        return None
    return candidate


def verify_artifacts(registry: dict[str, Any], root: Path = REPO_ROOT) -> list[str]:
    problems: list[str] = []
    if registry.get("schemaVersion") != "1.0":
        problems.append("artifact registry: unsupported schemaVersion")
    types = registry.get("artifactTypes")
    statuses = registry.get("statusLegend")
    artifacts = registry.get("artifacts")
    if not isinstance(types, dict) or not types:
        problems.append("artifact registry: artifactTypes must be non-empty")
        types = {}
    if not isinstance(statuses, dict) or not statuses:
        problems.append("artifact registry: statusLegend must be non-empty")
        statuses = {}
    if not isinstance(artifacts, list):
        problems.append("artifact registry: artifacts must be a list")
        return problems

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for index, artifact in enumerate(artifacts):
        label = f"artifact[{index}]"
        if not isinstance(artifact, dict):
            problems.append(f"{label}: record must be an object")
            continue
        artifact_id = artifact.get("id")
        if not isinstance(artifact_id, str) or not ID_PATTERN.fullmatch(artifact_id):
            problems.append(f"{label}: invalid id {artifact_id!r}")
            continue
        if artifact_id in seen_ids:
            problems.append(f"duplicate artifact id: {artifact_id}")
        seen_ids.add(artifact_id)
        relative = artifact.get("path")
        if isinstance(relative, str) and relative in seen_paths:
            problems.append(f"duplicate artifact path: {relative}")
        if isinstance(relative, str):
            seen_paths.add(relative)
        target = _safe_repo_path(root, relative, artifact_id, problems)
        if target is not None and not target.is_file():
            problems.append(f"{artifact_id}: artifact path does not exist: {relative}")
        if artifact.get("type") not in types:
            problems.append(f"{artifact_id}: unknown artifact type {artifact.get('type')!r}")
        if artifact.get("status") not in statuses:
            problems.append(f"{artifact_id}: unknown artifact status {artifact.get('status')!r}")
        for field in ("title", "authority", "summary"):
            if not _nonempty_string(artifact.get(field)):
                problems.append(f"{artifact_id}: {field} must be a non-empty string")
        if not isinstance(artifact.get("entrypoint"), bool):
            problems.append(f"{artifact_id}: entrypoint must be boolean")
        related = artifact.get("related")
        if not isinstance(related, list):
            problems.append(f"{artifact_id}: related must be a list")
        elif not all(isinstance(item, str) for item in related):
            problems.append(f"{artifact_id}: related items must be strings")
        elif len(related) != len(set(related)):
            problems.append(f"{artifact_id}: related contains duplicates")

    for artifact in artifacts:
        if not isinstance(artifact, dict) or not isinstance(artifact.get("id"), str):
            continue
        for related in artifact.get("related", []):
            if isinstance(related, str) and related not in seen_ids:
                problems.append(f"{artifact['id']}: related unknown artifact {related!r}")
    return problems


def _iter_code_files(base: Path):
    for path in base.rglob("*"):
        if not path.is_file() or path.suffix not in CODE_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def compute_metrics(module_path: Path) -> dict[str, int]:
    code_loc = 0
    code_files = 0
    nonempty = 0
    for path in _iter_code_files(module_path):
        code_files += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        code_loc += len(text.splitlines())
        if text.strip():
            nonempty += 1
    return {"codeLoc": code_loc, "codeFiles": code_files, "nonemptyCodeFiles": nonempty}


def verify_modules(registry: dict[str, Any], root: Path = REPO_ROOT) -> list[str]:
    problems: list[str] = []
    if registry.get("schemaVersion") != "1.0":
        problems.append("module registry: unsupported schemaVersion")
    statuses = registry.get("statusLegend")
    controls = registry.get("cvfControlVocabulary")
    modules = registry.get("modules")
    if not isinstance(statuses, dict) or not statuses:
        problems.append("module registry: statusLegend must be non-empty")
        statuses = {}
    if not isinstance(controls, list) or len(controls) != len(set(controls)):
        problems.append("module registry: cvfControlVocabulary must be a unique list")
        controls = []
    elif set(controls) != CANONICAL_CVF_CONTROLS:
        problems.append("module registry: cvfControlVocabulary must contain the canonical twelve controls")
    if not isinstance(modules, list):
        problems.append("module registry: modules must be a list")
        return problems

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for index, module in enumerate(modules):
        label = f"module[{index}]"
        if not isinstance(module, dict):
            problems.append(f"{label}: record must be an object")
            continue
        module_id = module.get("id")
        if not isinstance(module_id, str) or not ID_PATTERN.fullmatch(module_id):
            problems.append(f"{label}: invalid id {module_id!r}")
            continue
        if module_id in seen_ids:
            problems.append(f"duplicate module id: {module_id}")
        seen_ids.add(module_id)
        relative = module.get("path")
        if isinstance(relative, str) and relative in seen_paths:
            problems.append(f"duplicate module path: {relative}")
        if isinstance(relative, str):
            seen_paths.add(relative)
        target = _safe_repo_path(root, relative, module_id, problems)
        if target is not None and not target.is_dir():
            problems.append(f"{module_id}: module path does not exist: {relative}")
        if module.get("status") not in statuses:
            problems.append(f"{module_id}: unknown module status {module.get('status')!r}")
        if module.get("kind") not in MODULE_KINDS:
            problems.append(f"{module_id}: unknown module kind {module.get('kind')!r}")
        for field in ("purpose", "enforcement", "nextStep"):
            if not _nonempty_string(module.get(field)):
                problems.append(f"{module_id}: {field} must be a non-empty string")
        module_controls = module.get("cvfControls")
        if not isinstance(module_controls, list):
            problems.append(f"{module_id}: cvfControls must be a list")
        elif not all(isinstance(item, str) for item in module_controls):
            problems.append(f"{module_id}: cvfControls items must be strings")
        else:
            if len(module_controls) != len(set(module_controls)):
                problems.append(f"{module_id}: cvfControls contains duplicates")
            for control in module_controls:
                if control not in controls:
                    problems.append(f"{module_id}: unknown CVF control {control!r}")
        tests = module.get("tests", [])
        if not isinstance(tests, list):
            problems.append(f"{module_id}: tests must be a list")
        elif not all(isinstance(item, str) for item in tests):
            problems.append(f"{module_id}: tests items must be strings")
        else:
            if len(tests) != len(set(tests)):
                problems.append(f"{module_id}: tests contains duplicates")
            for test_path in tests:
                target_test = _safe_repo_path(root, test_path, f"{module_id} test", problems)
                if target_test is not None and not target_test.is_file():
                    problems.append(f"{module_id}: test path does not exist: {test_path}")

    for module in modules:
        if not isinstance(module, dict) or not isinstance(module.get("id"), str):
            continue
        depends_on = module.get("dependsOn", [])
        if not isinstance(depends_on, list):
            problems.append(f"{module['id']}: dependsOn must be a list")
            continue
        if not all(isinstance(item, str) for item in depends_on):
            problems.append(f"{module['id']}: dependsOn items must be strings")
            continue
        if len(depends_on) != len(set(depends_on)):
            problems.append(f"{module['id']}: dependsOn contains duplicates")
        for dependency in depends_on:
            if dependency not in seen_ids:
                problems.append(f"{module['id']}: dependsOn unknown module {dependency!r}")
    return problems


def enrich_module_metrics(registry: dict[str, Any], root: Path = REPO_ROOT) -> dict[str, Any]:
    enriched = copy.deepcopy(registry)
    by_status: dict[str, int] = {}
    total_loc = 0
    total_files = 0
    for module in enriched["modules"]:
        metrics = compute_metrics(root / module["path"])
        module["metrics"] = metrics
        total_loc += metrics["codeLoc"]
        total_files += metrics["codeFiles"]
        by_status[module["status"]] = by_status.get(module["status"], 0) + 1
    enriched["metrics"] = {
        "computedBy": "scripts/manage_catalog.py",
        "totals": {
            "modules": len(enriched["modules"]),
            "codeLoc": total_loc,
            "codeFiles": total_files,
            "byStatus": dict(sorted(by_status.items())),
        },
    }
    return enriched


def _md_link(path: str) -> str:
    return "../" + path if not path.startswith("docs/") else path.removeprefix("docs/")


def render_index(registry: dict[str, Any]) -> str:
    artifacts = registry["artifacts"]
    lines = [
        "# Project Documentation Index",
        "",
        "> GENERATED FILE — do not edit by hand. Source: "
        "[`catalog/ARTIFACT_REGISTRY.json`](catalog/ARTIFACT_REGISTRY.json).",
        "",
        "## Start Here",
        "",
    ]
    for artifact in artifacts:
        if artifact["entrypoint"]:
            lines.append(
                f"- [{artifact['title']}]({_md_link(artifact['path'])}) — {artifact['summary']}"
            )
    lines.extend(["", "## Artifact Registry Summary", ""])
    status_counts: dict[str, int] = {}
    for artifact in artifacts:
        status_counts[artifact["status"]] = status_counts.get(artifact["status"], 0) + 1
    lines.append(f"- Registered artifacts: **{len(artifacts)}**")
    lines.append("- By status: " + ", ".join(f"{k}={v}" for k, v in sorted(status_counts.items())))

    for artifact_type in TYPE_ORDER:
        selected = [item for item in artifacts if item["type"] == artifact_type and not item["entrypoint"]]
        if not selected:
            continue
        title = artifact_type.replace("_", " ").title()
        lines.extend(["", f"## {title}", ""])
        for artifact in selected:
            lines.append(
                f"- [{artifact['title']}]({_md_link(artifact['path'])}) "
                f"— `{artifact['status']}` — {artifact['summary']}"
            )

    lines.extend(
        [
            "",
            "## Governed Artifact Families",
            "",
            "- Decisions: [`docs/decisions/`](decisions/)",
            "- Roadmaps: [`docs/roadmaps/`](roadmaps/)",
            "- Specifications: [`docs/specs/`](specs/)",
            "- Work orders: [`docs/work_orders/`](work_orders/)",
            "- Reviews and evidence: [`docs/reviews/`](reviews/)",
            "",
            "## Verification",
            "",
            "```powershell",
            "python scripts/manage_catalog.py --check",
            "python -m unittest tests.test_catalog_management -v",
            "```",
            "",
            "## Claim Boundary",
            "",
            registry["claimBoundary"],
            "",
        ]
    )
    return "\n".join(lines)


def render_module_catalog(registry: dict[str, Any]) -> str:
    totals = registry["metrics"]["totals"]
    lines = [
        "# Module Catalog",
        "",
        "> GENERATED FILE — do not edit by hand. Source: "
        "[`MODULE_REGISTRY.json`](MODULE_REGISTRY.json).",
        "",
        "## Totals",
        "",
        f"- Modules: **{totals['modules']}**",
        f"- Code LOC: **{totals['codeLoc']}**",
        f"- Code files: **{totals['codeFiles']}**",
        "- By status: " + (", ".join(f"{k}={v}" for k, v in totals["byStatus"].items()) or "none"),
        "",
        "## Status Legend",
        "",
    ]
    for status, meaning in registry["statusLegend"].items():
        lines.append(f"- **{status}** — {meaning}")
    lines.extend(["", "## Modules", ""])
    if not registry["modules"]:
        lines.append("No source-backed modules are registered. Roadmap entries are not modules.")
    else:
        lines.extend(["| Module | Path | Status | LOC | CVF controls | Purpose |", "|---|---|---|---:|---|---|"])
        for module in sorted(registry["modules"], key=lambda item: (STATUS_ORDER.get(item["status"], 9), item["id"])):
            controls = ", ".join(module["cvfControls"]) or "—"
            purpose = module["purpose"].replace("|", "\\|")
            lines.append(
                f"| `{module['id']}` | `{module['path']}` | {module['status']} | "
                f"{module['metrics']['codeLoc']} | {controls} | {purpose} |"
            )
    lines.extend(["", "## Claim Boundary", "", registry["claimBoundary"], ""])
    return "\n".join(lines)


def verify_all(root: Path = REPO_ROOT) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    artifacts = load_json(root / "docs" / "catalog" / "ARTIFACT_REGISTRY.json")
    modules = load_json(root / "docs" / "catalog" / "MODULE_REGISTRY.json")
    problems = verify_artifacts(artifacts, root) + verify_modules(modules, root)
    return artifacts, modules, problems


def run(write: bool, root: Path = REPO_ROOT) -> list[str]:
    artifacts, modules, problems = verify_all(root)
    if problems:
        return problems
    enriched = enrich_module_metrics(modules, root)
    expected_index = render_index(artifacts)
    expected_catalog = render_module_catalog(enriched)
    module_registry_path = root / "docs" / "catalog" / "MODULE_REGISTRY.json"
    index_path = root / "docs" / "INDEX.md"
    catalog_path = root / "docs" / "catalog" / "MODULE_CATALOG.md"
    if write:
        module_registry_path.write_text(json.dumps(enriched, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        index_path.write_text(expected_index, encoding="utf-8")
        catalog_path.write_text(expected_catalog, encoding="utf-8")
        return []
    if modules != enriched:
        problems.append("MODULE_REGISTRY.json metrics are stale; run --write")
    if not index_path.is_file() or index_path.read_text(encoding="utf-8") != expected_index:
        problems.append("docs/INDEX.md has drifted; run --write")
    if not catalog_path.is_file() or catalog_path.read_text(encoding="utf-8") != expected_catalog:
        problems.append("docs/catalog/MODULE_CATALOG.md has drifted; run --write")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Regenerate metrics and Markdown views")
    mode.add_argument("--check", action="store_true", help="Check registries and generated views")
    args = parser.parse_args(argv)
    problems = run(write=args.write)
    if problems:
        print("INDEX/CATALOG: FAIL")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("INDEX/CATALOG: PASS")
    print("  Generated views updated." if args.write else "  Registries and generated views are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
