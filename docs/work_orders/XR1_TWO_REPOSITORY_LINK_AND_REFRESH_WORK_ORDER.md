# Work Order — XR1 Two-Repository Portable Link and Governed Shift Refresh

- Work Order ID: `OW-XR1-WO-001`
- Date: 2026-07-24
- Implements: `ADR-OW-006`, `OW-XR1-SPEC-001`
- Status: DRAFT (pending independent REVIEW_PASS)
- Repository scope: `CVF-Operations-Workspace` only. `shift-operations-workspace`
  is read-only evidence in this round and receives no BUILD from this
  document.

## Repair note (round 1, 2026-07-24)

Independent Codex review returned `XR1-R1` through `XR1-R7` (full detail in
`ADR-OW-006`'s repair note). This work order is repaired accordingly:

- **XR1-R1** — every "F1A uncommitted/awaiting review" statement below is
  corrected: F1A is **CLOSED, FROZEN, PARKED** (C1
  `d731762a9e135b075261831ed7eb0df4badc98dd`, C2
  `9e59cfdcf3d1da2644540088e748123cd41f14e9`, C3
  `4cdd7f06e040fee43ab733d3dc608aa4d425452b`, C4
  `0efa7f23bfb2ea5677b680ed35ca0ae3f057e715`); the regression baseline is
  **177** tests; the stale parenthetical about "pre-existing,
  still-uncommitted F1A BUILD content" is removed. F1A is not reopened.
- **`XR1-O-C1` wording** — the authorization-round and commit-plan
  descriptions are corrected to name exactly the six paths, without a
  "plus authorization continuity" appendage (the continuity files are
  three of the six, not a seventh addition).
- **`XR1-R2`–`XR1-R7`** — the BUILD changed-set ceiling gains
  `scripts/linked_sources/apply_manifest.schema.json` (`XR1-R3`); the stop
  conditions gain explicit entries for accounting-model violations
  (`XR1-R2`), unverifiable apply authorization (`XR1-R3`), destination-path
  escape (`XR1-R4`), partial-apply/rollback failure (`XR1-R5`), unsafe
  discovery (`XR1-R6`), and filter-precedence/secret-persistence violations
  (`XR1-R7`).

Repaired inside the same six-path ceiling; no seventh path. Role:
`REPAIR_WORKER`. Codex retains independent `REVIEWER`/`COMMIT_STEWARD`
authority; this round does not self-grant REVIEW_PASS. Status:
`REPAIRED_PENDING_INDEPENDENT_RE_REVIEW`.

## Repair note (round 2, 2026-07-24)

Independent Codex review returned `XR1-R7B` (a fresh finding, renamed in
round 3's governance-id cleanup from a reused `XR1-R7`; round 1's closed
`XR1-R7` is unaffected) through `XR1-R10` (full detail in `ADR-OW-006`'s
repair notes). Repaired: the "five dispositions" stop-condition phrasing
corrected to the four `scan`-time classifications plus the separate
`APPROVED_APPLY` lifecycle state (`XR1-R7B`); the BUILD ceiling gains
`provenance/.../apply/<manifest-sha>/{apply_receipt,failure_recovery_receipt}.json`
and gitignored `.cvf/local-linked-source-recovery/<run-id>/**`, and the
`.gitignore` bullet is extended to cover both new ignored paths (`XR1-R9`);
new stop conditions cover operation-schema/destination-precondition
violations (`XR1-R8`, further tightened by round 3's `XR1-R12`), recovery
artifacts appearing outside their authorized locations (`XR1-R9`), and scan
side-effects beyond the exact boundary (`XR1-R10`). Repaired inside the
same six-path ceiling; no seventh path. Status:
`REPAIRED_PENDING_INDEPENDENT_RE_REVIEW_2`.

## Repair note (round 3, 2026-07-24)

Independent Codex review returned `XR1-R11`–`XR1-R13`. Repaired: the
authorization-verification stop condition rewritten for the non-circular
two-artifact model — `apply` takes `--authorization-commit`/
`--authorization-receipt` as external CLI arguments, the manifest carries
no `authorizationCommit` field, and a separate independent review receipt
supplies the approval evidence (`XR1-R11`); the BUILD ceiling's manifest
schema fields corrected to name the `renamed` operation's
`oldDestinationPrecondition`/`newDestinationPrecondition` fields exactly
(`XR1-R12`); the "any secret read" exclusion and the "secret detection"
stop condition both corrected to prohibit human/agent/provider/log/
tracked-file exposure of secret content while accurately describing a
future authorized detector's bounded, machine-local-only blob inspection —
`XR1-O-C2` itself performs no real Shift scan and reads no real secret
(`XR1-R13`). Repaired inside the same six-path ceiling; no seventh path.
Status: `REPAIRED_PENDING_INDEPENDENT_RE_REVIEW_3`.

## Role route

```text
ORCHESTRATOR -> SPEC_AUTHOR -> WORK_ORDER_AUTHOR (Claude, this authorization
round) -> REVIEWER -> COMMIT_STEWARD (XR1-O-C1, Codex) -> [Shift-side
XR1-S-C1/C2/C3, out of this repository's control] -> IMPLEMENTATION_WORKER
(XR1-O-C2 BUILD, blocked until Shift XR1-S-C3 closure is confirmed) ->
REVIEWER -> REPAIR_WORKER if needed -> RE_REVIEW -> COMMIT_STEWARD
(XR1-O-C2 commit) -> REVIEWER (independent receipt) -> COMMIT_STEWARD
(XR1-O-C3) -> CLOSER -> SESSION_SYNC_STEWARD -> ORCHESTRATOR
```

Claude holds ORCHESTRATOR -> SPEC_AUTHOR -> WORK_ORDER_AUTHOR only, this
round. Does not self-grant REVIEW_PASS, does not stage/commit/push, does
not author the independent review receipt, and does not touch
`shift-operations-workspace`.

## Authorization-round changed set (this round only — authoring, not BUILD)

Exactly six paths, no seventh:

1. `docs/decisions/ADR_2026-07-24_XR1_TWO_REPOSITORY_LINK_AND_REFRESH.md`
2. `docs/specs/XR1_TWO_REPOSITORY_LINK_AND_REFRESH_SPEC.md`
3. `docs/work_orders/XR1_TWO_REPOSITORY_LINK_AND_REFRESH_WORK_ORDER.md`
4. `IMPLEMENTATION_STATUS.json`
5. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
6. `CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-07-23.md`

Not touched this round (corrected, `XR1-R1`: F1A is closed/frozen, not
uncommitted content pending this round's forbearance): canonical roadmap,
`docs/catalog/**`, `docs/INDEX.md`, `.cvf/manifest.json`,
`.cvf/workspace-link.json`, `.cvf/local-workspace-link.json`,
`scripts/linked_sources/**`, `tests/linked_sources/**`, `provenance/**`,
`AGENTS.md`, any F1A path (`contracts/**`, `tests/contracts/**`,
`requirements-contract-validator.txt`, `docs/reviews/F1A_*`),
`shift-operations-workspace` (any path), the CVF core repository.

## BUILD changed-set ceiling for `XR1-O-C2` (authorized only after Codex REVIEW_PASS on this package AND Shift `XR1-S-C3` closure is confirmed)

Every path named exactly — not a wildcard grant:

**Descriptor files (new):**

- `.cvf/workspace-link.json` (tracked, exact schema per `ADR-OW-006`
  section A / `XR1-AC-01`)
- `.cvf/local-workspace-link.json` (new `.gitignore` entry added for this
  path; the file itself is never committed)

**Tool (new):**

- `scripts/linked_sources/workspace_link.py`
- `scripts/linked_sources/scan.py`
- `scripts/linked_sources/apply.py`
- `scripts/linked_sources/dispositions.py`
- `scripts/linked_sources/filtering_policy.json`
- `scripts/linked_sources/apply_manifest.schema.json` (new, `XR1-R3` — the
  versioned apply-manifest schema, `ADR-OW-006` section G)

**Tests (new):**

- `tests/linked_sources/__init__.py`
- `tests/linked_sources/workspace_link_test.py`
- `tests/linked_sources/scan_test.py`
- `tests/linked_sources/apply_test.py`
- `tests/linked_sources/dispositions_test.py`
- `tests/linked_sources/apply_manifest_test.py` (new, `XR1-R3`)

**Provenance (new, per candidate commit scanned — not created until a real
`scan` runs against a real candidate):**

- `provenance/shift-operations/<candidate-commit>/linked_sources_scan_report.json`
- `provenance/shift-operations/<candidate-commit>/linked_sources_inventory.json`
- `provenance/shift-operations/<candidate-commit>/apply/<manifest-sha>/apply_receipt.json`
  and `.../failure_recovery_receipt.json` (new, `XR1-R9` — not created
  until a real `apply` runs; hashes/statuses only, `ADR-OW-006` section I)

**Local, gitignored, never committed (new, `XR1-R9`):**

- `.cvf/local-linked-source-recovery/<run-id>/**` — raw `apply` preimage
  bytes, section I

**Repository config (modified):**

- `.gitignore` (add `.cvf/local-workspace-link.json` and
  `.cvf/local-linked-source-recovery/`, `XR1-R9`)

**Continuity/status paths (BUILD-time updates):**

- `IMPLEMENTATION_STATUS.json`
- `CVF_SESSION/ACTIVE_SESSION_STATE.json`
- `CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-07-23.md`

No other path may be touched by `XR1-O-C2` — specifically excluded:
`docs/roadmaps/**`, `docs/INDEX.md`, `docs/catalog/ARTIFACT_REGISTRY.json`,
`.cvf/manifest.json`, `AGENTS.md`, any `contracts/**` or F1A test/schema
path, any path inside `shift-operations-workspace`, the CVF core
repository, and any third repository.

## Cross-repository blocking precondition

`XR1-O-C2` may not begin until: (a) `XR1-O-C1` (this package) is
independently REVIEW_PASS'd and pushed; and (b) Shift's `XR1-S-C3` closure
commit is independently confirmed at its exact hash, recording that Shift's
core-pin prerequisite (`XR1-S-C2`) and Shift's own reciprocal
`.cvf/workspace-link.json` are complete and independently reviewed. Absent
(b), `XR1-O-C2` is a scope-expansion stop condition, not a judgment call any
worker may waive.

## Explicit exclusions (stop and escalate if touched)

CVF core/bootstrap implementation or modification; any bootstrap-learning
artifact; any third application repository; any workspace-root tracked
artifact; any Git submodule; F1A (`XR1-R1`: reopening, modifying, or
amending the CLOSED/FROZEN tranche or any of its four commits in any way);
Shift lane 2 (`P2B-APPROVER-IDENTITY-RECONCILIATION`) implementation; any
runtime asset port/import from Shift into Operations; any provider/AI call;
any exposure of secret-shaped content to a human, agent, provider, log,
prompt, or tracked file (`XR1-R13`: this round performs no `scan`/`apply`
and reads no content at all — a future authorized detector's bounded,
machine-local-only blob inspection, `ADR-OW-006` section C, is not
authorized by this round either); `shift-operations-workspace` in any way,
including its untracked assessment file.

## Roles and ownership

- **IMPLEMENTATION_WORKER** (provider-neutral role contract, `XR1-O-C2`
  only, future): authors exactly the BUILD ceiling above. Does not stage,
  commit, push, self-approve REVIEW_PASS, or declare FREEZE. Does not
  touch `shift-operations-workspace`.
- **REVIEWER / COMMIT_STEWARD** (Codex, independent from
  IMPLEMENTATION_WORKER for this R2 risk tranche): reviews this
  authorization package (`XR1-O-C1`), confirms Shift's `XR1-S-C3` closure
  before `XR1-O-C2` may start, reviews the BUILD, authors the independent
  review receipt and `XR1-O-C3` closure continuity.

## Tasks (this authorization round)

1. Author `ADR-OW-006`, `OW-XR1-SPEC-001`, `OW-XR1-WO-001`.
2. Record the XR1 authorization entry in the active handoff; set
   continuity to `WORK_ORDER`/`WORK_ORDER_AUTHOR`, F1A explicitly recorded
   as CLOSED, FROZEN, and PARKED (C1–C4 on `origin/main`, 177-test
   baseline — unchanged by this round), awaiting Codex REVIEWER for XR1.
3. Do not touch `docs/catalog/**`, `docs/INDEX.md`, the roadmap,
   `.cvf/workspace-link.json`, `scripts/linked_sources/**`,
   `tests/linked_sources/**`, any F1A path, or
   `shift-operations-workspace`.

## Commit plan (Operations side; owned exclusively by Codex COMMIT_STEWARD)

- **`XR1-O-C1` — Authorization package.** Stages exactly the six
  authorization-round paths above — no more, no fewer (`XR1-R1` repair:
  removed the "plus authorization continuity" phrasing, since the three
  continuity paths are three of those six, not a seventh addition).
  Explicit-path staging only. Rehearsed post-commit/pre-push in a temporary
  sibling worktree. Pushed only after PASS.
- **`XR1-O-C2` — Descriptor/tool/tests BUILD.** Stages exactly the BUILD
  ceiling paths actually created, plus BUILD self-report continuity.
  Blocked until Shift `XR1-S-C3` is independently confirmed (see
  "Cross-repository blocking precondition"). Same staging/rehearsal/push
  discipline.
- **`XR1-O-C3` — Independent review receipt and closure continuity.**
  Stages the independent review receipt plus the three continuity paths.
  Same discipline. Any post-push continuity synchronization (mirroring
  F1A's C4 precedent) is its own separate, later commit — never folded
  into `XR1-O-C3` itself.

Shift-side commits (`XR1-S-C1`, `XR1-S-C2`, `XR1-S-C3`) belong to Shift's
own repository and are outside this work order's authority; this document
only records their existence as a precondition for `XR1-O-C2`. **No
cross-repository atomic commit is claimed or possible** — each commit
above is a fully independent, single-repository action with its own
rehearsal.

Every commit, in either repository:

1. Explicit-path staging only (never `git add -A` or `git add .`).
2. Commit created by Codex.
3. Post-commit/pre-push sibling-worktree rehearsal.
4. Push only after the rehearsal PASSes.
5. No amend, rebase, force-push, `git add .`, or `git add -A`, ever.

## Stop conditions

- Remote or commit drift (either repository's HEAD/origin/main, or the CVF
  core pin, no longer matches this package's recorded values at BUILD
  time).
- A non-ancestor candidate-commit update presented to `scan`/`apply`
  without a separately authorized override.
- Dirty or mutated Shift input beyond the one disclosed, byte-identical
  untracked assessment file.
- Any mutation to that assessment file's bytes (hash mismatch against
  `168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2`).
- Any secret-shaped content exposed to a human, agent, provider, log,
  prompt, or tracked file — `HARD_EXCLUDE`'s own classification/quarantine
  of secret-shaped content is expected behavior, not itself a stop
  condition (`XR1-R13`).
- An unaccounted changed path (any path not landing in exactly one of
  `unchanged`/`new`/`modified`/`deleted`/`renamed`, or not landing in
  exactly one of the four `scan`-time classifications — corrected
  `XR1-R7B`).
- A nondeterministic inventory (two scans of the same base/candidate pair
  producing different hashes for the deterministic dataset).
- Descriptor disagreement between the two repositories' `.cvf/workspace-link.json`
  files once both exist.
- A local absolute path entering any tracked file.
- Any mutation of the Shift sibling's checked-out branch or worktree by
  `scan` or `apply`.
- Authorization ambiguity (this package's own text self-contradicting).
- `apply` invoked without an exact, repository-tracked, independently
  reviewed manifest.
- Auto-application of a deletion or rename disposition.
- Scope expansion into CVF core/bootstrap/learning, F1A, or Shift lane 2.
- Catalog/continuity conflict (state, handoff, and status disagreeing —
  stop at INTAKE, do not choose one silently).
- A failed rollback rehearsal for any `apply` run.
- `XR1-O-C2` beginning before Shift `XR1-S-C3` closure is independently
  confirmed.
- **Accounting-model violation (`XR1-R2`).** A `scan` report whose
  disposition/bucket counts do not satisfy `ADR-OW-006` section B's exact
  equation, or that records a rename as two separate entries instead of one
  logical record.
- **Unverifiable apply authorization, non-circular model (`XR1-R3`;
  `XR1-R11`).** `apply` proceeding when the CLI-supplied
  `--authorization-commit` is not reachable from Operations `origin/main`;
  when the manifest/receipt blob is not present, byte-for-byte, at that
  exact commit; when the receipt does not name that manifest's exact hash
  with `decision: REVIEW_PASS`; when the receipt's
  `scanDatasetSha256`/`filteringPolicySha256` disagree with the manifest's;
  or when the manifest itself carries an `authorizationCommit` field or any
  self-declared status/approval field (schema-rejected, `XR1-R11`).
- **Destination-path escape (`XR1-R4`).** Any destination path accepted
  despite failing section H's checks — absolute/UNC path, traversal
  (including mixed-separator), reserved/ADS/NUL component, case/Unicode
  collision, duplicate destination, protected-path destination, a
  symlink/junction ancestor, an escape of the repository root, or a
  Git-mode `120000`/`160000` source ever being applied.
- **Partial apply without full rollback (`XR1-R5`).** Any `apply` failure
  that leaves even one destination path in a mutated-but-not-restored
  state, or a rollback bundle written or verified after any destination
  mutation instead of before it.
- **Unsafe discovery (`XR1-R6`).** `scan` searching the filesystem beyond
  the three bounded resolution steps, or writing into a non-empty,
  wrong-remote directory.
- **Filter-precedence or secret-persistence violation (round 1 `XR1-R7`).**
  A change record classified against the stated precedence order
  incorrectly, `dispositions.py` emitting `APPROVED_APPLY`, or any report
  persisting a matched secret substring or raw secret-bearing file content.
- **Filter-lifecycle separation violation (`XR1-R7B`).** Any `scan` report
  containing the string `APPROVED_APPLY` as a classification value, or
  classification counts that do not sum to the four-classification total.
- **Operation-schema or destination-precondition violation (`XR1-R8`; exact
  rename field names, `XR1-R12`).** A manifest entry not matching its
  operation's exact `oneOf` shape; a `deleted` entry requiring/accepting a
  candidate blob; a `renamed` entry using a generic `destinationPrecondition`
  field instead of `oldDestinationPrecondition`/`newDestinationPrecondition`;
  a write proceeding despite a `destinationPrecondition` mismatch (including
  either rename-specific field) at initial check or at the immediate
  pre-mutation recheck; or a case/Unicode-only rename-destination collision
  not rejected under section H's collision rule.
- **Recovery artifact outside its authorized location (`XR1-R9`).** Raw
  preimage bytes appearing anywhere other than
  `.cvf/local-linked-source-recovery/<run-id>/`; that path, or any file
  under it, being staged or committed; or a tracked `apply`/
  `failure_recovery` receipt containing raw preimage bytes, a matched
  secret value, a credential, or an absolute local path.
- **Scan side-effect beyond the exact boundary (`XR1-R10`).** Any `scan`
  run changing a tracked Operations path other than its own declared
  provenance output and `.cvf/local-workspace-link.json`, mutating a
  pre-existing Shift sibling's branch/worktree/`HEAD`, or writing into a
  peer-clone destination outside the bounded resolution order.

## Completion boundary

This work order authorizes, for `CVF-Operations-Workspace` only: a
portable, tracked two-repository descriptor pair; a `scan`/`apply` tool and
its tests; a machine-readable filtering policy; and the continuity updates
recording this program. It does not authorize any change to
`shift-operations-workspace`, any CVF core/bootstrap change, any bootstrap-
learning artifact, any third repository or Git submodule, any F1A resumption,
any Shift lane-2 implementation, or any runtime asset import. `XR1-O-C2`
BUILD may begin only after this package is independently reviewed,
REVIEW_PASS'd, `XR1-O-C1` is committed/rehearsed/pushed, and Shift's
`XR1-S-C3` closure is independently confirmed at its exact commit hash.
