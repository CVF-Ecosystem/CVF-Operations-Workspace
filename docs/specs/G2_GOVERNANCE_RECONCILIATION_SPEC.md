# Spec — G2 Governance Reconciliation

- Spec ID: `OW-G2-SPEC-001`
- Date: 2026-07-23 (repaired 2026-07-23, repair round 1)
- Status: AUTHORED — awaiting `OW-G2-WO-001` authorization and independent
  review before BUILD
- Risk: R2 governance-significant
- Governing decision: `ADR-OW-003`
  (`docs/decisions/ADR_2026-07-23_GOLDEN_DOWNSTREAM_CATALOG_RECONCILIATION.md`)

## Repair note (round 1)

This spec was originally authored against public CVF core `origin/main` at
`571cb21b7026f0cd925279ba698bf30a291a4644`. Independent review found the
public tip had advanced to `27137db4d9aa2aea931ddd2507185d5c24943080`
(finding `G2-R1`; full history and repair record in `ADR-OW-003`'s "Repair
History" section and the active handoff). All pin references below are
re-pinned to `27137db4d9aa2aea931ddd2507185d5c24943080` — the four Golden Kit
payload files are byte-identical between the two commits, so no acceptance
criterion below changes in substance, only the target SHA.

## Purpose

Define testable acceptance criteria for reconciling this project's CVF core
pin and downstream catalog with CVF core `origin/main` at
`27137db4d9aa2aea931ddd2507185d5c24943080`, migrating the existing catalog to
Golden Downstream Catalog Kit 1.1 per `ADR-OW-003`'s disposition table, and
resolving the workspace doctor's `DAMAGED_GOVERNED_KIT` failure — without
importing runtime, touching the roadmap, or creating any capability claim.

## Claim boundary (repeated from ADR — binding on all criteria below)

G0, G1 and F0 are complete and closed. No runtime module is imported or
implemented by this spec. `docs/catalog/MODULE_REGISTRY.json` remains an
empty, source-backed registry after migration. No new CVF control (`GC-xxx`)
claim, module status, or roadmap change is authorized here.

## Acceptance criteria

**G2-AC-01 — Core pin/remote verification.** `git -C
../.Controlled-Vibe-Framework-CVF rev-parse HEAD`,
`git -C ../.Controlled-Vibe-Framework-CVF rev-parse origin/main`, and `git -C
../.Controlled-Vibe-Framework-CVF remote get-url origin` all resolve to
`27137db4d9aa2aea931ddd2507185d5c24943080` /
`https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`, worktree
clean, recorded verbatim in BUILD evidence. (Re-pinned per `G2-R1`; satisfied
by the repair-round reconciliation already performed via
`update_cvf_workspace_public_core.ps1` — verified HEAD = origin/main =
`27137db4d9aa2aea931ddd2507185d5c24943080`.)

**G2-AC-02 — Manifest pin and kit marker.** `.cvf/manifest.json` sets
`cvfCoreCommit` to the full 40-character SHA `27137db4d9aa2aea931ddd2507185d5c24943080`
(re-pinned per `G2-R1`; no abbreviation), adds `catalogKitVersion: "1.1"`, and
leaves `workspaceLayout`, `cvfCoreRelativePath`, `phaseModel` unchanged. This
criterion is still open — `.cvf/manifest.json` remains untouched and pinned
to `6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2` until BUILD.

**G2-AC-03 — Manifest requiredDocs completeness.** `.cvf/manifest.json`
`requiredDocs` includes, in addition to existing entries:
`docs/catalog/ARTIFACT_REGISTRY.json`,
`docs/catalog/schemas/ARTIFACT_REGISTRY.schema.json`,
`docs/catalog/schemas/MODULE_REGISTRY.schema.json`,
`scripts/manage_cvf_downstream_catalog.ps1`,
`scripts/lib/downstream_catalog/CvfDownstreamCatalogLib.ps1`.

**G2-AC-04 — Manager/library byte/hash parity.**
`scripts/manage_cvf_downstream_catalog.ps1` and
`scripts/lib/downstream_catalog/CvfDownstreamCatalogLib.ps1` are byte-identical
(SHA-256 match, recorded in evidence) to
`../.Controlled-Vibe-Framework-CVF/scripts/lib/downstream_catalog/{manage_cvf_downstream_catalog.ps1,CvfDownstreamCatalogLib.ps1}`
at the pinned commit.

**G2-AC-05 — Schema byte/hash parity.**
`docs/catalog/schemas/ARTIFACT_REGISTRY.schema.json` and
`docs/catalog/schemas/MODULE_REGISTRY.schema.json` are byte-identical
(SHA-256 match, recorded in evidence) to
`../.Controlled-Vibe-Framework-CVF/scripts/lib/downstream_catalog/schemas/{ARTIFACT_REGISTRY.schema.json,MODULE_REGISTRY.schema.json}`
at the pinned commit.

**G2-AC-06 — Artifact Registry migrated to Golden closed schema.**
`docs/catalog/ARTIFACT_REGISTRY.json` matches
`docs/catalog/schemas/ARTIFACT_REGISTRY.schema.json`: every entry has exactly
`id, family, path, status, description`; `family` ∈ `{schema, tool, manifest,
policy, continuity, implementation_truth, generated_view,
governed_artifact_family}`; `status` ∈ `{ACTIVE, DEPRECATED, RETIRED}`;
`scripts/manage_cvf_downstream_catalog.ps1 -Check` accepts it with zero
violations.

**G2-AC-07 — All 28 legacy paths dispositioned.** Every one of the 28 paths
listed in `ADR-OW-003`'s disposition table is accounted for: MIGRATE/REPLACE
entries appear in the new registry under their stated new id; RETIRE entries
are absent from the registry with the file-level fate matching the ADR;
RETAIN entries either appear under a `governed_artifact_family` folder they
sit inside, or are named in `IMPLEMENTATION_STATUS.json.evidence`. BUILD
evidence includes a 28-row reconciliation table matching the ADR 1:1 — no row
added, removed, or reworded without a corresponding ADR line.

**G2-AC-08 — Mandatory Golden baseline entries present.** All 17 baseline ids
from CVF core's `Get-CvfDefaultArtifactRegistryEntries`
(`schema-artifact-registry`, `schema-module-registry`, `tool-catalog-manager`,
`tool-catalog-library`, `manifest-cvf`, `policy-cvf`,
`continuity-session-memory`, `continuity-active-session-state`,
`continuity-initial-handoff`, `truth-implementation-status`,
`view-docs-index`, `view-module-catalog`, `family-decisions`,
`family-roadmaps`, `family-specs`, `family-work-orders`, `family-reviews`)
exist with the exact paths CVF core defines; `scripts/manage_cvf_downstream_catalog.ps1
-Check`'s baseline check passes with zero missing/mismatched entries.

**G2-AC-09 — Module Registry migrated, still empty.**
`docs/catalog/MODULE_REGISTRY.json` matches
`docs/catalog/schemas/MODULE_REGISTRY.schema.json` shape
(`schemaVersion, projectName, updatedAt, claimBoundary, modules`), `modules`
is `[]`, and `claimBoundary` states no status may represent plan-only intent.
No `GC-xxx` control token or module dependency is introduced.

**G2-AC-10 — Single canonical generator.** After migration, only
`scripts/manage_cvf_downstream_catalog.ps1 -Write` produces
`docs/INDEX.md` and `docs/catalog/MODULE_CATALOG.md`. `scripts/manage_catalog.py`'s
generator code paths for those two files are not invoked in any post-migration
workflow, script, or CI-equivalent step referenced by this repository's docs.

**G2-AC-11 — Competing writer resolved.** `scripts/manage_catalog.py` and
`tests/test_catalog_management.py` are either (a) deleted, with BUILD evidence
showing the Golden manager's `-Check` independently reproduces every guarantee
the retired test suite proved (schema closure, path existence, duplicate
id/path rejection, path-escape rejection, generated-view drift detection), or
(b) retained but marked `DEPRECATED`/excluded from any generation path, with
the same evidence recorded. No outcome is accepted without the evidence; "we
copied four files" alone does not satisfy this criterion.

**G2-AC-12 — Generated views byte-match.** `docs/INDEX.md` and
`docs/catalog/MODULE_CATALOG.md` on disk are byte-identical to what
`scripts/manage_cvf_downstream_catalog.ps1 -Write` renders from the migrated
registries (verified by running `-Check` immediately after `-Write` with no
diff).

**G2-AC-13 — Positive check PASS.** `scripts/manage_cvf_downstream_catalog.ps1
-Check` exits 0 with `[PASS]` against the final registries and views.

**G2-AC-14 — Negative fail-closed tests.** A negative-test evidence set (new
or adapted test file within the BUILD ceiling) demonstrates the manager
rejects, one scenario at a time, restored from a passing baseline each time:
unknown top-level or entry field; invalid `status`/`family` value; a missing
mandatory baseline entry (or one with a wrong path); duplicate `id`; duplicate
`path`; a path using `..`, a leading `/`, a drive letter, or a backslash;
a `MODULE_REGISTRY.json` entry with a plan-only status (e.g. `PLANNED`); a
module entry missing `evidence`; an unknown `GC-xxx` control token or unknown
module `dependencies` id; and a hand-edited `docs/INDEX.md` or
`docs/catalog/MODULE_CATALOG.md` that no longer matches the rendered output.

**G2-AC-15 — F0 provenance untouched.** Every path and content hash under
`provenance/shift-operations/`, `scripts/source_intake/`,
`tests/source_intake/`, and `docs/architecture/` is byte-identical before and
after this tranche (`git diff` empty for those paths).

**G2-AC-16 — No excluded-path writes.** `git status`/`git diff --stat` for the
full tranche show zero changes under `apps/`, `packages/`, `database/`,
`provenance/shift-operations/`, `docs/roadmaps/`, `.github/`, or any path
outside `OW-G2-WO-001`'s changed-set ceiling.

**G2-AC-17 — Full existing test suite PASS.** `python -m unittest discover -s
tests -p "test_*.py"` passes at the same or higher count than the pre-tranche
104 (93 F0 + 11 G1), accounting for any tests retired under G2-AC-11 with
recorded rationale.

**G2-AC-18 — Workspace doctor PASS.** Project-scoped
`check_cvf_workspace_agent_enforcement.ps1 -ProjectPath <this project>`
reports PASS with the governed downstream catalog kit complete (no
`DAMAGED_GOVERNED_KIT`, no `MIGRATION_REQUIRED`, no `LEGACY_PROJECT` note).

**G2-AC-19 — Continuity/status drift closed.** `docs/CVF_BOOTSTRAP_LOG_20260723.md`,
`AGENTS.md`, `IMPLEMENTATION_STATUS.json`, and `CVF_SESSION` continuity
surfaces show no stale reference to the old core pin
(`6ce1cf00c31a7f825d4c3fa3e66e8a3509e4a4b2`) or the old catalog schema after
FREEZE.

**G2-AC-20 — No secret/provider exposure.** No file touched by this tranche
contains an API key, token, or `.env`-sourced value; no live provider API call
is made or required to satisfy any criterion above.

**G2-AC-21 — Diff hygiene.** `git diff --check` reports no whitespace errors;
no `__pycache__` or other generated cache path is staged; the total changed
set is a subset of `OW-G2-WO-001`'s ceiling.

**G2-AC-22 — Rollback rehearsal.** Each BUILD commit (per `OW-G2-WO-001`'s
C1/C2/C3 plan) is rehearsed post-commit/pre-push in a temporary sibling git
worktree by Codex acting as COMMIT_STEWARD — this criterion is not satisfied
by Claude and is not exercised during this authorization round.

## Out of scope for this spec

- Any change to `docs/roadmaps/**`.
- Any runtime module implementation, import, or `MODULE_REGISTRY.json` entry.
- Any change to CVF core.
- Any live provider call.

## Verification commands (for BUILD, not this round)

```powershell
git -C ../.Controlled-Vibe-Framework-CVF rev-parse HEAD origin/main
powershell -ExecutionPolicy Bypass -File scripts/manage_cvf_downstream_catalog.ps1 -Check
powershell -ExecutionPolicy Bypass -File scripts/manage_cvf_downstream_catalog.ps1 -Write
powershell -ExecutionPolicy Bypass -File scripts/manage_cvf_downstream_catalog.ps1 -Check
python -m unittest discover -s tests -p "test_*.py"
powershell -ExecutionPolicy Bypass -File ../.Controlled-Vibe-Framework-CVF/scripts/check_cvf_workspace_agent_enforcement.ps1 -ProjectPath .
git diff --check
```

## Claim boundary

Satisfying every criterion above proves catalog/pin reconciliation and
doctor PASS. It does not prove runtime governance behavior, does not
authorize roadmap work, and does not by itself constitute BUILD — BUILD
requires the separately authorized `OW-G2-WO-001`.
