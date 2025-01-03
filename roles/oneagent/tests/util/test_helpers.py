import functools
import logging
from pathlib import Path
from typing import Any, Callable

from ansible.config import AnsibleConfig
from ansible.runner import AnsibleRunner
from command.platform_command_wrapper import PlatformCommandWrapper
from util.common_utils import get_oneagentctl_path, get_platform_argument
from util.constants.common_constants import (
    INSTALLER_CERTIFICATE_FILE_NAME,
    INSTALLER_PARTIAL_NAME,
    INSTALLER_SERVER_TOKEN,
    SERVER_CERTIFICATE_FILE_NAME,
    SERVER_DIRECTORY,
)
from util.test_data_types import DeploymentPlatform, DeploymentResult, PlatformCollection

CallableOperation = Callable[[DeploymentPlatform, str, Any], None]


def _get_param_by_name(name: str, **kwargs) -> Any:
    assert name in kwargs, f"No '{name}' parameter in parameters list"
    return kwargs[name]


def enable_for_system_family(family: str) -> Callable:
    def func_wrapper(func):
        @functools.wraps(func)
        def params_wrapper(*args, **kwargs):
            config: AnsibleConfig = _get_param_by_name("configurator", **kwargs)
            platforms: PlatformCollection = _get_param_by_name("platforms", **kwargs)
            if any(p.family() == family for p in platforms.keys()):
                config.set_deployment_hosts(family)
                func(*args, **kwargs)
            else:
                logging.info("Skipping test for specified platform")

        return params_wrapper

    return func_wrapper


def perform_operation_on_platforms(platforms: PlatformCollection, operation: CallableOperation, *args) -> None:
    for platform, hosts in platforms.items():
        for address in hosts:
            operation(platform, address, *args)


def set_ca_cert_download_params(config: AnsibleConfig, installer_server_url: str) -> None:
    config.set_common_parameter(
        config.CA_CERT_DOWNLOAD_URL_KEY, f"{installer_server_url}/{INSTALLER_CERTIFICATE_FILE_NAME}"
    )
    config.set_common_parameter(config.CA_CERT_DOWNLOAD_CERT_KEY, f"{SERVER_DIRECTORY / SERVER_CERTIFICATE_FILE_NAME}")
    config.set_common_parameter(config.FORCE_CERT_DOWNLOAD_KEY, True)


def set_installer_download_params(config: AnsibleConfig, installer_server_url: str) -> None:
    config.set_common_parameter(config.ENVIRONMENT_URL_KEY, installer_server_url)
    config.set_common_parameter(config.PAAS_TOKEN_KEY, INSTALLER_SERVER_TOKEN)
    config.set_common_parameter(
        config.INSTALLER_DOWNLOAD_CERT_KEY, f"{SERVER_DIRECTORY / SERVER_CERTIFICATE_FILE_NAME}"
    )
    for platform in DeploymentPlatform:
        config.set_platform_parameter(platform, config.INSTALLER_ARCH_KEY, platform.arch())

    set_ca_cert_download_params(config, installer_server_url)


def run_deployment(runner: AnsibleRunner, ignore_errors: bool = False) -> DeploymentResult:
    results = runner.run_deployment()
    logging.info("Deployment finished")
    for result in results:
        logging.debug("Exit code: %s\nOutput: %s, Error: %s", result.returncode, result.stdout, result.stderr)

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
    assert result.returncode == 0 if installed else 1


def check_download_directory(
    platform: DeploymentPlatform,
    address: str,
    wrapper: PlatformCommandWrapper,
    exists: bool,
    unix_path: Path,
    windows_path: Path,
) -> None:
    logging.debug("Platform: %s, IP: %s", platform, address)
    download_path: Path = get_platform_argument(platform, unix_path, windows_path)
    installer_path = download_path / f"{INSTALLER_PARTIAL_NAME}*"
    assert wrapper.directory_exists(platform, address, download_path).returncode == 0
    assert wrapper.file_exists(platform, address, installer_path).returncode == 0 if exists else 1
