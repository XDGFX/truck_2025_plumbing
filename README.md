# Truck Plumbing Diagrams

Plumbing topology diagrams for the truck, generated from YAML source files using [pipeviz](https://github.com/xdgfx/pipeviz).

## How It Works

`generate_all.py` finds all `src/*.yml` files and calls `pipeviz` for each, prepending `shared.yml` to inject the project's shared component library. Outputs go to `out/`.

## Generating Diagrams

```bash
python3 generate_all.py                           # Generate all files as SVG
python3 generate_all.py --format png              # Generate all files as PNG
python3 generate_all.py --output-dir diagrams/    # Custom output directory
python3 generate_all.py src/fresh_water.yml       # Generate specific file
```

## Diagram Files

Each `src/*.yml` file is a diagram. Add new ones and they are picked up automatically.

## Shared Component Library

`shared.yml` defines the reusable components (tanks, pumps, valves, fixtures) and visual templates for this project. It is prepended to every diagram before processing.

For the full pipeviz YAML authoring reference, see the [pipeviz SYNTAX.md](https://github.com/xdgfx/pipeviz/blob/master/SYNTAX.md).

## Configuration

Project-level settings live in `config.py`:

| Constant                 | Purpose                                            |
| ------------------------ | -------------------------------------------------- |
| `PLUMBING_FILE_PATTERN`  | Glob for diagram source files                      |
| `SHARED_COMPONENTS_FILE` | Path to the prepend file                           |
| `DEFAULT_FORMAT`         | Output format when `--format` is not passed        |
| `DEFAULT_OUTPUT_DIR`     | Output directory when `--output-dir` is not passed |

## Requirements

```bash
pip install -r requirements.txt
```

The `dot` binary (Graphviz) must be available on your PATH.
