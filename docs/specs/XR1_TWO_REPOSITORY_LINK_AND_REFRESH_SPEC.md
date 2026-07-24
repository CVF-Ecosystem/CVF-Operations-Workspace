# Spec — XR1 Two-Repository Portable Link and Governed Shift Refresh

- Spec ID: `OW-XR1-SPEC-001`
- Date: 2026-07-24
- Implements: `ADR-OW-006`
- Status: DRAFT (pending independent REVIEW_PASS)

## Repair note (round 1, 2026-07-24)

Independent Codex review returned `XR1-R1` through `XR1-R7` (full detail in
`ADR-OW-006`'s repair note). This spec is repaired accordingly: the claim
boundary and `XR1-AC-33` are corrected to the post-F1A-closure 177-test
baseline (`XR1-R1`); `XR1-AC-11` is bound to `ADR-OW-006` section B's exact
accounting equation; and `XR1-AC-35` through `XR1-AC-44` are added to bind
`XR1-R2` (rename-as-one-record), `XR1-R3` (apply-manifest schema and
verification), `XR1-R4` (destination path safety), `XR1-R5` (rollback
atomicity), `XR1-R6` (bounded discovery), and `XR1-R7` (filter precedence
and secret-content handling). No other acceptance criterion's substance
changed. Role: `REPAIR_WORKER`. Codex retains independent
`REVIEWER`/`COMMIT_STEWARD` authority; this round does not self-grant
REVIEW_PASS.

## Repair note (round 2, 2026-07-24)

Independent Codex review returned `XR1-R7B` (a fresh finding, renamed in
round 3's governance-id cleanup from a reused `XR1-R7`; round 1's
`XR1-R7` remains closed and unaffected) through `XR1-R10`. Repaired:
`XR1-AC-21` corrected from a "five-way partition" to the exact four
`scan`-time classifications plus the separate `APPROVED_APPLY` lifecycle
state (`XR1-R7B`); `XR1-AC-13` corrected to the exact `scan` side-effect
boundary (`XR1-R10`); new `XR1-AC-45`/`46` bind the operation-specific
manifest `oneOf` and `destinationPrecondition` (`XR1-R8`, further tightened
by round 3's `XR1-R12`); new `XR1-AC-47` binds the exact recovery-artifact
locations and retention rule (`XR1-R9`). Role: `REPAIR_WORKER`. Codex
retains independent `REVIEWER`/`COMMIT_STEWARD` authority; this round does
not self-grant REVIEW_PASS.

## Repair note (round 3, 2026-07-24)

Independent Codex review returned `XR1-R11`–`XR1-R13`, plus a governance-id
cleanup renaming round 2's reused `XR1-R7` to `XR1-R7B` (round 1's `XR1-R7`
is unaffected). Repaired: `XR1-AC-38`/`39` rewritten for the non-circular
two-artifact model — the manifest carries no `authorizationCommit` field,
a separate independent review receipt supplies `decision`/`manifestSha256`/
etc., and `apply` takes `--authorization-commit`/`--authorization-receipt`
as external CLI arguments (`XR1-R11`); `XR1-AC-45`/`46` extended with the
rename operation's exact `oldDestinationPrecondition`/
`newDestinationPrecondition` field names and their required states
(`XR1-R12`); `XR1-AC-44` extended to separate `XR1-O-C2` BUILD-time
synthetic-fixture testing from a future real Shift scan's own bounded
execution work order (`XR1-R13`). Role: `REPAIR_WORKER`. Codex retains
independent `REVIEWER`/`COMMIT_STEWARD` authority; this round does not
self-grant REVIEW_PASS. Status: `REPAIRED_PENDING_INDEPENDENT_RE_REVIEW_3`.

## Purpose

Bind `ADR-OW-006`'s decisions to testable acceptance criteria for a future
`XR1-O-C2` BUILD. This spec authorizes no BUILD itself and makes no runtime,
Shift-modification, F1A, or lane-2 claim.

## Claim boundary (repeated from ADR — binding on all criteria below)

- Proves portable discovery, deterministic accounting, filtering, and
  governed apply mechanics only — not Shift MVP compatibility, F1A/F1B
  runtime behavior, AI governance, production readiness, or the correctness
  of any individual porting decision (`ADR-OW-001` remains authoritative for
  `PORT_AS_IS`/`ADAPT`/`REIMPLEMENT`/`REFERENCE_ONLY`/`REJECT`).
- `shift-operations-workspace` is never modified by this spec's criteria —
  every write happens inside `CVF-Operations-Workspace` only.
- F1A (`XR1-R1`: **CLOSED, FROZEN, and PARKED** — C1
  `d731762a9e135b075261831ed7eb0df4badc98dd`, C2
  `9e59cfdcf3d1da2644540088e748123cd41f14e9`, C3
  `4cdd7f06e040fee43ab733d3dc608aa4d425452b`, C4
  `0efa7f23bfb2ea5677b680ed35ca0ae3f057e715`, all on `origin/main`) and
  Shift's lane 2 (`P2B-APPROVER-IDENTITY-RECONCILIATION`, parked) are
  unaffected; no criterion below touches either. The current regression
  baseline is **177** tests (116 pre-F1A + 61 F1A).

## Acceptance criteria — descriptor and portability (A)

- **XR1-AC-01 — Exact descriptor schema.** `.cvf/workspace-link.json` exists
  with exactly the fields in `ADR-OW-006` section A: `schemaVersion`,
  `workspaceId`, `thisRepo` (`repoId`, `role`, `remote`), `peerRepo`
  (`repoId`, `role`, `remote`), `relationshipDirection`, `sourcePin`,
  `pinUpdatePolicy`. `workspaceId` is exactly `cvf-operations-workspace`.
- **XR1-AC-02 — No absolute path in tracked content.** A text scan of
  `.cvf/workspace-link.json` finds no drive letter (`[A-Za-z]:\`), no
  `/home/`, `/Users/`, or `C:\`-style path, and no hostname.
- **XR1-AC-03 — Local binding is ignored and regenerable.**
  `.cvf/local-workspace-link.json` is listed in `.gitignore`; deleting it
  and re-running `scan` recreates it without altering
  `.cvf/workspace-link.json`'s `sourcePin`.
- **XR1-AC-04 — Negative: descriptor mismatch detection.** Validator
  rejects (with a named, non-generic error) each of: mismatched
  `workspaceId`; `thisRepo.repoId` != peer's `peerRepo.repoId`; `remote`
  not matching the peer's recorded `peerRepo.remote`; a non-complementary
  role pair; a `relationshipDirection` mismatch; a `sourcePin` that does
  not resolve to a real commit in the peer's history.
- **XR1-AC-05 — Single-repo sufficiency.** Given only
  `.cvf/workspace-link.json` (no Shift clone present, no
  `.cvf/local-workspace-link.json`), the peer's exact `repoId` and `remote`
  are still recoverable from that one file alone.
- **XR1-AC-06 — Pin-update discipline.** No code path in `scan` writes to
  `.cvf/workspace-link.json`'s `sourcePin`; only a documented, separate
  `apply`-cycle-driven update path (never automatic) may change it, and
  `scan` alone never does.

## Acceptance criteria — scan mode (B.1)

- **XR1-AC-07 — Sibling discovery/clone.** Given no local Shift clone and
  no `.cvf/local-workspace-link.json`, `scan` clones Shift read-only via
  `peerRepo.remote` and records the resulting local path only in
  `.cvf/local-workspace-link.json`.
- **XR1-AC-08 — Fetch-only, no worktree mutation.** After `scan` runs
  against an already-present Shift sibling, that sibling's `git status`,
  current branch, and `HEAD` are byte-for-byte identical to before the run
  (only `git fetch` was performed; no checkout, reset, pull, or merge).
- **XR1-AC-09 — Remote/pin/ancestry verification.** `scan` rejects (stop,
  no report written) if: the resolved clone's `origin` does not equal
  `peerRepo.remote`; the base pin does not exist in Shift's history; the
  candidate commit does not exist; or the candidate is not an ancestor-or-
  equal relationship to the base in the expected direction (a non-ancestor
  candidate is rejected unless an explicit override is separately
  authorized).
- **XR1-AC-10 — Git-object-level diff, not checkout bytes.** `scan`'s diff
  is produced from Git blob/tree objects (e.g. `git diff --name-status`,
  `git hash-object`/`git cat-file`), never from files read off a checked-out
  worktree; a test asserts the reported blob hashes match `git cat-file -p
  <blob>` output exactly, independent of the local worktree's line-ending
  configuration.
- **XR1-AC-11 — Exhaustive, exactly-once accounting (bound to `ADR-OW-006`
  section B's equation, `XR1-R2`).** For a representative base/candidate
  pair, `|unchanged| + |modified| + |added| + |deleted| + |renamed| =
  |B ∪ C| − |R|` holds exactly, where `B`/`C` are the base/candidate path
  sets and `R` is the set of matched rename pairs; a path never appears in
  two buckets and a rename pair is never also counted as a separate
  addition-plus-deletion.
- **XR1-AC-12 — Deterministic inventory.** Two independent `scan` runs
  against the identical base/candidate pair produce byte-identical
  SHA-256 inventories once the isolated `generatedAt`/host-context fields
  are excluded.
- **XR1-AC-13 — No import during scan, exact side-effect boundary
  (corrected, `XR1-R10`).** After `scan` completes, the **only** changes
  anywhere are: its own declared output under
  `provenance/shift-operations/<candidate>/`; `.cvf/local-workspace-link.json`;
  and, only when a fresh clone was genuinely required, a new peer clone at
  the bounded destination. A test asserts every other tracked Operations
  path's pre/post `git status` is identical, and — when a pre-existing
  Shift sibling was used — that sibling's `git status`, branch, and `HEAD`
  are also byte-for-byte identical (restating `XR1-AC-08`).

## Acceptance criteria — apply mode (B.2)

- **XR1-AC-14 — Disabled without a manifest.** `apply` invoked with no
  `--manifest` argument (or a manifest path that does not exist / is not
  repository-tracked) performs zero writes and exits with a named refusal.
- **XR1-AC-15 — Re-verification before write.** `apply` re-derives a fresh
  `scan` internally and rejects (zero writes) if any manifest entry's base
  commit, target commit, source blob hash, destination path, or
  disposition disagrees with that fresh scan.
- **XR1-AC-16 — Allowlist-only application.** `apply` writes exactly the
  destination paths the manifest names and no others, byte-identical to
  the named source blob.
- **XR1-AC-17 — Scan report is never treated as approval.** Invoking
  `apply` with a `scan` report file (not a work-order-shaped manifest) in
  place of `--manifest` is rejected, not silently accepted as equivalent.
- **XR1-AC-18 — No Shift write.** `apply`'s implementation contains no code
  path capable of writing into the Shift sibling clone; a static test
  asserts no filesystem-write call is ever constructed with the Shift
  sibling's path as a target.
- **XR1-AC-19 — No auto rename/delete.** A manifest that authorizes a
  file's `new`/`modified` counterpart but does not separately, explicitly
  name a `deleted` or `renamed` entry results in that deletion/rename being
  skipped, not silently applied.
- **XR1-AC-20 — Rollback evidence produced.** After any successful `apply`,
  a rollback/revert record exists capturing the exact pre-apply state
  (absence or prior bytes) of every path that was written.

## Acceptance criteria — filtering dispositions (C)

- **XR1-AC-21 — Exhaustive four-way `scan`-time partition (corrected,
  `XR1-R7B`).** Every path from `XR1-AC-11`'s accounting
  receives exactly one of the **four** `scan`-time classifications
  (`HARD_EXCLUDE`, `PROTECTED_SOURCE_ONLY`, `QUARANTINE_REVIEW`,
  `ELIGIBLE_CANDIDATE`); the report's own per-classification counts sum to
  the total accounted-path count. `APPROVED_APPLY` is a separate
  post-review `apply`-lifecycle state, never a `scan` classification: a
  test asserts the string `APPROVED_APPLY` never appears anywhere in a
  `scan` report's output, and is excluded from the classification-count
  sum by construction, not merely by convention.
- **XR1-AC-22 — `HARD_EXCLUDE` coverage.** Representative fixtures for a
  `.env` file, an embedded credential-shaped filename, a `.git/` internal
  path, `__pycache__/`, and a `.pyc` file each classify as `HARD_EXCLUDE`.
- **XR1-AC-23 — `PROTECTED_SOURCE_ONLY` visible-but-unportable.**
  Representative fixtures under Shift's `SESSION/**`,
  `CVF_SESSION_MEMORY.md`, `docs/decisions/**`, and a provider-evidence
  receipt path each classify as `PROTECTED_SOURCE_ONLY`; a test asserts no
  manifest may name a `PROTECTED_SOURCE_ONLY` path as `APPROVED_APPLY` —
  `apply` rejects such a manifest outright.
- **XR1-AC-24 — `QUARANTINE_REVIEW` triggers.** Representative fixtures for
  a binary file, a symlink, an oversized file (above a stated byte
  threshold), a migration/database file, a public-API route change, an
  authentication/security-relevant change, and a destructive delete/rename
  each classify as `QUARANTINE_REVIEW`.
- **XR1-AC-25 — `ELIGIBLE_CANDIDATE` default.** An ordinary, unremarkable
  source/doc/test path change that matches none of the above rules
  classifies as `ELIGIBLE_CANDIDATE`, never left unclassified.
- **XR1-AC-26 — `APPROVED_APPLY` reachable only via manifest.** No path
  reaches `APPROVED_APPLY` from `scan` alone; only `apply`, consuming an
  explicit manifest, can mark an entry `APPROVED_APPLY`, and only for paths
  the manifest names.
- **XR1-AC-27 — Orthogonality to `ADR-OW-001`'s vocabulary.** A test/
  assertion documents (and a code comment states) that `ELIGIBLE_CANDIDATE`/
  `APPROVED_APPLY` are not `PORT_AS_IS`/`ADAPT`/`REIMPLEMENT` dispositions;
  no function in `dispositions.py` emits any of `ADR-OW-001`'s five
  porting-vocabulary values.

## Acceptance criteria — cross-machine determinism (D)

- **XR1-AC-28 — Timestamp isolation.** The scan report's deterministic
  dataset (paths, hashes, dispositions, accounting totals) is a distinct,
  separately-hashable structure from its `generatedAt`/host-context fields.
- **XR1-AC-29 — Path-normalization safety.** A fixture containing a file
  whose Shift-side line endings are LF is scanned from a Windows checkout
  and reproduces the identical blob hash Shift's own `git cat-file` would
  report — proving the tool reads Git objects, not the local working
  tree's normalized bytes.

## Acceptance criteria — program discipline and claim boundary (E, F, G)

- **XR1-AC-30 — `XR1-O-C2` blocked pending Shift `XR1-S-C3`.** The work
  order's stated BUILD ceiling is not authorized to begin until Shift's
  `XR1-S-C3` closure commit is independently confirmed at its exact hash —
  stated as a precondition, not merely a note.
- **XR1-AC-31 — Independent repository histories.** No artifact in this
  spec's scope claims or requires a single atomic commit spanning both
  repositories; the six-commit sequence (`XR1-O-C1`–`C3`, `XR1-S-C1`–`C3`)
  is stated as fully independent per-repository history.
- **XR1-AC-32 — Claim-boundary statement present.** Each of
  `scan.py`/`apply.py`/`dispositions.py`'s module docstrings states the
  claim boundary from `ADR-OW-006` section F.
- **XR1-AC-33 — Repository gates pass (corrected, `XR1-R1`).** The full
  then-current regression suite — **177 tests as of this repair round**
  (116 pre-F1A + 61 F1A; whatever the count is at `XR1-O-C2` BUILD time,
  never assumed to still be 116) — continues to pass; `git diff --check`
  clean; `scripts/manage_cvf_downstream_catalog.ps1 -Check` PASS;
  project-scoped workspace doctor PASS 25/25 — evaluated at `XR1-O-C2`
  BUILD time, not this authorization round.
- **XR1-AC-34 — No provider call.** No task under this spec invokes an
  AI/agent provider API.
- **XR1-AC-35 — Rename is one logical record (`XR1-R2`).** A fixture
  rename (identical content, different path) produces exactly one
  `renamed` record carrying both `oldPath` and `newPath` — never a
  separate `deleted` record for `oldPath` plus a separate `added` record
  for `newPath`.
- **XR1-AC-36 — Rename-with-content-change stays one record (`XR1-R2`).**
  A fixture rename where the content also changes produces exactly one
  `renamed` record with `contentChanged: true` — it is never additionally
  counted as a `modified` record.
- **XR1-AC-37 — Deterministic tests per change type (`XR1-R2`).**
  Dedicated, independent fixtures and assertions exist for: an addition
  alone, a deletion alone, a pure rename alone, and a rename-with-
  modification — each verified against `ADR-OW-006` section B's exact
  total equation.
- **XR1-AC-38 — Apply-manifest schema, non-circular (`XR1-R3`; corrected,
  `XR1-R11`).** `scripts/linked_sources/apply_manifest.schema.json` exists
  and a manifest missing any of `schemaVersion`, `workspaceId`,
  `baseCommit`, `candidateCommit`, `scanDatasetSha256`,
  `filteringPolicyVersion`, `filteringPolicySha256`, any entry's
  operation-specific fields (`XR1-AC-45`), `authorizationReceiptPath`, or
  `manifestSha256` fails schema validation and is rejected by `apply`.
  `manifestSha256` is computed over UTF-8 JSON after removing that field and
  serializing with sorted keys, compact separators, and unescaped Unicode; a
  known-vector test reproduces it independently and rejects a mutated value. The
  schema has **no** `authorizationCommit` field and no self-declared
  status/approval field — a manifest carrying either is rejected as an
  unknown/disallowed field, not silently accepted.
- **XR1-AC-39 — Apply authorization verification, two-artifact model
  (`XR1-R3`; non-circular, `XR1-R11`).** `apply` takes the authorization
  commit and receipt path as external CLI arguments
  (`--authorization-commit`/`--authorization-receipt`), never read from
  inside the manifest, and rejects (zero writes) if: the given commit is
  not reachable from Operations `origin/main`; the manifest or receipt blob
  does not exist byte-for-byte at that exact commit; the receipt's
  `decision` is not exactly `REVIEW_PASS` naming that manifest's exact
  `manifestSha256`; the receipt's `scanDatasetSha256`/
  `filteringPolicySha256` do not match the manifest's own fields; or the
  canonical digests recomputed from the working manifest and parsed committed
  manifest blob do not both equal the manifest field and receipt's
  `manifestSha256`. Each
  of the following is individually tested and rejected: an
  arbitrary/unpushed local authorization commit; a manifest or receipt blob
  missing or byte-different at the given commit; a receipt naming a
  different `manifestSha256`; mismatched `scanDatasetSha256`/
  `filteringPolicySha256`; a locally-edited/drifted manifest; a `scan`
  report or repository-tracked-but-unreviewed draft used as the manifest;
  an uncommitted manifest file; and a manifest carrying its own
  self-declared `"status": "approved"`-shaped field.
- **XR1-AC-40 — Destination path escape, exhaustive negatives (`XR1-R4`).**
  Each of the following is rejected, fail-closed, individually tested: an
  absolute path; a drive-letter path; a UNC path; an empty path component;
  a `.`/`..` traversal component (forward-slash, backslash, and mixed-
  separator); a NUL byte in a component; an NTFS ADS-marker (`:`) in a
  component; a Windows reserved device name component
  (case-insensitive, with/without extension); two manifest entries
  resolving to the same destination; two destinations colliding only under
  case-insensitive or Unicode-normalization comparison; a destination under
  `.git/` or a protected governance/continuity/catalog path; a destination
  whose resolved path has a symlink/junction/reparse-point ancestor
  directory; a destination whose fully-resolved path escapes this
  repository's root; and a source entry recorded with Git mode `120000`
  (symlink) or `160000` (submodule) — the latter two are never applied and
  remain quarantine-only.
- **XR1-AC-41 — Apply atomicity and rollback (`XR1-R5`).** The rollback/
  preimage bundle exists and is hash-verified before the first destination
  write in a dry-run/order-of-operations test. A dedicated test injects a
  failure immediately after the first successful write and proves: every
  previously-mutated path in that run is restored, a failure/recovery
  receipt is produced naming what was attempted/mutated/restored, and the
  resulting working tree has zero residual content delta from its
  pre-apply state.
- **XR1-AC-42 — Bounded discovery, no filesystem search (`XR1-R6`).**
  `scan` resolves the Shift sibling only via the three-step order
  (validated local binding; exact expected sibling directory; explicit
  `--clone-to` or documented default) and never scans the filesystem
  looking for candidate directories. `scan` refuses to write into an
  existing, non-empty directory whose `origin` does not match
  `peerRepo.remote`. `.cvf/local-workspace-link.json` is asserted to never
  appear in `git status --porcelain`'s stageable output.
- **XR1-AC-43 — Deterministic filter precedence (`XR1-R7`).** A fixture
  matching both a `HARD_EXCLUDE` rule and a `PROTECTED_SOURCE_ONLY` rule
  classifies `HARD_EXCLUDE`; a fixture matching both `PROTECTED_SOURCE_ONLY`
  and `QUARANTINE_REVIEW` classifies `PROTECTED_SOURCE_ONLY`; a fixture
  matching both `QUARANTINE_REVIEW` and the `ELIGIBLE_CANDIDATE` default
  classifies `QUARANTINE_REVIEW` — the full
  `HARD_EXCLUDE > PROTECTED_SOURCE_ONLY > QUARANTINE_REVIEW >
  ELIGIBLE_CANDIDATE` order is exercised. No function in `dispositions.py`
  (the `scan`-side classifier) ever returns `APPROVED_APPLY`.
- **XR1-AC-44 — Secret-content detection without persistence, bounded
  execution scope (`XR1-R7`; scope corrected, `XR1-R13`).** Using only
  safe, synthetic fixture strings (never real credentials), a
  private-key-header-shaped fixture and a cloud-credential-token-shaped
  fixture each classify `HARD_EXCLUDE`. The scan report for those fixtures
  contains only `path`, `disposition`, a fixed `reason` rule identifier, and
  a `sha256` — a test asserts the matched substring and the file's raw
  content never appear anywhere in the report's serialized output.
  `XR1-O-C2`'s own test suite exercises this detector only against
  synthetic Git fixtures created for the tests — it performs no real `scan`
  or `apply` against Shift content and reads no real secret; a test asserts
  no test in this suite opens a real Shift sibling clone. A future real
  Shift `scan` is out of this spec's scope and requires its own bounded
  execution work order naming the exact candidate commit.
- **XR1-AC-45 — Operation-specific manifest `oneOf` (`XR1-R8`; rename
  precondition fields named exactly, `XR1-R12`).** A manifest entry
  validates against exactly one of the `new`/`modified`, `deleted`, or
  `renamed` shapes (`ADR-OW-006` section G); a `deleted` entry carrying a
  candidate-blob field, a `new`/`modified` entry missing
  `candidateSourceGitMode`, or a `renamed` entry missing `oldDestinationPath`,
  `newDestinationPath`, `oldDestinationPrecondition`, or
  `newDestinationPrecondition` each fail schema validation. A `deleted`
  entry never requires or accepts a nonexistent candidate blob hash. A
  `renamed` entry using a generic `destinationPrecondition` field name
  instead of the two exact rename-specific field names fails schema
  validation.
- **XR1-AC-46 — Destination precondition enforcement, per operation
  (`XR1-R8`; exact rename semantics, `XR1-R12`).** `new` requires
  `destinationPrecondition: {"state": "ABSENT"}`, rejected if the
  destination already exists; `modified`/`deleted` require `{"state":
  "PRESENT", "sha256": "<hash>"}`, rejected if absent or if the actual
  on-disk hash differs (destination drift); `renamed` requires
  `oldDestinationPrecondition: {"state": "PRESENT", "sha256": "<hash>"}`
  (rejected if absent or hash-mismatched) and `newDestinationPrecondition:
  {"state": "ABSENT"}` (rejected if the new destination already exists).
  Every invalid operation/precondition combination is individually tested
  (e.g. `new` with `PRESENT`, `deleted` with `ABSENT`, rename with
  `oldDestinationPrecondition: ABSENT` or `newDestinationPrecondition:
  PRESENT`). A dedicated test covers a rename whose `newDestinationPath`
  collides with another entry's destination only under case-insensitive or
  Unicode-normalization comparison (rename collision, rejected under
  section H's collision rule, not treated as a distinct destination) and a
  `deleted` entry whose destination was locally modified after the
  manifest was authored (rejected as drift, not silently applied). Every
  precondition is re-checked immediately before that entry's mutation, not
  only once at batch start, and a test proves a destination changed
  between the initial check and the write is caught.
- **XR1-AC-47 — Recovery artifact locations and retention (`XR1-R9`).** A
  successful `apply` run's raw preimage bytes exist only under
  `.cvf/local-linked-source-recovery/<run-id>/` and that path is listed in
  `.gitignore`; `git status --porcelain` and `git add -n
  .cvf/local-linked-source-recovery` both show it as ignored, never
  stageable. The committed
  `provenance/shift-operations/<candidate>/apply/<manifest-sha>/apply_receipt.json`
  (success) or `failure_recovery_receipt.json` (failure) contains only
  paths, dispositions, before/after `sha256` values, and an outcome
  field — a test asserts no raw file content, secret value, credential, or
  absolute local filesystem path appears anywhere in either receipt's
  serialized output.

## Out of scope for this spec

- Any modification to `shift-operations-workspace`, including its core-pin
  drift (`6ce1cf0` -> `27137db4`) — Shift's own prerequisite (`XR1-S-C2`).
- Any F1A schema/test/tool/registry change, or resumption of F1A BUILD.
- Shift's lane 2 (`P2B-APPROVER-IDENTITY-RECONCILIATION`).
- CVF core or bootstrap implementation/modification; any bootstrap-learning
  artifact.
- Any third application repository or Git submodule.
- Any change to `docs/roadmaps/CVF_OPERATIONS_WORKSPACE_ROADMAP.md`,
  `docs/catalog/ARTIFACT_REGISTRY.json`, `docs/INDEX.md`, `.cvf/manifest.json`,
  or `AGENTS.md`.

## Claim boundary

Satisfying every criterion above proves the two-repository descriptor
contract and the `scan`/`apply` tool's discovery, accounting, filtering,
and governed-application mechanics are correct and deterministic — nothing
about Shift's runtime behavior, F1A/F1B, AI governance, or any specific
porting decision's correctness.
