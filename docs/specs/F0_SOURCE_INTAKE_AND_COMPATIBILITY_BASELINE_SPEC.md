# F0 Source Intake and Compatibility Baseline Specification

- Spec ID: `OW-F0-SPEC-001`
- Date: 2026-07-23
- Status: AUTHORIZED
- Risk: R2
- Implements: `ADR-OW-001`, roadmap F0

## Objective

Produce a reproducible, secret-safe and machine-checkable basis for deciding
which Shift assets may later be ported. F0 imports no runtime source.

## Inputs

1. Source repository: `shift-operations-workspace`.
2. Initial source pin: `f98f29e145fa002be070e9d44520d20f0f82dcb3`.
3. Claude assessment, identified by SHA-256
   `168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2`.
4. Review bundle manifest, identified by SHA-256
   `7f4632c437058a814de4ce70d47b8234fdc2c94edfe8c8c4e577231749c84283`.

The assessment and bundle are reference inputs. Git-tracked source at the full
pin is the only source-code authority.

## Functional requirements

- FR-01: Capture from a detached temporary worktree at the exact source pin.
- FR-02: Refuse a missing, abbreviated, unreachable or changed source pin.
- FR-03: Do not read source `.env`, credentials, local bindings or ignored
  files; inventory paths from Git objects and allowlisted tracked files.
- FR-04: Record tracked source path, blob SHA-256, size and candidate class.
- FR-05: Record public HTTP methods/paths for every application ingress,
  including integration-edge.
- FR-06: Record database migration order and SHA-256 without executing them.
- FR-07: Record application roots, package roots and import/dependency edges.
- FR-08: Record Module Registry status without promoting any module.
- FR-09: Record test commands and outcomes with `PASS`, `FAIL`, `BLOCKED`, or
  `NOT_RUN`; never convert absence into success.
- FR-10: Produce an import ledger whose every candidate has one ADR-defined
  disposition and a reviewer field.
- FR-11: Normalize repository-relative paths to `/` in all artifacts.
- FR-12: Fail non-zero on dirty temporary inputs, duplicate ledger paths,
  missing hashes, unclassified candidates, or self-scan violations.
- FR-13: Exclude caches, build outputs, generated evidence, local continuity,
  secrets and provider transcripts from import candidacy.
- FR-14: Leave both source repository and source commit untouched.
- FR-15: Do not create `apps/`, `packages/` or `database/` in the target.
- FR-16: Register discoverable F0 artifacts in Artifact Registry and regenerate
  Index; never hand-edit generated Index or modify Module Registry.

## Import ledger minimum schema

```text
source_repository
source_commit
source_path
source_sha256
target_path
disposition
rationale
license_status
dependency_impact
behavioral_evidence
review_status
```

## Required evidence

- exact source pin reachability;
- source and target Git status before/after;
- inventory hashes and deterministic rerun comparison;
- route and migration snapshots;
- module-status summary;
- negative tests for Windows separators, dirty input, self-reference,
  credential-like URL redaction and unclassified candidates;
- target workspace doctor and `git diff --check`.

## Acceptance criteria

- AC-01 through AC-15 correspond one-to-one with FR-01 through FR-15.
- AC-16: two consecutive captures at the same pin are byte-identical except
  for explicitly separated runtime timestamps.
- AC-17: no raw secret value appears in stdout, evidence or repository diff.
- AC-18: independent review confirms no runtime source was imported.
- AC-19: Artifact Registry and generated Index agree; Module Registry remains
  unchanged and empty.

## Non-goals

- source copying or adaptation;
- dependency installation solely to run imported code;
- database execution or provider call;
- GitHub rename, Shift repository mutation or cutover;
- platform/module implementation claims.
