# Work Order — F1A Versioned Contract Foundation

- Work Order ID: `OW-F1A-WO-001`
- Date: 2026-07-24
- Implements: `ADR-OW-005`, `OW-F1A-SPEC-001`
- Status: DRAFT (pending independent REVIEW_PASS)

## Repair note (round 1, 2026-07-24)

Independent Codex review returned `F1A_AUTHORIZATION_REVIEW_FAIL`
(`F1A-R1` through `F1A-R5`, full detail in `ADR-OW-005`'s repair note). This
work order is repaired accordingly:

- **F1A-R1** — the "Validator dependency manifest/lock (new)" entry below is
  rewritten from a one-package description to the exact, real 19-package
  hash-pinned closure authorized in `ADR-OW-005` Decision 12, with an
  isolated-environment install policy.
- **F1A-R5** — the Module Registry entry below is replaced with the exact
  authorized JSON, verbatim; "something like" is removed.
- **F1A-R2/R3/R4** are bound at the ADR/spec level (Decisions 3/5/6/12,
  `F1A-AC-10`/`F1A-AC-11`/`F1A-AC-30`/`F1A-AC-31`); this work order's stop
  conditions are expanded to name their exact triggers explicitly.

Repaired inside the same six-path ceiling; no seventh path. Role:
`REPAIR_WORKER`. Codex retains independent `REVIEWER`/`COMMIT_STEWARD`
authority; this round does not self-grant REVIEW_PASS.

## Role route

```text
ORCHESTRATOR -> SPEC_AUTHOR -> WORK_ORDER_AUTHOR (Claude, this authorization
round) -> REVIEWER -> COMMIT_STEWARD (C1, Codex) -> IMPLEMENTATION_WORKER
(BUILD) -> REVIEWER -> REPAIR_WORKER if needed -> RE_REVIEW ->
COMMIT_STEWARD (C2) -> REVIEWER (independent review receipt) ->
COMMIT_STEWARD (C3) -> COMMIT_STEWARD (C4, post-push closure sync only) ->
CLOSER -> SESSION_SYNC_STEWARD -> ORCHESTRATOR
```

Claude holds ORCHESTRATOR -> SPEC_AUTHOR -> WORK_ORDER_AUTHOR only, this
round. Claude does not self-grant REVIEW_PASS, does not stage/commit/push,
and does not author the independent review receipt, this round or any later
one under this work order.

## Authorization-round changed set (this round only — authoring, not BUILD)

Exactly six paths, no seventh:

1. `docs/decisions/ADR_2026-07-24_F1A_VERSIONED_CONTRACT_FOUNDATION.md`
2. `docs/specs/F1A_VERSIONED_CONTRACT_FOUNDATION_SPEC.md`
3. `docs/work_orders/F1A_VERSIONED_CONTRACT_FOUNDATION_WORK_ORDER.md`
4. `IMPLEMENTATION_STATUS.json`
5. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
6. `CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-07-23.md`

Not touched this round: canonical roadmap, `docs/catalog/**`, `docs/INDEX.md`,
`contracts/**`, `tests/**`, `scripts/**`, `apps/**`, `packages/**`,
`database/**`, `provenance/**`, `.cvf/**`, `AGENTS.md`, either read-only input
repository/folder.

## BUILD changed-set ceiling (authorized only after Codex REVIEW_PASS on this package)

Every path named exactly — not a wildcard grant:

**Schema files (new):**

- `contracts/core/common-definitions.schema.json`
- `contracts/core/profile-manifest.schema.json`
- `contracts/core/operational-session.schema.json`
- `contracts/core/command-envelope.schema.json`
- `contracts/core/event-envelope.schema.json`
- `contracts/core/capability-manifest.schema.json`

**Validator dependency manifest/lock (new, corrected `F1A-R1`):**

- `requirements-contract-validator.txt` (repository root — one file, but not
  one package: lists all **19** packages from `ADR-OW-005` Decision 12's
  table — `jsonschema[format-nongpl]==4.26.0` and its full transitive
  closure — each with an exact `==` pin and a `--hash=sha256:...` line
  matching the table exactly). Installed with
  `pip install --require-hashes -r requirements-contract-validator.txt`
  into a temporary, isolated virtual environment created solely for the
  F1A contract test run — never the user/global Python environment.
  `--no-deps` is never used. BUILD evidence must record the real install
  output (or an equivalently reproducible transcript), not merely restate
  the table.

**Test file (new):**

- `tests/contracts/test_f1a_contracts.py` (single file: meta-schema
  validation, offline `$ref` resolution scan, positive/negative fixtures per
  `F1A-AC-06` through `F1A-AC-22`, provider-token scan, claim-boundary
  assertions per `F1A-AC-23`)
- `tests/contracts/__init__.py` (empty, package marker only, if required by
  the test discovery pattern already in use)

**BUILD evidence file (new):**

- `docs/reviews/F1A_BUILD_EVIDENCE_2026-07-24.md`

**Module Registry and generated Module Catalog (conditional — only if
`F1A-AC-25` and the Golden schema permit it; exact entry, corrected
`F1A-R5`):**

- `docs/catalog/MODULE_REGISTRY.json` — append exactly this entry, verbatim,
  no paraphrase or reordering of content:

  ```json
  {
    "id": "contracts-core-f1a",
    "name": "F1A Core Contract Foundation",
    "path": "contracts/core",
    "status": "CONTRACT_ONLY",
    "description": "Versioned closed JSON Schema contracts for the provider-neutral operations-workspace core; no runtime enforcement.",
    "evidence": "contracts/core/*.schema.json; tests/contracts/test_f1a_contracts.py; docs/reviews/F1A_BUILD_EVIDENCE_2026-07-24.md",
    "controls": [],
    "dependencies": []
  }
  ```

  Added only after all F1A contract tests pass.
- `docs/catalog/MODULE_CATALOG.md` (generated only, via
  `scripts/manage_cvf_downstream_catalog.ps1 -Write` — never hand-edited)

**Continuity/status paths (BUILD-time updates):**

- `IMPLEMENTATION_STATUS.json`
- `CVF_SESSION/ACTIVE_SESSION_STATE.json`
- `CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-07-23.md`

No other path — `docs/roadmaps/**`, `docs/INDEX.md`,
`docs/catalog/ARTIFACT_REGISTRY.json`, `apps/**`, `packages/**`,
`database/**`, any API route, any provider adapter, `.cvf/**`, `AGENTS.md`,
either read-only input repository/folder — may be touched by BUILD.

## C3 closure ceiling (owned exclusively by Codex — IMPLEMENTATION_WORKER may not author or modify)

- `docs/reviews/F1A_INDEPENDENT_REVIEW_2026-07-24.md` (the independent
  review receipt itself)
- `IMPLEMENTATION_STATUS.json`
- `CVF_SESSION/ACTIVE_SESSION_STATE.json`
- `CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-07-23.md`

Consistent with the `OW-G2-WO-001`/`OW-RM1-WO-001` precedent: the same three
continuity paths appear in both the IMPLEMENTATION_WORKER BUILD ceiling and
the C3 closure ceiling because both roles may need to update them at
different points in the sequence, but only Codex may create or edit the
independent review receipt itself, under any circumstance.

## Explicit exclusions (stop and escalate if touched)

`docs/roadmaps/CVF_OPERATIONS_WORKSPACE_ROADMAP.md`, `docs/catalog/ARTIFACT_REGISTRY.json`,
`docs/INDEX.md`, `.cvf/manifest.json`, `AGENTS.md`, any file under `apps/`,
`packages/`, `database/`, any API route or provider-adapter source, the
`shift-operations-workspace` read-only repository, the
`operations-workspace-all-phases`/`operations-workspace-review-baseline`
read-only folders, and the CVF core repository.

## Module Registry rule

If BUILD succeeds: register **exactly one** source-backed contract module,
only if `docs/catalog/schemas/MODULE_REGISTRY.schema.json`'s closed schema
permits representing it (it does — `CONTRACT_ONLY` is an enumerated status,
Decision confirmed by reading the schema this round). Status must be
`CONTRACT_ONLY`; evidence must name real schema and test file paths, never a
plan or prompt. Do not claim `PARTIAL` or `ENFORCED`. Module Catalog must be
regenerated using `scripts/manage_cvf_downstream_catalog.ps1 -Write` only. If
a catalog/schema conflict is found (e.g. the closed schema cannot represent
the claim honestly), BUILD stops and reports rather than inventing a new
status value or hand-editing the generated catalog.

## Roles and ownership

- **IMPLEMENTATION_WORKER** (provider-neutral role contract): authors the
  six schema files, the validator dependency manifest, the test file, the
  BUILD evidence file, and the conditional Module Registry/Catalog change,
  strictly inside the BUILD ceiling above. Does not stage, commit, push,
  amend, self-approve REVIEW_PASS, or declare FREEZE. Does not author or
  modify the C3 closure ceiling's independent review receipt.
- **REVIEWER / COMMIT_STEWARD** (Codex, independent from
  IMPLEMENTATION_WORKER for this R2 risk tranche): reviews this
  authorization package (C1), reviews the BUILD (before C2), authors the
  independent review receipt and closure continuity (C3), and performs
  post-push closure synchronization (C4).

## Tasks (this authorization round)

1. Author `ADR-OW-005`, `OW-F1A-SPEC-001`, `OW-F1A-WO-001`.
2. Record the F1A authorization entry in the active handoff and set
   continuity (`IMPLEMENTATION_STATUS.json`,
   `CVF_SESSION/ACTIVE_SESSION_STATE.json`) to `WORK_ORDER`/`WORK_ORDER_AUTHOR`,
   awaiting Codex REVIEWER.
3. Do not touch `docs/catalog/**`, `docs/INDEX.md`, the roadmap, `contracts/**`,
   `tests/**`, `scripts/**`, or either read-only input.

## Commit plan (owned exclusively by Codex COMMIT_STEWARD)

- **C1 — Authorization package.** Stages exactly the 6 authorization-round
  paths above, plus authorization continuity. Explicit-path staging only.
  Created by Codex. Rehearsed post-commit/pre-push in a temporary sibling
  worktree. Pushed only after PASS.
- **C2 — BUILD deliverables.** Stages exactly the BUILD-ceiling paths that
  were actually created/changed (schema files, validator manifest, test
  file, BUILD evidence, conditional Module Registry/Catalog change), plus
  the BUILD self-report continuity update. Same explicit-path staging,
  rehearsal, and push-after-PASS discipline as C1.
- **C3 — Independent review receipt and FREEZE-pending continuity.** Stages
  exactly the C3 closure ceiling: the independent review receipt plus the
  three continuity paths, synchronized to record REVIEW_PASS and FREEZE
  disposition. Same rehearsal/push discipline.
- **C4 — Post-C3-push closure synchronization.** A commit cannot truthfully
  record its own future push: C3's continuity text can state "C3 passed
  rehearsal and is ready to push," but not "C3 has been pushed," until after
  the fact. C4 exists solely to synchronize the already-observed C3
  rehearsal/push result into continuity (the same three paths as C3's
  closure ceiling) — it must not change any BUILD content, schema file,
  test file, or evidence file. Same rehearsal/push discipline.

Every commit:

1. Explicit-path staging only (`git add <path> <path> ...`, never `git add -A`
   or `git add .`).
2. Commit created by Codex.
3. Post-commit/pre-push sibling-worktree rehearsal.
4. Push only after the rehearsal PASSes.
5. No amend, rebase, force-push, `git add .`, or `git add -A`, ever.

## Stop conditions

- Target/core/source pin drift (any of the three verified pins in
  `ADR-OW-005` no longer matches at BUILD time).
- Dirty or mutated read-only input (`shift-operations-workspace`,
  `operations-workspace-all-phases`, `operations-workspace-review-baseline`).
- Contract namespace/version ambiguity (a schema needed that doesn't fit the
  `$id`/version scheme cleanly).
- Incompatible contract evolution (a change that would require a MAJOR bump
  discovered mid-BUILD without a fresh authorization round).
- Unresolved opaque-payload boundary (a need for a third opaque field beyond
  `metadata`/`payload` not named/bounded/justified in `ADR-OW-005`).
- Unresolved validator dependency (any of `ADR-OW-005` Decision 12's 19
  pinned packages cannot be reproduced with an exact version and verified
  `sha256` hash at BUILD time) — `BLOCKED_VALIDATOR_DEPENDENCY`. Named
  triggers (corrected `F1A-R1`, not exhaustive but each independently
  sufficient to stop): dependency-resolution drift (BUILD's own resolution
  yields a different 19-package closure, a different version, or a
  different hash than Decision 12's table); a missing compatible wheel for
  the authorized `CPython 3.13`/`win_amd64` combination; any unpinned
  (non-`==`) dependency; any missing or unverifiable hash; a source-build
  fallback for any of the 19 packages; an attempted `--no-deps` workaround
  to bypass a hash mismatch or unresolvable dependency; or installation
  into the user/global Python environment instead of a temporary isolated
  one.
- Remote `$ref` requirement (any schema needs to reference something outside
  the six local files).
- Provider-specific coupling (`F1A-AC-22` fails).
- Schema or catalog conflict (Golden Module Registry schema cannot represent
  the `CONTRACT_ONLY` claim as intended).
- Inability to validate against the selected meta-schema (`F1A-AC-04` fails
  for any file).
- Negative tests unexpectedly passing (a fixture meant to be rejected is
  accepted — investigate before treating any negative case as satisfied).
- Module Registry overclaim (any status other than `CONTRACT_ONLY`
  attempted).
- Need for runtime implementation (any temptation to write an importable
  Python module, API route, or state-machine handler under this ceiling).
- Continuity conflict (state, handoff, and status disagree — stop at INTAKE
  per `AGENTS.md`, do not choose one silently).
- Secret exposure.
- Provider call becoming necessary (none is required by this spec; if one
  seems needed, stop and escalate rather than assume).
- Changed-set expansion (any path outside this document's ceilings).

## Completion boundary

This work order authorizes: authoring six closed JSON Schema contract files,
one pinned validator dependency manifest, one test file, one BUILD evidence
file, and — conditionally — one Module Registry entry plus a generated
Module Catalog update. It does not authorize any runtime implementation,
database change, API route, profile registry runtime, session state-machine
runtime, command handler, provider adapter, frontend change, deployment, or
any F1B+ work. BUILD may begin only after this package (`ADR-OW-005`,
`OW-F1A-SPEC-001`, `OW-F1A-WO-001`) is independently reviewed, REVIEW_PASS'd,
and C1 is committed, rehearsed, and pushed.
