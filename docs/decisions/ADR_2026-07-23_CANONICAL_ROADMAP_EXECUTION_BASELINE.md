# ADR — Canonical Roadmap Execution Baseline

- ADR ID: `ADR-OW-004`
- Date: 2026-07-23 (repaired 2026-07-23, repair round 1 — `RM1-R1`; repaired
  again 2026-07-23, repair round 2 — `RM1-R3`)
- Status: REVIEW_PASS — accepted as the RM1 BUILD baseline after independent
  authorization re-review
- Decision owner: repository owner
- Risk: R1 documentation/planning
- Supersedes in part: nothing. Extends `ADR-OW-001` (platform/profile boundary),
  `ADR-OW-002` (Index/Catalog governance) and `ADR-OW-003` (Golden Catalog
  reconciliation) without reopening any of them.

## Context

`docs/roadmaps/CVF_OPERATIONS_WORKSPACE_ROADMAP.md` (`OW-RM-001`) is stale. It
still records the retired G0 core pin, lists G1's now-deleted
`scripts/manage_catalog.py` as current tooling, shows F0 as `NEXT` although F0
BUILD/REVIEW_PASS/FREEZE are complete, is silent on G2, and its claim boundary
says "Only G0 is complete" — all four contradict the independently verified
state confirmed live during this round: target HEAD = origin/main =
`34519a3b17b416b11f64bae1da602c8fb9a7eb1a`, CVF core HEAD = origin/main =
`27137db4d9aa2aea931ddd2507185d5c24943080`, workspace doctor PASS 25/25, 116/116
tests, Module Registry empty.

A second, unrelated input arrived: `operations-workspace-all-phases`, a
194-physical-file / 191-manifest-entry review bundle (`MIGRATION_MANIFEST.json`
SHA-256 `7e900e85460061064d56818071c31486def91ce5c84784ec92a2d194a6b86b90`,
independently verified this round — see Section "Verified input truth" below)
proposing a nine-phase rename-and-extract migration of
`shift-operations-workspace` itself into a repository called
`operations-workspace`. This is a different strategy from `ADR-OW-001`, which
the owner already accepted: build the platform greenfield in
`CVF-Operations-Workspace` and port only source-verified assets, rather than
renaming or restructuring the Shift repository in place.

This ADR does not reopen `ADR-OW-001`. It decides how the roadmap reconciles
the two inputs (verified G0–G2 truth in this repository, and the reviewed
full-bundle) into one canonical execution baseline, and what a future
`RM1_BUILD_EVIDENCE`/roadmap-rewrite tranche may and may not claim.

## Verified input truth

Independently reproduced live during this authorization round, not carried
forward from a prior self-report:

- Target `CVF-Operations-Workspace`: HEAD = `origin/main` =
  `34519a3b17b416b11f64bae1da602c8fb9a7eb1a`, worktree clean.
- CVF core: HEAD = `origin/main` = `27137db4d9aa2aea931ddd2507185d5c24943080`,
  worktree clean.
- `shift-operations-workspace` source: HEAD =
  `f98f29e145fa002be070e9d44520d20f0f82dcb3`, worktree clean except the
  pre-existing untracked
  `docs/decisions/ASSESSMENT_2026-07-23_OPERATIONS_WORKSPACE_REPOSITIONING.md`
  (unchanged, predates F0, disclosed since F0 BUILD).
- `python -m unittest discover -s tests -p "test_*.py"` → 116/116 OK.
- Project-scoped workspace doctor → PASS (25/25).
- `operations-workspace-all-phases/MIGRATION_MANIFEST.json` SHA-256 =
  `7e900e85460061064d56818071c31486def91ce5c84784ec92a2d194a6b86b90` — matches
  the value recorded for this round exactly.
- 194 physical files on disk; 191 entries in the manifest's `files` array; all
  191 independently re-hashed against disk with **zero mismatches and zero
  missing files**. `MIGRATION_MANIFEST.json` itself is not a member of its
  own `files` array (independently confirmed) — it is a top-level artifact
  compared separately by its own SHA-256, not one of the 191 listed entries.
  194 physical and 191 manifest entries are both correct and not in tension:
  194 = 191 listed entries + `MIGRATION_MANIFEST.json` itself (1) + 2
  unmanifested `.pyc` files (see next bullet).
- 12 `.pyc` files exist on disk in total. 10 of them are listed in the
  manifest's `files` array; 2 are not:
  `scripts/migration/__pycache__/run_all_structural_validators.cpython-313.pyc`
  and `scripts/migration/__pycache__/validate_bundle_integrity.cpython-313.pyc`.
  Being listed in the manifest does not make a `.pyc` file source: all 12 are
  generated Python bytecode binaries, and **all 12** — manifest-listed or not
  — are excluded from source, from evidence, from learning-assessment
  candidacy, and from every disposition in this ADR. The manifest's inclusion
  of 10 of them is a fact about the manifest's own contents, not a
  reclassification of those files as reviewable design input.

### Delta accounting — full failure history (RM1-R1, RM1-R3)

This figure has been wrong twice before reaching its current, independently
reproduced form. Every prior value is preserved below as **failure history**,
not silently dropped, per this repository's practice of recording failures
rather than erasing them:

| Stage | Old-baseline paths | Unchanged | Changed | New | Status |
|---|---|---|---|---|---|
| Round's opening estimate | 25 | 21 | 4 | 169 | **superseded** — omitted `scripts/migration/README.md` from the changed set |
| First correction (this package, pre-`RM1-R1`) | 26 | 21 | 5 | 168 | **superseded** — compared `operations-workspace-review-baseline/` with `__pycache__` excluded against `operations-workspace-all-phases/` with `__pycache__` **included**, an asymmetric comparison |
| `RM1-R1` Codex reviewer amendment | 26 | 21 | 5 | 168 | **superseded** — accepted the corrected changed-set (5, including `scripts/migration/README.md`) but did not detect the asymmetric cache-inclusion defect underlying "168 new"; withdrawn by `RM1-R3` |
| `RM1-R3` Codex independent re-review finding `ASYMMETRIC_CACHE_FILTER_INVALID_DELTA` | 26 | 21 | 5 | 156 | **current, Codex-accepted, independently reproduced** — symmetric comparison, `__pycache__` excluded from both inputs |

The changed set (5 files) has been stable and correct since the first
correction: `MIGRATION_MANIFEST.json`, `README.md`, `REVIEW_CHECKLIST.md`,
`scripts/migration/README.md`, `TREEVIEW.md`. Only the "new" count moved, and
only because of how `__pycache__` was handled on each side of the comparison.

**What `RM1-R3` found.** The 168-new figure came from comparing
`operations-workspace-review-baseline/` (26 non-`__pycache__` paths) against
`operations-workspace-all-phases/` counted **with its `__pycache__` paths
still included** (194 physical files, including all 12 `.pyc` files). That
asymmetry counted every one of the bundle's 12 `.pyc` files as "new," even
though 2 of the old baseline's own excluded paths were themselves
`__pycache__` files that happen to also exist in the new bundle. Applying the
same inclusion/exclusion rule to both sides — `__pycache__` excluded from
both, exactly as the old-baseline side already was — gives:

- old-baseline non-`__pycache__` paths: 26;
- full-bundle non-`__pycache__` paths: 182;
- unchanged: 21 (confirmed, unchanged by this repair);
- changed: 5 (confirmed, unchanged by this repair);
- missing old paths in the new bundle: 0;
- **new: 156**;
- **disposition candidates: 161** (5 changed + 156 new).

Independently reproduced by comparing the two path lists directly (`comm`
against sorted, symmetric non-`__pycache__` file listings from both
directories) with zero missing paths and the same 5-file changed set as
every prior stage.

**This is not input drift.** Neither `operations-workspace-review-baseline/`
nor `operations-workspace-all-phases/` changed at any point between the
original count, `RM1-R1`, and `RM1-R3` — every SHA-256 and every path list
reproduces identically at every stage. What changed is the **comparison
method**: the first correction applied `__pycache__` exclusion to only one
side of the comparison. This is a reviewer/counting-method defect discovered
during independent re-review, not a change in the underlying inputs, and it
is recorded and named as such rather than folded into the input-drift
category it superficially resembles.

**Resolution authority.** Codex, acting independently as `REVIEWER`,
reproduced the symmetric comparison from first principles, confirmed the
asymmetry, and — in that independent capacity — withdraws the `RM1-R1`
reviewer amendment's "168 new" figure and issues a new reviewer amendment:
**26 old-baseline paths / 21 unchanged / 5 changed / 156 new / 161 total
disposition candidates is accepted as the authoritative RM1 input baseline**,
superseding both the original 25/21/4/169 estimate and the intermediate
26/21/5/168 figure. `RM1-R1`'s separate finding — that the authorization
author was not entitled to self-classify a triggered stop condition as
non-blocking — remains closed and is not reopened by this repair; what is
withdrawn here is only the numeric "168" that finding had accepted, not the
principle that resolution belongs to an independent reviewer.
`RM1_CANONICAL_PLATFORM_ROADMAP_SPEC.md` (`RM1-AC-03`, `RM1-AC-24`) binds the
future roadmap and learning-assessment BUILD to these Codex-accepted 26/21/5/156
figures and forbids re-review of the 21 unchanged non-cache files' content.

**Standing comparison rule.** Any future delta comparison between these two
inputs, or between either input and a successor version of itself, must apply
identical inclusion/exclusion rules to both sides — in particular,
`__pycache__`/`.pyc` paths must be excluded from both sides symmetrically, or
included on both sides symmetrically, never mixed. Two distinct failure modes
are tracked separately going forward:

- **`BLOCKED_INPUT_DRIFT`** — the underlying input content itself changes
  (a path count, a hash, or a manifest value no longer reproduces against a
  previously recorded value for the same comparison method).
  `operations-workspace-all-phases/MIGRATION_MANIFEST.json`'s SHA-256
  (`7e900e85460061064d56818071c31486def91ce5c84784ec92a2d194a6b86b90`), the
  194/191 physical/manifest counts, and the 12/10/2 `.pyc` breakdown are the
  values a future mismatch would be checked against.
- **`BLOCKED_EVIDENCE_METHOD`** — the comparison methodology itself becomes
  asymmetric, non-reproducible, or otherwise unable to be independently
  re-derived from the same inputs, even though the inputs themselves have not
  changed. This is the category `RM1-R3` belongs to.

No worker, in any role, may waive either condition or reclassify a triggered
instance of either as bounded, resolved, or non-blocking on their own
authority. The worker who finds either condition stops and reports it by
name; only an independent reviewer may resolve it.

## Decision

1. **One canonical roadmap.** `docs/roadmaps/CVF_OPERATIONS_WORKSPACE_ROADMAP.md`
   is the only roadmap for this repository. No competing or parallel roadmap
   file may be created.
2. **`CVF-Operations-Workspace` is the platform.** It owns Workspace Core,
   shared contracts, the profile registry, replaceable capabilities, and
   integrated applications, per `ADR-OW-001`.
3. **Shift Operations is the first profile and MVP proof**, not a rename
   target and not the platform itself.
4. **`shift-operations-workspace` remains canonical for its existing
   implementation** until an explicit, evidence-gated cutover decision (F3,
   `KEEP_DUAL` / `TARGET_BECOMES_CANONICAL` / `DEFER_CUTOVER`) says otherwise.
   No implicit archival, deletion, or authority transfer occurs before then.
5. **`operations-workspace-all-phases` is a design input, never a runtime or
   continuity authority.** Its phase numbering (0–9), its proposed rename to
   `operations-workspace`, and its "Runtime implementation status: Not applied
   by this bundle" self-disclosure are read as one reviewed set of design
   ideas to selectively learn from — not as a competing execution plan, not as
   evidence of anything having been built, and not as a second roadmap.
6. **No rename, overlay, or whole-folder copy.** The bundle's own proposed
   repository rename (`shift-operations-workspace` → `operations-workspace`)
   is rejected for the same reason `ADR-OW-001` rejected renaming in place:
   it would import stale continuity, unfinished modules and Shift-specific
   coupling as platform truth. Every one of the 161 non-cache disposition
   candidates (156 new relative to the old baseline plus 5 changed) is a
   **reference-only design input** until a dedicated learning-assessment
   tranche (BUILD-phase, out of this round's ceiling) dispositions it as
   `adopt` / `adapt` / `reference-only` / `reject`. No `.pyc`/`__pycache__`
   path is a disposition candidate at all — see "Delta accounting" above.
7. **Every port goes through per-asset disposition and a dedicated work
   order.** `ADR-OW-001`'s five-value vocabulary (`PORT_AS_IS`, `ADAPT`,
   `REIMPLEMENT`, `REFERENCE_ONLY`, `REJECT`) and
   `docs/architecture/PLATFORM_BOUNDARY_AND_PORTING_RULES.md` govern every
   future asset from both the Shift source and the full bundle. No batch
   folder move is authorized by this ADR or by any future roadmap edit alone.
8. **Structural validation is not runtime evidence.** The full bundle's own
   phase map states each phase's structural validators prove only that
   "required files/contracts are present and selected forbidden-dependency
   scans found no violation" — never that "the phase runtime is complete."
   The roadmap must carry this distinction forward explicitly: a PASS from a
   structural/architecture validator, a mock, or a fixture is never cited as
   proof of runtime, provider, or governance behavior. Only real execution
   evidence (test runs against real code, live provider calls where a
   governance claim is made, real database round-trips) satisfies a runtime
   claim, per `AGENTS.md`'s Mandatory Governance Proof rule.
9. **Agent Operations begins only after a credible Shift MVP baseline** (F2
   compatibility MVP evidence, not merely F1's thin vertical).
10. **Live View precedes Human Takeover.** Observation-only capability must be
    proven before any input-control capability is authorized.
11. **Human Takeover requires its own security ADR, threat model, and owner
    approval** — distinct from this ADR and from the platform ADR. Neither
    this ADR nor the roadmap it authorizes may imply Human Takeover
    authorization.
12. **Roadmap phases are not the CVF seven-step control chain.** `F0`–`F7` in
    the roadmap name planning/execution *tranches*; they are unrelated to, and
    must not be conflated with, the CVF phase model
    (`INTAKE -> DESIGN -> SPEC -> WORK_ORDER -> BUILD -> REVIEW -> FREEZE`)
    that every individual work order still independently traverses. The
    roadmap must state this distinction explicitly.

## Consequences

Positive:

- the roadmap stops asserting a retired core pin, a deleted tool, and a false
  "only G0 complete" boundary;
- the full bundle's genuinely useful design ideas (phase-gated evidence
  discipline, `OperationalSession` framing, `NO_AI`/`RULES_ONLY` operating
  modes, dependency-direction diagrams) become available as reviewed,
  attributed input without importing its rename strategy, its unverified
  runtime claims, or its folder layout wholesale;
- F1–F7 gain concrete tranche breakdowns (per `RM1-AC-10` through `RM1-AC-18`)
  so F1A can open without re-deriving architecture, dependency, evidence, or
  stop-condition decisions.

Costs:

- the roadmap grows substantially (bounded to under 600 lines by
  `RM1-AC-23`) to hold the added tranche detail;
- a dedicated learning-assessment tranche is still required before any bundle
  idea can be cited as adopted;
- maintaining two read-only external inputs (Shift source, full bundle)
  alongside the platform repository adds review overhead to every future F1+
  work order that touches porting.

## Rejected alternatives

1. **Treat the full bundle as the new execution plan**, superseding
   `OW-RM-001`. Rejected: it proposes a rename `ADR-OW-001` already rejected,
   and its own README states its runtime status is "Not applied by this
   bundle" — it is unverified design input, not continuity authority.
2. **Leave the roadmap as-is and only patch the stale claims.** Rejected: the
   roadmap would still lack concrete F1–F7 tranche breakdowns, forcing the
   next tranche to re-derive architecture and dependency decisions from
   scratch — the exact gap `RM1-AC-09`/`RM1-AC-10` close.
3. **Create a second, "full-bundle-derived" roadmap alongside `OW-RM-001`.**
   Rejected by `RM1-AC-23`: exactly one canonical roadmap is authorized.
4. **Silently normalize either delta-accounting discrepancy without
   disclosure.** Rejected: this would hide a real, verifiable finding —
   inconsistent with this repository's practice of recording failures rather
   than erasing them (see F0's classifier-iteration disclosure and G2's
   repair rounds). This alternative is not the same question as whether the
   round's stop conditions applied: they did apply, both times (see "Delta
   accounting — full failure history" above), and the worker who found each
   mismatch was not the one authorized to decide whether stopping was
   warranted. That decision belongs to Codex as independent `REVIEWER`, who
   has since reviewed the reproduced evidence and issued the reviewer
   amendments recorded above — first accepting 168, then, on discovering the
   asymmetric-comparison defect in `RM1-R3`, withdrawing 168 and accepting
   156.

## Gate

This ADR authorizes documentation-planning work only: the specification and
work order it accompanies, and — once independently reviewed and
`REVIEW_PASS`'d by Codex — a bounded BUILD limited to rewriting the roadmap and
authoring the learning assessment and build-evidence documents. It does not
authorize F1+ implementation, any import of Shift or full-bundle source, any
change to the Module Registry, or any runtime, provider, or governance
behavior claim.

Independent authorization re-review reproduced the symmetric
`26/21/5/156/161` delta, the `194/191` physical/manifest counts, the
12/10/2 `.pyc` breakdown, catalog PASS, 116/116 tests, and workspace doctor
PASS 25/25. `RM1-R1`, `RM1-R2`, and `RM1-R3` are closed without waiver.
