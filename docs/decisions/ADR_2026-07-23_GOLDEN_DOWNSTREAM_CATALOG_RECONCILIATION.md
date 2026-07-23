# ADR — Golden Downstream Catalog Kit 1.1 Reconciliation

- ADR ID: `ADR-OW-003`
- Date: 2026-07-23 (repaired 2026-07-23, repair round 1 — see Repair History)
- Status: ACCEPTED
- Risk: R2 governance-significant
- Supersedes (for catalog *mechanism* only, not history): `ADR-OW-002`
  (`docs/decisions/ADR_2026-07-23_INDEX_CATALOG_GOVERNANCE.md`)
- Governs: `OW-G2-SPEC-001`, `OW-G2-WO-001`

## Context

`.cvf/manifest.json` currently pins CVF core at
`6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2`. This ADR was originally authored
against public CVF core `origin/main` at
`571cb21b7026f0cd925279ba698bf30a291a4644`; independent review (finding
`G2-R1`, see Repair History below) found the public tip had since advanced to
`27137db4d9aa2aea931ddd2507185d5c24943080`. **`27137db4d9aa2aea931ddd2507185d5c24943080`
is the operative reconciliation target for this ADR and for `OW-G2-SPEC-001`/
`OW-G2-WO-001`.** That commit ships a governed downstream catalog kit ("Golden
Downstream Catalog Kit 1.1", `catalogKitVersion: "1.1"`) at
`scripts/lib/downstream_catalog/{manage_cvf_downstream_catalog.ps1,
CvfDownstreamCatalogLib.ps1, schemas/ARTIFACT_REGISTRY.schema.json,
schemas/MODULE_REGISTRY.schema.json}`.

## Repair History — Round 1 (2026-07-23)

**G2-R1 — BLOCKER_BASELINE_DRIFT (repaired).** Independent Codex review of
this package found that public CVF core `origin/main` had moved from
`571cb21b7026f0cd925279ba698bf30a291a4644` (this ADR's original target) to
`27137db4d9aa2aea931ddd2507185d5c24943080`, commit message
`fix(sync): reconcile golden downstream bootstrap from provenance`. The
downstream hidden core clone was still at `571cb21…`, so the workspace doctor
reported `BEHIND_PUBLIC_REMOTE`. Verification
(`git diff 571cb21b7026f0cd925279ba698bf30a291a4644
27137db4d9aa2aea931ddd2507185d5c24943080 --
scripts/lib/downstream_catalog/{manage_cvf_downstream_catalog.ps1,CvfDownstreamCatalogLib.ps1,schemas/ARTIFACT_REGISTRY.schema.json,schemas/MODULE_REGISTRY.schema.json}`)
confirmed all four Golden Kit payload files are **byte-identical** between
the two commits — the disposition table, schema shapes, and byte/hash-parity
criteria below are unaffected in substance. What changed between the two
commits is the workspace doctor/guard itself
(`scripts/check_cvf_workspace_agent_enforcement.ps1`,
`governance/toolkit/05_OPERATION/downstream_catalog/CVF_DOWNSTREAM_CATALOG_GUARD.md`,
`scripts/lib/downstream_catalog/CvfGoldenHarnessSupport.ps1`) plus reference
docs — none of which this project reads as catalog-schema authority beyond
the guard doc already cited above. **Repair:** REPAIR_WORKER ran the official
`scripts/update_cvf_workspace_public_core.ps1 -WorkspaceRoot
"D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace"` (no `-UpdateProjectManifests`, no
`-OverlaySourcePath`, no `-AllowPendingCoreBackup`) to reconcile the hidden
core; it backed up the prior clone to
`_cvf-core-backups/.Controlled-Vibe-Framework-CVF-20260723-200246` (preserved,
not deleted) and cloned fresh from the public remote. Post-repair, hidden core
HEAD = `origin/main` = `27137db4d9aa2aea931ddd2507185d5c24943080`, worktree
clean. This ADR, `OW-G2-SPEC-001`, and `OW-G2-WO-001` are re-pinned to
`27137db4d9aa2aea931ddd2507185d5c24943080` throughout; the guard/doctor at
that commit is the authority for the independent re-review that follows this
repair. The original `571cb21…` target is preserved above, not erased, as the
record of what this package first authorized against.

See the active handoff for disposition of findings `G2-R2` (continuity
phase/role drift), `G2-R3` (stale F0 claim), and `G2-R4` (incomplete role
route) — those findings are about this project's own continuity surfaces and
the work order's role route, not about this ADR's decision content, and are
repaired in `CVF_SESSION/ACTIVE_SESSION_STATE.json`,
`CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-07-23.md`, and `OW-G2-WO-001`
respectively.

Per `CVF_DOWNSTREAM_CATALOG_GUARD.md`, the workspace doctor classifies a
project as governed if its manifest carries `catalogKitVersion` **or** any of
five marker surfaces exist. This project's `docs/catalog/ARTIFACT_REGISTRY.json`
already exists but does not conform to the Golden closed schema, and the four
other marker surfaces
(`scripts/manage_cvf_downstream_catalog.ps1`,
`scripts/lib/downstream_catalog/CvfDownstreamCatalogLib.ps1`,
`docs/catalog/schemas/ARTIFACT_REGISTRY.schema.json`,
`docs/catalog/schemas/MODULE_REGISTRY.schema.json`) are absent. This is exactly
the guard's `DAMAGED_GOVERNED_KIT` condition: partial governed-kit signal,
blocking failure, and — per the guard's own text — "a governed-kit deletion
can never silently fall back to legacy compatibility."

The existing registry is not merely missing four files. It uses a materially
different schema:

| | Existing (this project) | Golden Kit 1.1 |
|---|---|---|
| Artifact fields | `id, title, type, authority, entrypoint, summary, related` | `id, family, path, status, description` (closed, `additionalProperties: false`) |
| Artifact `type`/`family` vocabulary | `continuity, implementation_truth, catalog, decision, roadmap, specification, work_order, review, guide` (open-ended) | `schema, tool, manifest, policy, continuity, implementation_truth, generated_view, governed_artifact_family` (closed, 8 values) |
| Status vocabulary | `active, generated, historical` | `ACTIVE, DEPRECATED, RETIRED` |
| Module fields | (Module Registry already close to Golden shape, but `schemaVersion`/`claimBoundary` prose differ) | `id, name, path, status, description, evidence, controls?, dependencies?` |
| Module status vocabulary | n/a (empty) | `ENFORCED, PARTIAL, CONTRACT_ONLY, STUB, DEPRECATED` (no `PLANNED`/plan-only value representable) |
| Writer | `scripts/manage_catalog.py` (Python stdlib) | `scripts/manage_cvf_downstream_catalog.ps1` (PowerShell, byte/hash-pinned to CVF core) |

Registering the existing 28 artifacts under the Golden schema by simply
renaming fields is not possible: Golden's `family` enum has no slot for
`decision`, `roadmap`, `specification`, `work_order`, `review`, or `guide`.
Golden's own baseline generator (`Get-CvfDefaultArtifactRegistryEntries` in
`CvfDownstreamCatalogLib.ps1`) does not register individual decision/spec/
work-order/review documents at all — it registers each of those *families* as
a single `governed_artifact_family` folder pointer (`docs/decisions`,
`docs/roadmaps`, `docs/specs`, `docs/work_orders`, `docs/reviews`), and its
generated `docs/INDEX.md` renderer (`ConvertTo-CvfIndexMarkdown`) only ever
prints per-document rows for the 7 "start here" families
(`schema, tool, manifest, policy, continuity, implementation_truth,
generated_view`); every `governed_artifact_family` row prints as one folder
link, not one link per contained document.

## Decision

1. **Golden Downstream Catalog Kit 1.1 becomes catalog governance canonical**
   for this project. Its manager
   (`scripts/manage_cvf_downstream_catalog.ps1` + `CvfDownstreamCatalogLib.ps1`)
   is the only writer of `docs/INDEX.md` and `docs/catalog/MODULE_CATALOG.md`
   after migration. `scripts/manage_catalog.py` stops being a competing
   generator of those two files.
2. **This is a deliberate migration, not a bootstrap overwrite.** No bootstrap
   script runs against this project. BUILD authors the new registries by hand
   against the Golden schema, using the disposition table below, and verifies
   them with the real Golden manager copied byte/hash-identical from CVF core
   pin `27137db4d9aa2aea931ddd2507185d5c24943080` (re-pinned per `G2-R1` —
   the four Golden payload files are unchanged from the originally-cited
   `571cb21b7026f0cd925279ba698bf30a291a4644`).
3. **Every one of the 28 currently-registered artifact paths is dispositioned
   below** as `MIGRATE` (carried into the Golden registry as an equivalent
   row), `REPLACE` (the row is superseded by a Golden-schema row at a
   different path or meaning), `RETIRE` (the *registry row* is dropped; the
   underlying file's fate is stated explicitly), or `RETAIN` (the file stays
   exactly where it is and remains discoverable, but drops out of the
   *machine registry* because Golden's closed vocabulary has no family for
   its document type).
4. **No artifact path is silently lost.** Every `RETIRE`/`RETAIN` disposition
   below names the alternate discovery surface (a `governed_artifact_family`
   folder entry, `IMPLEMENTATION_STATUS.json`'s evidence list, or an F0/G1
   review receipt) that still makes the path findable after migration.
5. **Module Registry stays empty.** `MODULE_REGISTRY.json` migrates to the
   Golden schema (`schemaVersion, projectName, updatedAt, claimBoundary,
   modules: []`) with `modules: []` unchanged. No module entry, `ENFORCED`
   status, `GC-xxx` control, or dependency is created by this tranche.
6. **F0 source/runtime truth and provenance are not touched.** Nothing under
   `provenance/shift-operations/`, `scripts/source_intake/`,
   `tests/source_intake/`, `docs/architecture/`, `apps/`, `packages/`, or
   `database/` changes path, hash, or content.
7. **`docs/INDEX.md` and `docs/catalog/MODULE_CATALOG.md` remain generated
   views only** — never hand-edited, byte-identical to the Golden manager's
   render of the post-migration registries.
8. **Only one canonical writer survives.** `scripts/manage_catalog.py` and
   `tests/test_catalog_management.py` are retired as the Golden manager
   becomes canonical. Deletion (as opposed to marking `DEPRECATED`/leaving in
   place) is authorized only after BUILD records regression evidence that the
   Golden manager's `-Check` independently reproduces every guarantee the
   Python tool's test suite proved (schema closure, path existence, duplicate
   detection, path-escape rejection, drift detection). No wrapper script is
   created to make the doctor pass without that evidence.
9. **CVF core is not modified.** The Golden manager, library, and both
   schemas are copied byte/hash-identical from
   `../.Controlled-Vibe-Framework-CVF@27137db4d9aa2aea931ddd2507185d5c24943080`
   (re-pinned per `G2-R1`) and never edited downstream to "loosen" a check.
10. **Roadmap is out of scope.** `docs/roadmaps/CVF_OPERATIONS_WORKSPACE_ROADMAP.md`
    is not read as an input to this decision and is not modified by this
    tranche.

## Disposition table — all 28 existing Artifact Registry entries

Golden baseline IDs referenced below (`schema-*`, `tool-*`, `manifest-cvf`,
`policy-cvf`, `continuity-*`, `truth-implementation-status`, `view-*`,
`family-*`) are the exact 17 mandatory entries produced by
`Get-CvfDefaultArtifactRegistryEntries` in CVF core's
`CvfDownstreamCatalogLib.ps1` at the pinned commit — not invented names.

| # | Existing id | Existing path | Disposition | New Golden home / rationale |
|---|---|---|---|---|
| 1 | `session-memory` | `CVF_SESSION_MEMORY.md` | MIGRATE | → `continuity-session-memory` (family `continuity`), same path |
| 2 | `active-session-state` | `CVF_SESSION/ACTIVE_SESSION_STATE.json` | MIGRATE | → `continuity-active-session-state` (family `continuity`), same path |
| 3 | `active-handoff` | `CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-07-23.md` | MIGRATE | → `continuity-initial-handoff` (family `continuity`), same path (project has only had one handoff generation, V1, so "initial" and "active" currently coincide) |
| 4 | `implementation-status` | `IMPLEMENTATION_STATUS.json` | MIGRATE | → `truth-implementation-status` (family `implementation_truth`), same path |
| 5 | `artifact-registry` | `docs/catalog/ARTIFACT_REGISTRY.json` | RETIRE (row) | Golden design never self-registers the registry inside itself (absent from the 17-entry baseline). File is retained as the canonical registry; discoverable via `.cvf/manifest.json requiredDocs` and `docs/catalog/README.md`, not as its own row. |
| 6 | `artifact-registry-schema` | `docs/catalog/ARTIFACT_REGISTRY.schema.json` | REPLACE | Superseded by Golden `schema-artifact-registry` at the *different* path `docs/catalog/schemas/ARTIFACT_REGISTRY.schema.json` (byte/hash-pinned to core). Old file is retired once the new registries validate only against the Golden schema; deletion gated on BUILD evidence, not this round. |
| 7 | `module-registry` | `docs/catalog/MODULE_REGISTRY.json` | RETIRE (row) | Same rationale as #5 — Golden never self-registers `MODULE_REGISTRY.json` inside itself. File retained, content migrated per §5 above. |
| 8 | `module-registry-schema` | `docs/catalog/MODULE_REGISTRY.schema.json` | REPLACE | Superseded by Golden `schema-module-registry` at `docs/catalog/schemas/MODULE_REGISTRY.schema.json`. Same retirement gating as #6. |
| 9 | `module-catalog` | `docs/catalog/MODULE_CATALOG.md` | MIGRATE | → `view-module-catalog` (family `generated_view`), same path, re-rendered by the Golden manager |
| 10 | `catalog-standard` | `docs/catalog/README.md` | RETAIN, content replaced | File kept and rewritten to describe the Golden two-registry model; Golden's closed family vocabulary has no `guide` slot, so it is de-registered as a row. Still referenced by `.cvf/manifest.json requiredDocs` and `CVF_SESSION_MEMORY.md`/`AGENTS.md` prose. |
| 11 | `catalog-tool` | `scripts/manage_catalog.py` | RETIRE | Superseded by Golden `tool-catalog-manager`. Two active catalog writers may never coexist (decision §8). Actual file deletion is a BUILD action gated on regression evidence, not authorized blind by this ADR. |
| 12 | `catalog-tests` | `tests/test_catalog_management.py` | RETIRE | Tests the retired Python tool. May be kept temporarily as regression evidence during BUILD's migration proof, then retired alongside #11 with the same evidence gate. |
| 13 | `assessment-reconciliation` | `docs/reviews/ASSESSMENT_RECONCILIATION_2026-07-23.md` | RETAIN | Inside `docs/reviews/`, covered by Golden `family-reviews` folder entry. Row de-registered; still listed in `IMPLEMENTATION_STATUS.json.evidence`. |
| 14 | `adr-greenfield` | `docs/decisions/ADR_2026-07-23_GREENFIELD_PLATFORM_AND_PROFILE_PORTING.md` | RETAIN | Covered by `family-decisions`. Decision history is immutable; not deleted. |
| 15 | `adr-index-catalog` | `docs/decisions/ADR_2026-07-23_INDEX_CATALOG_GOVERNANCE.md` | RETAIN | Covered by `family-decisions`. Superseded in *mechanism* by this ADR but kept as historical decision record. |
| 16 | `platform-roadmap` | `docs/roadmaps/CVF_OPERATIONS_WORKSPACE_ROADMAP.md` | RETAIN, untouched | Covered by `family-roadmaps`. Explicitly out of scope (decision §10); content not read or modified by this tranche. |
| 17 | `f0-spec` | `docs/specs/F0_SOURCE_INTAKE_AND_COMPATIBILITY_BASELINE_SPEC.md` | RETAIN | Covered by `family-specs`. |
| 18 | `f0-work-order` | `docs/work_orders/F0_SOURCE_INTAKE_AND_COMPATIBILITY_BASELINE_WORK_ORDER.md` | RETAIN | Covered by `family-work-orders`. |
| 19 | `f0-work-order-amendment-1` | `docs/work_orders/F0_SOURCE_INTAKE_AND_COMPATIBILITY_BASELINE_WORK_ORDER_AMENDMENT_1.md` | RETAIN | Covered by `family-work-orders`. |
| 20 | `g1-spec` | `docs/specs/G1_INDEX_CATALOG_GOVERNANCE_SPEC.md` | RETAIN | Covered by `family-specs`. |
| 21 | `g1-work-order` | `docs/work_orders/G1_INDEX_CATALOG_GOVERNANCE_WORK_ORDER.md` | RETAIN | Covered by `family-work-orders`. |
| 22 | `g1-work-order-amendment-1` | `docs/work_orders/G1_INDEX_CATALOG_GOVERNANCE_WORK_ORDER_AMENDMENT_1.md` | RETAIN | Covered by `family-work-orders`. |
| 23 | `f0-architecture-rules` | `docs/architecture/PLATFORM_BOUNDARY_AND_PORTING_RULES.md` | RETAIN | No Golden `governed_artifact_family` baseline entry exists for `docs/architecture/`. File untouched (F0 boundary); discoverable via `IMPLEMENTATION_STATUS.json.evidence` and F0 review receipts rather than a generated-Index row. |
| 24 | `f0-source-intake-tool` | `scripts/source_intake/capture.py` | RETAIN | F0 source path, explicitly protected. Same discovery-surface note as #23. |
| 25 | `f0-source-intake-tests` | `tests/source_intake/test_capture_integration.py` | RETAIN | Same as #24. |
| 26 | `f0-capture-receipt` | `provenance/shift-operations/f98f29e145fa002be070e9d44520d20f0f82dcb3/capture_receipt.json` | RETAIN | F0 provenance, explicitly protected and unmodified. Same discovery-surface note. |
| 27 | `f0-build-evidence` | `docs/reviews/F0_BUILD_EVIDENCE_2026-07-23.md` | RETAIN | Covered by `family-reviews`. |
| 28 | `f0-independent-review` | `docs/reviews/F0_INDEPENDENT_REVIEW_2026-07-23.md` | RETAIN | Covered by `family-reviews`. |

Totals: 5 MIGRATE, 2 REPLACE, 4 RETIRE, 17 RETAIN. 28/28 dispositioned.

New rows with no prior counterpart, added because Golden's baseline requires
them: `manifest-cvf` (`.cvf/manifest.json`), `policy-cvf` (`.cvf/policy.json`),
`tool-catalog-manager`, `tool-catalog-library`, `view-docs-index`,
`family-decisions`, `family-roadmaps`, `family-specs`, `family-work-orders`,
`family-reviews`. These were never registered under the old schema; adding
them is new coverage, not a disposition of a pre-existing row.

## Named, accepted trade-off

`docs/INDEX.md`'s generated "Start Here" section currently deep-links every
decision/spec/work-order/review document individually with a one-line
summary. Under Golden Kit 1.1's renderer, a `governed_artifact_family` entry
prints as a single folder link — this is Golden's designed behavior, not a
defect this migration introduces, and reversing it would require either
hand-editing the generated view (forbidden) or extending CVF core's closed
schema (forbidden — core is read-only reference). This ADR accepts that
reduction in generated-Index granularity as a deliberate, disclosed
consequence of adopting the canonical Golden schema. It is not a loss of the
underlying files: every path in the table above remains exactly where it is,
still governed by its `governed_artifact_family` folder entry, and still
listed in `IMPLEMENTATION_STATUS.json.evidence` or an existing F0/G1 review
receipt where applicable.

## Consequences

- BUILD (a later, separately authorized tranche per `OW-G2-WO-001`) rewrites
  `docs/catalog/ARTIFACT_REGISTRY.json` and `docs/catalog/MODULE_REGISTRY.json`
  to the Golden closed schema using exactly this table.
- `docs/catalog/README.md` is rewritten to describe the two-registry model
  under Golden vocabulary.
- `.cvf/manifest.json` gains `catalogKitVersion: "1.1"` and `requiredDocs`
  entries for the four new governed surfaces.
- `scripts/manage_catalog.py` and `tests/test_catalog_management.py` retire
  once Golden `-Check` evidence is recorded; until then they remain and must
  not silently diverge from the migrated registries.
- No claim boundary, module count, or roadmap status changes as a result of
  this ADR.

## Claim boundary

This decision governs catalog *mechanism* (which schema, which writer, which
registry rows exist) and does not itself constitute BUILD. It creates no new
runtime capability claim, adds no module, and does not assert that migration
has occurred — only that it is authorized to occur under the bounded work
order this ADR governs.
