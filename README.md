# Plumbing Diagram Generator

This project generates plumbing topology diagrams for the truck from YAML files using Graphviz.

The schema is intentionally small:

- `diagram` sets graph-level metadata such as title and layout direction.
- `components` defines the nodes shown in the graph.
- `edges` defines directed flow connections between component ports.
- An optional `shared.yml` prepend file can define reusable component definitions and visual templates for the project.

## How It Works

`generate_all.py` reads each `src/*.yml` file, optionally prepending `shared.yml` if present, resolves component references and templates, validates the topology, and renders the result with Graphviz's `dot` command.

Supported outputs:

- `svg` - default vector output
- `png` - raster output
- `html` - self-contained HTML page with embedded SVG
- `gv` - raw Graphviz source

## Diagram Files

Each `src/*.yml` file is a diagram. Add as many as needed — all are picked up automatically.

Add `src/*.yml` files to describe each system — all are picked up automatically.

## Optional Prepend File

`shared.yml` is an optional project-specific file for reusable component definitions and
visual templates. It is merged before each diagram file is processed. It is not a standard
library — define only what is relevant to your project, and omit the file entirely if
you do not need shared definitions.

## Named Colours

All colour fields (`fillcolor`, `color`, `bgcolor`) accept 2-letter WireViz colour codes as well as hex strings. For example, `fillcolor: RD` is equivalent to `fillcolor: "#ff0000"`. See [SYNTAX.md](SYNTAX.md#named-colours) for the full palette.

## Requirements

- Python packages: install `PyYAML`
- Graphviz: the `dot` binary must be available on your PATH

## Generation

Run the generator from the project root:

```bash
python3 generate_all.py
```

Examples:

```bash
python3 generate_all.py --format png
python3 generate_all.py --output-dir diagrams/
python3 generate_all.py src/my_system.yml
```
