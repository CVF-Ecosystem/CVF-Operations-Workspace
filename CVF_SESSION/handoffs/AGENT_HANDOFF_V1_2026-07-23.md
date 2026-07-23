# Agent Handoff V1

Status: ACTIVE

## Current State

- Project: CVF-Operations-Workspace
- Current mode: INTAKE
- Active phase: INTAKE
- Active role: ORCHESTRATOR
- Next allowed move: Complete INTAKE before DESIGN.
- Parked operator checkpoint: none

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

## Open Work

- Capture the first governed request through INTAKE.

## Claim Boundary

This handoff records initial project state only. It does not claim that any
feature, test, release, deployment, or provider integration is complete.
