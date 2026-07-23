# Work Order — F0 Source Intake and Compatibility Baseline

- Work order ID: `OW-F0-WO-001`
- Date: 2026-07-23
- Status: AUTHORIZED
- Phase: WORK_ORDER
- Risk: R2
- Governing spec: `OW-F0-SPEC-001`
- Commit ownership: COMMIT_STEWARD only
- Authorization: owner instruction to hand work to the implementation worker,
  recorded 2026-07-23 after REVIEWER amendment `OW-F0-WO-001-A1`

## Authority boundary

This work order is a ceiling, not a target. The implementation worker may
create only what is necessary to satisfy F0. It may not begin until an
independent reviewer records authorization.

## Roles

- ORCHESTRATOR: routes scope and stop conditions.
- IMPLEMENTATION_WORKER: builds the bounded F0 tooling and evidence.
- REVIEWER: a different agent independently checks source, tests and claims.
- COMMIT_STEWARD: explicitly stages approved paths and owns commits/pushes.
- SESSION_SYNC_STEWARD: synchronizes canonical continuity after disposition.

## Authorized changed-set ceiling

```text
docs/architecture/**
docs/reviews/F0_*
provenance/shift-operations/**
scripts/source_intake/**
tests/source_intake/**
docs/catalog/ARTIFACT_REGISTRY.json
docs/INDEX.md  # generated only
IMPLEMENTATION_STATUS.json
CVF_SESSION/ACTIVE_SESSION_STATE.json
CVF_SESSION/handoffs/**
```

The worker must not modify existing planning artifacts unless a reviewer
finding explicitly authorizes a repair amendment.

## Explicit exclusions

```text
apps/**
packages/**
database/**
.github/**
.cvf/**
AGENTS.md
docs/catalog/MODULE_REGISTRY.json
docs/catalog/MODULE_CATALOG.md
secrets and provider configuration
source repository files
review-bundle files
```

No `git add .`, `git add -A`, amend, rebase, force-push, source-repository
commit, provider call or secret read is authorized.

## Build tasks

1. Record worker acknowledgment and transition to IMPLEMENTATION_WORKER.
2. Create a detached temporary worktree at the exact source pin.
3. Implement deterministic, cross-platform source-intake tooling.
4. Generate route, migration, dependency, module and file inventories.
5. Generate a complete import ledger with conservative default disposition.
6. Add negative tests covering the five lessons from the old verifier plus
   secret-safe URL handling and unclassified candidates.
7. Register discoverable F0 artifacts, regenerate Index, and prove catalog
   `--check` passes without changing Module Registry.
8. Run the evidence matrix and leave all changes unstaged for review.
9. Stop at `READY_FOR_INDEPENDENT_F0_REVIEW`.

## Evidence matrix

| Acceptance group | Evidence |
|---|---|
| AC-01–04 | full-pin/worktree/file inventory tests and receipts |
| AC-05–08 | routes, migrations, dependencies and module snapshot |
| AC-09–13 | outcome taxonomy, ledger validation and negative tests |
| AC-14–15 | before/after source status and forbidden-target scan |
| AC-16 | deterministic two-run comparison |
| AC-17 | secret-pattern scan with values redacted |
| AC-18 | independent changed-set and claim-boundary review |

## Commit plan

After REVIEW_PASS only:

1. `C1`: source-intake tooling and tests.
2. `C2`: generated provenance/baseline evidence.
3. `C3`: review receipt and continuity closure.

Each commit stages an explicit allowlist. The COMMIT_STEWARD verifies the
staged diff, file-size guard, doctor, tests and repository status before each
commit. Push occurs only after the final post-commit review.

## Rollback rehearsal

After each proposed commit and before push, COMMIT_STEWARD creates a temporary
worktree from the parent, applies the commit(s), runs the relevant checks, then
removes the temporary worktree. No destructive reset of the primary worktree.

## Stop conditions

Stop immediately on source-pin drift, dirty detached input, secret exposure,
license ambiguity, unexpected route/database surface, nondeterministic output,
scope expansion, source mutation, catalog/continuity conflict, test failure
that cannot be repaired inside scope, or any need to import runtime source.

## Completion boundary

F0 FREEZE proves only that the source baseline and import decisions are
reproducible. It does not authorize an asset import or claim that any platform
or Shift runtime capability exists in this repository.
