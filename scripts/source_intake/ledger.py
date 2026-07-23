"""Import ledger construction and validation for F0 source intake (FR-10).

ADR-OW-001 defines exactly five dispositions. F0 imports no runtime source,
so it never assigns PORT_AS_IS, ADAPT or REIMPLEMENT itself — those require
a human/reviewer decision in a later, dedicated work order. F0's own rule
engine only ever emits REFERENCE_ONLY (safe default for real, reviewable
content) or REJECT (binaries, and a final catch-all for anything matching
no inclusion rule). Every row gets exactly one disposition: nothing is
left blank, and nothing is silently dropped.
"""

from __future__ import annotations

import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import paths as si_paths  # noqa: E402

VALID_DISPOSITIONS = {"PORT_AS_IS", "ADAPT", "REIMPLEMENT", "REFERENCE_ONLY", "REJECT"}

_REQUIRED_FIELDS = (
    "source_repository", "source_commit", "source_path", "source_sha256",
    "target_path", "disposition", "rationale", "license_status",
    "dependency_impact", "behavioral_evidence", "review_status",
)

_LICENSE_STATUS = "NOT_ASSESSED_SAME_OWNER_INTERNAL_REPOSITORY"
_DEPENDENCY_IMPACT_NOT_IMPORTED = "none_not_imported"
_BEHAVIORAL_EVIDENCE_NOT_EXECUTED = "not_executed_f0_imports_no_runtime_source"
_REVIEW_STATUS_PENDING = "PENDING_REVIEWER"


def _default_disposition(record: dict) -> tuple[str, str]:
    candidate_class = record["candidate_class"]
    if record.get("is_binary"):
        return (
            "REJECT",
            "Binary asset carries no text-diff provenance value for F0; "
            "reviewer may reclassify with explicit evidence.",
        )
    if candidate_class == "database_migration":
        return (
            "REFERENCE_ONLY",
            "Database migrations require a dedicated compatibility and "
            "rollback work order per ADR-OW-001; not portable via generic "
            "asset review.",
        )
    if candidate_class == "test_code":
        return (
            "REFERENCE_ONLY",
            "Test evidence is only meaningful alongside the implementation "
            "it verifies; import together in a future dedicated work order, "
            "not standalone.",
        )
    if candidate_class == "contract_or_schema":
        return (
            "REFERENCE_ONLY",
            "Contract/policy definitions inform target design, but "
            "ADR-OW-001 forbids batch folder moves; requires independent "
            "authorship review.",
        )
    if candidate_class in {"application_code", "package_code"}:
        return (
            "REFERENCE_ONLY",
            "Runtime source; F0 makes no import decision. Candidate for a "
            "future F1+ work order pending architecture-boundary placement "
            "(core/profile/capability).",
        )
    if candidate_class == "configuration":
        return (
            "REFERENCE_ONLY",
            "Tooling/config baseline informs target environment setup but "
            "must be authored fresh for this repository's own dependency "
            "and CI identity.",
        )
    if candidate_class in {"documentation", "ci_or_governance"}:
        return "REFERENCE_ONLY", "Retained as reference input; not source code."
    if candidate_class == "lock_or_dependency_manifest":
        return (
            "REFERENCE_ONLY",
            "Dependency manifest is informative only; this repository's "
            "dependency identity must be authored independently.",
        )
    return (
        "REJECT",
        "No matching inclusion rule; default-safe rejection pending "
        "explicit reviewer classification.",
    )


def build_ledger(inventory: list[dict], source_repository: str, source_commit: str) -> list[dict]:
    """Build one ledger row per inventory record, sorted by source_path."""
    rows: list[dict] = []
    for record in sorted(inventory, key=lambda item: item["source_path"]):
        disposition, rationale = _default_disposition(record)
        rows.append(
            {
                "source_repository": source_repository,
                "source_commit": source_commit,
                "source_path": record["source_path"],
                "source_sha256": record["sha256"],
                "target_path": None,
                "disposition": disposition,
                "rationale": rationale,
                "license_status": _LICENSE_STATUS,
                "dependency_impact": _DEPENDENCY_IMPACT_NOT_IMPORTED,
                "behavioral_evidence": _BEHAVIORAL_EVIDENCE_NOT_EXECUTED,
                "review_status": _REVIEW_STATUS_PENDING,
            }
        )
    return rows


def validate_ledger(rows: list[dict]) -> list[str]:
    """Return a list of problems; empty means the ledger is valid.

    Checks: every required field present, unique source_path, non-empty
    hash, disposition in the closed ADR vocabulary, target_path is null
    (F0 never assigns one), and no path contains a backslash.
    """
    problems: list[str] = []
    seen_paths: set[str] = set()
    for index, row in enumerate(rows):
        label = f"ledger[{index}]"
        missing = [field for field in _REQUIRED_FIELDS if field not in row]
        if missing:
            problems.append(f"{label}: missing required field(s): {missing}")
            continue
        source_path = row["source_path"]
        if not source_path:
            problems.append(f"{label}: source_path must be non-empty")
        elif si_paths.contains_backslash(source_path):
            problems.append(f"{label}: source_path must use '/' separators: {source_path!r}")
        if source_path in seen_paths:
            problems.append(f"duplicate ledger source_path: {source_path}")
        seen_paths.add(source_path)
        if not row.get("source_sha256"):
            problems.append(f"{label} ({source_path}): missing source_sha256")
        if row["disposition"] not in VALID_DISPOSITIONS:
            problems.append(
                f"{label} ({source_path}): unclassified/invalid disposition {row['disposition']!r}"
            )
        if row["target_path"] is not None:
            problems.append(
                f"{label} ({source_path}): F0 must not assign a target_path, got {row['target_path']!r}"
            )
        if not row.get("rationale"):
            problems.append(f"{label} ({source_path}): rationale must be non-empty")
    return problems
