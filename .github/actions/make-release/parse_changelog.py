#!/usr/bin/env python3

import argparse
from pathlib import Path

def get_section(input_file: Path, version: str):
    result = []
    with open(input_file, encoding="utf-8") as f:
        found: bool = False
        header_start = "## "
        lines = f.readlines()
        for i, line in enumerate(lines):
            if not found and line.startswith(header_start) and line.find(version) != -1:
                found = True
                continue
            if found:
                if line.startswith(header_start):
                    break
                result.append(line)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse changelog version")
    parser.add_argument("input_file", help="Path to input file")
    parser.add_argument("output_file", help="Path to output file")
    parser.add_argument("version", help="Version to process")
    args = parser.parse_args()

    section = get_section(args.input_file, args.version)

    if not section:
        print(f"Version {args.version} not found in {args.input_file}")
        exit(1)

    with open(args.output_file, "w") as file:
        file.write("".join(section).strip())