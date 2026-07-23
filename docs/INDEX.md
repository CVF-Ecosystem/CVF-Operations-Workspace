# Project Documentation Index

> GENERATED FILE — do not edit by hand. Source: [`catalog/ARTIFACT_REGISTRY.json`](catalog/ARTIFACT_REGISTRY.json).

## Start Here

- [Project Session Memory](../CVF_SESSION_MEMORY.md) — Startup order and canonical continuity pointer.
- [Active Session State](../CVF_SESSION/ACTIVE_SESSION_STATE.json) — Current phase, role, next move and parked checkpoint.
- [Active Agent Handoff](../CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-07-23.md) — Human-readable current state and claim boundary.
- [Implementation Status](../IMPLEMENTATION_STATUS.json) — Current implemented capabilities, limitations and active work orders.
- [Artifact Registry](catalog/ARTIFACT_REGISTRY.json) — Machine source for documentation discovery and generated Index.
- [Module Registry](catalog/MODULE_REGISTRY.json) — Machine source for source-backed module claims.
- [Module Catalog](catalog/MODULE_CATALOG.md) — Generated human view of the Module Registry.
- [Index and Catalog Governance](catalog/README.md) — Registry maintenance, generation and claim-boundary rules.

## Artifact Registry Summary

- Registered artifacts: **21**
- By status: active=15, awaiting_authorization=2, generated=1, historical=3

## Catalog

- [Artifact Registry Schema](catalog/ARTIFACT_REGISTRY.schema.json) — `active` — JSON Schema contract for Artifact Registry records.
- [Module Registry Schema](catalog/MODULE_REGISTRY.schema.json) — `active` — JSON Schema contract for source-backed module records.

## Decision

- [Greenfield Platform and Governed Profile Porting](decisions/ADR_2026-07-23_GREENFIELD_PLATFORM_AND_PROFILE_PORTING.md) — `active` — Defines platform/profile ownership and per-asset porting.
- [Machine-Governed Documentation Index and Module Catalog](decisions/ADR_2026-07-23_INDEX_CATALOG_GOVERNANCE.md) — `active` — Separates documentation discovery from implementation claims.

## Roadmap

- [CVF Operations Workspace Roadmap](roadmaps/CVF_OPERATIONS_WORKSPACE_ROADMAP.md) — `active` — Greenfield delivery sequence G0 and F0 through F7.

## Specification

- [F0 Source Intake and Compatibility Baseline Specification](specs/F0_SOURCE_INTAKE_AND_COMPATIBILITY_BASELINE_SPEC.md) — `awaiting_authorization` — Requirements for reproducible source intake without runtime import.
- [G1 Index and Catalog Governance Specification](specs/G1_INDEX_CATALOG_GOVERNANCE_SPEC.md) — `historical` — Requirements for schema-backed registries and drift checks.

## Work Order

- [F0 Source Intake and Compatibility Baseline Work Order](work_orders/F0_SOURCE_INTAKE_AND_COMPATIBILITY_BASELINE_WORK_ORDER.md) — `awaiting_authorization` — Bounded F0 work order; BUILD remains prohibited.
- [G1 Index and Catalog Governance Work Order](work_orders/G1_INDEX_CATALOG_GOVERNANCE_WORK_ORDER.md) — `historical` — Authorized R1 changed-set ceiling for Index/Catalog governance.
- [G1 Work Order Amendment 1 — Python Generated Cache Exclusion](work_orders/G1_INDEX_CATALOG_GOVERNANCE_WORK_ORDER_AMENDMENT_1.md) — `historical` — Adds Python generated-cache exclusions to the G1 ceiling.

## Review

- [Index and Catalog Management Tests](../tests/test_catalog_management.py) — `active` — Positive, negative and generated-drift checks for registry governance.
- [Assessment Reconciliation](reviews/ASSESSMENT_RECONCILIATION_2026-07-23.md) — `active` — Reconciles the old rename assessment with the greenfield decision.

## Guide

- [Index and Catalog Manager](../scripts/manage_catalog.py) — `active` — Validates registries, computes metrics and generates both human views.

## Governed Artifact Families

- Decisions: [`docs/decisions/`](decisions/)
- Roadmaps: [`docs/roadmaps/`](roadmaps/)
- Specifications: [`docs/specs/`](specs/)
- Work orders: [`docs/work_orders/`](work_orders/)
- Reviews and evidence: [`docs/reviews/`](reviews/)

## Verification

```powershell
python scripts/manage_catalog.py --check
python -m unittest tests.test_catalog_management -v
```

## Claim Boundary

The artifact registry governs discovery and authority metadata; source, tests, implementation status and review evidence govern capability truth.
