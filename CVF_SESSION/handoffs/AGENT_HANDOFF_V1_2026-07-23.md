# Agent Handoff V1

Status: ACTIVE

## Current State

- Project: CVF-Operations-Workspace
- Current mode: WORK_ORDER
- Active phase: WORK_ORDER
- Active role: REVIEWER (must be independent from the planning author for
  authorization disposition)
- Next allowed move: independently review `OW-F0-WO-001` and record
  AUTHORIZE, AMEND, or REJECT. Do not begin BUILD before authorization.
- Parked operator checkpoint: `OW-F0-WO-001` is authored and awaiting
  independent authorization review.

## Seven-Step Control Chain

INTAKE -> DESIGN -> SPEC -> WORK_ORDER -> BUILD -> REVIEW -> FREEZE

## Role Assignment

Roles are responsibilities, not provider names. One agent may hold several
roles only when each transition is recorded. Available roles are ORCHESTRATOR,
SPEC_AUTHOR, WORK_ORDER_AUTHOR, IMPLEMENTATION_WORKER, REVIEWER, REPAIR_WORKER,
CLOSER, COMMIT_STEWARD, and SESSION_SYNC_STEWARD. High-risk work requires an
independent reviewer.

## Completed

- Project governance bootstrap created the initial continuity surfaces.
- INTAKE: owner chose a clean greenfield platform repository; the existing
  Shift repository remains a use-case/source repository, not the new root.
- DESIGN: `ADR-OW-001` establishes platform/profile boundaries and governed
  per-asset porting with provenance.
- SPEC: `OW-F0-SPEC-001` defines the source-intake and compatibility baseline.
- WORK_ORDER: `OW-F0-WO-001` was authored with an explicit changed-set ceiling,
  evidence matrix, roles, commit plan, rollback rehearsal and stop conditions.
- Planning-author checks passed: JSON parsing, `git diff --check`, file-size
  ceiling, forbidden BUILD-path scan and workspace doctor 24/24.
- Planning artifacts were committed separately as
  `d47127852e59868fc03680fa962192e70b08d762`; continuity is a distinct commit.
- Claude's repositioning assessment was reconciled as reviewed input; rename
  instructions were superseded and no bundle/source content was imported.

## Open Work

- Independent authorization review of `OW-F0-WO-001`.
- BUILD remains prohibited until authorization is recorded.

## Claim Boundary

This handoff records a planning baseline only. G0 bootstrap is complete; F0 is
not built. It does not claim that any runtime module, Shift profile, test
baseline, release, deployment, provider integration, Agent Operations, Live
View, or Human Takeover capability is implemented.
