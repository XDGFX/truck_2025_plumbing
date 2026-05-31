# ADR 0002: Unused Tank Ports Modelled as Connected Bung Components

- Status: Accepted
- Date: 2026-05-31
- Context: Truck 2025 plumbing diagram authoring conventions

## Decision

Every unused tank port must be explicitly connected to a bung component in the diagram. Ports must never be silently omitted on the grounds that nothing flows through them.

## Rationale

A bung is a purchased part. It must appear in the BOM. A port without a connection provides no information about whether the port is blanked, capped, or simply forgotten — diagrams are used for sourcing and installation, not just flow tracing.

## Consequences

- All tank component definitions include all physical ports, not just the connected ones.
- `bung_3_4_bsp` (and equivalent bung sizes) are defined in `shared.yml` as first-class fitting components.
- A diagram with an unconnected port is treated as incomplete, not as "port is unused."

## Alternatives Rejected

**Omit unused ports from the component definition** — loses physical accuracy and breaks BOM completeness. A future reader cannot tell whether the port exists or was simply not needed.

**Comment unused ports** — YAML comments are not processed; they do not appear in generated output or BOMs.
