# Specification — RM1 Canonical Platform Roadmap Synthesis

- Spec ID: `OW-RM1-SPEC-001`
- Date: 2026-07-23 (repaired 2026-07-23, repair round 1 — `RM1-R1`; repaired
  again 2026-07-23, repair round 2 — `RM1-R3`; see `OW-RM1-WO-001`)
- Decision: `ADR-OW-004`
- Status: REVIEW_PASS — independently accepted for bounded RM1 BUILD
- Risk: R1 documentation/planning

## Purpose

Define the testable acceptance criteria a future BUILD tranche must satisfy
when it rewrites `docs/roadmaps/CVF_OPERATIONS_WORKSPACE_ROADMAP.md` and
authors the learning assessment and BUILD-evidence documents authorized by
`OW-RM1-WO-001`. This document specifies intended content and structure; it
does not itself edit the roadmap.

## Inputs this spec binds to

- Verified baselines (this round): target HEAD/origin `34519a3b17b416b11f64bae1da602c8fb9a7eb1a`;
  CVF core HEAD/origin `27137db4d9aa2aea931ddd2507185d5c24943080`; shift source
  HEAD `f98f29e145fa002be070e9d44520d20f0f82dcb3`; 116/116 tests; doctor 25/25.
- `operations-workspace-all-phases/MIGRATION_MANIFEST.json` SHA-256
  `7e900e85460061064d56818071c31486def91ce5c84784ec92a2d194a6b86b90`; 194
  physical files; 191 manifest entries; 12 total `.pyc` files (10
  manifest-listed, 2 unmanifested) — all 12 excluded from source, evidence,
  and candidacy regardless of manifest membership.
- Corrected delta accounting: 26 old-baseline paths (excluding
  `__pycache__` symmetrically from both inputs), 21 unchanged, 5 changed, 156
  new, 161 total disposition candidates. This figure is a Codex reviewer
  amendment (`RM1-R3`), not a self-classification by the authorization
  author. It supersedes two prior superseded figures, both preserved as
  failure history: the round's opening 25/21/4/169 estimate, and an
  intermediate 26/21/5/168 figure (itself a `RM1-R1` reviewer amendment) later
  found to result from an asymmetric `__pycache__`-inclusion comparison
  defect, not from any change in the underlying inputs. See `ADR-OW-004`'s
  "Delta accounting — full failure history (RM1-R1, RM1-R3)" section.
- `ADR-OW-001`, `ADR-OW-002`, `ADR-OW-003`, `ADR-OW-004`.
- `docs/architecture/PLATFORM_BOUNDARY_AND_PORTING_RULES.md`.
- F0/G2 build and independent-review evidence
  (`docs/reviews/F0_BUILD_EVIDENCE_2026-07-23.md`,
  `docs/reviews/F0_INDEPENDENT_REVIEW_2026-07-23.md`,
  `docs/reviews/G2_BUILD_EVIDENCE_2026-07-23.md`,
  `docs/reviews/G2_INDEPENDENT_REVIEW_2026-07-23.md`).

## Acceptance criteria

**RM1-AC-01** — The roadmap's current-truth section states the target/core
baseline pins, doctor result, and clean-worktree status exactly as
independently verified in `ADR-OW-004`'s "Verified input truth", not as a
carried-forward self-report.

**RM1-AC-02** — The roadmap (or the learning assessment it references) records
the full-bundle manifest SHA-256
(`7e900e85460061064d56818071c31486def91ce5c84784ec92a2d194a6b86b90`) and its
read-only location (`../operations-workspace-all-phases`, sibling to this
project, never copied in) accurately.

**RM1-AC-03** — Delta accounting is stated as the corrected, independently
verified figures — 26 old-baseline paths, 21 unchanged, 5 changed, 156 new,
161 total non-cache disposition candidates — not the round's superseded
25/21/4/169 or 26/21/5/168 figures (both preserved only as labelled failure
history). The 21 unchanged non-cache files' *content* is not re-reviewed;
only the 5 changed and 156 new non-cache candidates receive a disposition in
the learning assessment. Every `__pycache__`/`.pyc` path, manifest-listed or
not, is excluded from candidate classification entirely — it is never
"new," "changed," or "unchanged" content to disposition.

**RM1-AC-04** — The roadmap or learning assessment states, without
euphemism: 194 physical files on disk, 191 manifest entries (`MIGRATION_MANIFEST.json`
is not a member of its own `files` array), and 12 total `.pyc` files (10
manifest-listed, 2 unmanifested:
`run_all_structural_validators.cpython-313.pyc`,
`validate_bundle_integrity.cpython-313.pyc`) as a disclosed integrity
picture. The text states explicitly that manifest membership does not make a
generated binary source — all 12 `.pyc` files are excluded from source and
evidence regardless of whether the manifest lists them.

**RM1-AC-05** — Every reference to the full bundle's Phase 0–9 structural
validators states plainly that a validator PASS proves file/contract presence
and forbidden-dependency-scan cleanliness only, never runtime completeness —
matching the bundle's own disclosed limitation
(`FINAL_PHASES_SUMMARY.md`'s phase map, "Runtime claim allowed after document
gate" column). No structural-validator result is cited as runtime or
governance evidence anywhere in the roadmap.

**RM1-AC-06** — The roadmap excludes every one of the following as invalid
future direction: renaming or overlaying `shift-operations-workspace` (or any
repository) in place; whole-folder copy of the full bundle or the Shift
source; pre-authorizing generic/unscoped future work orders; a `DIAGNOSE`
phase name (non-canonical against the CVF seven-step model); treating
`__pycache__`/`.pyc` content as source; treating a mock, fixture, or
structural-validator result as runtime proof.

**RM1-AC-07** — The roadmap's current-state section states plainly: G0
bootstrap, G1 Index/Catalog governance, F0 source-intake baseline, and G2
Golden Catalog reconciliation are all complete, independently REVIEW_PASS'd,
and FREEZE'd; Module Registry remains empty (`modules: []`); no runtime has
been imported into the target repository.

**RM1-AC-08** — The roadmap preserves, without weakening, `ADR-OW-001`'s
dependency direction (`Applications -> Profiles -> Workspace Core -> Shared
Contracts`; `Profiles -> Capability Interfaces <- Provider Adapters`;
`Protected Command -> CVF Gates -> Profile Handler -> Ledger -> Audit`) and
its forbidden-edge list, and `docs/architecture/PLATFORM_BOUNDARY_AND_PORTING_RULES.md`'s
five-value disposition vocabulary and F0 classification-rule table.

**RM1-AC-09** — Every future phase (F1 through F7) is broken into named,
concrete tranches with their own scope — not left as a single undifferentiated
phase paragraph as in the current `OW-RM-001`.

**RM1-AC-10** — F1 (Platform Foundation) contains at minimum these five
tranches:

- **F1A** — versioned closed contracts (profile manifest schema, capability
  interface schema, `OperationalSession` contract schema);
- **F1B** — `OperationalSession` runtime plus Shift binding (state machine
  `DRAFT -> OPEN -> ACTIVE -> CLOSING -> CLOSED -> FROZEN`, ownership,
  evidence scope);
- **F1C** — profile registry (registration, discovery, `profile_id`/
  `profile_version` resolution, no cross-profile business coupling);
- **F1D** — governed command composition plus one thin Shift vertical
  (Request -> Authenticated Principal -> Versioned Action Contract -> CVF
  gates -> Approval Gate -> Profile Command Handler -> Ledger Mutation ->
  Audit Evidence);
- **F1E** — architecture/compatibility enforcement (dependency-direction
  architecture tests, forbidden-edge negative tests, CI wiring).

**RM1-AC-11** — The roadmap names the first thin vertical explicitly as the
Shift lifecycle **create/open -> close -> freeze**, running with AI and
external channels disabled, and states this is the F1D gate condition.

**RM1-AC-12** — F2 (Shift Compatibility MVP) is split into named work-order
scopes covering at minimum: auth/users/approval-principal reconciliation;
events/evidence/corrections; tasks/customer requests; incidents/handover with
forward migration; reporting; frontend/PWA; and integration
edge/offline/degraded behavior.

**RM1-AC-13** — F3 (Hardening and Cutover) covers at minimum: real PostgreSQL
parity; migration lifecycle; reconnect/concurrency; audit rollback;
backup/reset/restore with hash/count comparison; security hardening; and
requires the owner to explicitly select one of `KEEP_DUAL`,
`TARGET_BECOMES_CANONICAL`, or `DEFER_CUTOVER` — no implicit default.

**RM1-AC-14** — F4 (Capability Normalization) covers at minimum: capability
registry, invocation, and termination; `NO_AI`/`RULES_ONLY` operating modes;
Refinery; AI provider adapters; channels; notifications; reporting; and
search/storage.

**RM1-AC-15** — F4's provider-failure handling requirement explicitly names:
timeout, retry, idempotency, partial output, cancellation, hard termination,
fallback, circuit breaker, audit, and cost — and states that no provider
failure may be used to confirm business truth or corrupt the ledger (carried
from `ADR-OW-001`'s F4 gate).

**RM1-AC-16** — F5 (Agent Operations Non-Streaming MVP) covers at minimum:
timeline, evidence, approval relay, ownership lease/version/heartbeat,
disconnect-safe behavior, and handoff/freeze — and explicitly forbids
keyboard-injection-simulated approval as a substitute for an authenticated
approval path.

**RM1-AC-17** — F6 (Live View and Human Takeover) covers at minimum: a
dedicated security ADR requirement, pairing, short-lived tokens, window
allowlist and revalidation, view-only capability preceding any input
capability, ownership/input lease, no dual input, revoke/fail-closed
behavior, audited context delta, and a replaceable streaming adapter —
consistent with `ADR-OW-004`'s Decision 10/11.

**RM1-AC-18** — F7 (Dual-Profile Hardening) requires evidence that Shift and
Agent Operations profiles are isolated from each other with no cross-profile
business coupling, matching `ADR-OW-001`'s forbidden-edge list.

**RM1-AC-19** — The roadmap states API/database ownership rules explicitly:
preserve released routes and identifiers (`shifts` route family, `shift_id`,
`shift_status`, `shifts` table); released migrations are immutable; only
forward migrations are permitted; no cosmetic table rename — carried from
`docs/architecture/PLATFORM_BOUNDARY_AND_PORTING_RULES.md` Section 4.

**RM1-AC-20** — The roadmap states compatibility-shim exit criteria: a named
canonical owner, identical delegation behavior, a removal milestone,
duplicate/schema-drift regression tests, and a rule against any permanent
circular dependency between a shim and its replacement.

**RM1-AC-21** — Every tranche entry in the rewritten roadmap states its
dependencies, inputs, deliverables, evidence/gate condition, stop conditions,
claim boundary, and next authorized move — not prose-only phase descriptions.

**RM1-AC-22** — The roadmap includes a near-term execution queue that
identifies F1A as the next candidate tranche, and states explicitly that
naming F1A as next does not itself authorize F1A BUILD — a separate INTAKE
through WORK_ORDER sequence is required.

**RM1-AC-23** — The rewritten `docs/roadmaps/CVF_OPERATIONS_WORKSPACE_ROADMAP.md`
is under 600 lines, and no second/competing roadmap file is created anywhere
in the repository.

**RM1-AC-24** — `docs/reviews/OPERATIONS_WORKSPACE_ALL_PHASES_LEARNING_ASSESSMENT_2026-07-23.md`
is under 600 lines and classifies every one of the 5 changed and 156 new
non-cache full-bundle candidates (161 total; individually or by named group)
into exactly one of: `adopt`, `adapt`, `reference-only`, `reject` — with
`adopt`/`adapt` explicitly meaning "informs a future work order," never "is
imported by this tranche." No `__pycache__`/`.pyc` path is a candidate.

**RM1-AC-25** — This tranche (authorization and any subsequent BUILD under
`OW-RM1-WO-001`) does not modify `docs/catalog/MODULE_REGISTRY.json`,
`docs/INDEX.md`, or `docs/catalog/MODULE_CATALOG.md`. `git diff` for all three
remains empty throughout.

**RM1-AC-26** — After the roadmap rewrite: the Golden downstream catalog check
(`scripts/manage_cvf_downstream_catalog.ps1 -Check`) passes, all 116 existing
tests still pass, the project-scoped workspace doctor still reports PASS
(25/25), and `git diff --check` reports no whitespace errors.

## Out of scope for this spec

- Any F1+ implementation, contract code, or runtime behavior.
- Any import, copy, or adaptation of Shift-source or full-bundle content.
- Any change to `.cvf/manifest.json`, `AGENTS.md`, `docs/INDEX.md`,
  `docs/catalog/**`, `scripts/**`, `tests/**`, `provenance/**`, `apps/**`,
  `packages/**`, `database/**`, or `.github/**`.
- Any provider/AI call or live governance-behavior claim.

## Claim boundary

This specification defines acceptance criteria for a future BUILD. It is not
itself the roadmap rewrite, the learning assessment, or the BUILD evidence,
and grants no F1+ implementation authority. Independent authorization
re-review passed all 26 criteria at the planning/specification boundary;
bounded RM1 documentation BUILD may begin only after C1 is committed,
rehearsed post-commit/pre-push, and pushed.
