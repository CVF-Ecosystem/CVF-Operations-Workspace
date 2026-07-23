# Work Order — RM1 Canonical Platform Roadmap Synthesis

- Work order ID: `OW-RM1-WO-001`
- Date: 2026-07-23 (repaired 2026-07-23, repair round 1; repaired again
  2026-07-23, repair round 2)
- Status: REVIEW_PASS — bounded RM1 BUILD authorized only after C1 is
  committed, rehearsed post-commit/pre-push, and pushed
- Risk: R1 documentation/planning
- Governing decision: `ADR-OW-004`
- Governing spec: `OW-RM1-SPEC-001`

## Repair round 1 — findings and disposition (2026-07-23)

Independent Codex review of the originally-authored package returned two
findings. Full narrative for the first is in `ADR-OW-004`'s "Delta accounting
— full failure history" section; disposition of each is recorded here for the
work order's own scope:

- **RM1-R1 — UNAUTHORIZED_STOP_CONDITION_REINTERPRETATION (repaired).** The
  original package's delta-accounting discrepancy (25/4/169 preliminary vs.
  26/21/5/168 independently re-derived) triggered this round's own
  `BLOCKED_INPUT_DRIFT` stop condition. The authorization author was not
  authorized to classify that mismatch as "bounded" or "non-blocking" and
  continue past it; only an independent reviewer holds that authority. Codex
  independently reproduced every count and hash and, as `REVIEWER`, issued an
  explicit reviewer amendment accepting 26 old-baseline paths / 21 unchanged /
  5 changed / 168 new as the authoritative RM1 input baseline. No BUILD
  occurred while the mismatch was unresolved — work was confined to
  authorization documentation only, and nothing was staged, committed, or
  pushed. `ADR-OW-004`, `OW-RM1-SPEC-001`, and this work order were corrected
  throughout to remove any claim that a worker may reclassify a triggered
  stop condition; a standing rule was recorded that any future mismatch
  against the corrected baseline is blocking with no worker discretion. **This
  finding remains closed.** Its numeric "168 new" figure was separately
  withdrawn in repair round 2 (`RM1-R3` below) for an unrelated reason — a
  comparison-method defect, not a reopening of `RM1-R1`'s own finding that
  worker self-classification of a triggered stop condition is unauthorized.
- **RM1-R2 — C3_REVIEW_RECEIPT_OUTSIDE_CEILING (repaired).** The original
  work order's commit plan claimed the independent review receipt
  (`docs/reviews/RM1_INDEPENDENT_REVIEW_2026-07-23.md`) was "covered by the
  BUILD ceiling's `docs/reviews/**` allowance" — no such wildcard exists in
  the BUILD ceiling, which lists two specific `docs/reviews/` files, not a
  folder-wide allowance. **Repair:** a separate "C3 closure ceiling" section
  is added below, owned exclusively by Codex; the BUILD (IMPLEMENTATION_WORKER)
  ceiling is restated as limited to the canonical roadmap, the learning
  assessment, RM1 BUILD evidence, BUILD-time continuity/status, and bounded
  authorization repair notes — IMPLEMENTATION_WORKER may not author or modify
  the independent review receipt under any circumstance. **This finding
  remains closed** and is unaffected by repair round 2.

## Repair round 2 — findings and disposition (2026-07-23)

Independent Codex re-review of the repaired package returned one finding.
Full narrative is in `ADR-OW-004`'s "Delta accounting — full failure history"
section; disposition is recorded here for the work order's own scope:

- **RM1-R3 — ASYMMETRIC_CACHE_FILTER_INVALID_DELTA (repaired).** The
  `RM1-R1`-accepted "168 new" figure was produced by an asymmetric
  comparison: `operations-workspace-review-baseline/` was counted with
  `__pycache__` paths excluded, while `operations-workspace-all-phases/` was
  still counted with its `__pycache__` paths (all 12 `.pyc` files) included.
  Applying `__pycache__` exclusion symmetrically to both sides gives 182
  full-bundle non-cache paths, not 194, and 156 new relative to the 26-path
  old baseline, not 168. **This is not input drift** — neither input's
  content changed between `RM1-R1` and `RM1-R3`; only the comparison method
  was defective. Codex, as `REVIEWER`, independently reproduced the symmetric
  comparison, confirmed 26 old-baseline paths / 21 unchanged / 5 changed / 156
  new / 161 total disposition candidates, withdrew the `RM1-R1` amendment's
  "168 new" figure specifically (not the rest of `RM1-R1`'s finding), and
  issued a new reviewer amendment accepting 156/161 as authoritative.
  **Repair:** `ADR-OW-004`'s delta-accounting section is rewritten as a full
  three-stage failure-history table (opening estimate, first correction,
  `RM1-R1` amendment, `RM1-R3` amendment); `OW-RM1-SPEC-001`'s `RM1-AC-03`,
  `RM1-AC-04`, and `RM1-AC-24` and this work order's stop conditions and
  tasks section are updated to the 156/161 figures; a distinct
  `BLOCKED_EVIDENCE_METHOD` stop condition is added alongside
  `BLOCKED_INPUT_DRIFT` to separately name "the comparison method became
  asymmetric or non-reproducible" from "the underlying input changed"; and
  the integrity discussion is corrected to state the full `.pyc` picture (12
  total, 10 manifest-listed, 2 unmanifested) and that
  `MIGRATION_MANIFEST.json` does not list itself in its own `files` array.

## Role route

```text
ORCHESTRATOR
-> SPEC_AUTHOR
-> WORK_ORDER_AUTHOR
-> REVIEWER                          (Codex, independent — never Claude)
-> COMMIT_STEWARD (C1 authorization) (Codex)
-> IMPLEMENTATION_WORKER             (BUILD, only after REVIEW_PASS on this package)
-> REVIEWER                          (Codex, independent post-BUILD review)
-> REPAIR_WORKER if needed           (bounded repair of accepted findings)
-> RE_REVIEW                         (Codex, independent)
-> COMMIT_STEWARD (C2/C3)            (Codex)
-> CLOSER                            (Codex)
-> SESSION_SYNC_STEWARD              (continuity closure)
-> ORCHESTRATOR                      (parked, next tranche)
```

`ORCHESTRATOR -> SPEC_AUTHOR -> WORK_ORDER_AUTHOR` on this authorization
package is held by Claude (this round, single agent, role transitions recorded
in the active handoff). Every `REVIEWER`, `COMMIT_STEWARD`, `RE_REVIEW`,
`CLOSER`, and `SESSION_SYNC_STEWARD` step is Codex, independent of Claude.
Claude does not self-grant REVIEW_PASS and does not stage, commit, or push at
any point in this tranche.

## Authorization-round changed set (this round only — authoring, not BUILD)

Exactly these six paths may be created or modified while authoring this
package, before Codex review — no seventh path:

```text
docs/decisions/ADR_2026-07-23_CANONICAL_ROADMAP_EXECUTION_BASELINE.md
docs/specs/RM1_CANONICAL_PLATFORM_ROADMAP_SPEC.md
docs/work_orders/RM1_CANONICAL_PLATFORM_ROADMAP_WORK_ORDER.md
IMPLEMENTATION_STATUS.json
CVF_SESSION/ACTIVE_SESSION_STATE.json
CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-07-23.md
```

Unlike `OW-G2-WO-001`'s precedent, this round does **not** register these
three new documents in `docs/catalog/ARTIFACT_REGISTRY.json` and does **not**
regenerate `docs/INDEX.md` — the Golden Artifact Registry already registers
`docs/decisions/`, `docs/specs/`, and `docs/work_orders/` as discoverable
folder families, and the round's own ceiling explicitly excludes
`ARTIFACT_REGISTRY.json`, `docs/INDEX.md`, `MODULE_REGISTRY.json`, and
`MODULE_CATALOG.md` from this round. `git diff` for all four must remain
empty throughout.

## BUILD changed-set ceiling — IMPLEMENTATION_WORKER only (authorized only after Codex REVIEW_PASS on this package)

This is a ceiling, not a commitment to touch every path, and it is
**IMPLEMENTATION_WORKER's ceiling only** — it does not grant IMPLEMENTATION_WORKER
any authority over the C3 closure ceiling defined in the next section. BUILD
may create or modify up to:

```text
docs/roadmaps/CVF_OPERATIONS_WORKSPACE_ROADMAP.md
docs/reviews/OPERATIONS_WORKSPACE_ALL_PHASES_LEARNING_ASSESSMENT_2026-07-23.md
docs/reviews/RM1_BUILD_EVIDENCE_2026-07-23.md
IMPLEMENTATION_STATUS.json
CVF_SESSION/ACTIVE_SESSION_STATE.json
CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-07-23.md
docs/decisions/ADR_2026-07-23_CANONICAL_ROADMAP_EXECUTION_BASELINE.md      (repair-note updates only, if a review finding requires it)
docs/specs/RM1_CANONICAL_PLATFORM_ROADMAP_SPEC.md                          (repair-note updates only, if a review finding requires it)
docs/work_orders/RM1_CANONICAL_PLATFORM_ROADMAP_WORK_ORDER.md              (repair-note updates only, if a review finding requires it)
```

In summary, this ceiling is limited to exactly five kinds of content: the
canonical roadmap; the learning assessment; RM1 BUILD evidence; BUILD-time
continuity/status updates; and bounded authorization repair notes on the
three RM1 authorization documents themselves. There is no `docs/reviews/**`
wildcard and no other implicit allowance — every path IMPLEMENTATION_WORKER
may touch is listed explicitly above. In particular, **IMPLEMENTATION_WORKER
must not author or modify `docs/reviews/RM1_INDEPENDENT_REVIEW_2026-07-23.md`**
— that file belongs exclusively to the C3 closure ceiling below.

No deletion is authorized anywhere in this ceiling. No path outside this
ceiling may be created, modified, or deleted. In particular: BUILD does not
touch `docs/catalog/ARTIFACT_REGISTRY.json`, `docs/catalog/MODULE_REGISTRY.json`,
`docs/INDEX.md`, or `docs/catalog/MODULE_CATALOG.md` — the roadmap and its two
companion review documents are discoverable through the existing
`docs/roadmaps/` and `docs/reviews/` folder families already registered in
the Golden Artifact Registry, exactly as `docs/catalog/README.md` is
discoverable through `requiredDocs` per `ADR-OW-003`'s precedent (`G2-BR1`).

## C3 closure ceiling — Codex-owned only

Distinct from the IMPLEMENTATION_WORKER ceiling above, and not derived from
any `docs/reviews/**` wildcard (none exists in this work order). This ceiling
belongs exclusively to Codex acting as `REVIEWER` / `COMMIT_STEWARD` / `CLOSER`
/ `SESSION_SYNC_STEWARD` at C3:

```text
docs/reviews/RM1_INDEPENDENT_REVIEW_2026-07-23.md
IMPLEMENTATION_STATUS.json
CVF_SESSION/ACTIVE_SESSION_STATE.json
CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-07-23.md
```

`IMPLEMENTATION_STATUS.json` and the two `CVF_SESSION/` continuity files
appear in both ceilings because they are updated twice — once by
IMPLEMENTATION_WORKER at BUILD self-report, and again by Codex at FREEZE
closure — matching the precedent already recorded for F0 and G2 in this
project's continuity history. `docs/reviews/RM1_INDEPENDENT_REVIEW_2026-07-23.md`
itself appears **only** in this C3 ceiling: IMPLEMENTATION_WORKER has no
authority to create, draft, or edit it under any circumstance, including as
a "repair note." Authoring the independent review receipt is what makes a
review independent; a self-authored receipt would not be one.

## Explicit exclusions (stop and escalate if touched)

```text
.cvf/**
AGENTS.md
docs/INDEX.md
docs/catalog/**
scripts/**
tests/**
provenance/**
apps/**
packages/**
database/**
.github/**
```

Also excluded, as read-only planning inputs only: the CVF core repository,
the `shift-operations-workspace` source repository, and the
`operations-workspace-all-phases` / `operations-workspace-review-baseline`
folders. No content in any of the four is created, modified, or copied by
this work order or by the BUILD it authorizes.

## Roles and ownership

- **ORCHESTRATOR / SPEC_AUTHOR / WORK_ORDER_AUTHOR** (Claude, this round):
  authors `ADR-OW-004`, `OW-RM1-SPEC-001`, `OW-RM1-WO-001`, and the 3
  authorization-round continuity files. Does not touch the BUILD ceiling.
  Does not commit.
- **REVIEWER** (Codex, independent from Claude): reviews this package against
  `OW-RM1-SPEC-001`'s 26 acceptance criteria, `ADR-OW-004`'s decisions, and
  the stop conditions below, before any BUILD work begins. Independently
  re-verifies the corrected delta accounting (21 unchanged / 5 changed / 156
  new / 161 total disposition candidates, applying `__pycache__` exclusion
  symmetrically to both inputs) and the manifest SHA-256/count/`.pyc`-integrity
  claims rather than trusting this package's restatement of them.
- **IMPLEMENTATION_WORKER** (assigned at BUILD authorization, after
  REVIEW_PASS on this package — role not yet opened by this work order):
  implements only the IMPLEMENTATION_WORKER BUILD ceiling — roadmap rewrite,
  learning assessment, BUILD evidence, and BUILD-time continuity/status
  updates (self-report only). Does not author the independent review receipt
  and does not perform FREEZE closure — both belong to Codex under the C3
  closure ceiling.
- **COMMIT_STEWARD** (Codex, exclusively): stages, commits, pushes; rehearses
  each commit in a temporary sibling worktree before it is considered final.
- **CLOSER** (Codex): confirms FREEZE disposition and continuity closure.

## Tasks (this authorization round)

1. Verify baselines live (target/core/source pins, doctor, tests) — done,
   recorded in `ADR-OW-004`.
2. Verify the full-bundle manifest SHA-256, physical/manifest file counts,
   and `.pyc` integrity gap — done, recorded in `ADR-OW-004`.
3. Re-derive the delta accounting against the old review baseline directly
   (not by trusting the round's opening figures) — done; found a mismatch
   against the round's opening 25/4/169 figures, which triggered
   `BLOCKED_INPUT_DRIFT`. Repaired in repair round 1 (`RM1-R1`): Codex
   independently reproduced the counts and, as `REVIEWER`, accepted 26 paths
   / 21 unchanged / 5 changed / 168 new as the authoritative baseline. Then
   repaired again in repair round 2 (`RM1-R3`): Codex found that "168 new"
   came from an asymmetric `__pycache__`-inclusion comparison defect (not
   from any input change), withdrew that figure, and accepted the symmetric
   26 / 21 unchanged / 5 changed / 156 new / 161 total disposition candidates
   as authoritative — see `ADR-OW-004`.
4. Author `ADR-OW-004` with the 12 canonical decisions and the corrected
   input-truth section.
5. Author `OW-RM1-SPEC-001` with RM1-AC-01 through RM1-AC-26.
6. Author this work order with ceiling, roles, commit plan, stop conditions.
7. Update `IMPLEMENTATION_STATUS.json` (`activeWorkOrders` includes
   `OW-RM1-WO-001`, status AUTHORED-NOT-AUTHORIZED).
8. Update `CVF_SESSION/ACTIVE_SESSION_STATE.json`
   (`activeRole: WORK_ORDER_AUTHOR`, `nextAllowedMove`: await Codex
   independent review of the RM1 package).
9. Update the active handoff: correct its stale "Current State" header (still
   describing the closed F0/pre-G2 tranche) and add an acknowledgment entry
   for this round.
10. Stop. Hand off to Codex as REVIEWER. Do not proceed to BUILD. Do not
    stage, commit, or push.

## Commit plan (owned exclusively by Codex COMMIT_STEWARD)

- **C1** — authorization package (`ADR-OW-004`, `OW-RM1-SPEC-001`,
  `OW-RM1-WO-001`) + authorization continuity
  (`IMPLEMENTATION_STATUS.json`, `CVF_SESSION/ACTIVE_SESSION_STATE.json`,
  `CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-07-23.md`).
- **C2** — BUILD deliverables under the IMPLEMENTATION_WORKER ceiling:
  roadmap rewrite, learning assessment, BUILD evidence document, plus
  BUILD-time continuity updates.
- **C3** — closure under the separate C3 closure ceiling above: the
  independent review receipt (`docs/reviews/RM1_INDEPENDENT_REVIEW_2026-07-23.md`,
  authored by Codex — never by IMPLEMENTATION_WORKER, and never under an
  undefined `docs/reviews/**` wildcard) + continuity/FREEZE closure.

Each commit is created by Codex COMMIT_STEWARD, then rehearsed post-commit and
pre-push in a temporary sibling worktree. A commit is not pushed or treated as
accepted until its rehearsal passes. No `git add .` / `git add -A`. No amend,
rebase, or force-push.

## Stop conditions

Stop immediately and report the named blocked state if any of the following
occurs:

- target, CVF core, or Shift source pin drifts from the values verified in
  `ADR-OW-004` at any checkpoint;
- the full-bundle manifest SHA-256, physical/manifest counts (194/191), or
  `.pyc` breakdown (12 total / 10 manifest-listed / 2 unmanifested) no longer
  reproduce as recorded — report `BLOCKED_INPUT_DRIFT`;
- the old-baseline/full-bundle delta no longer reproduces as the Codex-accepted
  26 paths / 21 unchanged / 5 changed / 156 new / 161 total disposition
  candidates, using `__pycache__` exclusion applied symmetrically to both
  inputs (see `ADR-OW-004`'s "Delta accounting — full failure history") —
  report `BLOCKED_INPUT_DRIFT` if the underlying input content itself no
  longer matches (a hash, path, or count changes); report
  `BLOCKED_EVIDENCE_METHOD` if the inputs still match but the comparison
  cannot be symmetrically and independently re-derived (for example, if
  `__pycache__`/`.pyc` handling becomes asymmetric again). Per the standing
  rule recorded there, no worker in any role may reclassify either condition
  as bounded or non-blocking on their own authority; only an independent
  reviewer may resolve it;
- a secret or generated binary (including any `.pyc`) is treated as source or
  evidence;
- a structural validator, mock, or fixture result is cited as runtime or
  governance proof;
- a runtime, module, or capability claim is made beyond what F0/G0/G1/G2
  evidence supports;
- BUILD needs to import or copy any Shift-source or full-bundle content;
- BUILD needs to change `docs/catalog/MODULE_REGISTRY.json`,
  `docs/catalog/ARTIFACT_REGISTRY.json`, `docs/INDEX.md`, or
  `docs/catalog/MODULE_CATALOG.md`;
- the rewritten roadmap exceeds 600 lines or a second/competing roadmap file
  is created;
- an unresolved architecture, catalog, or continuity conflict is found;
- a live provider call becomes necessary;
- the changed-set ceiling needs to expand beyond what is listed above.

On any stop condition: halt, do not commit, and report the specific named
condition — do not choose silently among alternatives.

## Validation (before this package is considered ready for review)

- `IMPLEMENTATION_STATUS.json` and `CVF_SESSION/ACTIVE_SESSION_STATE.json`
  parse as valid JSON.
- `git diff --check` reports no whitespace errors.
- `git status` shows exactly the 6 authorization-round paths changed — no
  more, no fewer.
- Each authored Markdown file is under 600 lines.
- `git diff` for `docs/catalog/ARTIFACT_REGISTRY.json`,
  `docs/catalog/MODULE_REGISTRY.json`, `docs/INDEX.md`, and
  `docs/catalog/MODULE_CATALOG.md` is empty.
- `git diff` for `shift-operations-workspace`,
  `operations-workspace-all-phases`, and `operations-workspace-review-baseline`
  is empty (all three are outside this repository and were only read).
- No secret was read; no provider/AI call was made.
- Golden downstream catalog check
  (`scripts/manage_cvf_downstream_catalog.ps1 -Check`) still passes; 116
  tests still pass; workspace doctor still reports PASS (25/25) — none of
  these were expected to change, and this round's changes do not affect them.

## Completion boundary

This work order authorizes authorship of the RM1 package and a bounded BUILD
ceiling for a *future*, separately reviewed BUILD phase limited to
documentation: the roadmap rewrite, the learning assessment, and the BUILD
evidence record. Codex independently recorded `REVIEW_PASS` after reproducing
the corrected evidence method and every repository gate. BUILD begins only
after Codex COMMIT_STEWARD creates C1, its post-commit/pre-push sibling
worktree rehearsal passes, and C1 is pushed. This work order does not import
or implement any runtime module, does not open F1A, and does not create any
new CVF control or capability claim.
