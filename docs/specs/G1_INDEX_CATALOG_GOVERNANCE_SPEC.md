# G1 Index and Catalog Governance Specification

- Spec ID: `OW-G1-SPEC-001`
- Date: 2026-07-23
- Status: AUTHORIZED
- Implements: `ADR-OW-002`

## Requirements

- G1-01: Artifact and module registries have committed JSON Schemas.
- G1-02: Registry IDs and paths are unique and use `/` separators.
- G1-03: Artifact paths and module paths resolve inside the repository.
- G1-04: Artifact type/status and module status use controlled vocabularies.
- G1-05: Artifact relationships and module dependencies resolve by ID.
- G1-06: CVF controls use the canonical twelve-control vocabulary.
- G1-07: Module code metrics are computed from disk.
- G1-08: One command regenerates both human-readable surfaces.
- G1-09: One non-mutating command fails on registry or Markdown drift.
- G1-10: Generated files identify their machine source and claim boundary.
- G1-11: Empty module catalog remains valid and makes no implementation claim.
- G1-12: Tests cover valid baseline, duplicates, missing paths, unknown status,
  unknown relationships/dependencies, path escape and generated drift.
- G1-13: `docs/INDEX.md` exposes continuity, implementation truth, active
  planning, governed artifact families and verification commands.
- G1-14: G1 does not add runtime modules or promote module status.

## Acceptance

All G1-01 through G1-14 must have executable or source-inspection evidence.
`python scripts/manage_catalog.py --check`, the catalog test suite,
`git diff --check`, JSON parsing and the workspace doctor must pass.

## Non-goals

- CI integration;
- runtime feature code;
- F0 source intake implementation;
- provider calls or governance-runtime claims.
