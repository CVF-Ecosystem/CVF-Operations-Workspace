"""Deterministic scan-time filtering for linked Shift source.

Claim boundary: classifications are discovery metadata, not the ADR-OW-001
porting decisions PORT_AS_IS/ADAPT/REIMPLEMENT/REFERENCE_ONLY/REJECT and not
authorization to apply, import, run, or deploy any source.

Policy: all reviewable rules are loaded from filtering_policy.json; no
governance rule is hard-coded outside that file.
"""

from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

HERE = Path(__file__).resolve().parent
_POLICY_PATH = HERE / "filtering_policy.json"

HARD_EXCLUDE = "HARD_EXCLUDE"
PROTECTED_SOURCE_ONLY = "PROTECTED_SOURCE_ONLY"
QUARANTINE_REVIEW = "QUARANTINE_REVIEW"
ELIGIBLE_CANDIDATE = "ELIGIBLE_CANDIDATE"
SCAN_CLASSIFICATIONS = (HARD_EXCLUDE, PROTECTED_SOURCE_ONLY, QUARANTINE_REVIEW, ELIGIBLE_CANDIDATE)


def _load_policy() -> dict[str, Any]:
    return json.loads(_POLICY_PATH.read_bytes())


# Load policy once at import time; the sha256 of the file is validated by
# apply.py via filteringPolicySha256 in the manifest.
_POLICY: dict[str, Any] = _load_policy()

OVERSIZED_BYTES: int = int(_POLICY.get("oversizedBytes", 1_048_576))

_SECRET_PATTERNS = (
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(rb"(?i)\b(?:api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}"),
)


def _glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Convert a glob pattern (supporting *, **, ?) to a compiled regex.

    Rules:
      **/  before a path component means "zero or more directories/"
      /**  or **  at end means "this directory or any descendant"
      *    matches any chars that are NOT /
      ?    matches a single char that is NOT /
      All other chars are matched literally.

    Pattern is anchored to full-string match.
    """
    p = pattern.lower().replace("\\", "/")
    parts: list[str] = []
    i = 0
    while i < len(p):
        if p[i:i + 2] == "**":
            # Consume the **
            i += 2
            has_slash = False
            if i < len(p) and p[i] == "/":
                i += 1
                has_slash = True
            if has_slash:
                # **/ → matches zero-or-more path-components with trailing /
                parts.append("(?:.+/)?")
            else:
                # ** at end (or before end-of-string): matches anything
                parts.append(".*")
        elif p[i] == "*":
            parts.append("[^/]*")
            i += 1
        elif p[i] == "?":
            parts.append("[^/]")
            i += 1
        else:
            parts.append(re.escape(p[i]))
            i += 1
    return re.compile("^" + "".join(parts) + "$")


def _matches_pattern(lower_path: str, pattern: str) -> bool:
    """Match a path against a policy glob pattern (case-already-lowered path)."""
    p = pattern.lower().replace("\\", "/")
    # Shortcut: no wildcards → exact-or-prefix match
    if "*" not in p and "?" not in p:
        # Exact filename-only match (no slash in pattern)
        if "/" not in p:
            return PurePosixPath(lower_path).name == p
        # Exact path or directory prefix
        return lower_path == p or lower_path.startswith(p.rstrip("/") + "/")
    # Wildcard: compile to regex and match
    try:
        rx = _glob_to_regex(p)
    except re.error:
        return False
    # Also try matching just the filename if the pattern has no /
    if "/" not in p:
        return bool(rx.match(PurePosixPath(lower_path).name))
    return bool(rx.match(lower_path))


def _matches_any(lower_path: str, patterns: list[str]) -> bool:
    return any(_matches_pattern(lower_path, pat) for pat in patterns)


def _is_hard_exclude_path(lower_path: str, lower_name: str) -> bool:
    hard_paths: list[str] = _POLICY.get("hardExcludePathPatterns", [])
    if _matches_any(lower_path, hard_paths):
        return True
    # Also check filename-only patterns against the filename
    for pat in hard_paths:
        p = pat.lower()
        if "/" not in p and _matches_pattern(lower_name, p):
            return True
    name_tokens: list[str] = _POLICY.get("hardExcludeNameTokens", [])
    if any(token in lower_name for token in name_tokens):
        return True
    return False


def _is_protected_source(lower_path: str) -> bool:
    patterns: list[str] = _POLICY.get("protectedSourcePatterns", [])
    return _matches_any(lower_path, patterns)


def _is_quarantine(lower_path: str, lower_name: str, mode: str, size: int, change: str, is_binary: bool) -> bool:
    if mode in {"120000", "160000"}:
        return True
    if size > OVERSIZED_BYTES:
        return True
    if is_binary:
        return True
    if change in {"deleted", "renamed"}:
        return True
    patterns: list[str] = _POLICY.get("quarantinePatterns", [])
    if _matches_any(lower_path, patterns):
        return True
    # Also match filename-only quarantine tokens against the filename
    for pat in patterns:
        p = pat.lower()
        if "/" not in p and _matches_pattern(lower_name, p):
            return True
    return False


def _is_license_ambiguous(lower_name: str) -> bool:
    patterns: list[str] = _POLICY.get("licenseAmbiguityPatterns", [])
    return _matches_any(lower_name, patterns)


def classify(record: dict[str, Any], content: bytes | None = None) -> tuple[str, str]:
    path = str(record.get("path") or record.get("newPath") or record.get("oldPath") or "")
    normalized = path.replace("\\", "/")
    lower = normalized.lower()
    name = PurePosixPath(normalized).name.lower()
    mode = str(record.get("candidateMode") or record.get("baseMode") or "")
    change = str(record.get("changeType", "")).lower()
    size = int(record.get("size") or 0)
    is_binary = record.get("binary") is True

    # HARD_EXCLUDE: path/name rules (no raw content written to reason)
    if _is_hard_exclude_path(lower, name):
        return HARD_EXCLUDE, "HARD_PATH"
    # HARD_EXCLUDE: content scan — content must be bytes, not None
    # For deleted entries, caller must supply base blob bytes as content.
    if content is not None and any(pattern.search(content) for pattern in _SECRET_PATTERNS):
        return HARD_EXCLUDE, "SECRET_CONTENT"

    # PROTECTED_SOURCE_ONLY
    if _is_protected_source(lower):
        return PROTECTED_SOURCE_ONLY, "PROTECTED_GOVERNANCE_SOURCE"

    # QUARANTINE_REVIEW: binary/oversized/mode/deleted/renamed/pattern
    if _is_quarantine(lower, name, mode, size, change, is_binary):
        return QUARANTINE_REVIEW, "REVIEW_REQUIRED"

    # QUARANTINE_REVIEW: license ambiguity
    if _is_license_ambiguous(name):
        return QUARANTINE_REVIEW, "LICENSE_AMBIGUOUS"

    return ELIGIBLE_CANDIDATE, "DEFAULT_ELIGIBLE"
