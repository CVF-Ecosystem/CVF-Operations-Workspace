# F0 Build Evidence — Source Intake and Compatibility Baseline

- Work order: `OW-F0-WO-001` (+ amendment `OW-F0-WO-001-A1`)
- Spec: `OW-F0-SPEC-001`
- Role: IMPLEMENTATION_WORKER
- Authority for this document: worker self-report, pending independent
  REVIEWER disposition. Not a REVIEW_PASS claim.
- Source pin: `f98f29e145fa002be070e9d44520d20f0f82dcb3`
  (`shift-operations-workspace`, branch `main`, verified as a full,
  reachable, unambiguous SHA — see AC-02 evidence below)

## 1. What was built

```text
scripts/source_intake/
  paths.py            path normalization, escape guard, self-scan guard, forbidden-target guard
  redact.py            credential-safe URL redaction (fixes a multi-'@' leak the old verifier had)
  git_pin.py            full-SHA verification, dirty-worktree guard, detached-worktree lifecycle
  inventory.py          tracked-file inventory, SHA-256, candidate classification, exclusions
  routes.py              app-agnostic FastAPI ingress discovery (AST-based)
  migrations.py          migration order + SHA-256 (no execution)
  dependency_graph.py    app/package roots + local import edges (AST-based, no hardcoded names)
  module_snapshot.py     read-only snapshot of the source's Module Registry
  test_outcomes.py       PASS/FAIL/BLOCKED/NOT_RUN taxonomy for candidate test commands
  ledger.py              import ledger builder + validator (closed 5-value disposition vocabulary)
  capture.py             CLI orchestrator; owns the temporary-worktree lifecycle end to end

tests/source_intake/    8 test files + __init__.py, 104 tests, all passing

docs/architecture/PLATFORM_BOUNDARY_AND_PORTING_RULES.md
provenance/shift-operations/f98f29e145fa002be070e9d44520d20f0f82dcb3/
  capture_receipt.json, capture_timing.json, file_inventory.json,
  exclusions.json, routes.json, migrations.json, dependency_graph.json,
  module_registry_snapshot.json, test_outcomes.json, import_ledger.json
```

Line counts after independent-review repair (largest file: 262 lines; ceiling
is 600):

```text
inventory.py 262, test_inventory.py 225, capture.py 203,
test_capture_integration.py 181, ledger.py 153, test_git_pin.py 137,
test_routes_and_migrations.py 134, test_ledger.py 123, git_pin.py 110,
routes.py 103, PLATFORM_BOUNDARY_AND_PORTING_RULES.md 97, paths.py 93,
dependency_graph.py 92, test_outcomes.py 89, test_paths.py 76,
module_snapshot.py 64, test_redact.py 61, migrations.py 45, redact.py 35
```

## 2. Real-repository capture result

Captured from a detached worktree at the exact pin, against the actual
`shift-operations-workspace` repository (not a fixture):

```text
tracked_files_inventoried: 577
tracked_files_excluded:      3  (.env.example, docs/security/CREDENTIAL_MANAGEMENT.md,
                                  tests/cvf/test_auth_config_secret_validation.py)
routes_discovered:          16  (14 workspace-api + 2 integration-edge: GET /health, POST /webhooks/generic)
migrations_discovered:       3
import_edges_discovered:     3  (workspace-api -> cvf-runtime, operations-domain, operations-ledger)
test_commands_attempted:     4  (pytest -q: PASS; three pnpm commands: NOT_RUN, pnpm not installed)
import_ledger rows:        577  (576 REFERENCE_ONLY, 1 REJECT after the first classifier pass;
                                  577 REFERENCE_ONLY, 0 REJECT after two classifier corrections — see below)
```

Source repository status before and after capture: identical
(`?? docs/decisions/ASSESSMENT_2026-07-23_OPERATIONS_WORKSPACE_REPOSITIONING.md`
in both, an untracked file that predates this work order and was never
touched). `git worktree list` in the source repository shows only the
primary checkout after capture — the temporary detached worktree was
removed.

### Known limitation: classifier iteration

The first real-repository run put 95 legitimate files (root governance docs
such as `AGENTS.md`, `CHANGELOG.md`, `.gitignore`, all of `scripts/`,
`database/`'s non-migration SQL, `infrastructure/`, `examples/`, `fixtures/`,
`SESSION/`, `CVF_SESSION/`) into the `other` catch-all class, which defaults
to `REJECT`. That was caught by inspecting the real output (a disposable
fixture repo in the test suite is too small to expose this) and fixed by
widening `inventory.classify()` with directory- and extension-based rules,
covered by 11 new unit tests. Re-running against the same pin dropped
unclassified/REJECT-defaulted files to 0. This is recorded here rather than
silently folded in, per the work order's "do not erase failures" spirit.

Separately, the exclusion heuristic is intentionally over-broad in one
direction: `docs/security/CREDENTIAL_MANAGEMENT.md` and
`tests/cvf/test_auth_config_secret_validation.py` were excluded because
their names contain "credential"/"secret", even though neither file holds
an actual secret value — they are documentation about, and a test of,
credential handling. This is a known false-positive exclusion, accepted
because the failure direction (over-exclude) is the safe one for FR-03/FR-13.
A reviewer may choose to loosen the heuristic in a future amendment.

### Independent-review repair

The first independent blob audit returned finding `F0-R1`: 537 of 577
inventory hashes matched Windows checkout bytes after LF-to-CRLF conversion,
not the pinned Git-object bytes required by FR-04. Same-machine reruns were
deterministic but the cross-platform claim was not valid. The repair changed
inventory, migration and module-snapshot reads to exact `git cat-file` blob
bytes, batches inventory reads for performance, added an EOL-conversion
regression test, regenerated all provenance, and independently compared all
577 rows back to `git cat-file` with zero mismatches.

Finding `F0-R2` corrected the test accounting: the verified suite is 93 F0
tests plus 11 pre-existing G1 catalog tests, not 94 plus 9.

## 3. Acceptance-criteria evidence matrix

| AC | Requirement | Evidence |
|---|---|---|
| AC-01 | Capture from a detached temporary worktree at the exact pin | `git_pin.create_detached_worktree`; `capture.py` creates and removes it around every run; `tests/source_intake/test_git_pin.py::WorktreeLifecycleTests` |
| AC-02 | Refuse missing/abbreviated/unreachable/changed pin | `git_pin.verify_pin_reachable`/`is_full_sha`; negative tests in `test_git_pin.py::IsFullShaTests`, `VerifyPinReachableTests`; end-to-end in `test_capture_integration.py::test_abbreviated_pin_is_rejected` |
| AC-03 | No `.env`/credentials/local bindings/ignored files read; inventory from Git objects + allowlist | `inventory.list_tracked_files` uses `git ls-files`; `is_excluded`; `test_inventory.py::IsExcludedTests`, `BuildInventoryTests` |
| AC-04 | Record source path, Git-blob SHA-256, size, candidate class | `inventory.build_inventory` reads exact pinned objects through `git cat-file --batch`; EOL regression test `test_hashes_git_blob_not_eol_converted_worktree_bytes`; real `file_inventory.json` (577 rows, independently rechecked with zero blob mismatches) |
| AC-05 | Public HTTP methods/paths for every ingress, including integration-edge | `routes.discover_routes` is app-agnostic; real `routes.json` includes both `workspace-api` and `integration-edge` routes; genericity proven by `test_routes_and_migrations.py::test_discovers_routes_from_an_arbitrary_unnamed_app` |
| AC-06 | Migration order + SHA-256, no execution | `migrations.discover_migrations`; real `migrations.json`; no SQL connection anywhere in the codebase |
| AC-07 | App/package roots + import/dependency edges | `dependency_graph.build_dependency_graph`; real `dependency_graph.json` |
| AC-08 | Module Registry status recorded, no module promoted | `module_snapshot.snapshot_module_registry` (read-only); target's own `docs/catalog/MODULE_REGISTRY.json` verified byte-identical before/after (Section 4) |
| AC-09 | PASS/FAIL/BLOCKED/NOT_RUN taxonomy, never silently converted | `test_outcomes.run_all`/`_classify`; real `test_outcomes.json` shows one PASS and three NOT_RUN, not fabricated PASS |
| AC-10 | Import ledger, one ADR-defined disposition + reviewer field per candidate | `ledger.build_ledger`/`validate_ledger`; every real row has `review_status: PENDING_REVIEWER` |
| AC-11 | Repository-relative paths use `/` in every artifact | `paths.to_posix_relative`; `contains_backslash` defensive guard in `inventory.py`/`ledger.py`; `test_paths.py` |
| AC-12 | Fail non-zero on dirty temp input, duplicate ledger paths, missing hashes, unclassified candidates, self-scan | `git_pin.assert_worktree_clean`, `ledger.validate_ledger`, `paths.assert_not_self_scan`; negative tests across `test_git_pin.py`, `test_ledger.py`, `test_paths.py`, `test_capture_integration.py::test_self_scan_of_tool_repository_is_rejected` |
| AC-13 | Exclude caches/build/generated evidence/local continuity/secrets/transcripts from candidacy | `inventory._EXCLUDED_DIR_PARTS`/`is_excluded`; real `exclusions.json` |
| AC-14 | Leave source repository and commit untouched | `capture_receipt.json.source_status_unchanged: true`; manual before/after `git status`/`git worktree list` in Section 2 |
| AC-15 | Do not create `apps/`, `packages/`, `database/` in target | `paths.assert_not_forbidden_target`; `test_paths.py::ForbiddenTargetGuardTests`; `test_capture_integration.py::test_forbidden_target_path_is_rejected_before_any_worktree_is_created` |
| AC-16 | Two captures at the same pin byte-identical except timestamp | Hermetic proof: `test_capture_integration.py::test_two_runs_at_the_same_pin_are_byte_identical_except_timing`. Real-repository proof: two independent runs against the actual 577-file Shift repository compared byte-for-byte in Section 2 of the build log — 9/9 datasets identical, only `capture_timing.json` differs |
| AC-17 | No raw secret value in stdout, evidence, or diff | `redact.redact_credential_urls` (fixes the old verifier's multi-`@` leak, see `test_redact.py`); `test_capture_integration.py::test_no_secret_value_appears_in_any_written_output` asserts the fixture's secret string is absent from every written file |
| AC-18 | Independent review confirms no runtime source imported | Pending — this is Codex's REVIEWER action, not self-certifiable here |
| AC-19 | Artifact Registry and Index agree; Module Registry unchanged and empty | `python scripts/manage_catalog.py --check`; Module Registry hash comparison — both in Section 4 |

## 4. Required checks — commands and results

```text
python -m unittest discover -s tests -p "test_*.py"
  -> Ran 104 tests. OK.   (93 F0 tests + 11 pre-existing G1 catalog tests, run together)

python scripts/source_intake/capture.py --source-repo-primary <shift-operations-workspace> \
  --source-commit f98f29e145fa002be070e9d44520d20f0f82dcb3 \
  --output-dir provenance/shift-operations/f98f29e145fa002be070e9d44520d20f0f82dcb3
  -> F0 CAPTURE: PASS. Exit 0.

Two-run determinism comparison (Section 2 method)
  -> 9/9 non-timing JSON files byte-identical. AC-16 satisfied on the real repository.

sha256sum docs/catalog/MODULE_REGISTRY.json docs/catalog/MODULE_CATALOG.md
  (before artifact registration) -> recorded; re-checked identical after
  registration and `--write` in this same evidence document's follow-up run.

python scripts/manage_catalog.py --check
  -> INDEX/CATALOG: PASS (after --write registered the five new F0 artifacts)

git diff --check
  -> no whitespace errors reported

Project-scoped workspace doctor
  (check_cvf_workspace_agent_enforcement.ps1 -ProjectPath CVF-Operations-Workspace)
  -> RESULT: PASS (24/24 checks passed), matching the precedent recorded for G0/G1
```

Exact command output for the checks above is not re-pasted verbatim here to
keep this document short; the reviewer can re-run every command listed —
none of them require network access, dependency installation, or a
provider call.

## 5. Explicit non-claims

- No runtime source was imported. `apps/`, `packages/`, `database/` were not
  created or modified in this repository.
- This repository's own `docs/catalog/MODULE_REGISTRY.json` remains empty
  and byte-identical to its pre-BUILD content.
- No module status was created, promoted, or implied.
- No GitHub rename, Shift repository mutation, or cutover occurred.
- No provider/AI call was made.
- This document does not constitute REVIEW_PASS or FREEZE. Disposition is
  Codex's, as independent REVIEWER and COMMIT_STEWARD.
