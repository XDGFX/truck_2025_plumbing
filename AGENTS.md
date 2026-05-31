# Truck 2025 Plumbing Project - Agent Handoff

## Summary
Created minimal scaffolding for **truck_2025_plumbing** project mirroring the electrical system structure. Ready for diagram expansion and validation.

## What Was Done
1. ✅ Created project structure: `/src/`, `/out/`, core configuration files
2. ✅ Documented `shared.yml` as an optional project-specific prepend file for reusable templates and component definitions
3. ✅ Created `config.py` for generation configuration
4. ✅ Implemented `generate_all.py` script (wireviz + graphviz based)
5. ✅ Created 3 minimal system diagram templates:
   - `fresh_water_supply.yml` — Tank, pump, distribution, fixtures
   - `hot_water_system.yml` — Tankless heater with mixing valve
   - `waste_system.yml` — Greywater tank, drains, venting
6. ✅ Added `README.md` with architecture overview

## Project Structure
```
truck_2025_plumbing/
├── src/                          # Plumbing system diagrams (YAML)
│   ├── fresh_water_supply.yml   # Fresh water tank → pump → distribution
│   ├── hot_water_system.yml     # Tankless heater + thermostatic mixing
│   └── waste_system.yml         # Greywater tank + drainage routing
├── out/                          # Generated diagram output (SVG/PNG/HTML/GV)
├── shared.yml                    # Optional prepend: project-specific reusable definitions
├── config.py                     # Configuration constants
├── generate_all.py               # Diagram generation script (executable)
├── README.md                     # Architecture overview
└── AGENTS.md                     # This file
```

## Key Design Decisions
- **Schema**: WireViz YAML format (same as electrical project) leveraging graphviz
- **Optional prepend file**: `shared.yml` is project-specific and not a bundled library — define only what this project needs. The generator runs without it.
- **Configuration**: `config.py` mirrors electrical patterns (LOOM_FILE_PATTERN, DEFAULT_FORMAT, output handling)
- **Generation**: `generate_all.py` reuses electrical project's approach (subprocess wireviz call, format mapping)

## Testing Checklist
- [ ] Run `python3 generate_all.py` to verify generation works
- [ ] Verify SVG/PNG output in `out/` directory
- [ ] Test individual file generation: `python3 generate_all.py src/fresh_water_supply.yml`
- [ ] Validate YAML syntax in all `src/*.yml` files

## Next Steps for Future Sessions

### Immediate (Quick Wins)
1. **Complete system diagrams** — Expand YAML files with full plumbing layouts (add connections between components)
2. **Validate generation** — Run `generate_all.py` and verify output
3. **Add system details** — Temperature sensors, pressure gauges, shutoff locations

### Short Term
1. **Create additional systems** — Add propane line diagram, grey/black water overflow routing
2. **Implement pin validation** — Similar to electrical `validate_pins.py` to catch:
   - Unused tank ports
   - Unconnected pump inlets/outlets
   - Missing drain paths
3. **Add materials/specs** — Document PEX sizes, PSI ratings, GPM flows

### Medium Term
1. **Cross-system integration** — Link to electrical system (pump relays, sensors on Cerbo GX)
2. **Component database** — Build MPN catalog for sourcing
3. **Documentation** — Installation guides, maintenance procedures

## Important Context
- **Location**: `/Users/cal/git/truck_2025_plumbing/`
- **Related project**: `/Users/cal/git/truck_2025_electrical/` — Reference for patterns/structure
- **Dependencies**: Requires `wireviz` and `graphviz` installed
- **Generation command**: `python3 generate_all.py [--format svg|png|html|gv] [--output-dir DIR]`

## Code Patterns Reused from Electrical
- **Config management** — Same `config.py` approach
- **YAML schema** — Connector/harness/options structure
- **Shared components** — YAML anchors (`&name`) for DRY definitions
- **Script structure** — File discovery, format mapping, subprocess handling
- **Output strategy** — Files in `out/` directory, configurable formats

## Files Created This Session
1. `/truck_2025_plumbing/config.py`
2. `/truck_2025_plumbing/generate_all.py`
4. `/truck_2025_plumbing/src/fresh_water_supply.yml`
5. `/truck_2025_plumbing/src/hot_water_system.yml`
6. `/truck_2025_plumbing/src/waste_system.yml`
7. `/truck_2025_plumbing/README.md`
8. `/truck_2025_plumbing/AGENTS.md`

## Known Limitations / TODOs
- [ ] YAML schemas in `src/` are minimal templates — need full component connections
- [ ] No pin validation yet (unlike electrical project with `validate_pins.py`)
- [ ] No component sourcing/BOM generation
- [ ] No integration with electrical system yet (sensor connections, 12V pump relay control)

## Questions for Next Session
1. What's the actual plumbing layout? (tank locations, fixture routing)
2. Hot water system details? (propane vs. diesel, mixing valve requirements)
3. Grey/black water capacity and overflow strategy?
4. Should plumbing diagrams validate against electrical (e.g., pump control circuits)?
