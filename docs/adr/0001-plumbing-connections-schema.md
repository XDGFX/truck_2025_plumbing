# ADR 0001: Plumbing Connections Schema and Resolution Rules

- Status: Accepted
- Date: 2026-05-28
- Context: Truck 2025 plumbing diagram model in `generate_all.py`

## Decision

Adopt WireViz-style `connections` chains as the preferred authored connectivity syntax for plumbing diagrams, with strict validation and deterministic defaulting rules.

### Locked Rules

1. Components require `label` and at least one of `ports` or `portcount`.
2. `ports` accepts either string-list or object-list input; normalise internally to object format.
3. If both `ports` and `portcount` exist, they must agree (`portcount == len(ports)`), and `ports` is authoritative.
4. Numeric ports are 1-based.
5. In any token, at most one port may be specified; multi-port token syntax is invalid.
6. In direct component-to-component hops, either side may omit a port and defaults to the first port.
7. `connections` chains are validated hop-by-hop and must have at least two tokens.
8. Allowed adjacent hop types: component↔component and component↔pipe. Pipe↔pipe is invalid.
9. All pipe types are declared under `pipes`.
10. Pipe references in chains are shorthand for unique unnamed pipe instances per usage.
11. Pipe ports default to first port when omitted.
12. Component instance forms are supported:
    - `component:[port]` base identity
    - `component.name:[port]` named instance
    - `component.:[port]` unnamed one-time instance
13. Port selection rules are independent of component instance form.

## Compatibility

- Keep accepting legacy `edges` during migration.
- Prefer `connections` for new authored diagrams.

## Implementation Handoff

Future implementation should:

1. Parse `connections` into adjacent validated hops.
2. Resolve component and pipe tokens using the rules above.
3. Instantiate a unique unnamed pipe node per pipe usage.
4. Enforce validation in `validate_diagram()` before DOT rendering.
5. Keep rendering behaviour where edges anchor to explicit node ports.

## Consequences

- Authoring stays concise but deterministic.
- Validation errors become earlier and clearer.
- Migration can be incremental due to `edges` compatibility.
