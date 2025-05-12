#!/usr/bin/env python3
import argparse
import yaml
import re
import sys

official_semver_regex = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
galaxy_yml = "galaxy.yml"
version_yml = "roles/oneagent/vars/version.yml"


class ListIndenter(yaml.Dumper):

    def increase_indent(self, flow=False, indentless=False):
        return super(ListIndenter, self).increase_indent(flow, False)


def string_presenter(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="")


def update_version_in_yaml(file_path, version_field_name, version):
    with open(file_path, "r") as file:
        yaml_data = yaml.safe_load(file)
    yaml_data[version_field_name] = version

    yaml.add_representer(str, string_presenter)
    with open(file_path, "w") as file:
        yaml.dump(
            yaml_data,
            file,
            Dumper=ListIndenter,
            sort_keys=False,
            explicit_start=True,
            indent=2,
            default_flow_style=False,
        )


def update_galaxy_yaml(version):
    update_version_in_yaml(galaxy_yml, "version", version)


def update_version_yaml(version):
    update_version_in_yaml(version_yml, "oneagent_script_version", version)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="update_version", description="Update version in all needed places across the repository"
    )

    parser.add_argument("new_version", help="New version in semver format")
    args = parser.parse_args()

    is_version_valid = re.match(official_semver_regex, args.new_version)
    if not is_version_valid:
        print("Version do not follow semver", file=sys.stderr)
        sys.exit(1)
    print(f"Apply new version: {args.new_version}")
    update_galaxy_yaml(args.new_version)
    update_version_yaml(args.new_version)
