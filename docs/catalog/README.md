# Index and Catalog Governance

The repository uses two machine sources and two generated views:

| Machine source | Generated view | Purpose |
|---|---|---|
| `ARTIFACT_REGISTRY.json` | `../INDEX.md` | Documentation discovery and authority |
| `MODULE_REGISTRY.json` | `MODULE_CATALOG.md` | Source-backed implementation claims |

Never edit either generated Markdown file by hand.

## Workflow

```powershell
python scripts/manage_catalog.py --write
python scripts/manage_catalog.py --check
python -m unittest tests.test_catalog_management -v
```

Register an artifact when it becomes an active or authoritative repository
surface. Register a module only when a real path exists. A roadmap entry alone
is not a module.

Module status changes require source and test evidence. `enforced` means
runtime code and blocking tests exist; it never means a document merely says a
control exists.

## Claim boundary

Passing catalog checks proves registry consistency and generated-view
freshness. It does not prove runtime governance behavior, provider readiness,
release readiness or production fitness.
