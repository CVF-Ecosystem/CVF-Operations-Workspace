# Index and Catalog Governance

The repository uses Golden Downstream Catalog Kit 1.1 (CVF core
`catalogKitVersion: "1.1"`), pinned byte-identical to CVF core commit
`27137db4d9aa2aea931ddd2507185d5c24943080`. Two machine sources generate two
views:

| Machine source | Generated view | Purpose |
|---|---|---|
| `docs/catalog/ARTIFACT_REGISTRY.json` | `../INDEX.md` | Bootstrap authority-surface discovery |
| `docs/catalog/MODULE_REGISTRY.json` | `MODULE_CATALOG.md` | Source-verified implementation claims |

Both registries validate against the closed schemas at
`docs/catalog/schemas/ARTIFACT_REGISTRY.schema.json` and
`docs/catalog/schemas/MODULE_REGISTRY.schema.json`
(`additionalProperties: false` — unknown fields are rejected, not ignored).
Never edit either generated Markdown file by hand; a hand-edit fails
`-Check` closed.

## Single canonical writer

`scripts/manage_cvf_downstream_catalog.ps1` (with
`scripts/lib/downstream_catalog/CvfDownstreamCatalogLib.ps1`) is the **only**
writer of `docs/INDEX.md` and `docs/catalog/MODULE_CATALOG.md`. The prior
Python manager (`scripts/manage_catalog.py`) and its schema files at
`docs/catalog/ARTIFACT_REGISTRY.schema.json` /
`docs/catalog/MODULE_REGISTRY.schema.json` (no `schemas/` subdirectory) are
retired — see `ADR-OW-003` and `docs/reviews/G2_BUILD_EVIDENCE_2026-07-23.md`
for the migration rationale, disposition of all 28 previously-registered
artifact paths, and the regression evidence proving the Golden manager
reproduces every guarantee the retired Python suite proved.

## Workflow

```powershell
powershell -ExecutionPolicy Bypass -File scripts/manage_cvf_downstream_catalog.ps1 -Write
powershell -ExecutionPolicy Bypass -File scripts/manage_cvf_downstream_catalog.ps1 -Check
python -m unittest tests.test_catalog_management -v
```

## Closed vocabulary

- Artifact `family`: `schema`, `tool`, `manifest`, `policy`, `continuity`,
  `implementation_truth`, `generated_view`, `governed_artifact_family`.
- Artifact `status`: `ACTIVE`, `DEPRECATED`, `RETIRED`.
- Module `status` (source-backed only, no plan-only value):
  `ENFORCED`, `PARTIAL`, `CONTRACT_ONLY`, `STUB`, `DEPRECATED`. Every module
  entry requires a non-empty `evidence` field naming a concrete file/line or
  test/gate. `controls` entries must match `^GC-[0-9]{3}$`; `dependencies`
  entries must reference another module `id` already in the registry.

A `governed_artifact_family` entry (`docs/decisions`, `docs/roadmaps`,
`docs/specs`, `docs/work_orders`, `docs/reviews`) registers the *folder*, not
each document inside it — Golden's closed schema has no per-document family
for decisions/specs/work-orders/reviews. Individual documents in those
folders remain discoverable by directory listing and by
`IMPLEMENTATION_STATUS.json`'s evidence list; they no longer get an
individual deep-linked row in the generated `docs/INDEX.md`. This is a
disclosed, deliberate trade-off of adopting the canonical Golden schema, not
a silent loss — see `ADR-OW-003`'s "Named, accepted trade-off" section.

Register a module only when a real path exists and is source-verified. A
roadmap entry alone is never a module.

## Claim boundary

Passing catalog checks proves registry consistency and generated-view
freshness. It does not prove runtime governance behavior, provider readiness,
release readiness, or production fitness.
