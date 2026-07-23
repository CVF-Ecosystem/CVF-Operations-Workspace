# CVF Operations Workspace Roadmap

- Roadmap ID: `OW-RM-001`
- Date: 2026-07-23
- Status: ACTIVE_PLANNING_BASELINE
- Strategy: greenfield platform, evidence-gated selective porting
- First use-case profile: Shift Operations

This roadmap describes what will be built. Each item still traverses the CVF
control chain independently:

```text
INTAKE -> DESIGN -> SPEC -> WORK_ORDER -> BUILD -> REVIEW -> FREEZE
```

## G0 — Clean governance bootstrap — COMPLETE

- New local project and public GitHub repository created.
- CVF core pinned at `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2`.
- Workspace doctor passed 24/24.
- Empty module registry and honest implementation status established.
- No Shift source or review-bundle content imported.

## G1 — Machine-governed Index and Catalog — COMPLETE

- Artifact Registry is the machine source for generated `docs/INDEX.md`.
- Module Registry is the machine source for generated Module Catalog claims.
- Both registries have committed JSON Schemas and controlled vocabularies.
- `scripts/manage_catalog.py --write/--check` generates and detects drift.
- Eleven tests cover valid state, duplicate IDs/paths, missing paths, unknown
  status/control/relationships/dependencies, required fields, path separators,
  path escape and generated hand edits.
- Module Registry remains empty; G1 creates no runtime capability claim.

## F0 — Source intake and compatibility baseline — NEXT

Goal: make reuse decisions from reproducible evidence rather than folder
copying.

Deliverables:

- detached source capture at a full Shift commit SHA;
- route, schema, migration, dependency, module and test baseline;
- secret/generated/local-state exclusion report;
- machine-readable import ledger with per-asset dispositions;
- platform boundary and architecture rules;
- negative tests for path normalization, dirty inputs and self-scanning.

Gate: baseline is reproducible, source worktree is untouched, no runtime source
has entered the new repository, and the first implementation import work order
can be bounded from the ledger.

## F1 — Platform contracts and one thin Shift vertical

Goal: prove the architecture with the smallest complete operational path.

Candidate scope, subject to F0 evidence:

- profile and capability manifests;
- operational session and ownership contracts;
- event/evidence/audit/freeze primitives;
- CVF integration boundary;
- one Shift lifecycle vertical through API, persistence and tests.

Gate: core imports no Shift or provider implementation; the vertical works
without AI; protected mutations have positive and bypass-negative evidence.

## F2 — Shift profile compatibility MVP

Goal: make Shift Operations a usable profile in the new platform without
breaking the original repository.

Scope is split into separate work orders for authentication, tasks/customer
requests, incidents, handovers, reporting, frontend and PostgreSQL evidence.
No database asset is ported without schema identity and rollback evidence.

Gate: a representative Shift lifecycle runs start-to-freeze with AI and
external channels disabled; compatibility differences are explicit; source
and target claims match evidence.

## F3 — Shift MVP hardening and cutover decision

Goal: reach a production-like local MVP and decide whether ownership should
move from the old repository.

Required evidence includes real PostgreSQL round trip/restore, authentication
hardening, permission and approval integrity, offline/degraded behavior,
reporting, correction/freeze invariants, security probes and operator UX.

Gate: owner explicitly chooses `KEEP_DUAL`, `TARGET_BECOMES_CANONICAL`, or
`DEFER_CUTOVER`. No implicit archival or deletion of the Shift repository.

## F4 — Capability normalization

Goal: make AI, Refinery, channels, notification, reporting, search and storage
replaceable behind capability contracts.

Gate: Shift remains functional with AI disabled; provider failures cannot
confirm business truth or corrupt the ledger; live governance claims use real
provider calls and sanitized evidence.

## F5 — Agent Operations discovery and non-streaming MVP

Goal: validate a second profile through timeline, evidence, approval, file/test
events, pause/resume, handoff and freeze before any remote-control feature.

Gate: provider-neutral contracts, official integration mechanisms only,
authenticated approvals, deterministic disconnect handling and no dependence
on session-cookie scraping or reverse-engineered tokens.

## F6 — Live View and Human Takeover security program

Goal: add observation first and input control only after ownership enforcement.

Precondition: separate security ADR, threat model and owner approval.

Gate: allowlisted capture, explicit host indication, short-lived authorization,
no dual input, revocation, fail-closed ambiguity, audited context delta, and a
replaceable streaming adapter.

## F7 — Dual-profile hardening and platform freeze

Goal: prove shared abstractions serve Shift and Agent profiles independently.

Gate: no cross-profile business coupling, capabilities are replaceable, CVF
controls are not duplicated, evidence traces to freeze, and neither profile's
quality regresses when the other is disabled.

## Global stop conditions

Stop the active work order on secret exposure, unpinned source, provenance
drift, license ambiguity, unexpected public API/database change, governance
bypass, failed rollback, module overclaim, provider failure used as proof,
ownership ambiguity, or scope beyond the authorized changed-set ceiling.

## Claim boundary

Only G0 is complete. F0 is authored but not built. F1–F7 are intended future
work and do not represent implemented modules.
