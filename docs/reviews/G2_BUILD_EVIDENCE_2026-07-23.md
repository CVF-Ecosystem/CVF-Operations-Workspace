# G2 BUILD Evidence — Golden Downstream Catalog Kit 1.1 Reconciliation

- Work order: `OW-G2-WO-001`
- Spec: `OW-G2-SPEC-001`
- Decision: `ADR-OW-003`
- Role: IMPLEMENTATION_WORKER (Claude, provider-neutral role contract)
- Authorization commit (C1): `3d1c316c343f9893b2e72672ef19c1ba68aa46f1`
- CVF core pin target: `27137db4d9aa2aea931ddd2507185d5c24943080`
- Date: 2026-07-23
- Status: BUILD complete, self-reported by IMPLEMENTATION_WORKER. **Not**
  independently reviewed, **not** REVIEW_PASS'd, **not** FREEZE'd. Codex
  REVIEWER performs the next, independent pass against this evidence.

## Failure and repair history (not erased)

This BUILD is downstream of an authorization package that needed two repair
rounds before independent REVIEW_PASS:

- **G2-R1 — BLOCKER_BASELINE_DRIFT**: the package was originally authored
  against CVF core `origin/main` at `571cb21b7026f0cd925279ba698bf30a291a4644`;
  independent review found the public tip had advanced to
  `27137db4d9aa2aea931ddd2507185d5c24943080` before BUILD started. Verified
  the four Golden Kit payload files are byte-identical between the two
  commits (see parity table below — this BUILD used the same verification
  method against the final pin). Repaired by running the official
  `update_cvf_workspace_public_core.ps1` reconciler; prior hidden core
  preserved at `_cvf-core-backups/.Controlled-Vibe-Framework-CVF-20260723-200246`.
- **G2-R2 — CONTINUITY_PHASE_ROLE_DRIFT**: `ACTIVE_SESSION_STATE.json` had
  stale FREEZE-phase/ORCHESTRATOR-role values; corrected to WORK_ORDER phase.
- **G2-R3 — STALE_F0_CLAIM**: a handoff claim understated F0 as "authorized
  but not yet built" when F0 BUILD/REVIEW_PASS/FREEZE were already complete;
  corrected.
- **G2-R4 — INCOMPLETE_ROLE_ROUTE**: the work order's role route omitted
  `IMPLEMENTATION_WORKER` and the post-BUILD review/repair/re-review loop;
  expanded.
- **G2-R5 — ROLLBACK_REHEARSAL_ORDER_CONTRADICTION**: the commit plan said
  rehearsal precedes the commit, contradicting `G2-AC-22`'s post-commit/
  pre-push order; corrected.

All five findings are closed and REVIEW_PASS was recorded before this BUILD
began (see the active handoff's "G2 Independent Authorization Re-review"
entry). During this BUILD, the first draft of
`tests/test_catalog_management.py` had a real test-isolation bug: `setUp()`
reset the two registry JSON files but not the generated views, so a
hand-edit made by one negative test (`test_hand_edited_generated_index_fails_closed`)
leaked into a later test and caused `test_real_repository_registries_pass_check`
to fail (`Ran 23 tests ... FAILED (failures=1)`). This is recorded, not
erased: the fix added `index_path`/`module_catalog_path` reset to `setUp()`,
after which all 23 tests in this file passed and the full suite reached
116/116 (see Validation below).

### BUILD Repair Round 1 (2026-07-23)

Independent Codex post-BUILD review returned two findings against this
evidence and the BUILD artifacts it describes:

- **G2-BR1 — INCOMPLETE_ARTIFACT_DISPOSITION_DISCOVERY (repaired).**
  Disposition row #10 below claimed `docs/catalog/README.md` was
  "discoverable via `.cvf/manifest.json requiredDocs`," but the manifest did
  not actually list that path — so `AC-07`'s 28/28 claim was not yet true by
  the ADR's own stated discovery mechanism for row #10. Golden's closed
  `family` vocabulary has no slot for a guide/README document, and the
  generated `docs/INDEX.md` never deep-links it either, so `requiredDocs` is
  the *only* remaining discovery surface for this file — it had to actually
  be present, not merely asserted. **Repair:** added
  `"docs/catalog/README.md"` to `.cvf/manifest.json`'s `requiredDocs` array.
  No change was made to the Golden Artifact Registry — no new `family` value
  was invented and no row was added for this file, since that would
  contradict the ADR's own decision that Golden's registry only self-registers
  the 17 baseline bootstrap-authority surfaces. `AC-03` and `AC-07` below are
  updated to reflect this, and disposition row #10 is corrected to state the
  actual (not merely intended) discovery mechanism.
- **G2-BR2 — STALE_BOOTSTRAP_DOCTOR_RECEIPT (repaired).** BUILD-time
  self-report ran the workspace doctor and got PASS 25/25 (recorded in the
  Doctor Receipt section below), and Codex's own post-BUILD review
  independently reproduced that PASS 25/25 result — but
  `docs/CVF_BOOTSTRAP_LOG_20260723.md` Section 5 still showed
  `[ ] Workspace doctor: PASS` (unchecked), understating what both BUILD and
  review had already confirmed. **Repair:** the bootstrap log's Section 5 now
  reads `[x] Workspace doctor: PASS (25/25)`, with a note that this is a
  BUILD-time enforcement-artifact result self-reported by IMPLEMENTATION_WORKER
  and independently reproduced by Codex REVIEWER — not a tranche FREEZE
  disposition. A governed-catalog-check command
  (`scripts\manage_cvf_downstream_catalog.ps1 -Check`) was added to Section 5
  alongside the existing doctor command, matching the Golden workflow. Live
  readiness, API health, frontend, and runtime-smoke checkboxes remain
  unchecked (none were run — no provider call was made). Section 6 (Approval)
  remains blank: this tranche is not FREEZE'd.

Neither finding required touching the registries, the Golden Kit payload
files, the generated views, or any test file; both are documentation-accuracy
repairs within the 4-path ceiling
(`.cvf/manifest.json`, `docs/CVF_BOOTSTRAP_LOG_20260723.md`, this file, and
the active handoff).

### Textual-reference disclosure — historical roadmap line

`docs/roadmaps/CVF_OPERATIONS_WORKSPACE_ROADMAP.md` (out of `OW-G2-WO-001`'s
ceiling; untouched, `git diff` empty — see F0/exclusion invariants below)
retains one historical line under its already-`COMPLETE` "G1 — Machine-governed
Index and Catalog" section: `` `scripts/manage_catalog.py --write/--check`
generates and detects drift. `` This is a *historical record* of what G1
built, not an active instruction, executable reference, or workflow step —
the roadmap does not run, import, or invoke that path, and nothing in this
repository executes it (the file itself is deleted; see Deleted/replaced
legacy paths above). This textual mention is explicitly **not** disturbed by
this BUILD or this repair round: the roadmap is excluded from `OW-G2-WO-001`'s
changed-set ceiling, and correcting this historical line to describe the
Golden manager instead is deferred to a future, separately authorized roadmap
tranche. **This evidence does not claim the repository contains zero textual
references to `scripts/manage_catalog.py`** — it claims only that no
competing *executable* catalog writer or generation workflow remains: the file
is deleted, `tests/test_catalog_management.py` no longer imports or invokes
it, and `docs/catalog/README.md`'s workflow section documents only the Golden
manager. AC-11's "competing writer resolved" claim is scoped to executable
writers/workflows, not to every prose mention of the old tool's name anywhere
in the repository's history.

## AC-01 through AC-22 matrix

| AC | Requirement | Evidence | Status |
|---|---|---|---|
| AC-01 | Core pin/remote verification | `git -C ../.Controlled-Vibe-Framework-CVF rev-parse HEAD` = `27137db4d9aa2aea931ddd2507185d5c24943080`; `rev-parse origin/main` = same; `remote get-url origin` = `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`; worktree clean (verified pre-BUILD, see IMPLEMENTATION_WORKER acknowledgment entry in the handoff) | PASS |
| AC-02 | Manifest pin and kit marker | `.cvf/manifest.json`: `cvfCoreCommit` = full `27137db4d9aa2aea931ddd2507185d5c24943080`, `catalogKitVersion` = `"1.1"`; `workspaceLayout`, `cvfCoreRelativePath`, `phaseModel` unchanged | PASS |
| AC-03 | Manifest requiredDocs completeness | `requiredDocs` now includes `docs/catalog/ARTIFACT_REGISTRY.json`, `docs/catalog/schemas/ARTIFACT_REGISTRY.schema.json`, `docs/catalog/schemas/MODULE_REGISTRY.schema.json`, `scripts/manage_cvf_downstream_catalog.ps1`, `scripts/lib/downstream_catalog/CvfDownstreamCatalogLib.ps1`, and `docs/catalog/README.md` (added in BUILD Repair Round 1 / `G2-BR1` — the only remaining discovery surface for this RETAIN-with-content-replaced file, since Golden's registry has no `guide` family and the generated Index does not deep-link it), in addition to all prior entries | PASS |
| AC-04 | Manager/library byte/hash parity | SHA-256 parity table below — both files match core pin exactly | PASS |
| AC-05 | Schema byte/hash parity | SHA-256 parity table below — both schemas match core pin exactly | PASS |
| AC-06 | Artifact Registry migrated to Golden closed schema | `docs/catalog/ARTIFACT_REGISTRY.json` rewritten to `id/family/path/status/description`; `manage_cvf_downstream_catalog.ps1 -Check` PASS | PASS |
| AC-07 | All 28 legacy paths dispositioned | 28-row reconciliation table below, 1:1 with `ADR-OW-003`. Row #10 (`catalog-standard` / `docs/catalog/README.md`) is only fully satisfied as of BUILD Repair Round 1 (`G2-BR1`), which added the file to `.cvf/manifest.json requiredDocs` — the disposition's own named discovery mechanism was not yet true when this evidence was first authored | PASS (as repaired) |
| AC-08 | Mandatory Golden baseline entries present | All 17 baseline ids present with exact CVF-core-defined paths; `-Check`'s baseline check passed with zero missing/mismatched entries | PASS |
| AC-09 | Module Registry migrated, still empty | `docs/catalog/MODULE_REGISTRY.json`: `schemaVersion/projectName/updatedAt/claimBoundary/modules`, `modules: []` | PASS |
| AC-10 | Single canonical generator | `docs/INDEX.md` and `docs/catalog/MODULE_CATALOG.md` regenerated only via `scripts/manage_cvf_downstream_catalog.ps1 -Write`; no other script references generating them | PASS |
| AC-11 | Competing writer resolved | `scripts/manage_catalog.py` and old-path schemas **deleted**; `tests/test_catalog_management.py` converted to 23 regression tests exercising the real Golden manager (see Negative Test Matrix) — all pass, reproducing every guarantee the retired suite proved plus new Golden-only guarantees | PASS |
| AC-12 | Generated views byte-match | `-Write` then `-Check` back-to-back: `[PASS] ... generated views match source truth` | PASS |
| AC-13 | Positive check PASS | `manage_cvf_downstream_catalog.ps1 -Check` → `[PASS]`, exit 0 | PASS |
| AC-14 | Negative fail-closed tests | 20 negative-path tests in `tests/test_catalog_management.py`, all failing closed as expected (see matrix below) | PASS |
| AC-15 | F0 provenance untouched | `git diff --stat -- provenance/shift-operations scripts/source_intake tests/source_intake docs/architecture` → empty | PASS |
| AC-16 | No excluded-path writes | `git diff --stat -- docs/roadmaps apps packages database .github` → empty | PASS |
| AC-17 | Full existing test suite PASS | `python -m unittest discover -s tests -p "test_*.py"` → **116/116 OK** (93 F0 + 23 Golden catalog regression, up from 104 = 93 F0 + 11 retired) | PASS |
| AC-18 | Workspace doctor PASS | `check_cvf_workspace_agent_enforcement.ps1` → **PASS (25/25)** (see Doctor Receipt below) | PASS |
| AC-19 | Continuity/status drift closed | `AGENTS.md`, bootstrap log, `.cvf/manifest.json` all reference `27137db4d9aa2aea931ddd2507185d5c24943080`; no remaining reference to the old core pin as *current* state (historical mentions in repair-history sections are intentionally preserved, not drift) | PASS |
| AC-20 | No secret/provider exposure | No `.env`/API-key file read or touched; no live provider call made at any point in BUILD | PASS |
| AC-21 | Diff hygiene | `git diff --check` → exit 0 (only benign CRLF-normalization notices); no `__pycache__` staged; changed set is a subset of the ceiling (see Exact Changed Set below) | PASS |
| AC-22 | Rollback rehearsal | Not applicable to this IMPLEMENTATION_WORKER pass — this criterion is satisfied by Codex COMMIT_STEWARD's post-commit/pre-push rehearsal of C2/C3, which has not yet occurred | PENDING (by design — Codex-owned) |

21/22 criteria satisfied by this BUILD; AC-22 is explicitly Codex's to satisfy at commit time, not claimed here.

## SHA-256 parity — four Golden Kit payload files vs. CVF core pin

| File (this project) | SHA-256 | Matches core pin `27137db4d9aa2aea931ddd2507185d5c24943080` |
|---|---|---|
| `scripts/manage_cvf_downstream_catalog.ps1` | `abce93c6aef48cd813bd7fcab57bc3b0e63400c4c0dd65337cdf0a069f96df80` | YES |
| `scripts/lib/downstream_catalog/CvfDownstreamCatalogLib.ps1` | `e354388f81c6b220e203a729f8587cd47928c7af42021905372d565dccc06e3c` | YES |
| `docs/catalog/schemas/ARTIFACT_REGISTRY.schema.json` | `6744c4c62c4f4585c69540af418ca87b9a1bef18137b0515228baea7cd6af301` | YES |
| `docs/catalog/schemas/MODULE_REGISTRY.schema.json` | `a5e02a0864eb777a858ed6583e96b9edc0d516ecf8bd6224e7014185f11557d4` | YES |

Verified by copying each file from
`../.Controlled-Vibe-Framework-CVF/scripts/lib/downstream_catalog/...` at
HEAD `27137db4d9aa2aea931ddd2507185d5c24943080` and comparing `sha256sum`
output against the destination — all four matched exactly, no edits applied
after copy.

## 28-row disposition reconciliation (1:1 with ADR-OW-003)

| # | Legacy id | Disposition | BUILD outcome |
|---|---|---|---|
| 1 | `session-memory` | MIGRATE | → `continuity-session-memory`, same path `CVF_SESSION_MEMORY.md` |
| 2 | `active-session-state` | MIGRATE | → `continuity-active-session-state`, same path `CVF_SESSION/ACTIVE_SESSION_STATE.json` |
| 3 | `active-handoff` | MIGRATE | → `continuity-initial-handoff`, same path `CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-07-23.md` |
| 4 | `implementation-status` | MIGRATE | → `truth-implementation-status`, same path `IMPLEMENTATION_STATUS.json` |
| 5 | `artifact-registry` | RETIRE (row) | Not self-registered (matches Golden design); file remains the canonical registry |
| 6 | `artifact-registry-schema` | REPLACE | Old `docs/catalog/ARTIFACT_REGISTRY.schema.json` **deleted**; superseded by `schema-artifact-registry` at `docs/catalog/schemas/ARTIFACT_REGISTRY.schema.json` |
| 7 | `module-registry` | RETIRE (row) | Not self-registered; file remains the canonical registry |
| 8 | `module-registry-schema` | REPLACE | Old `docs/catalog/MODULE_REGISTRY.schema.json` **deleted**; superseded by `schema-module-registry` at `docs/catalog/schemas/MODULE_REGISTRY.schema.json` |
| 9 | `module-catalog` | MIGRATE | → `view-module-catalog`, same path `docs/catalog/MODULE_CATALOG.md`, re-rendered by Golden manager |
| 10 | `catalog-standard` | RETAIN, content replaced | `docs/catalog/README.md` rewritten for the Golden two-registry model; de-registered as a row (no `guide` family in Golden's closed vocabulary — no family was invented to force one). Discoverable via `.cvf/manifest.json requiredDocs`, where it is **actually listed** (added in BUILD Repair Round 1 / `G2-BR1`, not merely asserted) — not via any module/artifact registry capability claim |
| 11 | `catalog-tool` | RETIRE | `scripts/manage_catalog.py` **deleted** after regression evidence (see Negative Test Matrix) |
| 12 | `catalog-tests` | RETIRE (converted) | `tests/test_catalog_management.py` **rewritten** as 23 Golden-manager regression tests, same file path retained |
| 13 | `assessment-reconciliation` | RETAIN | Inside `docs/reviews/`, covered by `family-reviews`; untouched, still in `IMPLEMENTATION_STATUS.json.evidence` |
| 14 | `adr-greenfield` | RETAIN | Inside `docs/decisions/`, covered by `family-decisions`; untouched |
| 15 | `adr-index-catalog` | RETAIN | Inside `docs/decisions/`, covered by `family-decisions`; untouched |
| 16 | `platform-roadmap` | RETAIN, untouched | Inside `docs/roadmaps/`, covered by `family-roadmaps`; `git diff` empty (verified) |
| 17 | `f0-spec` | RETAIN | Inside `docs/specs/`, covered by `family-specs`; untouched |
| 18 | `f0-work-order` | RETAIN | Inside `docs/work_orders/`, covered by `family-work-orders`; untouched |
| 19 | `f0-work-order-amendment-1` | RETAIN | Inside `docs/work_orders/`, covered by `family-work-orders`; untouched |
| 20 | `g1-spec` | RETAIN | Inside `docs/specs/`, covered by `family-specs`; untouched |
| 21 | `g1-work-order` | RETAIN | Inside `docs/work_orders/`, covered by `family-work-orders`; untouched |
| 22 | `g1-work-order-amendment-1` | RETAIN | Inside `docs/work_orders/`, covered by `family-work-orders`; untouched |
| 23 | `f0-architecture-rules` | RETAIN | `docs/architecture/` has no Golden folder family; file untouched, `git diff` empty (verified), still in `IMPLEMENTATION_STATUS.json.evidence` |
| 24 | `f0-source-intake-tool` | RETAIN | F0 protected path; `git diff` empty (verified) |
| 25 | `f0-source-intake-tests` | RETAIN | F0 protected path; `git diff` empty (verified) |
| 26 | `f0-capture-receipt` | RETAIN | F0 protected provenance path; `git diff` empty (verified) |
| 27 | `f0-build-evidence` | RETAIN | Inside `docs/reviews/`, covered by `family-reviews`; untouched |
| 28 | `f0-independent-review` | RETAIN | Inside `docs/reviews/`, covered by `family-reviews`; untouched |

5 MIGRATE, 2 REPLACE, 4 RETIRE, 17 RETAIN — 28/28 accounted for, matching
`ADR-OW-003` exactly. No path was silently dropped: every RETIRE/RETAIN row
above names its post-migration discovery surface.

Final `docs/catalog/ARTIFACT_REGISTRY.json` contains exactly the 17 Golden
baseline entries (the migrated/replaced rows above ARE those baseline
entries; no row was added beyond the baseline, matching the ADR's decision
that Golden's registry only self-registers bootstrap authority surfaces).

## Negative fail-closed test matrix (AC-14, all in `tests/test_catalog_management.py`)

| Test | Scenario | Expected failure text | Result |
|---|---|---|---|
| `test_unknown_top_level_field_fails` | extra top-level field | `additional property not allowed` | FAIL as expected |
| `test_unknown_entry_field_fails` | old-schema `title` field on an entry | `additional property not allowed` | FAIL as expected |
| `test_invalid_family_fails` | `family: "not-a-real-family"` | `invalid family` | FAIL as expected |
| `test_invalid_status_fails` | `status: "imaginary"` | `invalid lifecycle status` | FAIL as expected |
| `test_duplicate_artifact_id_fails` | duplicated `id` | `duplicate id` | FAIL as expected |
| `test_duplicate_artifact_path_fails` | duplicated `path` | `duplicate path` | FAIL as expected |
| `test_missing_artifact_path_fails` | path to nonexistent file | `registered path does not exist` | FAIL as expected |
| `test_windows_backslash_path_fails` | backslash-separated path | `path escape or non-portable path` | FAIL as expected |
| `test_path_traversal_escape_fails` | `../WORKSPACE_RULES.md` | `path escape or non-portable path` | FAIL as expected |
| `test_leading_slash_path_fails` | `/etc/passwd` | `path escape or non-portable path` | FAIL as expected |
| `test_drive_letter_path_fails` | `C:/Windows/...` | `path escape or non-portable path` | FAIL as expected |
| `test_missing_mandatory_baseline_entry_fails` | remove `manifest-cvf` row | `missing mandatory authority surface` | FAIL as expected |
| `test_mandatory_baseline_entry_wrong_path_fails` | wrong path on `policy-cvf` | `has unexpected path` | FAIL as expected |
| `test_module_plan_only_status_fails` | module `status: "PLANNED"` | `invalid status` + `plan-only` | FAIL as expected |
| `test_module_missing_evidence_fails` | module with empty `evidence` | `evidence` | FAIL as expected |
| `test_module_unknown_control_token_fails` | `controls: ["identity"]` | `unknown CVF control token` | FAIL as expected |
| `test_module_unknown_dependency_fails` | `dependencies: ["nonexistent-module"]` | `unknown module dependency` | FAIL as expected |
| `test_hand_edited_generated_index_fails_closed` | append text to `docs/INDEX.md` | `hand-edited or stale` | FAIL as expected |
| `test_hand_edited_module_catalog_fails_closed` | append text to `MODULE_CATALOG.md` | `hand-edited or stale` | FAIL as expected |
| `test_registry_project_identity_mismatch_fails` | mismatched `projectName` | `registry project identity mismatch` | FAIL as expected |

20 negative cases plus 3 positive cases (`test_real_repository_registries_pass_check`,
`test_cli_check_passes_without_writing`, `test_write_then_check_has_no_drift`)
= 23 tests total in this file, all run against a disposable
`tempfile.TemporaryDirectory()` copy of the repository — never the real
registries — and all invoke the actual
`scripts/manage_cvf_downstream_catalog.ps1` as an external process, not a
re-implementation of its logic.

Coverage vs. the retired Python suite: every guarantee it proved (duplicate
id/path, missing path, invalid status, windows-separator/path-escape,
hand-edited generated index, CLI check) has an equivalent case above. The
retired suite's `related`-field relationship check has no literal Golden
equivalent (Golden's schema has no `related` field); the equivalent concept
— an unknown cross-reference — is instead covered for
`MODULE_REGISTRY.json`'s `dependencies` field
(`test_module_unknown_dependency_fails`), which is the closest Golden
analogue. Golden's closed-schema, baseline-enforcement, and module-vocabulary
rules add guarantees the old open schema never had.

## Deleted / replaced legacy paths

| Path | Action | Rationale |
|---|---|---|
| `scripts/manage_catalog.py` | **Deleted** | Retired competing writer (ADR-OW-003 §8); regression evidence above proves the Golden manager reproduces its guarantees |
| `docs/catalog/ARTIFACT_REGISTRY.schema.json` (old path, no `schemas/` subdir) | **Deleted** | Superseded by `docs/catalog/schemas/ARTIFACT_REGISTRY.schema.json` |
| `docs/catalog/MODULE_REGISTRY.schema.json` (old path) | **Deleted** | Superseded by `docs/catalog/schemas/MODULE_REGISTRY.schema.json` |
| `scripts/__pycache__/` | Removed (was git-ignored, never tracked) | Stale bytecode cache referencing the deleted module |
| `tests/test_catalog_management.py` | **Rewritten in place** (same path) | Converted from Python-API unit tests to Golden-manager subprocess regression tests |

No other deletion occurred. Only one canonical catalog writer
(`scripts/manage_cvf_downstream_catalog.ps1`) exists after this BUILD.

## F0 protected-path invariants

`git diff --stat` for `provenance/shift-operations/`, `scripts/source_intake/`,
`tests/source_intake/`, and `docs/architecture/` is empty — byte-identical
before and after this BUILD. `docs/roadmaps/`, `apps/`, `packages/`,
`database/`, and `.github/` are likewise untouched (empty diff). F0's
completion status (BUILD/REVIEW_PASS/FREEZE, commits C1
`8c193984c5fc158ca65ea554dd8d4934d12c28f4`, C2
`39541d5e84b06f8650ce2b0f6341425c7a05d7bf`, C3
`3064d4bce08d36f553516d59719358fd8788cbcf`) is unchanged by this tranche.

## Exact changed set (this BUILD)

```text
M  .cvf/manifest.json
M  AGENTS.md
M  CVF_SESSION/ACTIVE_SESSION_STATE.json
M  CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-07-23.md
M  docs/CVF_BOOTSTRAP_LOG_20260723.md
M  docs/INDEX.md                                 (generated)
M  docs/catalog/ARTIFACT_REGISTRY.json
D  docs/catalog/ARTIFACT_REGISTRY.schema.json     (old path — retired)
M  docs/catalog/MODULE_CATALOG.md                (generated)
M  docs/catalog/MODULE_REGISTRY.json
D  docs/catalog/MODULE_REGISTRY.schema.json       (old path — retired)
M  docs/catalog/README.md
D  scripts/manage_catalog.py                      (retired)
M  tests/test_catalog_management.py               (converted)
?? docs/catalog/schemas/ARTIFACT_REGISTRY.schema.json   (new, byte-identical to core)
?? docs/catalog/schemas/MODULE_REGISTRY.schema.json     (new, byte-identical to core)
?? scripts/lib/downstream_catalog/CvfDownstreamCatalogLib.ps1 (new, byte-identical to core)
?? scripts/manage_cvf_downstream_catalog.ps1            (new, byte-identical to core)
```

Plus this file (`docs/reviews/G2_BUILD_EVIDENCE_2026-07-23.md`, new) and the
subsequent continuity closure (`IMPLEMENTATION_STATUS.json`,
`CVF_SESSION/ACTIVE_SESSION_STATE.json`, `CVF_SESSION/handoffs/**`). Every
path above is inside `OW-G2-WO-001`'s BUILD changed-set ceiling; no path
outside the ceiling was touched (verified: empty diff for every excluded
path listed in the work order).

## Validation

```text
$ powershell -File scripts/manage_cvf_downstream_catalog.ps1 -Write
[OK] Regenerated docs/INDEX.md and docs/catalog/MODULE_CATALOG.md from registries.

$ powershell -File scripts/manage_cvf_downstream_catalog.ps1 -Check
[PASS] Governed downstream catalog is valid and generated views match source truth.

$ python -m unittest discover -s tests -p "test_*.py"
Ran 116 tests in 86.904s
OK

$ git diff --check
(exit 0; only CRLF-normalization warnings, no whitespace errors)
```

## Doctor receipt (post-BUILD)

```text
CVF Workspace Agent Enforcement Doctor
Project: D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\CVF-Operations-Workspace

  CVF public core matches origin/main                [PASS]
  CVF public core worktree clean                      [PASS]
  CVF core commit matches manifest                     [PASS]
  Required docs referenced by manifest exist           [PASS]
  Governed downstream catalog validates (--check)      [PASS]
  ... (20 further checks) ...                          [PASS]

  RESULT: PASS (25/25 checks passed)
  This workspace is agent-enforcement-ready.
```

No `BEHIND_PUBLIC_REMOTE`, no core-pin mismatch, no `DAMAGED_GOVERNED_KIT`,
no `MIGRATION_REQUIRED`, no `LEGACY_PROJECT` note. This is the first PASS
result for this project's doctor since G2 began (repair rounds 1–2 and the
authorization re-review all recorded the expected pre-BUILD FAIL).

## Claim boundary

This evidence proves catalog/pin reconciliation mechanics: schema closure,
byte/hash parity, disposition completeness, fail-closed negative behavior,
full test-suite pass, diff hygiene, and doctor PASS. It does not prove
runtime governance behavior, does not authorize roadmap work, does not import
or implement any module (`docs/catalog/MODULE_REGISTRY.json` remains
`modules: []`), and is not itself a REVIEW_PASS or FREEZE — those remain
Codex's independent authority, exercised separately after this evidence is
reviewed.
