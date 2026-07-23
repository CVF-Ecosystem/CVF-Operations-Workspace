# CVF Operations Workspace Roadmap

- Roadmap ID: `OW-RM-001`
- Date: 2026-07-23 (rewritten under `OW-RM1-WO-001`, `RM1-AC-01`–`RM1-AC-26`)
- Status: ACTIVE_PLANNING_BASELINE
- Strategy: greenfield platform, evidence-gated selective porting (`ADR-OW-001`,
  `ADR-OW-004`)
- First use-case profile: Shift Operations
- Canonical: this is the **only** roadmap file in this repository. No
  competing or parallel roadmap exists or may be created (`RM1-AC-23`).

**Roadmap phases (`F0`–`F7`) are not the CVF seven-step control chain.** They
name planning/execution tranches. Every individual work order under any
tranche still independently traverses:

```text
INTAKE -> DESIGN -> SPEC -> WORK_ORDER -> BUILD -> REVIEW -> FREEZE
```

## Current execution truth (independently verified 2026-07-23)

- Target `CVF-Operations-Workspace` has two valid historical checkpoints,
  both on `main`/`origin/main`, in sequence:
  - **RM1 input-verification baseline** — `34519a3b17b416b11f64bae1da602c8fb9a7eb1a`
    — the commit against which this roadmap's input truth (target/core/Shift
    pins, doctor, tests, full-bundle manifest, delta accounting) was
    independently verified before the RM1 authorization package was
    authored.
  - **RM1 authorization/BUILD baseline (C1)** — `ed0d1cd7ea70a51ed8e350afed8cc3b38647ca45`
    — the subsequent commit, containing the reviewed and pushed RM1
    authorization package (`ADR-OW-004`, `OW-RM1-SPEC-001`, `OW-RM1-WO-001`),
    from which this documentation BUILD began. HEAD = `origin/main` = this
    commit at BUILD time, worktree clean.
  Both are real, sequential commits on this repository's history, not
  competing claims — the second supersedes the first as the live baseline
  once C1 was independently reviewed, committed, rehearsed, and pushed.
- CVF core: HEAD = `origin/main` = `27137db4d9aa2aea931ddd2507185d5c24943080`,
  worktree clean.
- Shift source (`shift-operations-workspace`, read-only): pin
  `f98f29e145fa002be070e9d44520d20f0f82dcb3`, worktree clean except the
  pre-existing untracked `docs/decisions/ASSESSMENT_2026-07-23_OPERATIONS_WORKSPACE_REPOSITIONING.md`.
- Golden Downstream Catalog Kit 1.1: structurally enforced, one executable
  catalog writer, closed registries, generated views.
- 116/116 tests pass. Project-scoped workspace doctor: PASS (25/25).
- `docs/catalog/MODULE_REGISTRY.json`: `modules: []` — **empty**. No runtime
  module has been implemented or imported into this repository.
- **G0** (clean governance bootstrap), **G1** (machine-governed Index/Catalog),
  **F0** (Shift source-intake and compatibility baseline, pin
  `f98f29e145fa002be070e9d44520d20f0f82dcb3`), and **G2** (Golden Catalog Kit
  1.1 / core-pin reconciliation) are all **complete, independently
  REVIEW_PASS'd, and FREEZE'd**. Full receipts: `docs/reviews/F0_BUILD_EVIDENCE_2026-07-23.md`,
  `docs/reviews/F0_INDEPENDENT_REVIEW_2026-07-23.md`,
  `docs/reviews/G2_BUILD_EVIDENCE_2026-07-23.md`,
  `docs/reviews/G2_INDEPENDENT_REVIEW_2026-07-23.md`.
- `operations-workspace-all-phases/` (a separate, read-only review bundle;
  194 physical files, 191 manifest entries, SHA-256
  `7e900e85460061064d56818071c31486def91ce5c84784ec92a2d194a6b86b90`) has been
  reviewed as design input only — see
  `docs/reviews/OPERATIONS_WORKSPACE_ALL_PHASES_LEARNING_ASSESSMENT_2026-07-23.md`.
  It is never a runtime or continuity authority (`ADR-OW-004`).

## Architecture invariants

Dependency direction (`ADR-OW-001`, unchanged):

```text
Applications -> Profiles -> Workspace Core -> Shared Contracts
Profiles -> Capability Interfaces <- Provider Adapters
Protected Command -> CVF Gates -> Profile Handler -> Ledger -> Audit
```

Forbidden: `Core -> Profile`, `Core -> Provider`, `Profile -> Provider`
implementation, `Provider/channel/live-view -> protected domain mutation`,
`Profile A -> Profile B` business logic.

Porting vocabulary (`ADR-OW-001`, `docs/architecture/PLATFORM_BOUNDARY_AND_PORTING_RULES.md`):
`PORT_AS_IS` / `ADAPT` / `REIMPLEMENT` (F1+ work order only) and
`REFERENCE_ONLY` / `REJECT` (F0/learning-assessment default). No batch folder
move is ever authorized. Structural validation (a file/contract-presence
check) is never runtime or governance evidence — real execution evidence
(test runs against real code, live provider calls where a governance claim is
made, real database round-trips) is required for any runtime claim
(`AGENTS.md` Mandatory Governance Proof rule).

## F1 — Platform Foundation

### F1A — Versioned closed contracts

- Dependencies: G0–G2 complete; `ADR-OW-001` boundary rules.
- Inputs: `contracts/*.schema.json` design input (`adapt`, learning
  assessment), `ADR-OW-001` disposition vocabulary.
- Deliverables: profile-manifest schema, capability-interface schema,
  `OperationalSession` contract schema, command/event/capability envelope
  schemas — versioned and closed (schema evolution requires a version bump,
  never a silent breaking change).
- Evidence/gate: schemas validate representative payloads; positive and
  negative schema tests pass; independent review confirms no forbidden edge.
- Stop conditions: schema ambiguity: a claim the schema cannot represent
  honestly; a breaking change without a version bump; cross-profile leakage
  in a shared schema.
- Claim boundary: contracts only — no runtime capability is implied or
  claimed.
- Next governed move: a dedicated F1A work order (fresh
  `INTAKE -> WORK_ORDER` sequence). Not authorized by this roadmap.

### F1B — `OperationalSession` runtime and Shift binding

- Dependencies: F1A contracts frozen.
- Inputs: `docs/architecture/OPERATIONAL_SESSION_MODEL.md` design input
  (`adapt`).
- Deliverables: `OperationalSession` state machine
  (`DRAFT -> OPEN -> ACTIVE -> CLOSING -> CLOSED -> FROZEN`), ownership and
  evidence-scope fields, Shift profile binding.
- Evidence/gate: state-transition tests including illegal-transition
  negatives; ownership enforcement test; ledger write on transition.
- Stop conditions: an illegal transition succeeds; ownership can be bypassed;
  a frozen session accepts an in-place edit.
- Claim boundary: runtime session lifecycle only — no capability, provider,
  or channel behavior implied.
- Next governed move: a dedicated F1B work order, after F1A REVIEW_PASS.

### F1C — Profile registry

- Dependencies: F1A contracts frozen.
- Inputs: `docs/architecture/PROFILE_MODEL.md` design input (`adapt`).
- Deliverables: profile registration/discovery, `profile_id`/
  `profile_version` resolution, no cross-profile business coupling.
- Evidence/gate: registry rejects a malformed/duplicate profile
  registration; resolution test for at least two registered profile
  identities.
- Stop conditions: a profile's business logic becomes reachable from Core or
  from another profile.
- Claim boundary: registration/discovery only — no profile runtime behavior
  claimed.
- Next governed move: a dedicated F1C work order, after F1A REVIEW_PASS.

### F1D — Governed command pipeline and thin Shift vertical

- Dependencies: F1A–F1C complete.
- Inputs: `docs/architecture/GOVERNED_COMMAND_PIPELINE.md` design input
  (`adapt`).
- Deliverables: `Request -> Authenticated Principal -> Versioned Action
  Contract -> CVF Gates -> Approval Gate -> Profile Command Handler -> Ledger
  Mutation -> Audit Evidence`; **one thin Shift lifecycle vertical**:
  create/open -> close -> freeze, with AI and external channels disabled.
- Evidence/gate: the thin vertical runs start-to-freeze with AI/channels off;
  a bypass-negative test shows a router/adapter cannot mutate a protected
  record directly.
- Stop conditions: any protected mutation reachable outside the pipeline;
  the vertical requires AI or an external channel to complete.
- Claim boundary: proves the pipeline shape only — not a Shift MVP (that is
  F2).
- Next governed move: a dedicated F1D work order, after F1B/F1C REVIEW_PASS.

### F1E — Architecture and compatibility enforcement

- Dependencies: F1A–F1D complete.
- Inputs: `docs/implementation/phase-2/ARCHITECTURE_TEST_PLAN.md` design
  input (`adapt`).
- Deliverables: automated dependency-direction architecture tests,
  forbidden-edge negative tests, CI wiring.
- Evidence/gate: architecture-test suite fails on an intentionally
  introduced forbidden edge (proven, not assumed).
- Stop conditions: a forbidden edge passes architecture tests.
- Claim boundary: enforcement tooling only.
- Next governed move: a dedicated F1E work order, after F1D REVIEW_PASS.
  **F1A is the next candidate tranche overall — see "Near-term execution
  queue" below. Naming it here does not authorize its BUILD.**

## F2 — Shift Compatibility MVP

F2 is a **compatibility MVP program**, not hardening (`F3`) and not cutover.
It is split into seven independently work-ordered sub-tranches, `F2A`–`F2G`
— no combined mega-scope work order is authorized.

### F2A — Authentication, users, approval principal

- Dependencies: F1 complete (F1A–F1E REVIEW_PASS'd and FROZEN).
- Inputs: F0 import ledger rows for auth/user assets (`REFERENCE_ONLY`);
  learning-assessment phase-3 `adapt` items (`API_COMPATIBILITY_MAP.md`,
  `DOMAIN_OWNERSHIP_MAP.md`).
- Deliverables: authenticated principal resolution reconciled with the
  approval-principal registry; user identity mapped into F1B's
  `OperationalSession`.
- Evidence/gate: an authenticated request resolves to exactly one principal
  in a positive test; an unauthenticated request is rejected in a negative
  test.
- Stop conditions: a principal can act without authentication; an approval
  can be attributed to the wrong principal.
- Claim boundary: authentication/identity reconciliation only — no
  authorization-policy claim beyond what is tested.
- Next governed move: a dedicated F2A work order, opened only after F1
  FREEZE.

### F2B — Events, evidence, corrections

- Dependencies: F2A complete.
- Inputs: F0 ledger rows for event/evidence assets; F1B `OperationalSession`
  evidence-scope contract.
- Deliverables: event capture, evidence attachment, append-only correction
  workflow (no in-place edit of a confirmed record).
- Evidence/gate: a correction test shows the original record is preserved
  and the correction is traceable to it.
- Stop conditions: a confirmed record can be edited in place.
- Claim boundary: event/evidence/correction mechanics only.
- Next governed move: a dedicated F2B work order, opened only after F2A
  FREEZE.

### F2C — Tasks and customer requests

- Dependencies: F2B complete.
- Inputs: F0 ledger rows for task/customer-request assets.
- Deliverables: task and customer-request lifecycle bound to
  `OperationalSession`.
- Evidence/gate: a task/customer-request lifecycle test runs create through
  resolution with evidence attached at each step.
- Stop conditions: a task can be resolved without evidence where evidence is
  required by the source behavior.
- Claim boundary: task/customer-request mechanics only.
- Next governed move: a dedicated F2C work order, opened only after F2B
  FREEZE.

### F2D — Incidents and handover

- Dependencies: F2C complete.
- Inputs: F0 ledger rows for incident/handover assets; forward-migration
  rule (Cross-cutting rules, below).
- Deliverables: incident and handover workflow, using **forward migrations
  only** — no destructive schema change.
- Evidence/gate: a handover test preserves incident history across the
  handover boundary.
- Stop conditions: a migration is non-forward (drops or destructively
  alters existing data).
- Claim boundary: incident/handover mechanics only.
- Next governed move: a dedicated F2D work order, opened only after F2C
  FREEZE.

### F2E — Reporting

- Dependencies: F2B complete (reporting reads confirmed/corrected events).
- Inputs: F0 ledger rows for reporting assets.
- Deliverables: end-shift-style report generation from confirmed Ledger
  data.
- Evidence/gate: a generated report's figures are traceable back to
  specific Ledger entries in a test.
- Stop conditions: a report figure cannot be traced to a Ledger entry.
- Claim boundary: reporting mechanics only — no claim about report content
  correctness beyond what is tested.
- Next governed move: a dedicated F2E work order, opened only after F2B
  FREEZE (may run in parallel with F2C/F2D).

### F2F — Frontend/PWA

- Dependencies: F2A–F2E each REVIEW_PASS'd for the surfaces the frontend
  exposes.
- Inputs: F0 ledger rows for frontend assets.
- Deliverables: minimal Mobile PWA / Desktop Web shell surfacing F2A–F2E.
- Evidence/gate: a frontend smoke test exercises the thin Shift vertical
  (F1D) through the UI, start to freeze.
- Stop conditions: the frontend can trigger a protected mutation outside the
  governed command pipeline.
- Claim boundary: UI shell only — no new business logic in the frontend
  layer.
- Next governed move: a dedicated F2F work order, opened only after the
  F2A–F2E surfaces it depends on are FROZEN.

### F2G — Integration edge, offline, and degraded behavior

- Dependencies: F2A–F2C complete.
- Inputs: F0 ledger rows for `integration-edge` assets.
- Deliverables: external-channel ingress boundary; explicit offline/degraded
  behavior when AI or an external channel is unavailable.
- Evidence/gate: a degraded-mode test shows the workspace continues to
  operate (per `ADR-OW-001` architecture principle 5) with AI/channels
  disabled.
- Stop conditions: the workspace cannot operate at all when AI/external
  channels are disabled.
- Claim boundary: edge/offline mechanics only.
- Next governed move: a dedicated F2G work order, opened only after F2A–F2C
  FREEZE.

**F2 evidence/gate (program-level):** a representative Shift lifecycle runs
start-to-freeze with AI and external channels disabled across F2A–F2G
together; every compatibility difference from the source repository is
explicit and evidenced, not assumed. **F2 stop conditions (program-level):**
a database asset is ported without schema-identity and rollback evidence; an
F0-classified `REFERENCE_ONLY` asset is imported without an F1+ work order's
explicit re-disposition.

## F3 — Shift Hardening and Cutover

- Dependencies: F2 complete.
- Inputs: learning-assessment `adapt` items for phase-5 domain documents.
- Deliverables: real PostgreSQL parity; migration lifecycle; reconnect/
  concurrency handling; audit rollback; backup/reset/restore with hash/count
  comparison; security hardening.
- Evidence/gate: a real backup/restore cycle reproduces identical row
  counts and hashes; concurrency test shows no lost update; security probes
  documented with results.
- Stop conditions: restore cannot be demonstrated; a security probe finds an
  unmitigated critical issue.
- Claim boundary: the owner must explicitly select exactly one of
  `KEEP_DUAL`, `TARGET_BECOMES_CANONICAL`, or `DEFER_CUTOVER` — no implicit
  authority transfer occurs, and no default is assumed.
- Next governed move: a dedicated F3 work order, opened only after F2 FREEZE.

## F4 — Capability Normalization

- Dependencies: F1 complete (capability interfaces are F1A contracts).
- Inputs: learning-assessment `adapt` items for phase-4 domain documents,
  including `FAILURE_AND_TERMINATION_MODEL.md`.
- Deliverables: capability registry, invocation, and termination; `NO_AI`
  and `RULES_ONLY` operating modes; Refinery boundary; AI provider adapters;
  channels; notifications; reporting; search/storage — each behind a
  capability interface.
- Evidence/gate: Shift remains fully functional with AI disabled
  (`NO_AI`/`RULES_ONLY` proven, not assumed); provider-failure handling
  proven for: timeout, retry, idempotency, partial output, cancellation,
  hard termination, fallback, circuit breaker, audit, and cost — no provider
  failure may confirm business truth or corrupt the ledger.
- Stop conditions: a provider failure is used as proof of a business fact;
  Shift functionality regresses when AI is disabled.
- Claim boundary: capability replaceability only — no specific provider's
  general availability is claimed by this tranche.
- Next governed move: a dedicated F4 work order, opened only after F1
  FREEZE (may run in parallel with F2/F3 once F1 is frozen).

## F5 — Agent Operations Non-Streaming MVP

- Dependencies: **credible Shift MVP evidence from F2, not merely F1's thin
  vertical** (`ADR-OW-004` Decision 9).
- Inputs: learning-assessment `adapt` items for phase-6/phase-7 domain
  documents.
- Deliverables: non-streaming timeline, evidence capture, approval relay,
  ownership lease with version and heartbeat, disconnect-safe behavior,
  handoff, and freeze.
- Evidence/gate: provider-neutral contracts; official integration
  mechanisms only; authenticated approvals; deterministic disconnect
  handling proven by test, not assumed.
- Stop conditions: approval is simulated via keyboard injection instead of
  an authenticated approval path; a session relies on cookie scraping or a
  reverse-engineered token.
- Claim boundary: non-streaming, local, supervised MVP only — no remote
  control or streaming capability is claimed.
- Next governed move: a dedicated F5 work order, opened only after F2
  FREEZE.

## F6 — Live View and Human Takeover Security Program

- Dependencies: F5 complete; **a separate security ADR and threat model,
  approved by the owner, precede any F6 BUILD** (`ADR-OW-004` Decision 11).
- Inputs: learning-assessment `adapt` items for phase-8 domain documents;
  `contracts/live-view/*.schema.json` (`adapt`).
- Deliverables: pairing and short-lived tokens; window allowlist and
  revalidation; **view-only capability before any input-control
  capability**; input/ownership lease; audited context delta; replaceable
  streaming adapter.
- Evidence/gate: no dual input is ever possible (proven by test); a lapsed
  or ambiguous authorization fails closed; revocation takes effect
  immediately, proven by test.
- Stop conditions: dual input becomes possible; an ambiguous authorization
  state defaults to allow instead of fail-closed.
- Claim boundary: view-only capability may be claimed only after F6's
  view-only gate passes; input-control capability requires its own
  additional gate and cannot be implied by the view-only gate.
- Next governed move: the separate security ADR and threat model, opened
  only after F5 FREEZE. This roadmap does not authorize that ADR.

## F7 — Dual-Profile Hardening and Platform Freeze

- Dependencies: F2–F6 complete for both profiles.
- Inputs: learning-assessment `adapt` items for phase-9 domain documents.
- Deliverables: cross-profile architecture tests, dual-profile hardening,
  Module Registry finalization, platform-freeze criteria, release plan.
- Evidence/gate: no cross-profile business coupling (proven by architecture
  test); disabling either profile does not regress the other's quality,
  proven by running each profile's test suite with the other disabled.
- Stop conditions: a shared abstraction only works when both profiles are
  present; CVF controls are duplicated per profile instead of shared.
- Claim boundary: platform freeze applies only once both profiles pass
  independently — it is not implied by either profile alone.
- Next governed move: a dedicated F7 work order, opened only after F3, F4,
  and F6 are each independently FROZEN.

## Cross-cutting rules

**API/database ownership.** Preserve released routes and identifiers
(`shifts` route family, `shift_id`, `shift_status` enum, `shifts` table);
released migrations are immutable; only forward migrations are permitted;
no cosmetic table rename (`docs/architecture/PLATFORM_BOUNDARY_AND_PORTING_RULES.md`
Section 4).

**Compatibility-shim exit criteria.** Any compatibility shim introduced
during F2/F3 must name: a canonical owner; identical delegation behavior to
the canonical implementation; an explicit removal milestone; duplicate/
schema-drift regression tests; and must never become a permanent circular
dependency with its replacement.

**Migration/security/evidence rules.** Every tranche's BUILD evidence
distinguishes self-report from independent review. A structural-validator
PASS is never cited as runtime or governance evidence anywhere in this
repository. Any claim that CVF governs AI/agent behavior requires a real
provider API call, recorded per `AGENTS.md`'s Mandatory Governance Proof
rule — mocks are permitted only for pure UI structure checks.

## Release slices

1. **Platform proof** (F1): thin Shift vertical, no AI, no external
   channels.
2. **Shift compatibility** (F2 + F4 partial): usable Shift profile with
   replaceable, disableable AI capability.
3. **Shift production-local** (F3): hardened, cutover-decided Shift MVP.
4. **Agent supervision** (F5): non-streaming Agent Operations MVP.
5. **Live View** (F6): view-only, then input-control, each independently
   gated.
6. **Platform freeze** (F7): both profiles hardened and isolated.

## Success metrics

- Zero forbidden dependency edges detected by architecture tests at every
  FREEZE.
- 100% of protected mutations reachable only through the governed command
  pipeline (proven by negative test, not code review alone).
- Shift functional test suite passes with `NO_AI` at every FREEZE from F4
  onward.
- Zero runtime/governance claims backed only by a mock or structural
  validator, at every FREEZE.

## Explicit non-goals

- Not a generic ERP or all-purpose workflow engine.
- Not a remote-desktop or TeamViewer replacement.
- Not a new IDE, web IDE, or agent framework.
- Not a provider-specific (Claude/Codex/Cursor) control panel.
- Not the CVF governance core repackaged as a business application.

**Explicitly rejected as future direction, for every tranche in this
roadmap** (consolidated from `ADR-OW-004` and the learning assessment; each
item applies repository-wide, not only to the full-bundle review):

1. **Repository rename or overlay** — no tranche renames or overlays
   `shift-operations-workspace`, this repository, or any other repository.
2. **Whole-folder copy** — no tranche performs a batch folder move or
   whole-repository copy; every asset import is per-file, evidence-gated,
   and dispositioned individually (`ADR-OW-001` vocabulary).
3. **Generic or pre-written work-order pre-authorization** — naming a future
   scope in this roadmap (including F1A–F1E, F2A–F2G, and any bundle-derived
   work-order reference in the learning assessment) never itself authorizes
   that work order's BUILD; each requires its own fresh
   `INTAKE -> WORK_ORDER` sequence.
4. **`DIAGNOSE` as a CVF phase** — this repository's phase model is exactly
   the seven-step chain at the top of this document; no tranche introduces
   or recognizes a `DIAGNOSE` phase.
5. **`__pycache__`/`.pyc` as source or evidence** — no tranche treats a
   compiled Python cache file as source code, design input, or verification
   evidence, regardless of whether it appears in any manifest.
6. **Mocks, fixtures, or structural validators as runtime/governance
   proof** — no tranche cites a mock result, a fixture-only test, or a
   structural/file-presence validator's PASS as evidence of runtime or
   governance behavior; only real execution evidence (test runs against real
   code, live provider calls where a governance claim is made, real database
   round-trips) satisfies a runtime claim.

## Global stop conditions

Stop the active work order and report the named condition on: secret
exposure; unpinned source; provenance drift; license ambiguity; unexpected
public API/database change; governance bypass; failed rollback; module
overclaim; a provider failure used as proof; ownership ambiguity; scope
beyond the authorized changed-set ceiling; `BLOCKED_INPUT_DRIFT` (an input's
content changes); or `BLOCKED_EVIDENCE_METHOD` (a comparison/verification
method becomes asymmetric or non-reproducible, even though inputs are
unchanged — see `ADR-OW-004`'s delta-accounting failure history for the
precedent this category was created from).

## Near-term execution queue

**F1A is the next candidate tranche.** Naming it here is planning only — it
does **not** authorize F1A BUILD. F1A requires its own
`INTAKE -> DESIGN -> SPEC -> WORK_ORDER` sequence before any implementation.

Next three executable work-order candidates, in dependency order:

1. **F1A** — versioned closed contracts (profile manifest, capability
   interface, `OperationalSession`, command/event envelopes).
2. **F1B** — `OperationalSession` runtime and Shift binding (depends on F1A
   FREEZE).
3. **F1C** — profile registry (depends on F1A FREEZE; may run in parallel
   with F1B).

## Claim boundary

**Complete:** G0 (bootstrap), G1 (Index/Catalog governance), F0 (Shift
source-intake baseline), G2 (Golden Catalog Kit 1.1 / core-pin
reconciliation) — all independently REVIEW_PASS'd and FREEZE'd. Module
Registry remains empty; no runtime module has been implemented or imported.

**Planned, not started:** F1 through F7 in full. No contract, no runtime
session, no profile registry, no capability normalization, no Agent
Operations, no Live View, and no Human Takeover capability is implemented or
claimed by this roadmap.

**Conditional:** F5 is gated on credible F2 evidence, not F1 alone. F6 is
gated on a separate security ADR/threat model and on F5 completion. F7 is
gated on F2–F6 completion for both profiles. Cutover (`F3`) requires an
explicit owner decision with no default.

This roadmap authorizes no BUILD by existing. Each tranche requires its own
`INTAKE -> WORK_ORDER` sequence before implementation begins.
