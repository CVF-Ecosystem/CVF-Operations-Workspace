# F1A Independent Review and FREEZE Disposition

- Review ID: `F1A-INDEPENDENT-REVIEW-2026-07-24`
- Work order: `OW-F1A-WO-001`
- Authorization C1: `d731762a9e135b075261831ed7eb0df4badc98dd`
- BUILD C2: `9e59cfdcf3d1da2644540088e748123cd41f14e9`
- Reviewer: Codex, independent from the Claude IMPLEMENTATION_WORKER
- Risk: R2
- Result: `REVIEW_PASS`

## Scope reviewed

The review compared ADR-OW-005, OW-F1A-SPEC-001 and OW-F1A-WO-001 against:

- six versioned JSON Schema 2020-12 files under `contracts/core/`;
- the exact 19-package validator lock;
- 61 new contract tests and the 116 pre-existing tests;
- F1A BUILD evidence;
- the exact `CONTRACT_ONLY` Module Registry entry and generated Module
  Catalog;
- continuity, changed-set, protected-path and repository gates.

## Independent verification

- `F1A-AC-01` through `F1A-AC-31`: PASS.
- Fresh CPython 3.13/win_amd64 virtual environment:
  `pip install --require-hashes` PASS.
- `pip check`: no broken requirements.
- Installed freeze: exactly the authorized 19 package/version pairs.
- `FormatChecker`: `date-time` registered; valid timestamp accepted and
  invalid month/day/hour timestamps rejected.
- Full suite: 177/177 PASS.
- Golden downstream catalog: PASS.
- Workspace doctor: PASS 25/25.
- JSON parsing and `git diff --check`: PASS.
- Six schema files and URN identifiers: exact.
- No remote `$ref`; offline registry resolution: PASS.
- Closed contract-owned objects, bounded opaque namespaces, stable-release
  SemVer and negative fixtures: PASS.
- Module Registry: exactly one entry,
  `contracts-core-f1a` / `CONTRACT_ONLY`.
- Target/core/source pins and protected paths: unchanged.

## Finding and repair

`F1A-BR1 — FORMAT_EXTRA_NOT_MATERIALIZED`

The worker lock initially contained `jsonschema==4.26.0`; authorization
required `jsonschema[format-nongpl]==4.26.0`. Although all extra dependencies
were explicitly present and tests passed, equivalent behavior was not accepted
as a substitute for the exact authorized expression.

A bounded reviewer amendment changed only the expression, retaining the exact
version, hash and remaining 18 package lines. A fresh isolated install and all
177 tests and repository gates passed afterward.

Disposition: closed without waiver.

## Claim boundary

F1A freezes versioned, closed, offline-resolvable contract/schema truth only.
It does not implement or prove an OperationalSession runtime state machine,
command execution, governance enforcement, provider behavior, profile
registry, database, API, frontend, deployment or any F1B+ capability.

No AI-provider call was required or made because no claim that CVF controls AI
or agent behavior is asserted.

## FREEZE disposition

`REVIEW_PASS`; FREEZE is authorized after this C3 receipt and synchronized
continuity pass post-commit/pre-push rehearsal and C3 is pushed. A separate C4
continuity-only commit records the successful C3 push because C3 cannot
truthfully record its own future push.
