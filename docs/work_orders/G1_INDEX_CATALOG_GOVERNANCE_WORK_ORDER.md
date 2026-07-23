# Work Order — G1 Index and Catalog Governance

- Work order ID: `OW-G1-WO-001`
- Date: 2026-07-23
- Status: AUTHORIZED
- Risk: R1
- Authorization: owner request to apply Index/Catalog standards on 2026-07-23
- Governing spec: `OW-G1-SPEC-001`

## Changed-set ceiling

```text
docs/catalog/README.md
docs/catalog/ARTIFACT_REGISTRY.json
docs/catalog/ARTIFACT_REGISTRY.schema.json
docs/catalog/MODULE_REGISTRY.json
docs/catalog/MODULE_REGISTRY.schema.json
docs/catalog/MODULE_CATALOG.md
docs/INDEX.md
scripts/manage_catalog.py
tests/test_catalog_management.py
docs/roadmaps/CVF_OPERATIONS_WORKSPACE_ROADMAP.md
IMPLEMENTATION_STATUS.json
CVF_SESSION/ACTIVE_SESSION_STATE.json
CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-07-23.md
```

The three G1 authorization artifacts are committed before BUILD and are not
part of the worker's mutable scope.

## Roles and route

- WORK_ORDER_AUTHOR / COMMIT_STEWARD: records and commits authorization.
- IMPLEMENTATION_WORKER: implements only the changed-set ceiling.
- REVIEWER: may be the same agent for this R1 metadata tranche only after an
  explicit role transition and negative evidence; no self-review exception is
  created for future R2 runtime/governance work.
- SESSION_SYNC_STEWARD: closes G1 and restores F0 as the parked next work order.

## Tasks

1. Commit ADR, spec and work order.
2. Record BUILD acknowledgment and role transition.
3. Implement schemas, registries, generator/checker and tests.
4. Generate Index and Module Catalog from machine sources.
5. Run positive, negative, drift, doctor and changed-set checks.
6. Commit BUILD separately from closure continuity.
7. Restore `OW-F0-WO-001` as authored/not authorized.

## Commit plan

- C1: G1 authorization artifacts.
- C2: schemas, registries, generated views, tooling and tests.
- C3: roadmap/status/continuity closure.

## Stop conditions

Stop on runtime/source scope expansion, non-deterministic output, path escape,
registry overclaim, test failure outside bounded repair, continuity conflict,
secret exposure or any need for a provider call.

## Completion boundary

G1 FREEZE proves structural repository governance only. It does not authorize
F0 BUILD and does not claim that a platform module is implemented.
