import yaml

import argparse
from pathlib import Path

def get_version(input_file: Path) -> str:
    with open("galaxy.yml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("version")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse changelog version")
    parser.add_argument("input_file", help="Path to input file")
    args = parser.parse_args()

    version = get_version(args.input_file)
    print(version)
