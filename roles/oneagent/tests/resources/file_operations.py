from pathlib import Path
from typing import cast

import yaml

YamlScalar = str | int | float | bool | None
YamlValue = YamlScalar | dict[str, YamlScalar] | list[YamlScalar]
ParsedYaml = dict[str, YamlValue] | list[YamlValue] | YamlScalar


def read_yaml_file(file: Path) -> ParsedYaml:
    with file.open("r") as config:
        data = cast(ParsedYaml, yaml.safe_load(config))
        return data


def write_yaml_file(file: Path, data: ParsedYaml) -> None:
    with file.open("w") as config:
        _unused = config.write(yaml.dump(data))
