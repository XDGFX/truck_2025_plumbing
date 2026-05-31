"""
Configuration constants for truck plumbing diagram generation.
"""

# File patterns and shared library location.
PLUMBING_FILE_PATTERN = "src/*.yml"
LOOM_FILE_PATTERN = PLUMBING_FILE_PATTERN
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
