#!/usr/bin/env python3

import argparse
from pathlib import Path

def get_section(file_name: Path, version: str):
    result = []
    with open(file_name, encoding="utf-8") as f:
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
    parser.add_argument("--file", required=True, help="Path to changelog file")
    parser.add_argument("--version", required=True, help="Version to process")
    args = parser.parse_args()

    section = get_section(args.file, args.version)

    if not section:
        print(f"Version {args.version} not found in {args.file}")
        exit(1)

    print("".join(section).strip())