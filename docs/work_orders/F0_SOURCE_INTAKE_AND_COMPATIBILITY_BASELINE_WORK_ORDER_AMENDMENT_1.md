# F0 Work Order Amendment 1 — Index/Catalog Integration

- Work order: `OW-F0-WO-001`
- Amendment: `OW-F0-WO-001-A1`
- Date: 2026-07-23
- Status: AUTHORIZED
- Finding owner: REVIEWER

## Finding

G1 made `docs/INDEX.md` a generated view whose machine source is
`docs/catalog/ARTIFACT_REGISTRY.json`. The original F0 ceiling allowed direct
Index modification but did not allow its machine source, creating an
unsatisfiable catalog gate.

## Amendment

Replace direct Index editing authority with generated-view authority:

```text
docs/catalog/ARTIFACT_REGISTRY.json
docs/INDEX.md  # generated only by scripts/manage_catalog.py --write
```

F0 artifacts that belong in repository discovery must be registered with
accurate lifecycle status. After generation, `python scripts/manage_catalog.py
--check` must pass.

`docs/catalog/MODULE_REGISTRY.json` and `MODULE_CATALOG.md` remain excluded.
F0 imports no runtime source and therefore creates or promotes no module.

No other scope, role, evidence or commit authority changes.
