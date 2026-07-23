# ADR — Greenfield Platform and Governed Profile Porting

- ADR ID: `ADR-OW-001`
- Date: 2026-07-23
- Status: ACCEPTED_FOR_PLANNING
- Decision owner: repository owner
- Risk: R2

## Context

`CVF-Operations-Workspace` now exists as a clean CVF-governed repository.
`shift-operations-workspace` is a mature but incomplete Shift-specific product
with reusable operational primitives, tests and governance integration. A
review bundle proposed renaming that repository and extracting a platform in
place. The owner instead chose a larger greenfield foundation.

## Decision

Build the platform in the new repository. Keep Shift Operations as the first
profile and MVP proof, but port only source-verified assets through bounded
work orders.

The target dependency direction is:

```text
Applications -> Profiles -> Workspace Core -> Shared Contracts
Profiles -> Capability Interfaces <- Provider Adapters
Protected Command -> CVF Gates -> Profile Handler -> Ledger -> Audit
```

Forbidden directions include:

```text
Core -> Profile
Core -> Provider
Profile -> Provider implementation
Provider/channel/live-view -> protected domain mutation
Profile A -> Profile B business logic
```

CVF remains the root governance authority. The application may implement a
runtime integration layer, but must not fork CVF doctrine or silently replace
live provider-backed governance evidence with mocks.

## Repository ownership

- `CVF-Operations-Workspace` owns the platform, shared contracts, profile
  registration, reusable capabilities and integrated applications.
- `shift-operations-workspace` remains source authority for its existing
  implementation until an explicit asset is accepted into this repository.
- Accepted assets gain new ownership only after provenance, tests and review
  are committed here.
- The review bundle is design input, never runtime or continuity authority.

## Porting policy

Every candidate asset receives exactly one disposition:

| Disposition | Meaning |
|---|---|
| `PORT_AS_IS` | Identical source is justified and retains behavior |
| `ADAPT` | Reuse with documented target-boundary changes |
| `REIMPLEMENT` | Contract/behavior is retained but source is rewritten |
| `REFERENCE_ONLY` | Useful documentation or evidence, not imported source |
| `REJECT` | Unsafe, stale, generated, secret-bearing, or architecturally wrong |

No batch folder move is allowed. Database migrations and history-bearing data
require dedicated compatibility and rollback work orders.

## Product sequencing

The Shift profile must prove Workspace Core abstractions before a second
profile expands them. Agent Operations may begin with discovery and contracts
only after the Shift MVP baseline is credible. Live View and Human Takeover
require a separate security ADR and cannot be implied by the platform name.

## Consequences

Positive:

- no risky rename or coupled history migration;
- clean ownership and claim boundaries;
- Shift remains operational while the platform matures;
- abstractions must earn reuse through a real first profile.

Costs:

- temporary duplication may exist during controlled porting;
- compatibility evidence must be maintained across repositories;
- source provenance and license checks add work to each tranche;
- cutover occurs later and requires an explicit owner decision.

## Rejected alternatives

1. Rename the Shift repository: rejected by owner decision and already
   superseded by creation of the new repository.
2. Copy the entire Shift tree: rejected because it imports stale continuity,
   incomplete modules and Shift-specific coupling as platform truth.
3. Build an abstract core without a Shift vertical: rejected as premature.
4. Start Agent Operations or Human Takeover first: rejected because the shared
   kernel and control ownership model are not yet proven.

## Gate

This ADR authorizes planning and work-order construction only. BUILD begins
only after the active work order is independently reviewed and authorized.
