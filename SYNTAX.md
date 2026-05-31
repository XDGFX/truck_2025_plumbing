# Diagram Authoring Reference

How to write a new diagram file in `src/`. Drop a `*.yml` file there and `generate_all.py` picks it up automatically.

---

## File Skeleton

```yaml
diagram:
  title: My System          # optional — defaults to filename
  rankdir: LR               # optional — LR (left-to-right, default) or TB (top-to-bottom)

components:
  my_component:
    label: Display Label    # required
    ports: [in, out]        # required — OR use portcount (see below)
    ref: shared_key         # optional — inherit label + ports from shared.yml
    template: valve         # optional — apply a visual style without inheriting ports
    # optional metadata (not validated, shown in tooltip/BOM):
    manufacturer: ACME
    model: AV-100
    description: Manual isolation valve

pipes:
  half_inch_pex:
    label: '1/2" PEX'       # required
    # optional pipe metadata:
    material: PEX-B
    size: '1/2"'
    service_rating: potable
    description: Cold supply run

connections:
  - [component_a:port, component_b:port]             # direct connection
  - [component_a:port, pipe_type, component_b:port]  # pipe-mediated
```

---

## Components

### Using prepend file components

If the project has a `shared.yml` prepend file, `ref:` copies a component definition
(label + ports) from it:

```yaml
components:
  main_pump:
    ref: pump_12v           # inherits label "12V Demand Pump" and ports [power, inlet, outlet]

  sink_a:
    ref: sink_faucet        # label and ports from shared.yml
```

Override any field after `ref:`:

```yaml
  kitchen_sink:
    ref: sink_faucet
    label: Kitchen Sink     # overrides the shared label
```

### Using templates (style only)

`template:` applies a visual style but does NOT inherit ports — you must declare them:

```yaml
  mixing_valve:
    template: valve
    label: Thermostatic Mixing Valve
    ports: [cold_in, hot_in, mixed_out, sensor]
```

### Numeric ports

Use `portcount` when ports will be referenced by number rather than name:

```yaml
  manifold:
    label: Distribution Manifold
    portcount: 4            # ports referenced as manifold:1, manifold:2, manifold:3, manifold:4
```

`ports` and `portcount` may coexist; `portcount` must equal the length of `ports` when both are present.

### Detailed port objects

When you need port-level metadata, use object form instead of a string list:

```yaml
  my_valve:
    label: Isolation Valve
    ports:
      - name: inlet
        connection_size: '1/2"'
        gender: female
        service_rating: potable
      - name: outlet
        connection_size: '1/2"'
        gender: male
```

---

## Pipes

Declare every pipe type under `pipes:` before using it in `connections`:

```yaml
pipes:
  pex_half:
    label: '1/2" PEX'
  pex_three_quarter:
    label: '3/4" PEX'
  copper_half:
    label: '1/2" Copper'
```

Each use of a pipe name in a `connections` chain creates a fresh unnamed pipe run — the same name can appear in multiple chains without conflict.

---

## Connections

### Token syntax

| Token | Meaning |
|-------|---------|
| `component` | Component, first port (default) |
| `component:port` | Component, named port |
| `component:3` | Component, third port (numeric, 1-based) |
| `component.name` | Named instance — same identity reused across chains |
| `component.name:port` | Named instance, specific port |
| `component.:port` | Unnamed instance — fresh occurrence each time |
| `pipe_type` | Creates a unique unnamed pipe run |

### Rules

- Every chain must have **at least 2 tokens**.
- **Pipe-to-pipe adjacency is invalid** — always separate pipes with a component token.
- Each `pipe_type` token in a chain is a fresh run; the same type can appear multiple times.

### Examples

```yaml
connections:
  # Direct connection (no pipe)
  - [pump:outlet, filter:inlet]

  # Pipe-mediated connection
  - [pump:outlet, pex_half, filter:inlet]

  # Multi-hop chain (two pipes, one component in the middle)
  - [tank:outlet, pex_three_quarter, pump:inlet]
  - [pump:outlet, pex_half, manifold:inlet]

  # Omitted port defaults to first port
  - [pump, filter]          # equivalent to pump:inlet → filter:inlet if those are first ports

  # Named instances — two sinks sharing the same manifold branch identity
  - [manifold:zone_1, pex_half, sink.kitchen:cold_in]
  - [manifold:zone_2, pex_half, sink.bathroom:cold_in]

  # Unnamed instance — each occurrence is a distinct component
  - [supply, pex_half, tee.]
  - [tee., pex_half, sink_a]
  - [tee., pex_half, sink_b]
```

---

## Prepend File Components

The generator has no built-in component library. Any `ref:` targets must be defined in
your project's prepend file (`shared.yml` by default). The tables below document what
**this project's `shared.yml`** defines — a different project would define its own.

### Tanks

| Key | Label | Ports |
|-----|-------|-------|
| `fresh_water_tank` | Fresh Water Tank | inlet, outlet, overflow, drain |
| `grey_water_tank` | Grey Water Tank | inlet, outlet, drain, vent |
| `black_water_tank` | Black Water Tank | inlet, drain, vent |

### Pumps

| Key | Label | Ports |
|-----|-------|-------|
| `pump_12v` | 12V Demand Pump | power, inlet, outlet |
| `pump_24v` | 24V Demand Pump | power, inlet, outlet |
| `pump_ac_shore` | AC Shore Pump | power, inlet, outlet |

### Filters

| Key | Label | Ports |
|-----|-------|-------|
| `sediment_filter` | Sediment Filter | inlet, outlet, drain |
| `carbon_filter` | Carbon Filter | inlet, outlet |

### Valves

| Key | Label | Ports |
|-----|-------|-------|
| `ball_valve_1_2` | Ball Valve 1/2" | inlet, outlet |
| `ball_valve_3_4` | Ball Valve 3/4" | inlet, outlet |
| `check_valve_1_2` | Check Valve 1/2" | inlet, outlet |
| `pressure_relief_50psi` | Pressure Relief 50 PSI | inlet, outlet |
| `drain_valve` | Manual Drain Valve | tank_inlet, drain_outlet |

### Heaters

| Key | Label | Ports |
|-----|-------|-------|
| `tankless_lp_heater` | Tankless Propane Heater | cold_inlet, hot_outlet, propane_in, drain |
| `diesel_heater` | Diesel Water Heater | cold_inlet, hot_outlet, fuel_in, drain, thermostat |

### Fixtures

| Key | Label | Ports |
|-----|-------|-------|
| `sink_faucet` | Sink Faucet | cold_in, hot_in, drain |
| `shower_head` | Shower Head | hot_inlet, cold_inlet, drain |
| `toilet` | Toilet | supply, drain |

### Offpage connectors

| Key | Label | Ports |
|-----|-------|-------|
| `offpage_in` | From Other System | in |
| `offpage_out` | To Other System | out |

### Vents

| Key | Label | Ports |
|-----|-------|-------|
| `greywater_vent` | Greywater Vent | vent_in |
| `overflow_vent` | Overflow Vent | vent_in |

---

## Visual Templates

Used with `template:` to control node appearance.

| Template | Shape | Fill colour |
|----------|-------|-------------|
| `tank` | 3D box | Blue |
| `pump` | Box | Orange |
| `filter` | Box | Light grey |
| `valve` | Box | Green |
| `heater` | Box | Red |
| `fixture` | Box | Sky blue |
| `manifold` | Box | Amber |
| `trap` | Box | Purple |
| `offpage` | Oval | Off-white |
| `vent` | Oval | Lime |

---

## Minimal Working Example

```yaml
diagram:
  title: Cold Water Supply

components:
  supply_in:
    ref: offpage_in
    label: Shore Water

  pump:
    ref: pump_12v

  sediment:
    ref: sediment_filter

  tap:
    ref: sink_faucet
    label: Kitchen Tap

pipes:
  pex_half:
    label: '1/2" PEX'

connections:
  - [supply_in:in, pex_half, pump:inlet]
  - [pump:outlet, pex_half, sediment:inlet]
  - [sediment:outlet, pex_half, tap:cold_in]
```
