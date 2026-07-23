"""Test-command outcome taxonomy for F0 source intake (FR-09).

F0 does not install the source repository's dependencies (that is an
explicit non-goal — installing dependencies "solely to run imported code"
is out of scope). Commands are attempted as-is in the detached worktree;
when they fail because the environment lacks a tool or dependency, that is
recorded as BLOCKED, never silently converted into PASS or hidden as
NOT_RUN. A real, non-environmental test failure is FAIL. A command whose
binary cannot be located at all is NOT_RUN.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import redact as si_redact  # noqa: E402

CANDIDATE_COMMANDS: list[list[str]] = [
    [sys.executable, "-m", "pytest", "-q"],
    ["pnpm", "run", "tree"],
    ["pnpm", "run", "test"],
    ["pnpm", "run", "build:web"],
]

_MISSING_DEPENDENCY_SIGNATURES = (
    "modulenotfounderror",
    "no module named",
    "cannot find module",
    "err_module_not_found",
    "importerror",
    "enoent",
    "npm err",
    "eresolve",
)

_EXCERPT_LIMIT = 500


def _excerpt(text: str) -> str:
    redacted = si_redact.redact_credential_urls(text)
    return redacted[-_EXCERPT_LIMIT:].strip()


def _classify(returncode: int | None, combined_output: str) -> tuple[str, str]:
    lowered = combined_output.lower()
    if returncode == 0:
        return "PASS", "command exited 0"
    if any(signature in lowered for signature in _MISSING_DEPENDENCY_SIGNATURES):
        return (
            "BLOCKED",
            "dependency or tool unavailable in this environment; F0 does not "
            f"install dependencies: {_excerpt(combined_output)}",
        )
    return "FAIL", f"command exited non-zero ({returncode}): {_excerpt(combined_output)}"


def run_command(command: list[str], cwd: Path, timeout: int = 120) -> dict:
    """Run one candidate command in ``cwd`` and classify its outcome.

    Never raises for expected failure modes (missing binary, timeout,
    non-zero exit); those all become a taxonomy entry instead.
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return {"command": command, "status": "NOT_RUN", "reason": f"tool not found: {command[0]}"}
    except subprocess.TimeoutExpired:
        return {"command": command, "status": "BLOCKED", "reason": f"timed out after {timeout}s"}

    status, reason = _classify(result.returncode, result.stdout + result.stderr)
    return {"command": command, "status": status, "reason": reason}


def run_all(worktree: Path, commands: list[list[str]] | None = None) -> list[dict]:
    selected = commands if commands is not None else CANDIDATE_COMMANDS
    return [run_command(command, worktree) for command in selected]
