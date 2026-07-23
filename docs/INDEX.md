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

- Registered artifacts: **31**
- By status: active=23, generated=1, historical=7

## Catalog

- [Artifact Registry Schema](catalog/ARTIFACT_REGISTRY.schema.json) — `active` — JSON Schema contract for Artifact Registry records.
- [Module Registry Schema](catalog/MODULE_REGISTRY.schema.json) — `active` — JSON Schema contract for source-backed module records.

## Decision

- [Greenfield Platform and Governed Profile Porting](decisions/ADR_2026-07-23_GREENFIELD_PLATFORM_AND_PROFILE_PORTING.md) — `active` — Defines platform/profile ownership and per-asset porting.
- [Machine-Governed Documentation Index and Module Catalog](decisions/ADR_2026-07-23_INDEX_CATALOG_GOVERNANCE.md) — `active` — Separates documentation discovery from implementation claims.
- [Golden Downstream Catalog Kit 1.1 Reconciliation](decisions/ADR_2026-07-23_GOLDEN_DOWNSTREAM_CATALOG_RECONCILIATION.md) — `active` — Decides Golden Downstream Catalog Kit 1.1 as canonical, dispositions all 28 legacy artifact paths, and reconciles the CVF core pin to 27137db4d9aa2aea931ddd2507185d5c24943080 (re-pinned per repair finding G2-R1; original target 571cb21b7026f0cd925279ba698bf30a291a4644 preserved as repair history).

## Roadmap

- [CVF Operations Workspace Roadmap](roadmaps/CVF_OPERATIONS_WORKSPACE_ROADMAP.md) — `active` — Greenfield delivery sequence G0 and F0 through F7.

## Specification

- [F0 Source Intake and Compatibility Baseline Specification](specs/F0_SOURCE_INTAKE_AND_COMPATIBILITY_BASELINE_SPEC.md) — `historical` — Requirements for reproducible source intake without runtime import.
- [G1 Index and Catalog Governance Specification](specs/G1_INDEX_CATALOG_GOVERNANCE_SPEC.md) — `historical` — Requirements for schema-backed registries and drift checks.
- [G2 Governance Reconciliation Specification](specs/G2_GOVERNANCE_RECONCILIATION_SPEC.md) — `active` — 22 testable acceptance criteria for core-pin reconciliation, Golden Catalog Kit 1.1 migration, and workspace doctor PASS.

## Work Order

- [F0 Source Intake and Compatibility Baseline Work Order](work_orders/F0_SOURCE_INTAKE_AND_COMPATIBILITY_BASELINE_WORK_ORDER.md) — `historical` — Authorized bounded F0 source-intake work order.
- [F0 Work Order Amendment 1 — Index/Catalog Integration](work_orders/F0_SOURCE_INTAKE_AND_COMPATIBILITY_BASELINE_WORK_ORDER_AMENDMENT_1.md) — `historical` — Requires Artifact Registry updates and generated Index while excluding Module Registry.
- [G1 Index and Catalog Governance Work Order](work_orders/G1_INDEX_CATALOG_GOVERNANCE_WORK_ORDER.md) — `historical` — Authorized R1 changed-set ceiling for Index/Catalog governance.
- [G1 Work Order Amendment 1 — Python Generated Cache Exclusion](work_orders/G1_INDEX_CATALOG_GOVERNANCE_WORK_ORDER_AMENDMENT_1.md) — `historical` — Adds Python generated-cache exclusions to the G1 ceiling.
- [G2 Governance Reconciliation Work Order](work_orders/G2_GOVERNANCE_RECONCILIATION_WORK_ORDER.md) — `active` — Independently REVIEW_PASS'd bounded BUILD changed-set ceiling, roles, commit plan and stop conditions for G2; BUILD starts only after C1 succeeds and the implementation worker acknowledges the transition.

## Review

- [Index and Catalog Management Tests](../tests/test_catalog_management.py) — `active` — Positive, negative and generated-drift checks for registry governance.
- [Assessment Reconciliation](reviews/ASSESSMENT_RECONCILIATION_2026-07-23.md) — `active` — Reconciles the old rename assessment with the greenfield decision.
- [F0 Source Intake Tests](../tests/source_intake/test_capture_integration.py) — `active` — End-to-end and negative-path evidence for the F0 capture tool; sibling unit tests in the same directory cover paths, redaction, pin verification, inventory, routes, migrations and the ledger.
- [F0 Capture Receipt — Shift Operations @ f98f29e1](../provenance/shift-operations/f98f29e145fa002be070e9d44520d20f0f82dcb3/capture_receipt.json) — `active` — Reproducible F0 baseline receipt for Shift Operations at the pinned commit: file, route, migration, dependency, module and test evidence, plus the import ledger, live in this same directory.
- [F0 Build Evidence and Acceptance-Criteria Matrix](reviews/F0_BUILD_EVIDENCE_2026-07-23.md) — `historical` — IMPLEMENTATION_WORKER self-report mapping OW-F0-SPEC-001's AC-01 through AC-19 to evidence; independently reviewed with two recorded and closed findings.
- [F0 Independent Review Receipt](reviews/F0_INDEPENDENT_REVIEW_2026-07-23.md) — `active` — Independent AC-01 through AC-19 disposition, including closure of Git-blob hash correctness and evidence-count findings.

## Guide

- [Index and Catalog Manager](../scripts/manage_catalog.py) — `active` — Validates registries, computes metrics and generates both human views.
- [Platform Boundary and Porting Rules](architecture/PLATFORM_BOUNDARY_AND_PORTING_RULES.md) — `active` — Concrete dependency-direction and disposition rules F0's ledger followed, binding on future F1+ import work orders.
- [F0 Source Intake Capture Tool](../scripts/source_intake/capture.py) — `active` — Captures a reproducible, secret-safe Shift Operations baseline into provenance/shift-operations/ without importing runtime source.

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
