import functools
import logging
import os
from pathlib import Path
from typing import Any, Callable, TypeVar, cast

from tests.ansible.config import AnsibleConfigurator
from tests.ansible.runner import AnsibleRunner
from tests.command.platform_command_wrapper import PlatformCommandWrapper
from tests.constants import (
    INSTALLER_CERTIFICATE_FILE_NAME,
    INSTALLER_PARTIAL_NAME,
    INSTALLER_SERVER_TOKEN,
    INSTALLER_SYSTEM_NAME_TYPE_MAP,
    SERVER_CERTIFICATE_FILE_NAME,
    UNIX_ONEAGENTCTL_PATH,
    WINDOWS_ONEAGENTCTL_PATH,
    WORK_DIR_PATH,
    WORK_INSTALLERS_DIR_PATH,
    WORK_SERVER_DIR_PATH,
)
from tests.deployment.deployment_platform import (
    DeploymentPlatform,
    DeploymentResult,
    PlatformCollection,
)

CallableOperation = Callable[[DeploymentPlatform, str, Any], None]


def prepare_test_dirs(test_case_name: str) -> None:
    Path(WORK_DIR_PATH / test_case_name).mkdir(parents=True, exist_ok=True)
    os.chdir(WORK_DIR_PATH)


def get_oneagentctl_path(platform: DeploymentPlatform) -> Path:
    return select_by_platform(platform, UNIX_ONEAGENTCTL_PATH, WINDOWS_ONEAGENTCTL_PATH)


PlatformSpecificValue = TypeVar("PlatformSpecificValue")


def select_by_platform(
    platform: DeploymentPlatform, unix_value: PlatformSpecificValue, windows_value: PlatformSpecificValue
) -> PlatformSpecificValue:
    return windows_value if platform == DeploymentPlatform.WINDOWS_X86 else unix_value


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


def _get_available_installers() -> dict[DeploymentPlatform, list[Path]]:
    installers: dict[DeploymentPlatform, list[Path]] = {platform: [] for platform in DeploymentPlatform}
    for installer in sorted(WORK_INSTALLERS_DIR_PATH.glob(f"{INSTALLER_PARTIAL_NAME}*")):
        platform = _get_platform_by_installer(installer)
        installers[platform].append(installer)
    return installers


def get_installers(system: str, arch: str, version: str = "", include_paths: bool = False) -> list[Path]:
    try:
        # Special handling for mocking server behavior as URL for Linux
        # installers contains "unix" instead of linux
        system = INSTALLER_SYSTEM_NAME_TYPE_MAP[system]
        platform_installers = _get_available_installers()[DeploymentPlatform.from_system_and_arch(system, arch)]
        installers = platform_installers if include_paths else [Path(ins.name) for ins in platform_installers]
        if not version:
            return installers
        if version == "latest":
            return [installers[-1]]
        return [installer for installer in installers if version in str(installer)]

    except Exception as ex:
        logging.error("Failed to get installer for %s_%s in %s version: %s", system, arch, version, ex)
        return []


def _get_kwarg_by_name(name: str, **kwargs: object) -> object:
    assert name in kwargs, f"No '{name}' parameter in parameters list"
    return kwargs[name]


def enable_for_system_family(family: str) -> Callable[[Callable[..., None]], Callable[..., None]]:
    def func_wrapper(func: Callable[..., None]) -> Callable[..., None]:
        @functools.wraps(func)
        def params_wrapper(*args: object, **kwargs: object) -> None:
            config = cast(AnsibleConfigurator, _get_kwarg_by_name("configurator", **kwargs))
            platforms = cast(PlatformCollection, _get_kwarg_by_name("platforms", **kwargs))
            matching_platforms = [p for p in platforms.keys() if p.family() == family]
            if matching_platforms:
                config.set_deployment_hosts(family)
                logging.debug("Running test for %s platform", family)
                func(*args, **kwargs)
            else:
                logging.info("Skipping test for %s platform", family)

        return params_wrapper

    return func_wrapper


def perform_operation_on_platforms(platforms: PlatformCollection, operation: CallableOperation, *args: object) -> None:
    for platform, hosts in platforms.items():
        for address in hosts:
            operation(platform, address, *args)


def set_ca_cert_download_params(config: AnsibleConfigurator, installer_server_url: str) -> None:
    config.set_common_parameter(
        config.CA_CERT_DOWNLOAD_URL_KEY, f"{installer_server_url}/{INSTALLER_CERTIFICATE_FILE_NAME}"
    )
    config.set_common_parameter(
        config.CA_CERT_DOWNLOAD_CERT_KEY, f"{WORK_SERVER_DIR_PATH / SERVER_CERTIFICATE_FILE_NAME}"
    )
    config.set_common_parameter(config.FORCE_CERT_DOWNLOAD_KEY, True)


def set_installer_download_params(config: AnsibleConfigurator, installer_server_url: str) -> None:
    config.set_common_parameter(config.ENVIRONMENT_URL_KEY, installer_server_url)
    config.set_common_parameter(config.PAAS_TOKEN_KEY, INSTALLER_SERVER_TOKEN)
    config.set_common_parameter(
        config.INSTALLER_DOWNLOAD_CERT_KEY, f"{WORK_SERVER_DIR_PATH / SERVER_CERTIFICATE_FILE_NAME}"
    )
    for platform in DeploymentPlatform:
        config.set_platform_parameter(platform, config.INSTALLER_ARCH_KEY, platform.arch())

    set_ca_cert_download_params(config, installer_server_url)


def run_deployment(runner: AnsibleRunner, configurator: AnsibleConfigurator, ignore_errors: bool = False, check_mode: bool = False) -> DeploymentResult:
    results = runner.run_deployment(configurator, check_mode=check_mode)

    if not ignore_errors:
        logging.info("Check exit codes")
        for out in results:
            assert out.returncode == 0
    return results


def check_agent_state(
    platform: DeploymentPlatform, address: str, wrapper: PlatformCommandWrapper, installed: bool
) -> None:
    logging.debug("Platform: %s, IP: %s", platform, address)
    result = wrapper.file_exists(platform, address, get_oneagentctl_path(platform))
    assert result.returncode == (0 if installed else 1)


def check_download_directory(
    platform: DeploymentPlatform,
    address: str,
    wrapper: PlatformCommandWrapper,
    exists: bool,
    unix_path: Path,
    windows_path: Path,
) -> None:
    logging.debug("Platform: %s, IP: %s", platform, address)
    download_path: Path = select_by_platform(platform, unix_path, windows_path)
    installer_path = download_path / f"{INSTALLER_PARTIAL_NAME}*"
    assert wrapper.directory_exists(platform, address, download_path).returncode == 0
    assert wrapper.file_exists(platform, address, installer_path).returncode == (0 if exists else 1)
