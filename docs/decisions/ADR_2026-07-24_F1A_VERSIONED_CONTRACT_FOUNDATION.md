# ADR — F1A Versioned Contract Foundation

- ADR ID: `ADR-OW-005`
- Date: 2026-07-24
- Status: ACCEPTED_FOR_PLANNING
- Decision owner: repository owner
- Risk: R2

## Repair note (round 1, 2026-07-24)

Independent Codex review returned `F1A_AUTHORIZATION_REVIEW_FAIL` with five
findings, all repaired in this round without waiver:

- **F1A-R1 — INCOMPLETE_HASH_LOCK_STRATEGY.** Decision 12 originally claimed
  `requirements-contract-validator.txt` would contain "one package" and that
  "`jsonschema` has no other dependency." Both claims were false and are
  removed. Decision 12 is rewritten with the real, tested, exact-version,
  hash-verified 19-package transitive closure (`jsonschema[format-nongpl]==4.26.0`
  plus 18 dependencies), an exact supported interpreter/platform, and an
  isolated-environment/`--require-hashes` install policy.
- **F1A-R2 — SEMVER_CONTRACT_CONTRADICTION.** Decision 3 called the version
  grammar "full SemVer 2.0.0"; Decision 6's regex did not actually enforce
  that grammar (it permitted leading zeroes and said nothing about
  prerelease/build-metadata suffixes). Both are corrected to a single,
  narrower, consistently-applied stable-release grammar.
- **F1A-R3 — TIMESTAMP_FORMAT_ASSERTION_GAP.** Decision 6 falsely claimed the
  timestamp regex alone "guarantees rejection of malformed timestamps
  regardless of validator configuration." Tested live this round: bare
  `jsonschema` (no `format`/`format-nongpl` extra) does not even register a
  `date-time` format checker (`'date-time' in FormatChecker().checkers` is
  `False`), so format assertion is silently a no-op without the extra; and
  the regex by itself, being purely structural, accepts calendar-impossible
  strings like `2026-13-40T25:00:00Z` and `2026-02-30T10:00:00Z`. Corrected:
  `jsonschema[format-nongpl]` (Decision 12) plus mandatory `FormatChecker`
  use is now the semantic proof; the regex is restated as defense-in-depth
  only.
- **F1A-R4 — OPAQUE_BOUNDARY_CLAIM_UNENFORCED.** Decision 5 claimed the
  `metadata`/`payload` opaque fields "cannot carry any contract-owned field
  name" — unenforceable by a `type: object` schema with no nested
  `additionalProperties: false`, since JSON Schema cannot forbid a specific
  key inside an intentionally-open object without closing it. Corrected to
  the bounded rule Codex specified: nested keys may share a name with a
  top-level field; they never override or bypass the top-level field's own
  validation.
- **F1A-R5 — NONDETERMINISTIC_MODULE_REGISTRY_ENTRY.** `OW-F1A-WO-001`'s
  Module Registry section said "something like" before an illustrative
  entry. Replaced with the exact authorized entry, verbatim, no
  discretion left to BUILD.

Repaired exactly the six paths this round's ceiling permits; no seventh
path. No `contracts/**`, `tests/**`, requirements file, catalog, Index,
roadmap, source, script, core-pin, or runtime path was touched. No BUILD
occurred. Role: `REPAIR_WORKER` (Claude, provider-neutral role contract).
Codex retains independent `REVIEWER`/`COMMIT_STEWARD` authority; this round
does not self-grant REVIEW_PASS.

## Repair note (round 2, 2026-07-24)

Independent Codex re-review verified `F1A-R1` through `F1A-R5` closed (19
wheels/hashes independently reproduced and matched exactly; `FormatChecker`
`date-time` activation and invalid-month/day/hour rejection independently
confirmed). One finding remained, repaired here without waiver:

- **F1A-R6 — VALIDATOR_WHEEL_PORTABILITY_COUNT_CONTRADICTION.** Decision
  12 said "17 of the 19 wheels are pure-Python ... the sole exception is
  `rpds-py`" — arithmetically wrong (19 − 1 = 18). Corrected to: "18 of the
  19 wheels are pure-Python (`py3-none-any` or `py2.py3-none-any`). The sole
  platform/interpreter-specific exception is `rpds-py`, whose authorized
  wheel is `rpds_py-2026.6.3-cp313-cp313-win_amd64.whl`." Nothing else in
  Decision 12 — package table, versions, hashes, supported platform,
  dependency/install policy — changed.

`F1A-R1`–`F1A-R5` and round 1's history are preserved unchanged and remain
closed. No SemVer, `FormatChecker`, opaque-boundary, Module Registry,
acceptance-criteria, or BUILD-ceiling content changed this round.
`OW-F1A-SPEC-001`/`OW-F1A-WO-001` never repeated the "17 of 19" figure and
are unchanged. Repaired this ADR plus the three continuity/status
files — still the same six-path total ceiling, no seventh path; no
`contracts/**`, `tests/**`, requirements file, catalog, Index, roadmap,
source, script, core-pin, or runtime path touched; no BUILD occurred. Role:
`REPAIR_WORKER`; Codex retains independent `REVIEWER`/`COMMIT_STEWARD`
authority; no self-granted REVIEW_PASS. Status:
`REPAIRED_PENDING_INDEPENDENT_RE_REVIEW_2`. Next move: Codex re-reviews this
single arithmetic correction.

## Context

`docs/roadmaps/CVF_OPERATIONS_WORKSPACE_ROADMAP.md` names `F1A — Versioned
closed contracts` as the next candidate tranche after G0/G1/F0/G2/RM1, all of
which are complete, independently REVIEW_PASS'd, and FREEZE'd. The roadmap
explicitly states naming F1A is planning only and does not authorize its
BUILD (`RM1-AC-06`, "Near-term execution queue"). This ADR opens that
authorization round.

F1A's job is to define the first versioned, closed JSON Schema contracts that
every later platform tranche (F1B `OperationalSession` runtime, F1C profile
registry, F1D governed command pipeline, F1E architecture enforcement, and
F2's Shift compatibility MVP) depends on. No runtime, database, API route, or
provider behavior is authorized by this ADR.

## Verified input truth (this round)

- Target `CVF-Operations-Workspace`: HEAD = `origin/main` =
  `a9c2505c0ff21df8600e5944383f6c04293eb2f4`, worktree clean.
- CVF core: HEAD = `origin/main` = `27137db4d9aa2aea931ddd2507185d5c24943080`,
  worktree clean, matching `.cvf/manifest.json`'s `cvfCoreCommit`.
- `docs/catalog/MODULE_REGISTRY.json`: `modules: []` — empty, confirmed by
  reading the file.
- 116/116 tests pass (`python -m unittest discover -s tests -p "test_*.py"`,
  reproduced this round).
- Shift source (`shift-operations-workspace`, read-only source evidence): pin
  `f98f29e145fa002be070e9d44520d20f0f82dcb3`. This repository is a Pydantic/
  FastAPI application, not a JSON Schema contract source — F0's import ledger
  contains no `contracts/*.schema.json`-shaped candidate from it. It is cited
  here only for baseline identity, not as a contract design input.
- `operations-workspace-all-phases/contracts/**` (read-only ADAPT design
  input, per `docs/reviews/OPERATIONS_WORKSPACE_ALL_PHASES_LEARNING_ASSESSMENT_2026-07-23.md`,
  "`contracts/` — versioned schema examples (15) — all `adapt`"): 15 schema
  files under `contracts/core/` (6), `contracts/agent-operations/` (6), and
  `contracts/live-view/` (3). Only the 5 files named in Decision 9 below are
  in scope for F1A; `agent-operations/**` and `live-view/**` belong to F5/F6
  per the roadmap and are not read further by this round.
- The 6 `contracts/core/` design-input files were read in full. Observed
  shape: JSON Schema draft 2020-12 (`$schema:
  https://json-schema.org/draft/2020-12/schema`), `additionalProperties:
  false` at the top level, flat objects, no `$id`, no `$ref`, no shared
  definitions file — every reusable shape (identifier, timestamp) is
  duplicated inline across files.
- This repository has no `pyproject.toml`, `requirements*.txt`, or
  `setup.py`; Python `jsonschema` is not installed
  (`ModuleNotFoundError: No module named 'jsonschema'`, reproduced this
  round). This is the validator dependency gap the roadmap and this
  authorization round must resolve.

## Correction to a prior claim boundary

`docs/architecture/PLATFORM_BOUNDARY_AND_PORTING_RULES.md`'s disposition
table lists `contract_or_schema` candidates as `REFERENCE_ONLY` under F0's own
rule engine, "requires independent authorship review" — consistent with
`ADR-OW-001`'s porting policy that `ADAPT` never means copy. This ADR does not
change that table; it exercises the "future F1+ import work order" it names,
for the `operations-workspace-all-phases/contracts/core/` design input only,
and decides to **author fresh contracts informed by, not copied from,** that
input, per the sections below.

## Decision

### 1. Canonical dialect and offline validation policy

**JSON Schema draft 2020-12** (`https://json-schema.org/draft/2020-12/schema`),
matching the design input's own dialect. Validation must be fully offline: the
Python `jsonschema` library (Decision 12) bundles the 2020-12 meta-schema and
vocabulary definitions as local package data, so meta-schema validation
(`F1A-AC-04`) requires no network call. No schema, test, or tool may fetch
`https://json-schema.org/...` at validation time; the `$schema` value is an
identifier only, never dereferenced live.

### 2. Stable `$id` / namespace convention

The design input has no `$id` at all. This round assigns a **URN** scheme,
not an `http(s)://` URL, specifically so no `$id` can be misread as something
requiring network resolution:

```text
urn:cvf-operations-workspace:contracts:core:<schema-name>:v<major>
```

Example: `urn:cvf-operations-workspace:contracts:core:profile-manifest:v1`.
The major version is embedded in the `$id` itself (Decision 3/4): a future
breaking change mints a new `$id` (`...:v2`) and a new file; it never mutates
`v1` in place.

### 3. Initial contract version and semantic-version policy

Every F1A schema starts at **`1.0.0`**. The grammar is deliberately narrower
than full SemVer 2.0.0 (`ADR-OW-005` repair round 1, `F1A-R2`): a **stable
MAJOR.MINOR.PATCH triplet only** — no prerelease suffix (`-alpha`, `-rc.1`),
no build-metadata suffix (`+build`), and no leading zeroes in any component
except the value zero itself. The exact grammar (also Decision 6's `semver`
definition, restated here for this decision's own clarity) is:

```regex
^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$
```

Policy:

- **MAJOR** — any breaking change: a removed/renamed required property, a
  narrowed type, a removed enum value, a new required property with no
  default, or any change that would reject a previously-valid instance.
- **MINOR** — an additive, backward-compatible change (e.g. a new optional
  property). Never silent or automatic — Decision 4 below requires the same
  authorization chain as a new schema.
- **PATCH** — a non-semantic fix (description text, formatting, comment)
  that changes no validation behavior. Verified by asserting the schema's
  validation behavior against a fixed instance corpus is byte-for-byte
  unchanged.

### 4. Compatibility rules

- **Released versions are immutable.** Once a schema file's version has
  passed independent REVIEW_PASS and FREEZE, its bytes are never edited in
  place; git history and the FREEZE receipt are the immutability proof.
- **Breaking changes require a new version.** A MAJOR bump creates a new
  file and a new `$id` (`v<n+1>`); the prior version's file is retained,
  untouched, alongside it.
- **Additive changes require explicit compatibility review.** A MINOR bump
  is never silent: it requires its own `INTAKE -> DESIGN -> SPEC ->
  WORK_ORDER` authorization round, exactly like a new contract, before BUILD.
- **No silent schema replacement.** Any change to a released schema file's
  bytes without a recorded version bump and a fresh authorization round is a
  stop condition (`SILENT_SCHEMA_REPLACEMENT`), not a permitted repair.

### 5. Closed-world semantics

Every F1A schema sets `"additionalProperties": false` at the top level and at
every nested contract-owned object (e.g. `OperationalSession.ownership`,
Decision 7). Exactly **two** intentionally opaque extension points exist,
each named, bounded, and justified — no other property anywhere in the F1A
set is open:

| Field | Schema | Type | Justification | Bound |
|---|---|---|---|---|
| `metadata` | `operational-session` | `object` (required) | Session-level operator/profile annotations that do not affect lifecycle semantics | Must be an object (not a scalar/array) |
| `payload` | `command-envelope`, `event-envelope` | `object` (required) | Profile/capability-owned business content the shared envelope cannot know in advance | Same as above |

**Bounded rule (`ADR-OW-005` repair round 1, `F1A-R4` — corrects an
unenforceable claim in the original decision):** `metadata` and `payload`
are opaque *nested namespaces*. They may contain arbitrary nested keys,
including keys whose names happen to match a contract-owned top-level field
(e.g. `payload.state`, `metadata.version`). This is not a gap: a nested key
inside an opaque object **never overrides or bypasses** the corresponding
top-level field's own validation — the top-level `state`/`version`/etc.
property is still independently required, typed, and enum/format-checked by
the closed envelope around `metadata`/`payload`, regardless of what those
opaque objects contain. JSON Schema cannot forbid a specific key name inside
an intentionally-open object without closing it, so no version of this
decision claims that; what it claims, and what `F1A-AC-31` tests, is that
the opaque content is inert with respect to the closed envelope's own
fields.

This narrowing (naming and bounding the two opaque fields at all) is a
deliberate improvement over the design input, which left `metadata` and
`payload`-equivalent fields open with no stated justification, and left
`ownership` open with no shape at all (Decision 7 closes it).

### 6. Shared identifier, timestamp, and version formats

Defined once in `common-definitions.schema.json` (Decision 10) and referenced
everywhere via `$ref`, never redefined inline:

- **`identifier`** — `{"type": "string", "minLength": 1, "maxLength": 128,
  "pattern": "^[A-Za-z0-9][A-Za-z0-9_.-]*$"}`. Used for every `*_id` field
  and `idempotency_key`.
- **`slug`** — `{"type": "string", "minLength": 1, "maxLength": 128,
  "pattern": "^[a-z][a-z0-9]*(?:[-_][a-z0-9]+)*$"}`. Used for `action` and
  `event_type` (profile/capability-authored names, not system-generated
  instance ids).
- **`semver`** — `{"type": "string", "pattern":
  "^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)$"}` (`ADR-OW-005`
  repair round 1, `F1A-R2` — corrected from an earlier, looser pattern that
  neither forbade leading zeroes nor matched the "full SemVer 2.0.0" label
  Decision 3 had used). Rejects `01.0.0`, `1.01.0`, `1.0.01`, `1.0.0-alpha`,
  `1.0.0+build`; accepts `0.0.0` and `1.0.0`. Used for `profile_version` and
  `capability-manifest.version`.
- **`timestamp`** — `{"type": "string", "format": "date-time", "pattern":
  "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$"}`.
  **Corrected claim (`ADR-OW-005` repair round 1, `F1A-R3`):** the original
  decision falsely claimed this regex alone "guarantees rejection of
  malformed timestamps regardless of validator configuration." Tested live
  this round — it does not: the regex is purely structural (digit-count and
  separator shape only), so it *accepts* calendar-impossible strings such as
  `2026-13-40T25:00:00Z` (month 13, day 40, hour 25) and
  `2026-02-30T10:00:00Z` (February 30th). Semantic validity requires
  `jsonschema`'s `FormatChecker` — which, confirmed by direct import this
  round, is not even registered for `date-time` in bare `jsonschema`
  (`'date-time' in jsonschema.FormatChecker().checkers` is `False` without
  the `format`/`format-nongpl` extra). Corrected policy: every
  instance-validation code path in the BUILD test harness **must** construct
  its validator with `jsonschema.FormatChecker()` supplied (Decision 12 pins
  `jsonschema[format-nongpl]`, which provides the `rfc3339-validator`
  dependency `date-time` checking actually needs) — this is mandatory, not
  optional. The regex remains in the schema only as defense-in-depth (it
  still rejects gross structural malformation, e.g. a bare date with no
  time, before format checking runs), never as the semantic proof.
- **`riskClass`** — `{"enum": ["R0", "R1", "R2", "R3"]}`, reusing this
  repository's own established CVF risk vocabulary (`.cvf/policy.json`
  `riskCeiling`), not a new invented scale. Used for `command-envelope.risk_class`
  and `capability-manifest.risk_ceiling`.

### 7. Cross-contract identity invariants

- `profile_id` (`identifier`) and `profile_version` (`semver`) appear
  together, via the same shared `$ref`, in `profile-manifest`,
  `operational-session`, `command-envelope`, and `event-envelope`. Both are
  always required together — never one without the other.
- `session_id` (`identifier`) is the foreign reference from `command-envelope`
  and `event-envelope` to `operational-session.session_id`.
- Actor/principal identity: `principal_id` (`identifier`) on `command-envelope`.
  Contract-only — this ADR does not decide the authentication mechanism that
  resolves it (that is the P2-B boundary in `shift-operations-workspace`,
  read-only evidence only, or a future F2A work order in this repository).
- Correlation/causation and ordering (roadmap/spec requirement, absent from
  the design input): `event-envelope` gains three fields not present in the
  `operations-workspace-all-phases` design input: `correlation_id`
  (`identifier`, required — groups events from one causal chain),
  `causation_id` (`identifier`, nullable, required — the event/command that
  directly caused this one; `null` only for a root event), and `sequence`
  (`integer`, `minimum: 0`, required — a monotonic counter scoped to
  `session_id`, assigned by the future event store, giving deterministic
  ordering independent of clock skew).
- Expected-version semantics (roadmap/spec requirement, absent from the
  design input): `command-envelope` gains `expected_version` (`integer`,
  `minimum: 1`, nullable, required) — an optimistic-concurrency check against
  `operational-session.version`. `null` means the command does not target a
  versioned aggregate.
- **Honest limitation, stated plainly:** JSON Schema validates one document's
  shape at a time. It cannot enforce, by itself, that a real command's
  `profile_id`/`profile_version` actually matches a real session's — that is
  cross-document referential integrity, a runtime concern for F1B, not
  something a static schema can assert. F1A's claim is bounded to: (a) every
  contract that carries `profile_id`/`profile_version`/`session_id` uses the
  identical shared definition (a structural, schema-file-level test, not a
  runtime one), and (b) a test-only fixture-pair comparison (plain Python
  equality over two static JSON fixtures, shipped only inside the test
  suite, never as importable production code) proves the *shape* supports
  detecting a mismatch. This is not a claim that CVF enforces identity
  consistency at runtime.

### 8. Provider-neutrality

No property name, enum value, or example in any of the 5 F1A contracts names
Claude, Codex, OpenAI, Alibaba, Anthropic, or any other specific AI/agent
provider. `capability-manifest.provider_id` remains a free-form `identifier`
— an opaque handle the future capability registry resolves, never a
provider-name enum. Verified by a repository-scoped test that greps every
F1A schema file for a fixed list of known provider name tokens and fails on
any match.

### 9. Exact initial F1A contract set

Exactly **five** contract schemas, matching the roadmap's F1A deliverables
line ("profile-manifest schema, capability-interface schema,
`OperationalSession` contract schema, command/event/capability envelope
schemas") and the design input's own contract-scope rationale ("these schema
shapes directly inform F1A's ... scope: profile manifest, `OperationalSession`,
command/event/capability envelopes"):

1. **Profile manifest** (`profile-manifest`)
2. **`OperationalSession`** (`operational-session`)
3. **Command envelope** (`command-envelope`)
4. **Event envelope** (`event-envelope`)
5. **Capability interface/manifest** (`capability-manifest`)

`capability-invocation.schema.json` (design input) is explicitly **out of
scope** for F1A: it describes a runtime invocation record, which belongs with
F1D's governed command pipeline or F4's capability normalization, not the
closed contract foundation. `agent-operations/**` and `live-view/**` design
input (12 files) are out of scope per the roadmap's F5/F6 gating and are not
touched.

### 10. Shared definitions: standalone, not embedded

Unlike the design input (which duplicates inline shapes across all 6 files),
this round decides on a **standalone shared-definitions file**, referenced by
`$ref` (Decision 11), so a future format tightening happens in one place, not
five. Exact resulting file list (Decision 9 + this decision), all under
`contracts/core/`:

1. `common-definitions.schema.json` — `$defs`: `identifier`, `slug`,
   `semver`, `timestamp`, `riskClass`. Not itself an instance-validating
   contract (no `type: object` payload shape); referenced only.
2. `profile-manifest.schema.json`
3. `operational-session.schema.json`
4. `command-envelope.schema.json`
5. `event-envelope.schema.json`
6. `capability-manifest.schema.json`

Six files total — one more than the design input's five relevant files,
because of the new shared-definitions file.

### 11. Offline, deterministic `$ref` resolution

Every internal `$ref` targets `common-definitions.schema.json`'s `$defs` by
its stable `$id` and a JSON Pointer fragment, e.g.:

```text
"$ref": "urn:cvf-operations-workspace:contracts:core:common-definitions:v1#/$defs/identifier"
```

No `$ref` in any F1A schema may begin with `http://` or `https://`. The BUILD
test harness constructs an in-memory schema registry (`jsonschema`'s
`referencing.Registry`, or equivalent) from the six local files before
validating anything — never a live network fetch, at test time or otherwise.
A negative test scans every F1A schema file's raw text for an `http(s)://`
`$ref` value and fails the suite if one is found.

### 12. Validator/toolchain strategy

**Rewritten in full (`ADR-OW-005` repair round 1, `F1A-R1`).** The original
decision claimed `requirements-contract-validator.txt` would contain "one
package" and that "`jsonschema` has no other dependency." Both claims were
false — checked directly this round by resolving the real PyPI dependency
graph, not assumed — and are withdrawn.

**Why `jsonschema[format-nongpl]`, not bare `jsonschema`:** `F1A-R3`
(Decision 6) established that semantic timestamp validation requires
`jsonschema.FormatChecker` to actually register a `date-time` checker, which
bare `jsonschema` does not do — the `format-nongpl` extra is required to
pull in `rfc3339-validator` (and friends), avoiding the GPL-licensed
`rfc3987` that the plain `format` extra would pull in instead.

**The complete, tested transitive dependency closure — 19 packages, exact
versions, exact `sha256` hashes.** Resolved and verified live this round via
`pip download --no-deps <pkg>==<version>` for each package individually
(never trusting a single aggregate resolver run — see the method note
below) and `hashlib.sha256` computed directly over each downloaded wheel
file:

| # | Package | Version | Wheel | `sha256` |
|---|---|---|---|---|
| 1 | `jsonschema` | `4.26.0` | `jsonschema-4.26.0-py3-none-any.whl` | `d489f15263b8d200f8387e64b4c3a75f06629559fb73deb8fdfb525f2dab50ce` |
| 2 | `attrs` | `26.1.0` | `attrs-26.1.0-py3-none-any.whl` | `c647aa4a12dfbad9333ca4e71fe62ddc36f4e63b2d260a37a8b83d2f043ac309` |
| 3 | `jsonschema-specifications` | `2025.9.1` | `jsonschema_specifications-2025.9.1-py3-none-any.whl` | `98802fee3a11ee76ecaca44429fda8a41bff98b00a0f2838151b113f210cc6fe` |
| 4 | `referencing` | `0.37.0` | `referencing-0.37.0-py3-none-any.whl` | `381329a9f99628c9069361716891d34ad94af76e461dcb0335825aecc7692231` |
| 5 | `rpds-py` | `2026.6.3` | `rpds_py-2026.6.3-cp313-cp313-win_amd64.whl` | `9250a9a0a6fd4648b3f868da8d91a4c52b5811a62df58e753d50ae4454a36f80` |
| 6 | `fqdn` | `1.5.1` | `fqdn-1.5.1-py3-none-any.whl` | `3a179af3761e4df6eb2e026ff9e1a3033d3587bf980a0b1b2e1e5d08d7358014` |
| 7 | `idna` | `3.18` | `idna-3.18-py3-none-any.whl` | `7f952cbe720b688055e3f87de14f5c3e5fdaa8bc3928985c4077ca689de849a2` |
| 8 | `isoduration` | `20.11.0` | `isoduration-20.11.0-py3-none-any.whl` | `b2904c2a4228c3d44f409c8ae8e2370eb21a26f7ac2ec5446df141dde3452042` |
| 9 | `jsonpointer` | `3.1.1` | `jsonpointer-3.1.1-py3-none-any.whl` | `8ff8b95779d071ba472cf5bc913028df06031797532f08a7d5b602d8b2a488ca` |
| 10 | `rfc3339-validator` | `0.1.4` | `rfc3339_validator-0.1.4-py2.py3-none-any.whl` | `24f6ec1eda14ef823da9e36ec7113124b39c04d50a4d3d3a3c2859577e7791fa` |
| 11 | `rfc3986-validator` | `0.1.1` | `rfc3986_validator-0.1.1-py2.py3-none-any.whl` | `2f235c432ef459970b4306369336b9d5dbdda31b510ca1e327636e01f528bfa9` |
| 12 | `rfc3987-syntax` | `1.1.0` | `rfc3987_syntax-1.1.0-py3-none-any.whl` | `6c3d97604e4c5ce9f714898e05401a0445a641cfa276432b0a648c80856f6a3f` |
| 13 | `uri-template` | `1.3.0` | `uri_template-1.3.0-py3-none-any.whl` | `a44a133ea12d44a0c0f06d7d42a52d71282e77e2f937d8abd5655b8d56fc1363` |
| 14 | `webcolors` | `25.10.0` | `webcolors-25.10.0-py3-none-any.whl` | `032c727334856fc0b968f63daa252a1ac93d33db2f5267756623c210e57a4f1d` |
| 15 | `arrow` | `1.4.0` | `arrow-1.4.0-py3-none-any.whl` | `749f0769958ebdc79c173ff0b0670d59051a535fa26e8eba02953dc19eb43205` |
| 16 | `python-dateutil` | `2.9.0.post0` | `python_dateutil-2.9.0.post0-py2.py3-none-any.whl` | `a8b2bc7bffae282281c8140a97d3aa9c14da0b136dfe83f850eea9a5f7470427` |
| 17 | `six` | `1.17.0` | `six-1.17.0-py2.py3-none-any.whl` | `4721f391ed90541fddacab5acf947aa0d3dc7d27b2e1e8eda2be8970586c3274` |
| 18 | `tzdata` | `2026.3` | `tzdata-2026.3-py2.py3-none-any.whl` | `dc096730c87af6cab1b171c9d532be840741ff5d459015e7f6947bd7d7e54931` |
| 19 | `lark` | `1.3.1` | `lark-1.3.1-py3-none-any.whl` | `c629b661023a014c37da873b4ff58a817398d12635d3bbb2c5a03be7fe5d1e12` |

All 19 resolved to **wheels** for the supported combination below — no
source distribution was needed for any package, at this pin, on this
platform. `requirements-contract-validator.txt` (materialized at BUILD,
Decision unchanged: still one file) must list all 19 with `==` exact
version and a `--hash=sha256:<value>` line each, installed with
`pip install --require-hashes -r requirements-contract-validator.txt`.

**Exact supported interpreter/platform (not a platform-neutral lock).**
**Corrected count (`ADR-OW-005` repair round 2, `F1A-R6`):** 18 of the 19
wheels are pure-Python (`py3-none-any` or `py2.py3-none-any`). The sole
platform/interpreter-specific exception is `rpds-py`, whose authorized wheel
is `rpds_py-2026.6.3-cp313-cp313-win_amd64.whl` — and it is `jsonschema`'s
own hard dependency, so it alone pins the whole lock. This ADR authorizes
exactly one supported combination,
**CPython 3.13 on `win_amd64`** — matching this repository's verified BUILD
environment (`python --version` → `3.13.12`, Windows) — because that is the
only combination whose wheels and hashes were actually resolved and verified
this round. A different interpreter or OS at BUILD time requires a
different `rpds-py` wheel/hash and is out of this authorization's scope
(stop condition: dependency-resolution drift).

**Method note — a resolver pitfall found and avoided this round.** An
initial attempt used `pip install jsonschema[format-nongpl]==4.26.0 --dry-run --report=<file>`
as a single aggregate command; it reported only **17** packages, silently
omitting `idna` and `six` — both genuine runtime dependencies (of
`rfc3339-validator`/`fqdn` and of `python-dateutil`/`rfc3339-validator`
respectively) — because `--dry-run` resolves against the **currently
running** interpreter's environment and treats already-satisfied packages
as nothing-to-install, not against a clean target. This authoring
environment happened to already have both installed globally, for unrelated
reasons, which would have made the omission invisible without a
cross-check. **Corrected method:** a real `pip install --target <empty dir>`
into a fresh, empty directory (which does install every dependency
regardless of ambient state) was used to enumerate the true installed
`*.dist-info` set (19, not 17), and each of the 19 was then re-fetched
individually with `pip download --no-deps <pkg>==<version>` and hashed
directly with `hashlib.sha256`, independent of any resolver's
already-satisfied bookkeeping. **BUILD must use the same discipline** —
resolve and hash against a fresh/empty target, never trust a `--dry-run`
run in an environment that might already have some dependency installed —
and must stop (`dependency-resolution drift`) if it obtains a different
19-package closure, a different version, a missing wheel for the
authorized platform, or a hash mismatch against this table.

**Installation policy:**

- Every one of the 19 packages uses an exact `==` pin and a verified
  `sha256` hash — no floating range, no unpinned transitive dependency.
- Install with `pip install --require-hashes -r requirements-contract-validator.txt`
  into a **temporary, isolated virtual environment created solely for
  running the F1A contract test suite** — never the user/global Python
  environment, never another project's environment. The venv is disposable:
  created fresh for the test run and not treated as a persistent repository
  artifact.
- `--no-deps` is never used as a workaround to skip a hash mismatch or an
  unresolvable transitive dependency; if any of the 19 pins cannot be
  installed with hashes verified, BUILD stops.
- No package in this closure may fall back to a source build at the
  authorized pin/platform (confirmed: none does). If BUILD's own resolution
  requires a source build for any of the 19 at the authorized combination,
  BUILD stops (`source-build fallback`) rather than compiling from source
  silently.
- Every schema's meta-schema check
  (`jsonschema.validators.validator_for(schema)(schema).check_schema(schema)`,
  or equivalent) and every instance-validation call use the *locally
  installed* pinned package set — no network call at test-validation time.
  Only the one-time, disclosed `pip install --require-hashes` step touches
  the network, and it is recorded, not silent.
- **Evidence/provenance disclosure:** the package registry is the public
  Python Package Index (`pypi.org` / `files.pythonhosted.org`), queried via
  pip's standard resolver and `pip download`. This is a public package-registry
  read, not an AI/agent-provider call, and required no credentials — none
  were used or exposed. BUILD evidence must record the real command output
  (or an equivalent reproducible transcript) that produced this table, not
  merely restate it.
- **Not fabricated:** every version and hash above was independently
  downloaded and hashed this round, not invented; BUILD's job is to
  materialize `requirements-contract-validator.txt` from this exact table
  and reproduce the same hashes — "the exact dependency set is determined
  in authorization now; BUILD merely materializes and verifies the
  authorized lock," per the reviewer's own instruction.
- If any of the above cannot be reproduced identically at BUILD time (a
  different resolved package, version, missing wheel, or hash mismatch),
  BUILD stops with `BLOCKED_VALIDATOR_DEPENDENCY` rather than silently
  substituting a different lock or falling back to a hand-written partial
  checker presented as full JSON Schema validation.

This is not a general project packaging migration: no `pyproject.toml`,
build backend, or persistent virtual-environment tooling is introduced by
this decision; only the one pinned, hash-locked validator dependency closure
needed to test these six schema files honestly, installed into a disposable
environment for the duration of the test run.

## Consequences

Positive:

- Five contracts get one canonical, versioned, closed definition each,
  unblocking F1B/F1C/F1D/F1E and F2's compatibility MVP.
- The URN `$id` and standalone shared-definitions file prevent the
  drift-by-duplication the design input itself exhibited.
- A real (pinned, not hand-rolled) JSON Schema validator makes `F1A-AC-04`
  ("validates against its meta-schema") an honest claim instead of a
  structural approximation.
- Adding `correlation_id`/`causation_id`/`sequence`/`expected_version` now,
  rather than retrofitting them later, avoids an early breaking MAJOR bump.

Costs:

- A 19-package hash-pinned validator dependency closure (`jsonschema[format-nongpl]`
  and its transitive dependencies) where none existed, requiring a one-time,
  disclosed, isolated-environment install — larger than originally scoped,
  but now exact and verified rather than understated (repair round 1,
  `F1A-R1`).
- The design input's `capability-invocation` schema is deliberately not
  adopted yet, so capability invocation remains undefined until F1D/F4 —
  disclosed, not silently dropped.
- Cross-document identity consistency is not runtime-enforced by F1A; a
  future runtime tranche (F1B) still has to build that enforcement.

## Rejected alternatives

1. **Copy the 15 `operations-workspace-all-phases/contracts/**` files
   verbatim.** Rejected: `ADR-OW-001`'s porting policy and the learning
   assessment both classify these as `adapt`, never `adopt`; a batch folder
   copy is explicitly forbidden roadmap-wide.
2. **`http(s)://` `$id`/`$ref` namespace.** Rejected: even a non-dereferenced
   `https://` identifier invites a future accidental live fetch; URN removes
   the ambiguity structurally.
3. **Hand-written structural checker only, no `jsonschema` dependency.**
   Rejected: the task's own instruction forbids claiming full JSON Schema
   validation from a hand-written partial checker; a real validator is
   required to make `F1A-AC-04` honest.
4. **Leave `metadata`/`payload`/`ownership` fully open (as the design
   input does).** Rejected: violates closed-world semantics; opaque
   boundaries must be named and bounded, not left as blanket `object` types
   with no justification.
5. **Include `capability-invocation.schema.json` in F1A.** Rejected: it is a
   runtime invocation record, not a closed contract-only shape; including it
   would blur F1A's "contracts only, no runtime capability" claim boundary.
6. **Trust a single `pip install --dry-run --report` run as the complete
   transitive dependency closure (repair round 1).** Rejected: demonstrated
   this round to silently omit already-satisfied packages (`idna`, `six`)
   because it resolves against the currently running environment, not a
   clean target — exactly the kind of undetected drift `F1A-R1` was raised
   to prevent.
7. **Claim the timestamp regex alone proves RFC3339 validity (repair round
   1).** Rejected: demonstrated this round to accept calendar-impossible
   strings (`2026-13-40T25:00:00Z`, `2026-02-30T10:00:00Z`); real semantic
   proof requires `jsonschema.FormatChecker` with the `format-nongpl` extra
   installed.

## Gate

This ADR authorizes planning and work-order construction only. BUILD begins
only after `OW-F1A-SPEC-001` and `OW-F1A-WO-001` are independently reviewed
and authorized (Codex REVIEWER -> COMMIT_STEWARD), and after this
authorization package's own commit (C1) is rehearsed and pushed.
