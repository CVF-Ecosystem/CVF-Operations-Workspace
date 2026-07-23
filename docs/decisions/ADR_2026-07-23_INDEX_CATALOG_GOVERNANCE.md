# ADR — Machine-Governed Documentation Index and Module Catalog

- ADR ID: `ADR-OW-002`
- Date: 2026-07-23
- Status: ACCEPTED
- Risk: R1 repository governance

## Decision

The repository will maintain two distinct machine sources:

1. `docs/catalog/ARTIFACT_REGISTRY.json` owns discoverability and generates
   `docs/INDEX.md`.
2. `docs/catalog/MODULE_REGISTRY.json` owns implementation claims and generates
   `docs/catalog/MODULE_CATALOG.md`.

Both registries are schema-backed and verified by one standard-library Python
tool. Generated Markdown is never edited by hand.

## Rationale

Documentation authority and runtime implementation truth are related but not
identical. A roadmap may be active while its modules are still planned; a
module may be enforced while historical work orders remain archived. Separate
registries prevent either surface from overstating the other.

## Required properties

- unique stable IDs and repository-relative POSIX paths;
- controlled status and type vocabularies;
- existing-path and relationship validation;
- module dependency and CVF-control validation;
- computed source metrics rather than hand-entered counts;
- deterministic generation and a non-mutating `--check` mode;
- explicit claim boundaries in generated output;
- negative tests proving drift and invalid records fail closed.

## Consequences

Every governed artifact is registered when it becomes authoritative or active.
Every module claim is updated only with source/test evidence. Plans never create
module entries merely to make a target architecture look implemented.

## Claim boundary

This decision governs repository metadata. It does not prove CVF runtime
behavior and therefore does not substitute for live provider-backed evidence.
