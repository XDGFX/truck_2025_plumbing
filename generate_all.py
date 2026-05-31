#!/usr/bin/env python3
"""
Generate all plumbing system diagrams.
Usage: python3 generate_all.py [--format FORMAT] [--output-dir DIR] [files...]
"""

import argparse
import glob
import os
import re
import subprocess
import sys
from copy import deepcopy
from html import escape
from pathlib import Path

import yaml

import config


def parse_connection_token(token: str) -> dict:
    """Parse a connection chain token into base_name, instance, and port components."""
    if not token:
        raise ValueError("Connection token must not be empty")

    colon_parts = token.split(":", 1)
    name_part = colon_parts[0]
    port_part = colon_parts[1] if len(colon_parts) > 1 else None

    if port_part is not None:
        if port_part.startswith("[") or "," in port_part:
            raise ValueError("Multi-port list syntax is invalid; at most one port per token")
        if re.search(r"^\d+-\d+$", port_part):
            raise ValueError("Multi-port range syntax is invalid; at most one port per token")

    if "." in name_part:
        dot_idx = name_part.index(".")
        base_name = name_part[:dot_idx]
        instance = name_part[dot_idx + 1:]
    else:
        base_name = name_part
        instance = None

    if not base_name:
        raise ValueError("Connection token must have a non-empty base name")

    return {"base_name": base_name, "instance": instance, "port": port_part}


def validate_connections_chain(
    chain: list,
    component_names: set,
    pipe_names: set,
) -> list:
    """Validate one connections chain and return the hops it produces."""
    if len(chain) < 2:
        raise ValueError("At least two tokens are required in a connection chain")

    def classify(token: str) -> tuple:
        parsed = parse_connection_token(token)
        base = parsed["base_name"]
        if base in component_names:
            return parsed, "component"
        if base in pipe_names:
            return parsed, "pipe"
        raise ValueError(f"Unknown name '{base}' not found in components or pipes")

    parsed_tokens = []
    for i, t in enumerate(chain):
        try:
            parsed_tokens.append(classify(t))
        except ValueError as exc:
            raise ValueError(f"token[{i}] {t!r}: {exc}") from exc

    hops = []
    for i in range(len(parsed_tokens) - 1):
        from_parsed, from_kind = parsed_tokens[i]
        to_parsed, to_kind = parsed_tokens[i + 1]
        if from_kind == "pipe" and to_kind == "pipe":
            raise ValueError(
                f"Pipe-to-pipe adjacent hops are invalid: "
                f"'{from_parsed['base_name']}' -> '{to_parsed['base_name']}'"
            )
        hops.append({"from": from_parsed, "to": to_parsed, "from_kind": from_kind, "to_kind": to_kind})

    return hops


def find_plumbing_files():
    """Find all plumbing system files in src directory"""
    plumbing_files = glob.glob(config.PLUMBING_FILE_PATTERN)
    prepend = os.path.basename(config.SHARED_COMPONENTS_FILE)
    plumbing_files = [f for f in plumbing_files if os.path.basename(f) != prepend]
    return sorted(plumbing_files)


def load_yaml_file(file_path):
    """Load a YAML file and return an empty mapping when the file is blank."""
    with open(file_path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def deep_merge(base, overlay):
    """Recursively merge dictionaries without mutating the inputs."""
    if not isinstance(base, dict):
        return deepcopy(overlay)
    if not isinstance(overlay, dict):
        return deepcopy(overlay)

    merged = deepcopy(base)
    for key, value in overlay.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def resolve_template(template_name, templates, stack=None):
    """Resolve a template, following any nested template chain."""
    stack = stack or []
    if template_name in stack:
        chain = " -> ".join(stack + [template_name])
        raise ValueError(f"Template cycle detected: {chain}")

    if template_name not in templates:
        raise ValueError(f"Unknown template: {template_name}")

    template = deepcopy(templates[template_name])
    parent_template = template.pop("template", None)
    if parent_template:
        template = deep_merge(
            resolve_template(parent_template, templates, stack + [template_name]),
            template,
        )
    return template


def resolve_component(
    component_name, component_spec, templates, component_library, stack=None
):
    """Resolve a component spec against shared refs and templates."""
    stack = stack or []
    if component_name in stack:
        chain = " -> ".join(stack + [component_name])
        raise ValueError(f"Component cycle detected: {chain}")

    resolved = deepcopy(component_spec) if isinstance(component_spec, dict) else {}

    reference_name = resolved.pop("ref", None)
    if reference_name:
        if reference_name not in component_library:
            raise ValueError(f"Unknown component reference: {reference_name}")
        resolved = deep_merge(
            resolve_component(
                reference_name,
                component_library[reference_name],
                templates,
                component_library,
                stack + [component_name],
            ),
            resolved,
        )

    template_name = resolved.pop("template", None)
    if template_name:
        resolved = deep_merge(resolve_template(template_name, templates), resolved)

    return resolved


def normalise_ports(component_spec):
    """Return the port list for a component as a list of dicts with at least a 'name' key."""
    if "ports" in component_spec:
        ports = component_spec["ports"]
        if isinstance(ports, dict):
            return [{"name": k} for k in ports.keys()]
        if isinstance(ports, list):
            return [p if isinstance(p, dict) else {"name": str(p)} for p in ports]
        return []
    portcount = component_spec.get("portcount")
    if portcount:
        return [{"name": str(i)} for i in range(1, portcount + 1)]
    return []


def dot_quote(value):
    """Quote a value for Graphviz DOT attributes."""
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


NAMED_COLORS: dict[str, str] = {
    "BK": "#000000",  # black
    "WH": "#ffffff",  # white
    "GY": "#999999",  # grey
    "PK": "#ff66cc",  # pink
    "RD": "#ff0000",  # red
    "OG": "#ff8000",  # orange
    "YE": "#ffff00",  # yellow
    "OL": "#708000",  # olive green
    "GN": "#00ff00",  # green
    "TQ": "#00ffff",  # turquoise
    "LB": "#a0dfff",  # light blue
    "BU": "#0066ff",  # blue
    "VT": "#8000ff",  # violet
    "BN": "#895956",  # brown
    "BG": "#ceb673",  # beige
    "IV": "#f5f0d0",  # ivory
    "SL": "#708090",  # slate
    "CU": "#d6775e",  # copper
    "SN": "#aaaaaa",  # tin
    "SR": "#84878c",  # silver
    "GD": "#ffcf80",  # gold
}


def resolve_color(value: str) -> str:
    """Resolve a colour value: WireViz 2-letter code → hex, or pass hex through."""
    upper = value.strip().upper()
    if upper in NAMED_COLORS:
        return NAMED_COLORS[upper]
    return value


_SERVICE_COLORS = {
    "potable": ("LB", "BU"),   # light blue fill, blue border
    "waste":   ("PK", "RD"),   # pink fill, red border
    "vent":    ("GN", "OL"),   # green fill, olive border
    "hot":     ("GD", "OG"),   # gold fill, orange border
}


def build_html_label(node_id, component_spec):
    """Build a Graphviz HTML label for a component with named ports."""
    label = escape(str(component_spec.get("label", node_id)))
    ports = normalise_ports(component_spec)
    fill_color = resolve_color(component_spec.get("fillcolor", "#e2e8f0"))
    border_color = resolve_color(component_spec.get("color", "#64748b"))

    ncols = 3  # port name | connection size | gender
    rows = []

    # Title row with template colour
    rows.append(
        f'<TR><TD COLSPAN="{ncols}" BORDER="1" BGCOLOR="{escape(fill_color)}" '
        f'COLOR="{escape(border_color)}" ALIGN="CENTER">{label}</TD></TR>'
    )

    # Optional metadata: manufacturer, model, mpn, supplier
    meta_parts = []
    for key in ("manufacturer", "model", "mpn", "supplier"):
        val = component_spec.get(key)
        if val:
            meta_parts.append(escape(str(val)))
    if meta_parts:
        rows.append(
            f'<TR><TD COLSPAN="{ncols}" BORDER="1" ALIGN="CENTER">'
            f'{" &middot; ".join(meta_parts)}</TD></TR>'
        )

    # Port rows omitted for simple components — edges attach to node border.
    # Two PORT anchors per row: port__w on col 1 (incoming :w), port__e on col 3 (outgoing :e).
    for port in ([] if component_spec.get("simple") else ports):
        port_name = str(port["name"])
        size_text = escape(str(port.get("connection_size", "")))
        gender_text = escape(str(port.get("gender", "")))
        rows.append(
            f'<TR>'
            f'<TD PORT="{escape(port_name)}__w" BORDER="1" ALIGN="CENTER">{escape(port_name)}</TD>'
            f'<TD BORDER="1" ALIGN="CENTER">{size_text}</TD>'
            f'<TD PORT="{escape(port_name)}__e" BORDER="1" ALIGN="CENTER">{gender_text}</TD>'
            f'</TR>'
        )

    # Description at bottom (collapsed + truncated)
    desc = str(component_spec.get("description", "")).strip()
    if desc:
        desc_clean = " ".join(desc.split())
        if len(desc_clean) > 80:
            desc_clean = desc_clean[:77] + "..."
        rows.append(
            f'<TR><TD COLSPAN="{ncols}" BORDER="1" ALIGN="CENTER">'
            f'{escape(desc_clean)}</TD></TR>'
        )

    rows_html = "\n".join(f"  {r}" for r in rows)
    return (
        '<<TABLE BORDER="0" CELLSPACING="0" CELLPADDING="3">\n'
        f'{rows_html}\n'
        '</TABLE>>'
    )


def build_pipe_html_label(pipe_name, pipe_spec):
    """Build a Graphviz HTML label for a pipe segment."""
    label = escape(str(pipe_spec.get("label", pipe_name)))
    service = pipe_spec.get("service_rating", "")
    raw_fill, raw_border = _SERVICE_COLORS.get(service, ("#f1f5f9", "#64748b"))
    fill_color, border_color = resolve_color(raw_fill), resolve_color(raw_border)

    rows = []
    rows.append(
        f'<TR><TD BORDER="1" BGCOLOR="{fill_color}" COLOR="{border_color}" ALIGN="CENTER">'
        f'{label}</TD></TR>'
    )

    meta_parts = []
    for key in ("size", "material"):
        val = pipe_spec.get(key)
        if val:
            meta_parts.append(escape(str(val)))
    if service:
        meta_parts.append(escape(str(service)))
    if meta_parts:
        rows.append(
            f'<TR><TD BORDER="1" ALIGN="LEFT">{" &middot; ".join(meta_parts)}</TD></TR>'
        )

    rows_html = "\n".join(f"  {r}" for r in rows)
    return (
        '<<TABLE BORDER="0" CELLSPACING="0" CELLPADDING="0">\n'
        f'{rows_html}\n'
        '</TABLE>>'
    )


def render_component_node(node_id, component_spec):
    """Render a component into a DOT node statement."""
    ports = normalise_ports(component_spec)
    label = component_spec.get("label", node_id)
    node_color = resolve_color(component_spec.get("color", "#334155"))
    fill_color = resolve_color(component_spec.get("fillcolor", "#e2e8f0"))
    shape = component_spec.get("shape", "box")
    style = component_spec.get("style", "rounded,filled")
    fontname = component_spec.get("fontname", config.GRAPHVIZ_FONT)

    if ports or component_spec.get("simple"):
        html_label = build_html_label(node_id, component_spec)
        return (
            f"  {dot_quote(node_id)} "
            f"[fontname={dot_quote(fontname)}, shape=none, margin=0, label={html_label}];"
        )

    return (
        f"  {dot_quote(node_id)} "
        f"[shape={dot_quote(shape)}, style={dot_quote(style)}, "
        f"fillcolor={dot_quote(fill_color)}, color={dot_quote(node_color)}, "
        f"fontname={dot_quote(fontname)}, label={dot_quote(label)}];"
    )


def validate_diagram(diagram, file_path):
    """Validate the resolved diagram structure before rendering."""
    components = diagram.get("components")
    if not isinstance(components, dict) or not components:
        raise ValueError(
            f"{file_path}: diagram must define a non-empty 'components' mapping"
        )

    connections = diagram.get("connections")
    if not isinstance(connections, list) or not connections:
        raise ValueError(
            f"{file_path}: diagram must define a non-empty 'connections' list"
        )

    for component_name, component_spec in components.items():
        if not isinstance(component_spec, dict):
            raise ValueError(
                f"{file_path}: component '{component_name}' must be a mapping"
            )
        if not component_spec.get("label"):
            raise ValueError(
                f"{file_path}: component '{component_name}' must define a label"
            )
        is_simple = bool(component_spec.get("simple"))
        has_ports = "ports" in component_spec
        has_portcount = "portcount" in component_spec
        if is_simple:
            if has_ports or has_portcount:
                raise ValueError(
                    f"{file_path}: simple component '{component_name}' must not define 'ports' or 'portcount'"
                )
        else:
            if not has_ports and not has_portcount:
                raise ValueError(
                    f"{file_path}: component '{component_name}' must define 'ports' or 'portcount'"
                )
            if has_ports and has_portcount:
                port_list = normalise_ports(component_spec)
                if component_spec["portcount"] != len(port_list):
                    raise ValueError(
                        f"{file_path}: component '{component_name}' portcount "
                        f"{component_spec['portcount']} does not match ports length {len(port_list)}"
                    )

    component_names = set(components.keys())
    pipe_names = set(diagram.get("pipes", {}).keys())

    for chain_idx, chain in enumerate(connections):
        try:
            validate_connections_chain(chain, component_names, pipe_names)
        except ValueError as exc:
            raise ValueError(
                f"{file_path}: connections[{chain_idx}] {chain}: {exc}"
            ) from exc

        for token in chain:
            try:
                parsed = parse_connection_token(token)
            except ValueError as exc:
                raise ValueError(
                    f"{file_path}: connections[{chain_idx}] {chain}, token {token!r}: {exc}"
                ) from exc
            base = parsed["base_name"]
            port = parsed["port"]
            if base in component_names and port is not None:
                if components[base].get("simple"):
                    raise ValueError(
                        f"{file_path}: simple component '{base}' does not support named port references in connections"
                    )
                comp_ports = normalise_ports(components[base])
                port_names = {p["name"] for p in comp_ports}
                if comp_ports and port not in port_names:
                    raise ValueError(
                        f"{file_path}: component '{base}' has no port named '{port}'"
                    )


def build_dot(diagram, file_path):
    """Convert a resolved diagram into Graphviz DOT text."""
    graph_defaults = diagram.get("diagram", {})
    title = graph_defaults.get("title", Path(file_path).stem.replace("_", " ").title())
    rankdir = graph_defaults.get("rankdir", config.GRAPHVIZ_DEFAULTS["rankdir"])
    splines = graph_defaults.get("splines", config.GRAPHVIZ_DEFAULTS["splines"])
    bgcolor = resolve_color(graph_defaults.get("bgcolor", config.GRAPHVIZ_DEFAULTS["bgcolor"]))
    ranksep = graph_defaults.get("ranksep", "2")
    nodesep = graph_defaults.get("nodesep", "0.33")
    fontname = graph_defaults.get("fontname", config.GRAPHVIZ_FONT)
    lines = ["digraph G {"]
    lines.append(
        f"  graph [rankdir={dot_quote(rankdir)}, splines={dot_quote(splines)}, "
        f"bgcolor={dot_quote(bgcolor)}, fontname={dot_quote(fontname)}, "
        f"ranksep={dot_quote(ranksep)}, nodesep={dot_quote(nodesep)}];"
    )
    lines.append(
        f'  node [fillcolor="#FFFFFF" fontname={dot_quote(fontname)} height=0 margin=0 shape=none style=filled width=0];'
    )
    lines.append(f"  edge [fontname={dot_quote(fontname)}, style=bold, dir=none];");
    lines.append('  labelloc="t";')
    lines.append(f"  label={dot_quote(title)};")
    lines.append("  fontsize=20;")

    lines.append("")
    connections = diagram.get("connections", [])
    pipes_spec = diagram.get("pipes", {})
    component_names = set(diagram["components"].keys())
    pipe_names = set(pipes_spec.keys())

    emitted_nodes = set()
    anon_counter = 0
    pipe_counter = 0

    for chain_idx, chain in enumerate(connections):
        try:
            hops = validate_connections_chain(chain, component_names, pipe_names)
        except ValueError as exc:
            raise ValueError(
                f"{file_path}: connections[{chain_idx}] {chain}: {exc}"
            ) from exc

        token_info = []
        for token in chain:
            parsed = parse_connection_token(token)
            base = parsed["base_name"]
            port = parsed["port"]
            instance = parsed["instance"]

            if base in pipe_names:
                node_id = f"{base}__{pipe_counter}"
                pipe_counter += 1
                token_info.append({"node_id": node_id, "base": base, "port": port, "is_pipe": True})
            else:
                if instance is None:
                    node_id = base
                elif instance == "":
                    node_id = f"{base}__{anon_counter}"
                    anon_counter += 1
                else:
                    node_id = f"{base}__{instance}"
                token_info.append({"node_id": node_id, "base": base, "port": port, "is_pipe": False})

        for ti in token_info:
            if ti["node_id"] not in emitted_nodes:
                if ti["is_pipe"]:
                    pipe_html = build_pipe_html_label(ti["base"], pipes_spec[ti["base"]])
                    lines.append(
                        f'  {dot_quote(ti["node_id"])} [shape=none, margin=0, label={pipe_html}];'
                    )
                else:
                    lines.append(render_component_node(ti["node_id"], diagram["components"][ti["base"]]))
                emitted_nodes.add(ti["node_id"])

        for hop_idx in range(len(hops)):
            fi = token_info[hop_idx]
            ti = token_info[hop_idx + 1]

            if fi["is_pipe"]:
                tail = dot_quote(fi["node_id"])
            else:
                port = fi["port"]
                if port is None:
                    comp_ports = normalise_ports(diagram["components"][fi["base"]])
                    if comp_ports:
                        port = comp_ports[0]["name"]
                if port:
                    tail = f'{dot_quote(fi["node_id"])}:{port}__e:e'
                elif diagram["components"][fi["base"]].get("simple"):
                    tail = f'{dot_quote(fi["node_id"])}:e'
                else:
                    tail = dot_quote(fi["node_id"])

            if ti["is_pipe"]:
                head = dot_quote(ti["node_id"])
            else:
                port = ti["port"]
                if port is None:
                    comp_ports = normalise_ports(diagram["components"][ti["base"]])
                    if comp_ports:
                        port = comp_ports[0]["name"]
                if port:
                    head = f'{dot_quote(ti["node_id"])}:{port}__w:w'
                elif diagram["components"][ti["base"]].get("simple"):
                    head = f'{dot_quote(ti["node_id"])}:w'
                else:
                    head = dot_quote(ti["node_id"])

            lines.append(f"  {tail} -> {head};")

    lines.append("}")
    return "\n".join(lines) + "\n"


def write_graphviz_output(dot_text, format_type, output_path):
    """Render DOT text to the requested output format."""
    if format_type == "gv":
        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write(dot_text)
        return

    if format_type == "html":
        svg_result = subprocess.run(
            [config.GRAPHVIZ_COMMAND, "-Tsvg"],
            input=dot_text,
            capture_output=True,
            check=True,
            text=True,
            encoding="utf-8",
        )
        html_text = (
            "<!doctype html>\n"
            '<html lang="en">\n'
            "<head>\n"
            '  <meta charset="utf-8">\n'
            f"  <title>{escape(Path(output_path).stem)}</title>\n"
            "  <style>body{margin:0;padding:1rem;background:#fff;font-family:system-ui,sans-serif;}"
            "svg{max-width:100%;height:auto;}</style>\n"
            "</head>\n"
            "<body>\n"
            f"{svg_result.stdout}\n"
            "</body>\n"
            "</html>\n"
        )
        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write(html_text)
        return

    is_text_output = format_type != "png"
    result = subprocess.run(
        [config.GRAPHVIZ_COMMAND, f"-T{format_type}"],
        input=dot_text if is_text_output else dot_text.encode("utf-8"),
        capture_output=True,
        check=True,
        text=is_text_output,
        encoding="utf-8" if is_text_output else None,
    )

    if format_type == "png":
        if not isinstance(result.stdout, (bytes, bytearray)):
            raise TypeError("Graphviz PNG output must be binary")
        with open(output_path, "wb") as handle:
            handle.write(result.stdout)
    else:
        if not isinstance(result.stdout, str):
            raise TypeError("Graphviz text output must be str")
        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write(result.stdout)


def run_graphviz(file_path, format_type, output_dir):
    """Render a single plumbing diagram file using Graphviz."""
    try:
        os.makedirs(output_dir, exist_ok=True)

        prepend_path = config.SHARED_COMPONENTS_FILE
        shared_data = load_yaml_file(prepend_path) if os.path.exists(prepend_path) else {}
        diagram_data = load_yaml_file(file_path)

        diagram = {
            "diagram": deep_merge(
                shared_data.get("diagram", {}), diagram_data.get("diagram", {})
            ),
        }

        templates = deep_merge(
            shared_data.get("templates", {}), diagram_data.get("templates", {})
        )
        component_library = deep_merge(
            shared_data.get("components", {}), diagram_data.get("components", {})
        )

        resolved_components = {}
        for component_name, component_spec in component_library.items():
            resolved_components[component_name] = resolve_component(
                component_name,
                component_spec,
                templates,
                component_library,
            )

        diagram["components"] = resolved_components
        diagram["connections"] = diagram_data.get("connections", [])
        diagram["pipes"] = diagram_data.get("pipes", {})

        validate_diagram(diagram, file_path)
        dot_text = build_dot(diagram, file_path)

        output_suffix = {"svg": ".svg", "png": ".png", "html": ".html", "gv": ".gv"}[
            format_type
        ]
        output_path = os.path.join(output_dir, f"{Path(file_path).stem}{output_suffix}")

        write_graphviz_output(dot_text, format_type, output_path)
        return True, f"Generated {output_path}"
    except subprocess.CalledProcessError as error:
        stderr = (
            error.stderr
            if isinstance(error.stderr, str)
            else error.stderr.decode("utf-8", "replace")
        )
        return False, f"Graphviz failed: {stderr.strip()}"
    except Exception as error:
        return False, f"Error: {error}"


def main():
    parser = argparse.ArgumentParser(
        description="Generate all plumbing system diagrams",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 generate_all.py                           # Generate all files as SVG
  python3 generate_all.py --format png              # Generate all files as PNG
  python3 generate_all.py --output-dir diagrams/    # Custom output directory
  python3 generate_all.py src/fresh_water.yml       # Generate specific file
  python3 generate_all.py --format png src/*.yml    # Generate multiple specific files
        """,
    )

    parser.add_argument(
        "--format",
        "-f",
        default=config.DEFAULT_FORMAT,
        choices=["svg", "png", "html", "gv"],
        help=f"Output format (default: {config.DEFAULT_FORMAT})",
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        default=config.DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {config.DEFAULT_OUTPUT_DIR})",
    )

    parser.add_argument(
        "files",
        nargs="*",
        help="Specific files to generate (default: all files in src/)",
    )

    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Determine which files to generate
    if args.files:
        # Use provided files, but filter to only include .yml files
        files_to_generate = [f for f in args.files if f.endswith(".yml")]
        if not files_to_generate:
            print("❌ No .yml files provided!")
            return 1
    else:
        # Auto-discover files
        files_to_generate = find_plumbing_files()
        if not files_to_generate:
            print("ℹ️  No plumbing system files found in src/ directory yet")
            return 0

    print(
        f"📁 Generating {len(files_to_generate)} plumbing diagram(s) in {args.format.upper()} format..."
    )
    print()

    success_count = 0
    failed_files = []

    for file_path in files_to_generate:
        # Extract just the filename for display
        filename = Path(file_path).name
        print(f"Generating {filename}...")

        success, output = run_graphviz(file_path, args.format, args.output_dir)
        if success:
            print(f"✅ {filename} generated successfully")
            success_count += 1
        else:
            print(f"❌ Failed to generate {filename}: {output}")
            failed_files.append(filename)
        print()

    # Summary
    print("=" * 50)
    print(f"📊 GENERATION SUMMARY")
    print(f"✅ Successfully generated: {success_count}/{len(files_to_generate)}")

    if failed_files:
        print(f"❌ Failed files: {', '.join(failed_files)}")
        return 1
    else:
        print("🎉 All plumbing diagrams generated successfully!")

        # Show generated files
        if files_to_generate:
            print(f"\n📁 Generated files in {args.output_dir}/:")
            try:
                files = os.listdir(args.output_dir)
                for file in sorted(files):
                    file_path = os.path.join(args.output_dir, file)
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        print(f"  {file} ({size} bytes)")
            except Exception as e:
                print(f"(Could not list files: {e})")

        return 0


if __name__ == "__main__":
    sys.exit(main())
