from pathlib import Path

import yaml

ParsedYaml = dict | list | None


def read_yaml_file(file: Path) -> ParsedYaml:
    with file.open("r") as config:
        data = yaml.load(config, Loader=yaml.Loader)
        return data


def write_yaml_file(file: Path, data: ParsedYaml) -> None:
    with file.open("w") as config:
        config.write(yaml.dump(data))
