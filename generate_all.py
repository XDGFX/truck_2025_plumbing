#!/usr/bin/env python3
"""
Generate all plumbing system diagrams.
Usage: python3 generate_all.py [--format FORMAT] [--output-dir DIR] [files...]
"""

import argparse
import glob
import os
import subprocess
import sys
from pathlib import Path

import config


def find_plumbing_files():
    """Find all plumbing system files in src directory"""
    plumbing_files = glob.glob(config.PLUMBING_FILE_PATTERN)
    prepend = os.path.basename(config.SHARED_COMPONENTS_FILE)
    plumbing_files = [f for f in plumbing_files if os.path.basename(f) != prepend]
    return sorted(plumbing_files)


def run_pipeviz(file_path, format_type, output_dir):
    """Run pipeviz for a single file using subprocess"""
    try:
        os.makedirs(output_dir, exist_ok=True)

        cmd = [
            "pipeviz",
            "--prepend",
            config.SHARED_COMPONENTS_FILE,
            file_path,
            "--format",
            format_type,
            "--output-dir",
            output_dir,
        ]

        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True, f"Generated {format_type} successfully"
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e.stderr}"
    except Exception as e:
        return False, f"Error: {str(e)}"


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
        choices=config.SUPPORTED_FORMATS,
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

    os.makedirs(args.output_dir, exist_ok=True)

    if args.files:
        files_to_generate = [f for f in args.files if f.endswith(".yml")]
        if not files_to_generate:
            print("❌ No .yml files provided!")
            return 1
    else:
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
        filename = Path(file_path).name
        print(f"Generating {filename}...")

        success, output = run_pipeviz(file_path, args.format, args.output_dir)
        if success:
            print(f"✅ {filename} generated successfully")
            success_count += 1
        else:
            print(f"❌ Failed to generate {filename}: {output}")
            failed_files.append(filename)
        print()

    print("=" * 50)
    print(f"📊 GENERATION SUMMARY")
    print(f"✅ Successfully generated: {success_count}/{len(files_to_generate)}")

    if failed_files:
        print(f"❌ Failed files: {', '.join(failed_files)}")
        return 1
    else:
        print("🎉 All plumbing diagrams generated successfully!")

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
