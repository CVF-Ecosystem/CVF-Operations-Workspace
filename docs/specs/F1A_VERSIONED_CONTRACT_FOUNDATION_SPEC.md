# Spec — F1A Versioned Contract Foundation

- Spec ID: `OW-F1A-SPEC-001`
- Date: 2026-07-24
- Implements: `ADR-OW-005`
- Status: DRAFT (pending independent REVIEW_PASS)

## Repair note (round 1, 2026-07-24)

Independent Codex review returned `F1A_AUTHORIZATION_REVIEW_FAIL`
(`F1A-R1` through `F1A-R5`, see `ADR-OW-005`'s repair note for full detail).
This spec is repaired accordingly: `F1A-AC-10` (SemVer grammar) and
`F1A-AC-11` (timestamp/`FormatChecker`) are corrected in place; `F1A-AC-25`
now embeds the exact authorized Module Registry entry instead of an
illustrative one; `F1A-AC-30` and `F1A-AC-31` are added to bind
`F1A-R3`/`F1A-R4`'s new proof obligations. No other acceptance criterion's
substance changed. Role: `REPAIR_WORKER`. Codex retains independent
`REVIEWER`/`COMMIT_STEWARD` authority; this round does not self-grant
REVIEW_PASS.

## Purpose

Bind `ADR-OW-005`'s twelve decisions to testable acceptance criteria for a
future bounded BUILD. This spec claims no runtime, database, API, or
provider-governance behavior. It defines contracts only.

## Claim boundary (repeated from ADR — binding on all criteria below)

- Contracts only. No `OperationalSession` runtime state machine, no command
  execution, no governance enforcement, no provider behavior is implemented
  or claimed by satisfying these criteria.
- No live provider/AI call is required or made — F1A asserts schema
  behavior, not CVF control over AI/agent behavior.
- Architecture/dependency boundaries (`ADR-OW-001`,
  `docs/architecture/PLATFORM_BOUNDARY_AND_PORTING_RULES.md`) are unchanged.
- Cross-document referential integrity (e.g. a command's `profile_id`
  actually matching a real session's) is not enforced by these criteria —
  see `ADR-OW-005` Decision 7's stated limitation. `F1A-AC-19` below is
  scoped accordingly.

## Exact schema files and identifiers (`F1A-AC-01`)

All six files exist under `contracts/core/`, each with the `$id` named
below, dialect `https://json-schema.org/draft/2020-12/schema`:

| File | `$id` |
|---|---|
| `common-definitions.schema.json` | `urn:cvf-operations-workspace:contracts:core:common-definitions:v1` |
| `profile-manifest.schema.json` | `urn:cvf-operations-workspace:contracts:core:profile-manifest:v1` |
| `operational-session.schema.json` | `urn:cvf-operations-workspace:contracts:core:operational-session:v1` |
| `command-envelope.schema.json` | `urn:cvf-operations-workspace:contracts:core:command-envelope:v1` |
| `event-envelope.schema.json` | `urn:cvf-operations-workspace:contracts:core:event-envelope:v1` |
| `capability-manifest.schema.json` | `urn:cvf-operations-workspace:contracts:core:capability-manifest:v1` |

## Acceptance criteria

- **F1A-AC-01 — Exact file/identifier set.** The six files above exist at
  the stated paths, each with the stated `$id` and no other schema file
  exists under `contracts/`.
- **F1A-AC-02 — Dialect.** Every schema file's `$schema` value is exactly
  `https://json-schema.org/draft/2020-12/schema`.
- **F1A-AC-03 — Parses.** Every schema file is syntactically valid JSON
  (`json.load` succeeds) and syntactically valid JSON Schema (top-level
  `type: object` where applicable; `common-definitions.schema.json` is a
  `$defs`-only document).
- **F1A-AC-04 — Meta-schema validation.** Each of the six files validates
  successfully against the JSON Schema 2020-12 meta-schema, using the
  pinned `jsonschema` library's bundled, offline meta-schema (`ADR-OW-005`
  Decision 12) — not a hand-written approximation.
- **F1A-AC-05 — Offline `$ref` resolution.** Every `$ref` in every schema
  resolves against a registry built only from the six local files; no
  `$ref` value starts with `http://` or `https://` (verified by a text scan
  across all six files, not only the ones expected to contain one).
- **F1A-AC-06 — Positive instances validate.** At least one representative,
  fully-populated positive instance fixture exists per contract-owned
  schema (profile-manifest, operational-session, command-envelope,
  event-envelope, capability-manifest — 5 fixtures minimum) and validates
  successfully against its schema.
- **F1A-AC-07 — Negative: missing required fields.** For each of the 5
  contract-owned schemas, at least one negative fixture omitting a required
  property is rejected.
- **F1A-AC-08 — Negative: unknown contract-owned properties.** For each of
  the 5 contract-owned schemas, a negative fixture adding an unrecognized
  top-level property is rejected; additionally, a negative fixture adding an
  unrecognized property inside `operational-session.ownership` (a nested
  contract-owned object, not the opaque `metadata`/`payload` boundary) is
  rejected.
- **F1A-AC-09 — Negative: malformed identifiers.** A fixture with an
  `*_id` field violating the shared `identifier` pattern (e.g. containing a
  space or exceeding 128 characters) is rejected, for at least one field in
  at least two different schemas.
- **F1A-AC-10 — Negative/positive: stable-release semantic versions
  (corrected, `F1A-R2`).** `profile_version` and `capability-manifest.version`
  use the narrower stable-release grammar
  `^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$` (`ADR-OW-005`
  Decision 3/6) — not full SemVer 2.0.0. Fixtures with `"01.0.0"`,
  `"1.01.0"`, `"1.0.01"`, `"1.0.0-alpha"`, and `"1.0.0+build"` are each
  rejected; fixtures with `"0.0.0"` and `"1.0.0"` each validate.
- **F1A-AC-11 — Negative: invalid timestamps, `FormatChecker`-enforced
  (corrected, `F1A-R3`).** Every instance-validation code path in the test
  suite constructs its validator with `jsonschema.FormatChecker()` supplied
  (via the pinned `jsonschema[format-nongpl]` dependency, `ADR-OW-005`
  Decision 12) — never format-assertion-only or bare structural checking. A
  fixture with a timestamp field (`opened_at`, `requested_at`, `created_at`,
  etc.) that is not a well-formed RFC3339 date-time (e.g. a bare date with
  no time, or a non-date string) is rejected, for at least two different
  schemas. In addition, fixtures that are **structurally well-formed but
  calendrically impossible** — invalid month (e.g. `"2026-13-01T00:00:00Z"`),
  invalid day (e.g. `"2026-02-30T00:00:00Z"`), and invalid hour (e.g.
  `"2026-07-24T25:00:00Z"`) — are each rejected, across at least two
  different schemas. The regex in `ADR-OW-005` Decision 6 is defense-in-depth
  only; `FormatChecker` is what these calendrically-impossible cases prove.
- **F1A-AC-12 — Negative: invalid `OperationalSession` states.** A fixture
  with `state` set to a value outside `DRAFT`, `OPEN`, `ACTIVE`, `CLOSING`,
  `CLOSED`, `FROZEN` is rejected.
- **F1A-AC-13 — Negative: invalid `expected_version`.** A `command-envelope`
  fixture with `expected_version` set to `0`, a negative integer, or a
  non-integer is rejected; a fixture with `expected_version: null` validates
  (Decision 7 — `null` is a legal "no targeted aggregate" value).
- **F1A-AC-14 — Cross-contract identity consistency (test-only, bounded).**
  A test-only helper (never shipped outside the test suite) compares a
  representative `operational-session` fixture against a representative
  `command-envelope` fixture referencing it: a positive case where
  `profile_id`/`profile_version` match passes; a negative case where the
  command fixture's `profile_version` is mutated to a different value fails.
  This proves the shape supports detecting a mismatch; per the claim
  boundary above, it is not a runtime enforcement claim.
- **F1A-AC-15 — Negative: invalid capability declarations.** A
  `capability-manifest` fixture with `status` outside its enum, or with
  `allowed_profiles` containing a non-string, is rejected.
- **F1A-AC-16 — Profile manifest contract.** `profile-manifest.schema.json`
  requires `profile_id`, `profile_version`, `display_name`, `status`,
  `owned_aggregates`, `supported_session_types`, `commands`, `events`,
  `capability_dependencies`, `cvf_profile_extension`; `status` is a closed
  enum (`planned`, `contract-only`, `partial`, `pilot`, `frozen`).
- **F1A-AC-17 — `OperationalSession` contract.** `operational-session.schema.json`
  requires `session_id`, `workspace_id`, `profile_id`, `profile_version`,
  `title`, `state` (the six-value lifecycle enum above), `participant_references`,
  `opened_at`, `policy_profile_id`, `evidence_scope`, `metadata`, `version`
  (integer, `minimum: 1` — optimistic concurrency); `ownership` is nullable
  and, when present, is a closed object requiring `owner_principal_id` and
  `acquired_at`.
- **F1A-AC-18 — Command envelope contract.** `command-envelope.schema.json`
  requires `command_id`, `workspace_id`, `session_id`, `profile_id`,
  `profile_version`, `principal_id`, `action`, `risk_class` (closed
  `R0`–`R3` enum), `evidence_references`, `idempotency_key`, `requested_at`,
  `payload`, and `expected_version` (Decision 7, nullable).
- **F1A-AC-19 — Event envelope contract, correlation/causation/ordering.**
  `event-envelope.schema.json` requires `event_id`, `event_type`,
  `profile_id`, `profile_version`, `session_id`, `source`, `data_state`
  (closed enum: `RAW`, `NORMALIZED`, `PROPOSED`, `CONFIRMED`, `REJECTED`,
  `CORRECTED`, `FROZEN`), `evidence_references`, `created_by`, `created_at`,
  `payload`, `correlation_id`, `causation_id` (nullable), and `sequence`
  (integer, `minimum: 0`).
- **F1A-AC-20 — Capability interface/manifest contract.**
  `capability-manifest.schema.json` requires `capability_id`, `version`
  (`semver`), `provider_id`, `status` (closed enum: `stub`, `contract-only`,
  `partial`, `pilot`, `production`), `allowed_profiles`,
  `data_classification`, `required_permissions`, `risk_ceiling` (closed
  `R0`–`R3` enum), `cost_policy`, `termination_contract`, `input_schema`,
  `output_schema`.
- **F1A-AC-21 — Opaque boundaries cannot bypass top-level closure.** A
  `command-envelope` (or `event-envelope`) fixture with an unrecognized
  top-level property is rejected even though the same fixture's `payload`
  object may contain arbitrary nested properties.
- **F1A-AC-22 — No provider-specific fields.** A text scan of all six
  schema files finds no property name, enum value, or `const` matching a
  fixed list of known AI/agent provider tokens (`claude`, `anthropic`,
  `codex`, `openai`, `gpt`, `alibaba`, `qwen`, `gemini`).
- **F1A-AC-23 — Claim-boundary statement present.** Each of the five
  contract-owned schema files' companion test module states, in a
  docstring/comment or an assertion message, that the schema is
  contract-only and implies no runtime state machine, command execution,
  governance enforcement, or provider behavior.
- **F1A-AC-24 — Architecture/dependency boundaries unchanged.** `git diff`
  against `docs/architecture/PLATFORM_BOUNDARY_AND_PORTING_RULES.md` and
  `ADR-OW-001` is empty; no forbidden edge (`ADR-OW-001`) is introduced by
  the new `contracts/core/` package (it has no imports at all — it is JSON
  data, not code).
- **F1A-AC-25 — Module Registry registration boundary (exact entry,
  corrected `F1A-R5`).** If BUILD succeeds, exactly one new Module Registry
  entry may be added, and it must be byte-identical in content to:

  ```json
  {
    "id": "contracts-core-f1a",
    "name": "F1A Core Contract Foundation",
    "path": "contracts/core",
    "status": "CONTRACT_ONLY",
    "description": "Versioned closed JSON Schema contracts for the provider-neutral operations-workspace core; no runtime enforcement.",
    "evidence": "contracts/core/*.schema.json; tests/contracts/test_f1a_contracts.py; docs/reviews/F1A_BUILD_EVIDENCE_2026-07-24.md",
    "controls": [],
    "dependencies": []
  }
  ```

  No discretion is left to BUILD to phrase this entry differently. This
  entry may be added only after all F1A contract tests pass. Never
  `PARTIAL` or `ENFORCED`. If the Golden schema
  (`MODULE_REGISTRY.schema.json`) cannot represent this exact entry, BUILD
  stops rather than inventing a new status value or altering the entry's
  content.
- **F1A-AC-26 — Module Catalog generation only.** If the Module Registry
  changes, `docs/catalog/MODULE_CATALOG.md` is regenerated only via
  `scripts/manage_cvf_downstream_catalog.ps1 -Write`, never hand-edited.
  `docs/catalog/ARTIFACT_REGISTRY.json` and `docs/INDEX.md` remain unchanged
  unless a separately reviewed catalog requirement proves otherwise (the
  Golden Artifact Registry already discovers `docs/decisions/`, `docs/specs/`,
  `docs/work_orders/`, and `docs/reviews/` as registered folder families).
- **F1A-AC-27 — Existing suite still passes.** All 116 pre-existing tests
  continue to pass unmodified; new F1A tests are additive to, not a
  replacement of, that count.
- **F1A-AC-28 — Repository gates pass.** `python -m unittest discover -s
  tests -p "test_*.py"` passes (116 + N, N ≥ 1); `git diff --check` is
  clean; `scripts/manage_cvf_downstream_catalog.ps1 -Check` passes;
  project-scoped workspace doctor passes 25/25.
- **F1A-AC-29 — No live provider call.** No BUILD task under this spec
  invokes a real AI/agent provider API; F1A asserts schema behavior only,
  not CVF control over AI/agent behavior (`ADR-OW-005` claim boundary).
- **F1A-AC-30 — `FormatChecker` is actually supplied and load-bearing (new,
  `F1A-R3`).** A dedicated test asserts, by direct import, that
  `'date-time' in jsonschema.FormatChecker().checkers` is `True` in the
  pinned-dependency test environment (proving the `format-nongpl` extra is
  really installed and active, not silently absent as bare `jsonschema`
  would leave it) — and asserts that every validator constructed elsewhere
  in the suite passes a non-`None` `format_checker`. This test fails loudly
  if the validator dependency is ever installed without the `format-nongpl`
  extra, rather than letting `F1A-AC-11`'s format cases pass vacuously.
- **F1A-AC-31 — Opaque nested keys never bypass the closed envelope (new,
  `F1A-R4`, the bounded rule from `ADR-OW-005` Decision 5).** Three
  required cases:
  1. A fixture with arbitrary nested keys inside `metadata` (on
     `operational-session`) and inside `payload` (on `command-envelope` or
     `event-envelope`) validates successfully — opaque nested content is
     accepted, not rejected.
  2. The identical unknown key, moved to the **top level** of the same
     envelope (sibling to `metadata`/`payload`, not nested inside it), is
     rejected — proving closure is a top-level property, not a blanket
     permission granted by having an opaque field at all (this restates and
     extends `F1A-AC-21`).
  3. A fixture omitting the required top-level `state` field from
     `operational-session` but placing a key literally named `state` inside
     `metadata` (e.g. `metadata: {"state": "FROZEN"}`) is still rejected for
     missing top-level `state` — the nested key does not satisfy or
     override it. The same is checked for `version` (nested inside
     `metadata` vs. the required top-level `version`).

## Out of scope for this spec

- `capability-invocation.schema.json` and any `agent-operations/**` or
  `live-view/**` contract (`ADR-OW-005` Decision 9).
- Any `OperationalSession` runtime, profile registry runtime, command
  handler, provider adapter, database schema/migration, API route, or
  frontend change (all F1B+).
- Any change to `docs/roadmaps/CVF_OPERATIONS_WORKSPACE_ROADMAP.md`,
  `docs/catalog/ARTIFACT_REGISTRY.json`, `docs/INDEX.md`, `.cvf/manifest.json`,
  `AGENTS.md`, or either read-only input repository/folder.
- Reconciling the design input's `agent-operations/**`/`live-view/**`
  schemas at all — deferred to F5/F6 per the roadmap.

## Verification commands (for BUILD, not this authorization round)

```text
python -m unittest discover -s tests -p "test_*.py"
python -c "import json,glob; [json.load(open(f, encoding='utf-8')) for f in glob.glob('contracts/core/*.schema.json')]"
git diff --check
powershell -ExecutionPolicy Bypass -File scripts/manage_cvf_downstream_catalog.ps1 -Check
```

## Claim boundary

This spec binds acceptance criteria for a contracts-only BUILD. It makes no
runtime, database, API, provider, or governance-enforcement claim. Satisfying
every criterion above proves the six schema files are well-formed, closed,
versioned, offline-resolvable JSON Schema documents with representative
positive/negative test coverage — nothing more.
