# ADR — XR1 Two-Repository Portable Link and Governed Shift Refresh

- ADR ID: `ADR-OW-006`
- Date: 2026-07-24
- Status: ACCEPTED_FOR_PLANNING
- Decision owner: repository owner
- Risk: R2

## Repair notes (rounds 1–3, 2026-07-24 — full finding-by-finding detail in the active handoff)

**Round 1 — `XR1-R1`–`XR1-R7`, closed without waiver:** baseline corrected
to Operations HEAD `0efa7f23bfb2ea5677b680ed35ca0ae3f057e715` (F1A
**CLOSED, FROZEN, PARKED**, C1–C4 through
`0efa7f23bfb2ea5677b680ed35ca0ae3f057e715`, 177-test baseline; `XR1-R1`);
one accounting universe/exact equation/single-record rename rule, section B
(`XR1-R2`); manifest schema and commit/receipt verification, section G —
**superseded by round 3's non-circular model, `XR1-R11`** (`XR1-R3`);
destination-path safety, section H (`XR1-R4`); rollback/atomicity, section
I (`XR1-R5`); bounded 3-step discovery, section B (`XR1-R6`); filter
precedence and secret-content rule, section C (`XR1-R7` — distinct from
round 2's `XR1-R7B` below, never the same finding).

**Round 2 — `XR1-R7B`–`XR1-R10`, closed without waiver** (governance-id
cleanup, round 3: this finding is `XR1-R7B`, never a reused `XR1-R7`):
`XR1-R7B` `INCOMPLETE_FILTER_LIFECYCLE_SEPARATION` — section C rewritten to
exactly **four** `scan`-time classifications plus a separate, never
`scan`-emitted `APPROVED_APPLY` lifecycle state. `XR1-R8`
`OPERATION_SCHEMA_AND_DESTINATION_DRIFT` — section G's manifest schema as
an operation-keyed `oneOf`, each shape's own `destinationPrecondition` —
**rename preconditions further named exactly by round 3, `XR1-R12`**.
`XR1-R9` `RECOVERY_ARTIFACTS_OUTSIDE_CEILING` — section I's exact recovery
locations. `XR1-R10` `SCAN_SIDE_EFFECT_CONTRADICTION` — `scan`'s exact
side-effect boundary (section B step 9).

**Round 3 — `XR1-R11`–`XR1-R13`, closed without waiver:** `XR1-R11`
`CIRCULAR_COMMIT_BINDING` — a file cannot contain the hash of the commit
that contains it; section G rewritten to a non-circular two-artifact model
(immutable manifest; separate independent review receipt; `apply` invoked
with an external `--authorization-commit`/`--authorization-receipt`
locator). `XR1-R12` `OPERATION_PRECONDITION_TOO_PERMISSIVE` — section G's
`renamed` shape now names `oldDestinationPrecondition`
(`PRESENT`+exact hash) and `newDestinationPrecondition` (`ABSENT`)
explicitly; case/Unicode-equivalent renames stay rejected under section
H's collision rule. `XR1-R13` `SECRET_SCAN_SCOPE_CONTRADICTION` — section
C separates `XR1-O-C2` BUILD (synthetic fixtures only, no real Shift scan
or secret read) from a future real Shift scan's own bounded execution work
order, whose detector may stream Git blob bytes locally, machine-only, for
classification but never expose them beyond that boundary.

All three rounds repaired exactly the six-path ceiling; no seventh path; no
BUILD; F1A not reopened. Role: `REPAIR_WORKER` (Claude, provider-neutral
role contract). Codex retains independent `REVIEWER`/`COMMIT_STEWARD`
authority; no self-granted REVIEW_PASS. Status (this round):
`REPAIRED_PENDING_INDEPENDENT_RE_REVIEW_3`.

## Context

`CVF-Operations-Workspace` and `shift-operations-workspace` are two
independent Git repositories under one owner (`ADR-OW-001`: greenfield
platform, Shift remains source authority until an explicit asset is
accepted). Today their relationship is informal: a hidden sibling checkout,
a hard-coded pin in `IMPLEMENTATION_STATUS.json`/F0 provenance, and no
machine-readable descriptor either repository can validate against. XR1
opens authorization for (a) a portable, tracked relationship contract
between the two repositories, valid from a fresh clone on any machine, and
(b) a governed, two-mode (`scan`/`apply`) refresh tool, Operations-side
only, that discovers Shift changes deterministically and never applies
anything without a separately reviewed, repository-tracked manifest.

This round authors authorization only, for the Operations repository only.
No BUILD occurs. `shift-operations-workspace` is not modified.

## Verified input truth (this round, post-F1A-closure baseline — `XR1-R1`)

- Operations: HEAD = `origin/main` = `0efa7f23bfb2ea5677b680ed35ca0ae3f057e715`.
- Shift (read-only): HEAD = `origin/main` = `f98f29e145fa002be070e9d44520d20f0f82dcb3`,
  worktree clean except the pre-existing untracked
  `docs/decisions/ASSESSMENT_2026-07-23_OPERATIONS_WORKSPACE_REPOSITIONING.md`
  (`sha256:168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2`,
  recorded this round as the byte-identity baseline this round must not
  disturb).
- CVF core: HEAD = `27137db4d9aa2aea931ddd2507185d5c24943080`, unchanged,
  matching `.cvf/manifest.json`.
- F1A (`ADR-OW-005`, `OW-F1A-SPEC-001`, `OW-F1A-WO-001`) is **CLOSED,
  FROZEN, and PARKED** — independently `REVIEW_PASS`'d and FREEZE'd, C1
  `d731762a9e135b075261831ed7eb0df4badc98dd` through C4
  `0efa7f23bfb2ea5677b680ed35ca0ae3f057e715` (this repository's current
  HEAD), all on `origin/main`. The **current regression baseline is 177
  tests** (116 pre-F1A + 61 F1A), not 116. F1A is not reopened, not
  modified, and not touched by this tranche — PARKED means
  closed-and-inert, not "still open elsewhere."
- Shift's own lane 2 (`OW-RM1`'s roadmap: known-principals.yaml <-> users
  reconciliation / `P2B-APPROVER-IDENTITY-RECONCILIATION`, authorized as a
  Shift-side work order at Shift commit `f98f29e145fa002be070e9d44520d20f0f82dcb3`)
  remains **PARKED**: not cancelled, not reordered, not touched.
- Shift's `.cvf/manifest.json` still pins CVF core
  `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2`, while the shared public core
  (and this repository's own pin) is `27137db4d9aa2aea931ddd2507185d5c24943080`.
  This is a **Shift-side prerequisite**, not an Operations-side or tool
  concern: fixing it requires Shift's own authorization/BUILD/commit,
  exactly mirroring how this repository resolved its own analogous drift in
  `ADR-OW-003`/`OW-G2-WO-001`. This ADR does not authorize touching it and
  the tool proposed below never silently includes a core-pin fix in any
  BUILD it performs.

## Decision

### A. Portable relationship contract

- **`workspaceId`**: `cvf-operations-workspace` — one stable identifier
  shared by both repositories' descriptors, never regenerated per clone or
  per machine.
- **Roles**: Operations = `PRIMARY_PLATFORM`; Shift = `PROFILE_SOURCE`.
- **Relationship direction**: `SHIFT_TO_OPERATIONS_GOVERNED_INTAKE` — Shift
  content flows into Operations only through the governed `scan`/`apply`
  tool below; Operations never writes to or pushes into Shift.
- **Canonical GitHub remotes** (exact, both descriptors must match these
  literally):
  - Operations: `https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git`
  - Shift: `https://github.com/CVF-Ecosystem/shift-operations-workspace.git`
- **Source pin and pin-update rule**: the descriptor's `sourcePin` is the
  exact Shift commit this repository's tooling/provenance was last governed
  against (currently `f98f29e145fa002be070e9d44520d20f0f82dcb3`, matching
  F0). The pin **only** advances as the recorded output of a reviewed
  `scan` -> authorized manifest -> `apply` -> independent review cycle
  (`OW-XR1-WO-001`'s commit sequence, section E below). No script, cron, CI
  step, or agent may silently rewrite `sourcePin` to Shift's current
  `HEAD`; that is precisely the "implicitly tracks latest Shift" failure
  mode section D forbids.
- **Tracked descriptor** — `.cvf/workspace-link.json` (new, this
  repository):

  ```json
  {
    "schemaVersion": "1.0",
    "workspaceId": "cvf-operations-workspace",
    "thisRepo": {
      "repoId": "cvf-operations-workspace",
      "role": "PRIMARY_PLATFORM",
      "remote": "https://github.com/CVF-Ecosystem/CVF-Operations-Workspace.git"
    },
    "peerRepo": {
      "repoId": "shift-operations-workspace",
      "role": "PROFILE_SOURCE",
      "remote": "https://github.com/CVF-Ecosystem/shift-operations-workspace.git"
    },
    "relationshipDirection": "SHIFT_TO_OPERATIONS_GOVERNED_INTAKE",
    "sourcePin": "f98f29e145fa002be070e9d44520d20f0f82dcb3",
    "pinUpdatePolicy": "REVIEWED_SCAN_APPLY_CYCLE_ONLY"
  }
  ```

  No field may hold an absolute filesystem path, a machine name, or a local
  username — this file is portable across clones and machines by
  construction.
- **Ignored local binding** — `.cvf/local-workspace-link.json` (new,
  gitignored, mirroring the existing `.cvf/local-binding.json` precedent
  for the CVF-core sibling path):

  ```json
  {
    "schemaVersion": "1.0",
    "workspaceId": "cvf-operations-workspace",
    "peerRepoId": "shift-operations-workspace",
    "peerLocalPath": "<absolute-or-relative-local-path-to-the-sibling-clone>"
  }
  ```

  This is the **only** file in this contract permitted to hold a local
  path. Clarified (`XR1-R6`): it is **ignored local execution state** —
  written or refreshed by `scan` as a side effect of the bounded
  resolution order below (never hand-authored, never required to exist
  beforehand), and it is never staged, never committed, and never a valid
  target for `git add` under any circumstance (enforced by `.gitignore`,
  not merely by convention). Deleting it is always safe: the tracked
  descriptor's `sourcePin` carries all durable state.
- **Both-present validation.** When both `.cvf/workspace-link.json` (this
  repository) and Shift's own future `.cvf/workspace-link.json` (Shift-side,
  authorized separately under `XR1-S-C2`, section E) are readable, a
  validator checks, failing closed on any mismatch: `workspaceId` equal on
  both sides; each side's `repoId` equals the other side's `peerRepo.repoId`;
  each side's own `remote` equals the other side's `peerRepo.remote`; roles
  are complementary (`PRIMARY_PLATFORM` <-> `PROFILE_SOURCE`);
  `relationshipDirection` identical; and this side's `sourcePin` resolves to
  a real, reachable commit in the peer's history (an ancestor of or equal
  to the peer's current `HEAD`).
- **Single-repo case.** If only one repository is cloned, its own
  `.cvf/workspace-link.json` alone must fully identify the exact peer
  (`peerRepo.repoId` + `peerRepo.remote`) so a fresh clone of the peer can
  be discovered or performed without any other input.

### B. Operations-side governed refresh tool

New paths (BUILD-only, `XR1-O-C2`, not created this round):

- `scripts/linked_sources/workspace_link.py` — loads/validates
  `.cvf/workspace-link.json` and, if present,
  `.cvf/local-workspace-link.json`, per section A's rules.
- `scripts/linked_sources/scan.py` — scan mode (below).
- `scripts/linked_sources/apply.py` — apply mode (below).
- `scripts/linked_sources/dispositions.py` — the filtering classifier
  (section C).
- `scripts/linked_sources/filtering_policy.json` — the machine-readable
  filtering policy: explicit path-glob/extension rule lists for
  `HARD_EXCLUDE`, `PROTECTED_SOURCE_ONLY`, and `QUARANTINE_REVIEW` trigger
  conditions, versioned and reviewable independently of the Python code
  that reads it.
- `scripts/linked_sources/apply_manifest.schema.json` (new, `XR1-R3`) —
  the versioned apply-manifest schema, section G.
- `tests/linked_sources/workspace_link_test.py`,
  `scan_test.py`, `apply_test.py`, `dispositions_test.py` (or one combined
  suite; exact file list is `OW-XR1-WO-001`'s job, not this ADR's).
- `provenance/shift-operations/<candidate-commit>/linked_sources_scan_report.json`
  and `.../linked_sources_inventory.json` — new output names, distinct from
  F0's existing `file_inventory.json`/`capture_receipt.json`/etc. at
  `f98f29e145fa002be070e9d44520d20f0f82dcb3`, so a future scan never
  overwrites F0's frozen historical evidence.
- `provenance/shift-operations/<candidate-commit>/apply/<manifest-sha>/apply_receipt.json`
  and `.../failure_recovery_receipt.json` (new, `XR1-R9`) — tracked-safe
  `apply` receipts, section I.
- `.cvf/local-linked-source-recovery/<run-id>/**` (new, `XR1-R9`,
  gitignored) — local raw preimage bytes, never tracked, section I.

**`scan` mode:**

1. **Bounded sibling resolution (corrected, `XR1-R6`) — never a filesystem
   search.** Exactly three ordered candidates, stopping at the first match,
   and no others ever considered: (1) a **validated**
   `.cvf/local-workspace-link.json` (named path exists, is a Git repo, its
   `origin` equals `peerRepo.remote` exactly — an invalid/stale binding is
   discarded, not repaired, and resolution falls through); (2) the exact
   expected sibling directory `../shift-operations-workspace`, if it exists
   with a matching `origin`; (3) an explicit `--clone-to <path>`, or the
   same default path, cloned read-only from `peerRepo.remote`. `scan`
   **never** overwrites, reuses, or writes into a directory that already
   exists, is non-empty, and does not match `peerRepo.remote` — that is a
   stop condition, never something to search past or repair silently.
2. `git fetch` only against the resolved Shift clone — never `checkout`,
   `reset`, `pull`, `merge`, or any command that changes Shift's current
   branch pointer or working tree.
3. Verify: the resolved clone's `origin` remote equals `peerRepo.remote`
   exactly; the descriptor's `sourcePin` (base) exists as a real commit in
   Shift's history; the candidate commit (explicitly supplied, e.g. Shift's
   current `origin/main` tip after fetch) exists; and the candidate is
   either equal to the base or a **descendant** of it (`git merge-base
   --is-ancestor <base> <candidate>`) — a non-ancestor candidate is a stop
   condition (`OW-XR1-WO-001`'s stop conditions), never silently accepted.
4. Diff **Git objects** (`git diff --name-status <base> <candidate>` plus
   per-blob `git cat-file`/`git hash-object` reads), never files checked out
   to disk — this is what makes the result immune to Windows line-ending or
   path-separator normalization (section D).
5. **Accounting model (corrected, `XR1-R2`) — one unambiguous comparison
   universe and one counting unit.** `B`/`C` = base/candidate tree path
   sets; `R` = matched rename pairs (Git similarity index, 50% default),
   each `(oldPath, newPath)` with `oldPath ∈ B\C`, `newPath ∈ C\B`, counted
   **once** as a single record carrying both paths — never as a separate
   deletion plus addition. Then: `unchanged = {p ∈ B∩C : hash_B(p)=hash_C(p)}`;
   `modified = {p ∈ B∩C : hash_B(p)≠hash_C(p)}` (excludes rename-pair
   paths); `added = {p ∈ C\B : p not a newPath in R}`; `deleted = {p ∈ B\C
   : p not an oldPath in R}`; `renamed = R`, each flagged
   `contentChanged = (hash_B(oldPath)≠hash_C(newPath))` — still **one**
   record even when content also changed, never additionally `modified`.
   **Exact total equation:** `|unchanged|+|modified|+|added|+|deleted|+
   |renamed| = |B ∪ C| − |R|` (each rename pair collapses two `B ∪ C`
   slots into its one record) — the single identity `scan` must satisfy;
   a report whose counts don't satisfy it is invalid, not incomplete.
6. Classify every accounted path into exactly one of section C's **four**
   `scan`-time classifications (never zero, never more than one, and
   never `APPROVED_APPLY` — that value never appears in a `scan` report;
   `XR1-R7B`).
7. Write a deterministic SHA-256 inventory (path -> blob hash ->
   disposition) and a candidate report to
   `provenance/shift-operations/<candidate-commit>/`, with all
   non-deterministic data (wall-clock timestamps, hostnames, absolute
   paths) isolated into a clearly separate `generatedAt`/`hostContext`
   section that is excluded from the dataset's own hash/determinism claim.
8. **Never import, copy, or write a single Shift source-file byte anywhere
   in this repository during `scan`.** Scan output is metadata (paths,
   hashes, classifications) only.
9. **Exact side-effect boundary (corrected, `XR1-R10`).** A `scan`
   invocation may change, at most: (a) its own declared provenance output
   under `provenance/shift-operations/<candidateCommit>/`; (b)
   `.cvf/local-workspace-link.json` (created or refreshed per step 1's
   bounded resolution); and (c), only when step 1's resolution reaches its
   third case, a **new** peer clone created at the bounded, validated
   clone destination (never an existing directory reused or overwritten).
   **No other path in this repository, and no path in an existing Shift
   sibling's tracked or worktree state, may change** — `scan` never
   touches any other Operations file (source, test, doc, or continuity)
   and never mutates a pre-existing Shift clone beyond the `git fetch` in
   step 2.

**`apply` mode:**

1. **Disabled by default.** Runs only when given an explicit
   `--manifest <path>` validating against section G's exact schema and
   passing section G's full commit/receipt verification — never this
   tool's own `scan` report, never an ad hoc CLI file list, never an
   uncommitted draft.
2. Before writing anything: re-verifies the manifest's stated base commit,
   target (candidate) commit, every listed source blob hash, every
   destination path (section H), and every listed disposition against a
   **fresh** `scan` of the same base/candidate pair. Any discrepancy —
   hash mismatch, path mismatch, disposition mismatch, or a manifest entry
   not present in the fresh scan — is drift: stop before writing
   (`OW-XR1-WO-001`'s stop conditions).
3. Applies **only** the exact files the manifest allowlists, verbatim,
   nothing inferred, nothing pattern-matched beyond the manifest's literal
   entries, and only after section H's destination-path safety checks pass.
4. **Never** treats a `scan` candidate report, by itself, as approval —
   approval exists only via section G's independently reviewed, committed
   receipt naming this exact manifest hash.
5. **Never** writes back to the Shift repository in any way.
6. **Never** auto-applies a `deleted` or `renamed` disposition — those
   require an explicit, individually named entry in the manifest; a
   manifest that only says "apply new/modified" does not implicitly cover
   deletions or renames.
7. Follows section I's all-or-restore atomicity contract: the rollback/
   preimage bundle is written and hash-verified before the first
   destination mutation, and any mid-batch failure restores every
   previously-mutated path in this run.

### C. Filtering dispositions

**Two-tier vocabulary (corrected, `XR1-R7B` — see repair notes above):
exactly four mutually exclusive `scan`-time classifications, plus one
separate post-review `apply`-lifecycle state never counted in `scan`'s
totals.**

**The four `scan`-time classifications**, applied by
`scripts/linked_sources/dispositions.py` and declared data-side in
`filtering_policy.json`:

| Classification | Meaning | Who/what may assign it |
|---|---|---|
| `HARD_EXCLUDE` | Secrets, `.env`, credentials, `.git/` internals, build caches, `__pycache__`, `.pyc`, and other known generated residue | `scan`'s rule engine, policy-file-driven, always |
| `PROTECTED_SOURCE_ONLY` | Shift's own governance, continuity, session-state, roadmap, and provider-evidence paths (e.g. `SESSION/**`, `CVF_SESSION_MEMORY.md`, `docs/decisions/**`, `docs/implementation/**`, provider-evidence receipts) — accounted for, visible in the report, **never** eligible for `apply` under any manifest | `scan`'s rule engine |
| `QUARANTINE_REVIEW` | Binary files, symlinks, oversized files, license-ambiguous files, migration/database files, public API surface changes, authentication/security-relevant changes, and any destructive deletion/rename | `scan`'s rule engine; always requires a human reviewer decision before any future manifest may reference it |
| `ELIGIBLE_CANDIDATE` | Ordinary source/docs/tests not matching any of the above — still requires a human disposition before any `apply` | `scan`'s rule engine (the conservative default bucket) |

**The one post-review lifecycle state**, entirely separate from `scan`'s
classification vocabulary:

| Lifecycle state | Meaning | Who/what may assign it |
|---|---|---|
| `APPROVED_APPLY` | A path already named, verbatim, in a manifest that has passed section G's full verification. Not a `scan` output; not counted in any `scan` report's classification totals; assignable only by `apply`, only at apply time. | Never `scan`; never self-assigned; never present in a `scan` report at all |

No classification may silently drop a changed path — every **logical
change record** from step 5's accounting (section B; a rename pair is one
record, per `XR1-R2`) lands in exactly one of the **four** `scan`-time
classifications, and a `scan` report's own accounting proves
`sum(HARD_EXCLUDE, PROTECTED_SOURCE_ONLY, QUARANTINE_REVIEW,
ELIGIBLE_CANDIDATE counts) = |unchanged| + |modified| + |added| +
|deleted| + |renamed|` exactly. `APPROVED_APPLY` is excluded from this sum
by definition — it is not a fifth bucket a `scan` report ever populates,
and no `scan` report may contain the string `APPROVED_APPLY` as a
classification value anywhere in its output.

**Deterministic precedence.** When a change record matches more than one
classification's trigger rules, exactly one applies, highest wins:
`HARD_EXCLUDE > PROTECTED_SOURCE_ONLY > QUARANTINE_REVIEW >
ELIGIBLE_CANDIDATE`. `APPROVED_APPLY` is outside this chain entirely — a
promotion `apply` alone may stamp onto a path already named, verbatim, in
a reviewed manifest (section G); `scan`'s classifier has no code path
capable of emitting it.

**Secret-content detection and execution-scope boundary (`XR1-R13`).**
`scan`'s `HARD_EXCLUDE` rules include content-pattern secret detection
(private-key headers, cloud-credential token shapes, high-entropy
assignments next to `key`/`token`/`secret`/`password`-like identifiers).
`XR1-O-C2` **builds and tests this detector against synthetic, non-secret
Git fixtures only** — it performs no real `scan`/`apply` against Shift
content and reads no real secret. A future **real** Shift `scan` is its own
bounded execution work order, naming the exact candidate commit, opened
only after `XR1-O-C2` closes. During such an authorized run, the detector
may stream Git blob bytes locally, machine-only, solely for
classification — it must never expose those bytes to a human, an agent, a
provider call, a log, a prompt, or any tracked file. The scan report
records **only** `path`, `disposition`, a fixed `reason` rule identifier
(e.g. `"secret_pattern:private_key_header"`), and the blob's `sha256` —
never the matched substring, plaintext content, or any other secret-shaped
byte sequence. Fail-closed default: content that cannot be conclusively
cleared of secrets is `HARD_EXCLUDE`, never `ELIGIBLE_CANDIDATE`, and a
`HARD_EXCLUDE` blob can never enter an `apply` manifest.

**Relationship to `ADR-OW-001`'s porting vocabulary (`PORT_AS_IS`/`ADAPT`/
`REIMPLEMENT`/`REFERENCE_ONLY`/`REJECT`):** these two vocabularies are
orthogonal, not competing. XR1's four `scan`-time classifications plus the
separate `APPROVED_APPLY` lifecycle state are a **pre-filter/triage layer**
run by the tool before any porting decision exists. Reaching
`ELIGIBLE_CANDIDATE` or being named in an `APPROVED_APPLY` manifest is
**not** itself a `PORT_AS_IS`/`ADAPT`/`REIMPLEMENT` decision — that decision
still requires its own dedicated F1+ work order and reviewer disposition,
exactly as `docs/architecture/PLATFORM_BOUNDARY_AND_PORTING_RULES.md`
already requires. The tool never automatically decides `ADAPT`,
`REIMPLEMENT`, or `REJECT` as if a filtering-stage classification were
reviewer approval.

### D. Cross-machine behavior

- GitHub is the only synchronization transport the tool relies on — no
  direct filesystem sync, no shared network drive assumption.
- Operations never implicitly tracks "latest Shift"; every `scan`/`apply`
  names an exact candidate commit.
- `.cvf/local-workspace-link.json` is regenerable and ignored; deleting it
  never loses governed state (`.cvf/workspace-link.json`'s `sourcePin` is
  the only durable pin).
- Git blob hashing (not checkout-normalized file reads) means Windows
  CRLF/path-separator normalization cannot change a recorded hash — the
  same base/candidate pair scanned on Windows or Linux must produce
  byte-identical non-timestamp datasets.
- All non-deterministic fields (`generatedAt`, hostname, absolute local
  paths) live in one isolated section of the scan report, never mixed into
  the hashed/deterministic inventory dataset.

### E. Two-repository commit discipline

Coordinated program, **independent repository histories** — no
cross-repository atomic commit is claimed or possible:

| Commit | Repository | Content |
|---|---|---|
| `XR1-O-C1` | Operations | Exactly the six authorization-round paths: `ADR-OW-006`, `OW-XR1-SPEC-001`, `OW-XR1-WO-001`, `IMPLEMENTATION_STATUS.json`, `CVF_SESSION/ACTIVE_SESSION_STATE.json`, `CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-07-23.md` — no seventh path (`XR1-R1` repair) |
| `XR1-S-C1` | Shift | Shift-side authorization, opened only after `XR1-O-C1` exists on Operations `origin/main` |
| `XR1-S-C2` | Shift | Shift's core-pin prerequisite fix (`6ce1cf0` -> `27137db4`) and Shift's own reciprocal `.cvf/workspace-link.json` BUILD |
| `XR1-S-C3` | Shift | Shift's independent review and closure of `XR1-S-C1`/`C2` |
| `XR1-O-C2` | Operations | Descriptor + tool + tests BUILD — **blocked until `XR1-S-C3` is closed**; pinned to that exact Shift commit |
| `XR1-O-C3` | Operations | Operations independent review and closure |

Any post-push continuity synchronization (mirroring `F1A`'s C4 precedent)
is its own separate commit in the relevant repository — never folded into
the commit whose push it is merely recording. Every commit, in either
repository, gets its own post-commit/pre-push sibling-worktree rehearsal
before being treated as final.

### F. Claim boundary

XR1 proves: portable cross-machine discovery of the Shift peer; exact, deterministic, Git-object-level source-change accounting; four-way exhaustive `scan`-time filtering plus a separate, apply-time-only `APPROVED_APPLY` lifecycle state; and governed, manifest-gated selective application mechanics. XR1 does **not** prove: Shift MVP compatibility; F1A/F1B runtime behavior; AI/agent governance; production readiness; or that any given porting decision (`PORT_AS_IS`/`ADAPT`/`REIMPLEMENT`) is correct — that remains a dedicated F1+ reviewer decision, per `ADR-OW-001`.

### G. Apply-manifest and independent-receipt verification (new, `XR1-R3`; non-circular two-artifact model, `XR1-R11`)

**Non-circular model (`XR1-R11`).** A file cannot contain the hash of the
Git commit that contains that same file, so the manifest never names its
own containing commit; approval is proven by a second, separate artifact.

**1. Manifest** (`scripts/linked_sources/apply_manifest.schema.json`, new,
added to `XR1-O-C2`'s BUILD ceiling) — immutable content only:
`schemaVersion`, `workspaceId` (must equal `.cvf/workspace-link.json`'s),
`baseCommit`, `candidateCommit`, `scanDatasetSha256` (hash of the exact
scan dataset, section B, this manifest was authored against),
`filteringPolicyVersion`/`filteringPolicySha256`, per-entry `operation`
plus operation-specific fields (below), `authorizationReceiptPath` (the
planned receipt path only, not a claim of existence), and `manifestSha256`,
computed over UTF-8 JSON after removing that field and serializing with
sorted keys, compact separators, and unescaped Unicode. No `authorizationCommit` field and no self-declared
status/approval field of any kind.

**2. Independent review receipt** (new, separate tracked file, authored
only by Codex `REVIEWER`, never by `IMPLEMENTATION_WORKER`/
`REPAIR_WORKER`) — `receiptSchemaVersion`, `decision` (exactly
`"REVIEW_PASS"`), `manifestPath`, `manifestSha256` (must equal the
manifest's own computed hash), reviewed `baseCommit`/`candidateCommit`,
`scanDatasetSha256`/`filteringPolicySha256` (must match the manifest's own
fields), reviewer role, and a review-evidence reference.

**3. `apply` invocation.** The authorization commit and receipt path are
external CLI arguments — e.g. `--authorization-commit <commit>
--authorization-receipt <path>` — never read from inside the manifest.

**Operation-specific entry shapes, `oneOf` keyed on `operation` (corrected,
`XR1-R8`; rename preconditions named exactly, `XR1-R12`)** — a single flat
shape cannot honestly represent a deletion (no candidate blob) or a rename
(two paths/hashes/preconditions): **`new`/`modified`** needs
`candidateSourcePath`/`candidateSourceBlobSha256`/`candidateSourceGitMode`
(never `120000`/`160000`, section H), `destinationPath`, and
`destinationPrecondition` (`new` = `{"state": "ABSENT"}`; `modified` =
`{"state": "PRESENT", "sha256": "<hash>"}`); **`deleted`** needs
`baseSourcePath`/`baseSourceBlobSha256` (from `baseCommit`; no candidate
blob is required, a deletion has none), `destinationPath`,
`destinationPrecondition` = `{"state": "PRESENT", "sha256": "<hash>"}`;
**`renamed`** needs `oldSourcePath`/`newSourcePath`,
`baseSourceBlobSha256`/`candidateSourceBlobSha256`, `contentChanged`
(boolean, `XR1-R2`'s rename accounting), `oldDestinationPath`/
`newDestinationPath`, and — exact field names, `XR1-R12` —
`oldDestinationPrecondition` (must be `{"state": "PRESENT", "sha256":
"<hash>"}`) and `newDestinationPrecondition` (must be `{"state":
"ABSENT"}`). A rename whose `newDestinationPath` collides with another
entry's destination only under case-insensitive or Unicode-normalization
comparison is rejected under section H's existing collision rule, never
treated as a distinct destination.

`apply` rejects before writing anything if any `destinationPrecondition`
(including the two rename-specific fields) disagrees with the
destination's *current* state/hash — wrong presence, wrong hash, each is
drift, not a warning — and re-checks every precondition **immediately
before** that entry's own mutation, closing the window between initial
verification and the write.

**Verification `apply` performs before any write** (all must hold, or
stop): (1) `<commit>` (the CLI `--authorization-commit`) is reachable from
Operations `origin/main` (`git merge-base --is-ancestor`), never
arbitrary/unpushed; (2) the manifest blob (at the given path) and the
receipt blob (at `--authorization-receipt <path>`) both exist
byte-for-byte at `<commit>`, not merely in working-tree state; (3) the
receipt's `decision` is exactly `REVIEW_PASS` naming this exact
`manifestSha256`, never a generic "reviewed" statement or a self-declared
status field inside the manifest; (4) the receipt's
`scanDatasetSha256`/`filteringPolicySha256` match the manifest's own
fields; (5) canonical digests recomputed from both the working manifest and
the parsed committed manifest blob equal the manifest field and the
receipt's `manifestSha256` — a
locally edited, drifted manifest is rejected even if the committed blob
once matched; (6) every operation-specific source field matches a fresh
`scan` of `baseCommit`/`candidateCommit` (section B's re-verification
step), and every `destinationPrecondition` matches the destination's
actual state, both at this check and again immediately before mutation.

A `scan` report, a merely repository-tracked but unreviewed draft, an
uncommitted manifest file, an arbitrary/unpushed local authorization
commit, or a manifest carrying its own self-declared `"status":
"approved"`-shaped field is **never** sufficient — approval exists only as
a separate independent receipt, committed, naming this exact manifest
hash.

### H. Destination path safety (new, `XR1-R4`)

Every `destinationPath` in an approved manifest is validated fail-closed by
`scan`'s and `apply`'s shared path-safety check before it is ever accepted
as `ELIGIBLE_CANDIDATE`/named in a manifest, and re-validated by `apply`
immediately before any write — no partial normalization "fix-up," reject
and stop. Rejected outright: absolute/drive-letter/UNC paths; empty or
`.`/`..` traversal components in any separator style, including mixed
`/`/`\`; NUL bytes, NTFS ADS markers (`:`), or Windows reserved device
names (`CON`, `PRN`, `AUX`, `NUL`, `COM1`–`COM9`, `LPT1`–`LPT9`); duplicate
destinations, including collisions only under case-insensitive or
Unicode-normalization (NFC/NFD) comparison; any path under `.git/` or a
protected governance/continuity/catalog path (`docs/roadmaps/**`,
`docs/catalog/**`, `docs/INDEX.md`, `.cvf/**`, `CVF_SESSION/**`,
`AGENTS.md`); any destination with a symlink/junction/reparse-point
**ancestor directory** (checked component-by-component); any destination
whose fully-resolved real path escapes this repository's root; and any
source blob with Git mode `120000` (symlink) or `160000` (submodule) —
**XR1 never applies a symlink or a submodule**, both remain permanently
`QUARANTINE_REVIEW`-only, pending separate, dedicated authorization if ever
revisited. Exhaustive negative-fixture coverage: `OW-XR1-SPEC-001`
`XR1-AC-40`.

### I. Apply atomicity and rollback (new, `XR1-R5`; locations corrected `XR1-R9`)

`apply` never claims impossible cross-filesystem atomicity. What it claims
and must test is **all-or-restore** behavior, with exact recovery locations
(new, `XR1-R9`, added to `XR1-O-C2`'s BUILD/runtime ceiling):

(1) Before the **first** destination mutation, `apply` writes a complete
rollback/preimage bundle — every destination's pre-apply state (absence or
exact prior bytes) — to gitignored, local-only, never-staged
`.cvf/local-linked-source-recovery/<run-id>/**` (added to `.gitignore`
alongside `.cvf/local-workspace-link.json`), and verifies the bundle's own
hashes before any real destination is touched. (2) Each destination write
uses a temporary file plus an atomic rename/replace (never
truncate-and-rewrite in place) — each file's write is itself atomic even
though the whole batch is not. (3) On any mid-batch failure, `apply`
restores **every** previously-mutated path from the local preimage bundle
and writes the tracked, committed
`provenance/shift-operations/<candidateCommit>/apply/<manifestSha256>/failure_recovery_receipt.json`
(and, on success, `apply_receipt.json`) — **hashes/statuses only** (path,
disposition, before/after `sha256`, outcome), never raw preimage bytes,
matched secret values, credentials, or absolute local paths. (4) A
dedicated test injects a failure after the first successful write and
proves **zero residual content delta** from pre-apply state. (5)
**Retention:** a local recovery bundle is kept until the operator removes
it or a later successful `apply` cleans up prior runs once their receipt
confirms `applied`; a bundle whose outcome is `restored`/failed is never
auto-deleted. Deleting a local bundle never affects tracked continuity —
the committed receipts are the durable record.

## Consequences

Positive: a durable, portable, machine-readable link between the two repositories that survives fresh clones; deterministic accounting removes the "trust me" gap in future selective porting; the disposition taxonomy gives Shift's governance/continuity content a permanent `PROTECTED_SOURCE_ONLY` shield against ever being silently ported.

Costs: two more tracked/ignored files and a new tool subtree to maintain; Shift's own authorization/BUILD sequence (`XR1-S-C1`–`C3`) is now a hard dependency blocking Operations' `XR1-O-C2`, adding cross-repository sequencing overhead; the core-pin drift remains open until Shift acts.

## Rejected alternatives

1. **Implicitly track Shift's live `HEAD`.** Rejected: violates section D; reintroduces `ADR-OW-004`'s "moving target" delta-accounting failure.
2. **A Git submodule.** Rejected: excluded by scope; couples checkout state/commit graphs against `ADR-OW-001`'s independent-ownership model.
3. **Fix Shift's core-pin drift inside this tool's BUILD.** Rejected: Shift's own prerequisite (`XR1-S-C2`), never silently absorbed here.
4. **Let `apply` infer approval from a `scan` report.** Rejected: collapses discovery and authorization, defeating the manifest-gated apply mode.
5. **Auto-apply renames/deletions alongside an approved `new`/`modified` counterpart.** Rejected: higher-risk operations must be named individually.
6. **Embed the authorization commit hash inside the manifest.** Rejected (`XR1-R11`): circular — a file cannot contain the hash of the commit that contains it; a separate independent receipt proves approval instead.

## Gate

This ADR authorizes planning and work-order construction only. BUILD
(`XR1-O-C2`) begins only after `OW-XR1-SPEC-001` and `OW-XR1-WO-001` are
independently reviewed and authorized, this package's own commit
(`XR1-O-C1`) is rehearsed and pushed, **and** Shift's `XR1-S-C3` closure is
independently confirmed at its exact commit hash.
