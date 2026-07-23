# Platform Boundary and Porting Rules

- Status: `active`
- Produced by: `OW-F0-WO-001` (F0 Source Intake and Compatibility Baseline)
- Implements: `ADR-OW-001` dependency-direction and porting-policy sections
- Scope: how F0's import ledger classifies candidates, and what rules any
  future F1+ import work order must respect when it actually moves source

This document restates `ADR-OW-001`'s architecture boundary as concrete,
checkable rules, and records exactly how F0's own tooling used them to build
the import ledger in `provenance/shift-operations/<commit>/import_ledger.json`.
It does not itself authorize any import; only a dedicated F1+ work order can
change a candidate's disposition to `PORT_AS_IS`, `ADAPT` or `REIMPLEMENT`.

## 1. Dependency direction

```text
Applications -> Profiles -> Workspace Core -> Shared Contracts
Profiles -> Capability Interfaces <- Provider Adapters
Protected Command -> CVF Gates -> Profile Handler -> Ledger -> Audit
```

Forbidden:

```text
Core -> Profile
Core -> Provider
Profile -> Provider implementation
Provider/channel/live-view -> protected domain mutation
Profile A -> Profile B business logic
```

Any F1+ work order that ports source must show, with an architecture test,
that the ported code does not introduce a forbidden edge. F0's own
`dependency_graph.json` records the *source* repository's real import edges
today (evidence), not a claim about the target.

## 2. Disposition vocabulary

Exactly five dispositions exist. F0's rule engine (`scripts/source_intake/ledger.py`)
only ever assigns two of them; the other three require a human/reviewer
decision in a dedicated future work order, never a default:

| Disposition | Meaning | Who may assign it |
|---|---|---|
| `PORT_AS_IS` | Identical source is justified and retains behavior | F1+ work order only |
| `ADAPT` | Reuse with documented target-boundary changes | F1+ work order only |
| `REIMPLEMENT` | Contract/behavior retained, source rewritten | F1+ work order only |
| `REFERENCE_ONLY` | Useful evidence/documentation, not imported source | F0 default for real, reviewable content |
| `REJECT` | Unsafe, stale, generated, secret-bearing, binary, or unclassifiable | F0 default catch-all and binary rule |

## 3. F0's own classification rules

F0 assigns a disposition per Git-tracked, non-excluded source file using
`candidate_class` (from `scripts/source_intake/inventory.py::classify`):

| `candidate_class` | Default disposition | Rationale summary |
|---|---|---|
| `database_migration` | `REFERENCE_ONLY` | Requires a dedicated compatibility/rollback work order (ADR-OW-001) |
| `test_code` | `REFERENCE_ONLY` | Only meaningful alongside the implementation it verifies |
| `contract_or_schema` | `REFERENCE_ONLY` | Batch folder moves are forbidden; needs independent authorship review |
| `application_code` / `package_code` | `REFERENCE_ONLY` | F0 makes no import decision; candidate for a future F1+ work order |
| `configuration` | `REFERENCE_ONLY` | Must be authored fresh for this repository's own dependency/CI identity |
| `documentation` / `ci_or_governance` | `REFERENCE_ONLY` | Retained as reference input, not source code |
| `lock_or_dependency_manifest` | `REFERENCE_ONLY` | Informative only |
| any binary file | `REJECT` | No text-diff provenance value for F0 |
| `other` (no matching rule) | `REJECT` | Default-safe rejection pending explicit reviewer classification |

Every row also carries `review_status: PENDING_REVIEWER` — F0 never
self-approves a disposition, and none of the above defaults are a
recommendation to import; they are a conservative floor a reviewer can
raise, never a ceiling F0 imposes on the reviewer.

## 4. What must never be renamed or altered while porting

Carried forward from `ADR-OW-001` / the prior review bundle's impact
analysis, because these identifiers are load-bearing across the API,
database, and domain layer of the source repository:

- `shifts` API route family, `shift_id`, `shift_status` enum, `shifts` table;
- Shift domain classes and their current Python import package names;
- current Docker database/volume identity;
- historical migration filenames and their SHA-256 hashes.

## 5. What this document does not do

- It does not import, adapt, or reimplement anything.
- It does not promote any module in this repository's Module Registry
  (which remains empty; see `docs/catalog/MODULE_REGISTRY.json`).
- It does not decide the eventual home (core/profile/capability) of any
  Shift asset; that is F1's job, informed by this ledger.

## Claim boundary

This document defines the rules F0's ledger followed and the rules a future
F1+ import work order must respect. It is not evidence that any asset has
been ported, and it is not itself a work order.
