"""
Configuration constants for truck plumbing diagram generation.
"""

# File patterns and shared library location.
PLUMBING_FILE_PATTERN = "src/*.yml"
SHARED_COMPONENTS_FILE = "shared.yml"

# Graphviz runtime.
GRAPHVIZ_COMMAND = "dot"
GRAPHVIZ_FONT = "JetBrains Mono"
GRAPHVIZ_DEFAULTS = {
    "rankdir": "LR",
    "splines": "spline",
    "bgcolor": "#FFFFFF",
}

# Default generation settings.
DEFAULT_FORMAT = "svg"
DEFAULT_OUTPUT_DIR = "out"
SUPPORTED_FORMATS = ["svg", "png", "html", "gv"]

# Service rating colours: maps a service name to (fill_code, border_code) WireViz 2-letter codes.
# The border colour is also used as the edge colour for pipe runs with that service rating.
# Add any custom services here — names are arbitrary strings matched against pipe spec `service_rating`.
SERVICE_COLORS: dict[str, tuple[str, str]] = {
    "potable": ("LB", "LB"),
    "waste": ("GY", "RD"),  # grey fill, red border
    "vent": ("BG", "OL"),  # green fill, olive border
    "hot": ("GD", "OG"),  # gold fill, orange border
}
