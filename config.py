"""
Configuration constants for truck plumbing diagram generation.
"""

# File patterns and shared library location.
PLUMBING_FILE_PATTERN = "src/*.yml"
SHARED_COMPONENTS_FILE = "shared.yml"

# Default generation settings.
DEFAULT_FORMAT = "svg"
DEFAULT_OUTPUT_DIR = "out"
SUPPORTED_FORMATS = ["svg", "png", "html", "gv"]
