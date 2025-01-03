import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict

import yaml
from util.constants.common_constants import (
    INSTALLER_PARTIAL_NAME,
    INSTALLER_SYSTEM_NAME_TYPE_MAP,
    INSTALLERS_DIRECTORY,
    TEST_DIRECTORY,
)
from util.constants.unix_constants import UNIX_ONEAGENTCTL_PATH
from util.constants.windows_constants import WINDOWS_ONEAGENTCTL_PATH
from util.test_data_types import DeploymentPlatform

ParsedYaml = dict | list | None


def prepare_test_dirs() -> None:
    remove_if_exists(TEST_DIRECTORY)
    Path(TEST_DIRECTORY).mkdir(parents=True)
    os.chdir(TEST_DIRECTORY)


def remove_if_exists(path: Path) -> None:
    if path.exists():
        try:
            shutil.rmtree(str(path)) if os.path.isdir(str(path)) else os.remove(str(path))
        except OSError as os_error:
            logging.error("Failed to remove %s: %s", path, os_error)


def read_yaml_file(file: Path) -> ParsedYaml:
    with file.open("r") as config:
        data = yaml.load(config, Loader=yaml.Loader)
        return data


def write_yaml_file(file: Path, data: ParsedYaml) -> None:
    with file.open("w") as config:
        config.write(yaml.dump(data))


def get_oneagentctl_path(platform: DeploymentPlatform) -> Path:
    return get_platform_argument(platform, UNIX_ONEAGENTCTL_PATH, WINDOWS_ONEAGENTCTL_PATH)


def get_platform_argument(platform: DeploymentPlatform, unix_arg: Any, windows_arg: Any) -> Any:
    return windows_arg if platform == DeploymentPlatform.WINDOWS_X86 else unix_arg


def _get_platform_by_installer(installer: Path) -> DeploymentPlatform:
    name = installer.name.lower()
    for platform in DeploymentPlatform:
        if platform.arch() in name and platform.system() in name:
            return platform

    # Special handling for Linux_x86 and Windows as the installer does not
    # contain architecture in its name
    if DeploymentPlatform.WINDOWS_X86.system() in name:
        return DeploymentPlatform.WINDOWS_X86
    return DeploymentPlatform.LINUX_X86


def _get_available_installers() -> Dict[DeploymentPlatform, list[Path]]:
    installers: dict[DeploymentPlatform, list[Path]] = {k: [] for k in DeploymentPlatform}
    for installer in sorted(INSTALLERS_DIRECTORY.glob(f"{INSTALLER_PARTIAL_NAME}*")):
        platform = _get_platform_by_installer(installer)
        installers[platform].append(installer)
    return installers


def get_installers(system: str, arch: str, version: str = "", include_paths: bool = False) -> list[Path | str]:
    try:
        # Special handling for mocking server behavior as URL for Linux
        # installers contains "unix" instead of linux
        system = INSTALLER_SYSTEM_NAME_TYPE_MAP[system]
        platform_installers = _get_available_installers()[DeploymentPlatform.from_system_and_arch(system, arch)]
        installers = platform_installers if include_paths else [ins.name for ins in platform_installers]
        if not version:
            return installers
        if version == "latest":
            return [installers[-1]]
        return [installer for installer in installers if version in str(installer)]

    except Exception as ex:
        logging.error("Failed to get installer for %s_%s in %s version: %s", system, arch, version, ex)
        return []
