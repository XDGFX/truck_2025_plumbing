# Context Glossary

## Strict Metadata
Required metadata fields are mandatory by definition and must always be present for valid diagram data.

## Optional Metadata
Optional metadata fields may be provided when available and omitted without invalidating diagram data.

## Component Required Metadata
Each component must include label and either ports or portcount.

## Component Optional Metadata
Component metadata such as manufacturer, model, description, sourcing, ratings, and notes is optional.

## Component Kind
`kind` is intentionally excluded from required metadata because it adds user overhead without enough value.

## Port Object Schema
`ports` is an array of objects, with `name` required.

## Portcount Alternative
Components may define portcount instead of ports. This is used when ports are referenced numerically.

## Ports And Portcount Together
`ports` and `portcount` may be provided together. At least one is required.

## Ports And Portcount Validation
When both are present, `portcount` must equal the number of entries in `ports`.

## Ports Precedence
When both are present and valid, `ports` is the source of truth for resolution.

## Numeric Port Indexing
Numeric port references are 1-based and must be in the range 1..portcount.

## Port Optional Metadata
Within each port object, `connection_size`, `gender`, and `service_rating` are optional.

## Port Format Compatibility
Both port formats are accepted: string list and object list. Inputs are normalised internally to object format.

## Port-Level Ratings
Connection size and service ratings are modeled at port level, not top-level component metadata.

## Pipe Optional Metadata
Pipe metadata such as material, size, length, service rating, description, notes, sourcing, and insulation is optional.

## Prepend File

An optional prepend file (default `shared.yml`) may be placed at the project root. When present, its `diagram`, `templates`, and `components` keys are merged before each diagram file is processed. It is project-specific and not a standard library — it is absent by default and the generator must not crash when it is missing.

## Direct Connection
Components may connect directly without an intermediate pipe when physical interfaces mate directly.

## Pipe-Mediated Connection
Connections may pass through explicit pipe runs and fittings between components, and these must be representable in the YAML model.

## Fittings As Components
Fittings are modeled as components, not as a separate type.

## Connectivity Syntax
Connectivity is expressed using WireViz-style `connections` chains rather than explicit `from`/`to` edge objects.

## Pipe Declaration Rule
All pipe types must be declared under `pipes`.

## Connection Chain Form
A valid chain can include component-port endpoints and a pipe in the middle, e.g. component:[port] -> pipe -> component:[port].

## Chain Validation
Connections are validated per adjacent hop in sequence.

## Chain Length
Each connection chain must contain at least two tokens.

## Allowed Hop Types
Allowed adjacent hop types are component-to-component and component-to-pipe in either direction.

## Single-Port Tokens
Each connection token may reference at most one port.

## Multi-Port Token Syntax
Multi-port list syntax in a single token is invalid.

## Direct Chain Adjacency
Component-to-component adjacency is valid in a `connections` chain and represents a direct mated connection.

## Pipe To Pipe
Pipe-to-pipe adjacency is invalid.

## Pipe Topology
Pipes are rendered as blocks and behave as single run elements that can be connected on left and right sides in the graph.

## Pipe Uniqueness
Each pipe usage in `connections` creates a unique pipe run instance.

## Pipe Instance Style
Pipes are always treated as unnamed instances in connection chains.

## Pipe Shorthand
Referencing a pipe type by name in a connection chain is shorthand for creating a fresh unnamed instance of that pipe type.

## Pipe Named Instances
Named pipe instances are not used in authored YAML.

## Pipe Port Default
When a pipe port is omitted, resolution defaults to the first port. This is valid because pipe definitions expose a single port.

## Component Base Reference
`component:[port]` refers to the default non-instanced component identity.

## Component Port Default
When a component port is omitted, resolution defaults to the first port.

## Direct Hop Port Omission
In direct component-to-component hops, omitted ports on either side default to the first port.

## Instance-Port Independence
Port selection is independent of instance form. `component`, `component.`, and `component.named` all follow the same port rules.

## Component Named Instance
`component.instance:[port]` creates or references a named instance that can be referenced anywhere in `connections`.

## Named Instance Scope
Named instance identity is scoped by base component name, so `tank.a` and `pump.a` are distinct valid instances.

## Component Unnamed Instance
`component.:[port]` creates an unnamed one-time instance that cannot be referenced again.

## Unnamed Instance Multiplicity
Each `component.` occurrence creates a fresh distinct unnamed instance, even within the same connection chain.

## Session Handoff Scope
The schema and glossary in this file are locked and should be implemented as written.

## Session Handoff Pending Work: Connections
Implement `connections` chain parsing in `generate_all.py` and normalise chains into validated adjacent hops.

## Session Handoff Pending Work: Pipes
Implement `pipes` declarations and render each pipe usage as a unique unnamed pipe instance.

## Session Handoff Pending Work: Validation
Enforce all rules in this file in `validate_diagram()`, including hop-type checks, token arity checks, and port resolution bounds.

## Session Handoff Compatibility
Continue accepting legacy `edges` while adding `connections` support, with `connections` as preferred syntax.

---

## Domain Glossary

## Crosslink
A pipe run connecting the low ports of two parallel fresh water tanks, equalising their fill levels so both tanks draw and fill simultaneously. In this project: 40mm flexible DWV hose between the 1-1/2" BSP DN40mm male low ports of the two 95L Camec tanks, via DWV BSP female → 40mm barb adapters.

## Bung
A male BSP plug fitted to an unused tank port. Modelled as a component in every diagram because it is a real purchased part that must appear in the BOM. Unused ports must never be silently omitted.

## Gravity Filler
An external deck-mounted fitting that accepts water from a hose and delivers it into the tank system by gravity. In this project: a Camec combination filler with a 25mm barbed fill port and a 10mm barbed breather/vent port. Acts as the single external interface for both the fill line and the breather line.

## Flex Union
A flexible disconnect union in a rigid pipe run that allows a tank to be physically removed for service without disturbing the fixed pipework. Modelled as a two-port fitting component.
