# Learning Assessment — operations-workspace-all-phases

- Review ID: `RM1-LEARNING-001`
- Date: 2026-07-23
- Governing: `ADR-OW-004`, `OW-RM1-SPEC-001` (`RM1-AC-24`), `OW-RM1-WO-001`
- Input: `operations-workspace-all-phases/` (read-only, sibling folder, never
  copied in), `MIGRATION_MANIFEST.json` SHA-256
  `7e900e85460061064d56818071c31486def91ce5c84784ec92a2d194a6b86b90`
- Baseline compared against: `operations-workspace-review-baseline/`
  (read-only, sibling folder)

## Purpose and boundary

This document is a **design-input review**, not a porting authorization and
not an implementation record. `adopt`/`adapt` below means "this idea informs
a future, separately governed work order" — never "this content is imported
or implemented by this tranche." No file from either input folder has been
copied, adapted, or executed as part of authoring this document or the
roadmap it accompanies. `ADR-OW-001`'s five-value disposition vocabulary
governs actual imports; this assessment uses the same four applicable values
(`adopt`, `adapt`, `reference-only`, `reject` — `PORT_AS_IS`/`ADAPT`/
`REFERENCE_ONLY`/`REJECT` in `ADR-OW-001` terms) because no candidate here is
source code being ported into a running module — the bundle is planning
documentation and illustrative schemas/scripts.

## Input accounting (Codex-accepted, RM1-R3)

Symmetric comparison, `__pycache__` excluded from both inputs:

| Metric | Value |
|---|---|
| Old-baseline non-cache paths | 26 |
| Full-bundle non-cache paths | 182 |
| Unchanged (byte-identical) | 21 |
| Changed | 5 |
| Missing old paths in new bundle | 0 |
| New relative to old baseline | 156 |
| **Total disposition candidates (changed + new)** | **161** |

The 21 unchanged files are **not re-reviewed** here (`RM1-AC-03`). All 12
`.pyc` files in the bundle (10 manifest-listed, 2 unmanifested) are excluded
from candidacy entirely — they are generated binaries, never source or
design input, regardless of manifest membership.

Full failure history behind these figures (25/21/4/169 → 26/21/5/168 →
26/21/5/156/161) is recorded in `ADR-OW-004` and is not repeated here.

## What is excluded from every disposition below

Per `RM1-AC-06`, the following are never assigned `adopt` or `adapt`,
regardless of content:

- Any path proposing to rename, overlay, or whole-folder-copy
  `shift-operations-workspace` (or any repository).
- Any file whose function is to physically apply/copy the bundle into a
  target repository.
- Any `__pycache__`/`.pyc` path.
- Any structural-validator script or its output, when cited as proof of
  runtime or governance behavior. The bundle's own `FINAL_PHASES_SUMMARY.md`
  phase map already discloses this limitation ("Runtime claim allowed after
  document gate" is `None` for structurally-gated phases); this assessment
  treats every one of the bundle's Phase 0–9 validators the same way — a
  validator PASS proves file/contract presence and forbidden-dependency-scan
  cleanliness only, never that a phase's runtime is complete.
- Any generic, pre-written work order — `RM1-AC-06` forbids
  pre-authorizing future work orders; a bundle-authored `WORK_ORDER_PHASE_*`
  file is read as background reference for scope, never as a ready-to-use
  authorization.
- A `DIAGNOSE` phase name — the bundle's own stop-condition table names a
  `DIAGNOSE` return state; this repository's phase model is the CVF
  seven-step chain (`INTAKE -> DESIGN -> SPEC -> WORK_ORDER -> BUILD ->
  REVIEW -> FREEZE`) and does not adopt `DIAGNOSE` as a phase.

## Changed candidates (5)

| Path | Disposition | Rationale |
|---|---|---|
| `MIGRATION_MANIFEST.json` | `reference-only` | The bundle's own internal file inventory/hash manifest; informative for verifying the bundle itself, not design content to adopt. |
| `README.md` | `reference-only` | Product positioning and architecture-principle framing informed this ADR's Decision 8 (structural validation is not runtime evidence) and background context; the document as a whole still assumes the rejected rename strategy, so it is read, not adopted. |
| `REVIEW_CHECKLIST.md` | `reference-only` | Useful checklist framing for a future review process; CVF's own REVIEW phase and independent-reviewer contract already govern this repository's review discipline. |
| `scripts/migration/README.md` | `reference-only` | Describes the 10 REJECTed validator scripts below; the description itself is informative but does not change their disposition. |
| `TREEVIEW.md` | `reject` | The proposed target tree is the rename/whole-folder-copy layout `ADR-OW-004` Decision 6 rejects outright. |

## New candidates (156), by named group

### Root-level bundle documents (4) — all `reference-only`

`EXECUTION_INDEX.md`, `FILE_INVENTORY.md`, `FINAL_PHASES_SUMMARY.md`,
`PHASE_2_9_REVIEW_SUMMARY.md` — navigation/summary documents for the bundle
itself; useful background, not design content to port. `FINAL_PHASES_SUMMARY.md`'s
phase map and stop-condition table directly informed this assessment's and
`ADR-OW-004`'s treatment of structural validation as non-runtime evidence.

### Root-level apply mechanism (1) — `reject`

`APPLY_TO_REPO.md` — instructs how to physically copy/overlay the bundle
into a target repository. This is the whole-folder-copy mechanism
`ADR-OW-004` Decision 6 rejects; excluded regardless of its content quality.

### `contracts/` — versioned schema examples (15) — all `adapt`

- `contracts/core/` (6): `capability-invocation.schema.json`,
  `capability-manifest.schema.json`, `command-envelope.schema.json`,
  `event-envelope.schema.json`, `operational-session.schema.json`,
  `profile-manifest.schema.json`.
- `contracts/agent-operations/` (6): `agent-event.schema.json`,
  `agent-session.schema.json`, `approval-request.schema.json`,
  `context-delta.schema.json`, `control-ownership.schema.json`,
  `takeover-session.schema.json`.
- `contracts/live-view/` (3): `input-lease.schema.json`,
  `live-view-session.schema.json`, `pairing-request.schema.json`.

Rationale: these schema shapes directly inform `F1A`'s "versioned closed
contracts" scope (profile manifest, `OperationalSession`, command/event/
capability envelopes) and, later, `F5`/`F6` contract design. `adapt`, not
`adopt`: any real contract for this repository must be authored fresh here,
reviewed, and tested — per `ADR-OW-001`'s `contract_or_schema` rule, batch
folder moves are forbidden and independent authorship review is required.

### `docs/architecture/` (6)

| Path | Disposition | Rationale |
|---|---|---|
| `CAPABILITY_MODEL.md` | `adapt` | Informs F4 capability-registry design. |
| `DEPENDENCY_RULES.md` | `reference-only` | Substantively already adopted via `ADR-OW-001`'s dependency-direction decision; confirmatory, not new. |
| `GOVERNED_COMMAND_PIPELINE.md` | `adapt` | Informs F1D governed command composition. |
| `LIVE_CONTROL_BOUNDARY.md` | `adapt` | Informs F6 security-boundary design. |
| `OPERATIONAL_SESSION_MODEL.md` | `adapt` | Informs F1B `OperationalSession` runtime. |
| `PROFILE_MODEL.md` | `adapt` | Informs F1C profile registry. |

### `docs/templates/` (4) — all `reference-only`

`DRIFT_AMENDMENT.md`, `INDEPENDENT_REVIEW_REPORT.md`,
`OWNER_FREEZE_RECEIPT.md`, `PHASE_EVIDENCE_RECEIPT.md` — evidence-document
shape ideas; this repository already has its own review/handoff/FREEZE
conventions (see `AGENTS.md`, `docs/reviews/*_INDEPENDENT_REVIEW_*.md`
precedents), so these inform format ideas only.

### `docs/work_orders/WORK_ORDER_PHASE_{2..9}_*.md` (8) — all `reference-only`

`WORK_ORDER_PHASE_2_WORKSPACE_CORE.md`,
`WORK_ORDER_PHASE_3_SHIFT_PROFILE.md`,
`WORK_ORDER_PHASE_4_CAPABILITY_NORMALIZATION.md`,
`WORK_ORDER_PHASE_5_SHIFT_MVP_FREEZE.md`,
`WORK_ORDER_PHASE_6_AGENT_CONTRACTS.md`, `WORK_ORDER_PHASE_7_AGENT_MVP.md`,
`WORK_ORDER_PHASE_8_LIVE_TAKEOVER.md`,
`WORK_ORDER_PHASE_9_PLATFORM_FREEZE.md`. Per the exclusion list above, no
pre-written work order is pre-authorized; read as scope background for the
matching F-phase only. Each real future work order is authored fresh through
`SPEC_AUTHOR`/`WORK_ORDER_AUTHOR` against this repository's own baseline.

### `examples/manifests/` (4) — all `reference-only`

`agent-operations.profile.yaml`, `deskhub.adapter.yaml`,
`live-view.capability.yaml`, `shift-operations.profile.yaml` — illustrative
example configs; the authoritative shapes are the `contracts/*.schema.json`
files above (already `adapt`), so these examples are read as secondary
illustration, not duplicated as separate adopted content.

### `scripts/migration/*.py` — new validator scripts (10) — all `reject`

`run_all_structural_validators.py`, `validate_bundle_integrity.py`,
`validate_phase_2_core.py`, `validate_phase_4_capabilities.py`,
`validate_phase_6_agent_contracts.py`, `verify_phase_3_shift_profile.py`,
`verify_phase_5_shift_mvp.py`, `verify_phase_7_agent_mvp.py`,
`verify_phase_8_live_view.py`, `verify_phase_9_platform_freeze.py`. Every one
of these checks for file/contract presence under the bundle's own
rename-and-whole-copy target layout (`TARGET_FILE_MAP.md` per phase, below);
adopting them would mean adopting that layout. Rejected as a group, and
independently: none of their PASS results may ever be cited as runtime or
governance evidence (see "What is excluded" above).

### `docs/implementation/phase-{2..9}/` — generic per-phase filenames (48)

Each of phase-2 through phase-9 (8 phases) repeats six generic filenames.
Disposition is by filename pattern, applied identically across all 8 phases:

| Filename pattern | Count | Disposition | Rationale |
|---|---|---|---|
| `ACCEPTANCE_GATES.md` | 8 | `adapt` | Directly informs each F-phase's required "evidence/gate" field (`RM1-AC-21`). |
| `ROLLBACK_PLAN.md` | 8 | `adapt` | Informs stop-condition and rollback-rehearsal design for each F-phase. |
| `EVIDENCE_PLAN.md` | 8 | `adapt` | Informs each F-phase's "evidence/gate" field. |
| `README.md` | 8 | `reference-only` | Phase overview prose; background only. |
| `IMPLEMENTATION_SEQUENCE.md` | 8 | `reference-only` | Bundle-specific ordering, useful background, not adopted as this repository's own sequence. |
| `TARGET_FILE_MAP.md` | 8 | `reject` | Prescribes exact paths under the rejected rename/whole-folder-copy repository layout. |

### `docs/implementation/phase-{2..9}/` — phase-specific domain documents (56)

The remaining, non-generic file per phase. All `adapt` except
`CONTRACT_MIGRATION_MAP.md` (`reference-only` — rename-mapping specific, not
reusable once the rename strategy is rejected):

| Phase | Files (all `adapt` unless noted) | Informs |
|---|---|---|
| phase-2 (4) | `WORKSPACE_CORE_EXTRACTION_PLAN.md`, `PROFILE_REGISTRY_SPEC.md`, `ARCHITECTURE_TEST_PLAN.md`; `CONTRACT_MIGRATION_MAP.md` (`reference-only`) | F1B, F1C, F1E |
| phase-3 (6) | `SHIFT_PROFILE_EXTRACTION_PLAN.md`, `API_COMPATIBILITY_MAP.md`, `DATABASE_OWNERSHIP_MAP.md`, `DOMAIN_OWNERSHIP_MAP.md`, `FRONTEND_PROFILE_ROUTING.md`, `REGRESSION_TEST_MATRIX.md` | F2 scope areas, API/DB ownership rules (`RM1-AC-19`) |
| phase-4 (6) | `CAPABILITY_NORMALIZATION_PLAN.md`, `CAPABILITY_REGISTRY_SPEC.md`, `CAPABILITY_INVOCATION_CONTRACT.md`, `CONVERSATION_ROUTING_SPLIT.md`, `FAILURE_AND_TERMINATION_MODEL.md`, `PROVIDER_ISOLATION_RULES.md` | F4 capability/provider layer, provider-failure taxonomy (`RM1-AC-15`) |
| phase-5 (6) | `SECURITY_HARDENING_MATRIX.md`, `RELEASE_READINESS_CHECKLIST.md`, `POSTGRESQL_EVIDENCE_PLAN.md`, `MODULE_CLAIM_FREEZE.md`, `FEATURE_COMPLETION_MATRIX.md`, `SHIFT_MVP_COMPLETION_PLAN.md` | F3 hardening/cutover (`RM1-AC-13`) |
| phase-6 (9) | `AGENT_OPERATIONS_DISCOVERY.md`, `CONTROL_OWNERSHIP_STATE_MACHINE.md`, `DOMAIN_MODEL.md`, `EVENT_MODEL.md`, `MVP_SCOPE.md`, `PRIVACY_AND_DATA_SCOPE.md`, `ADAPTER_FEASIBILITY_MATRIX.md`, `THREAT_MODEL.md`, `HUMAN_TAKEOVER_CONTRACT.md` | F5 contracts, F6 security-ADR/threat-model precondition |
| phase-7 (10) | `AGENT_OPERATIONS_MVP_PLAN.md`, `APPROVAL_RELAY.md`, `DESKTOP_HOST_ARCHITECTURE.md`, `EVIDENCE_AND_FREEZE.md`, `MOBILE_PWA_FLOW.md`, `OBSERVABILITY_BRIDGE.md`, `OWNERSHIP_LOCK.md`, `SAFE_DISCONNECT.md`, `TEST_MATRIX.md`, `VSCODE_COMPANION_SPEC.md` | F5 non-streaming MVP (`RM1-AC-16`) |
| phase-8 (8) | `DESKHUB_ADAPTER.md`, `DEVICE_PAIRING_AND_SESSION_TOKENS.md`, `FAILURE_AND_RECOVERY.md`, `HUMAN_TAKEOVER_RUNTIME.md`, `INPUT_OWNERSHIP_LEASE.md`, `LIVE_VIEW_CAPABILITY.md`, `SECURITY_HARDENING.md`, `WINDOW_ALLOWLIST.md` | F6 Live View/Human Takeover (`RM1-AC-17`) |
| phase-9 (7) | `AGENT_PILOT.md`, `CROSS_PROFILE_ARCHITECTURE_TESTS.md`, `DUAL_PROFILE_HARDENING.md`, `MODULE_REGISTRY_FINALIZATION.md`, `PLATFORM_FREEZE_CRITERIA.md`, `RELEASE_PLAN.md`, `SHIFT_PILOT.md` | F7 dual-profile hardening/freeze (`RM1-AC-18`) |

## Coverage accounting

| Group | Count |
|---|---|
| Changed candidates | 5 |
| Root bundle documents | 4 |
| Root apply mechanism | 1 |
| `contracts/` schemas | 15 |
| `docs/architecture/` | 6 |
| `docs/templates/` | 4 |
| `docs/work_orders/WORK_ORDER_PHASE_*` | 8 |
| `examples/manifests/` | 4 |
| `scripts/migration/*.py` (new) | 10 |
| Phase generic filenames (6 patterns x 8 phases) | 48 |
| Phase domain-specific documents | 56 |
| **New subtotal** | **156** |
| **Total (changed + new)** | **161** |

Disposition totals:

- `adopt`: 0.
- `adapt`: 99 — 15 `contracts/` schemas + 5 `docs/architecture/` files
  (`CAPABILITY_MODEL`, `GOVERNED_COMMAND_PIPELINE`, `LIVE_CONTROL_BOUNDARY`,
  `OPERATIONAL_SESSION_MODEL`, `PROFILE_MODEL`) + 24 generic per-phase files
  (`ACCEPTANCE_GATES.md` 8 + `ROLLBACK_PLAN.md` 8 + `EVIDENCE_PLAN.md` 8) +
  55 `adapt`-dispositioned phase-specific domain documents (56 total domain
  documents across phase-2..9, of which 55 are `adapt` and 1
  (`CONTRACT_MIGRATION_MAP.md`) is `reference-only`) = 15+5+24+55 = 99.
- `reference-only`: 42 — 4 changed (`MIGRATION_MANIFEST.json`, `README.md`,
  `REVIEW_CHECKLIST.md`, `scripts/migration/README.md`) + 4 root bundle
  documents + 8 phase `README.md` + 8 phase `IMPLEMENTATION_SEQUENCE.md` + 1
  `docs/architecture/DEPENDENCY_RULES.md` + 4 `docs/templates/` + 8
  `docs/work_orders/WORK_ORDER_PHASE_*` + 4 `examples/manifests/` + 1
  `CONTRACT_MIGRATION_MAP.md` = 4+4+8+8+1+4+8+4+1 = 42.
- `reject`: 20 — 1 changed (`TREEVIEW.md`) + 1 `APPLY_TO_REPO.md` + 8
  `TARGET_FILE_MAP.md` + 10 new `scripts/migration/*.py` validators =
  1+1+8+10 = 20.

`0 + 99 + 42 + 20 = 161` — every one of the 161 candidates is classified
exactly once.

## Claim boundary

This assessment is a design-input review only. No file above has been
imported, copied, executed, or implemented. `adopt`/`adapt` marks a
candidate as informing a future, separately governed F1+ work order — never
as authorization for that work order, and never as evidence that any F-phase
capability exists today. `reference-only` and `reject` candidates carry no
future import path through this document. The 21 unchanged old-baseline
files were not re-reviewed, per `RM1-AC-03`. This document does not modify
`docs/catalog/MODULE_REGISTRY.json`, `docs/INDEX.md`, or
`docs/catalog/MODULE_CATALOG.md`, and creates no runtime, provider, or
governance-behavior claim.
