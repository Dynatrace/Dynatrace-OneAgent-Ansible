import functools
import logging
from pathlib import Path
from typing import Callable, Any

from command.platform_command_wrapper import PlatformCommandWrapper

from technology.deployment_config import DeploymentConfig
from technology.deployment_runner import DeploymentRunner
from util.common_utils import get_oneagentctl_path, get_platform_argument
from util.constants.common_constants import INSTALLER_PARTIAL_NAME, HOST_SERVER_ADDRESS, HOST_SERVER_TOKEN
from util.test_data_types import DeploymentPlatform, DeploymentResult, PlatformCollection

CallableOperation = Callable[[DeploymentPlatform, str, Any], None]


def _get_param_by_name(name: str, **kwargs) -> Any:
    assert name in kwargs, f"No '{name}' parameter in parameters list"
    return kwargs[name]


def disable_for_localhost():
    def func_wrapper(func):
        @functools.wraps(func)
        def platforms_wrapper(*args, **kwargs):
            platforms: DeploymentConfig = _get_param_by_name("platforms", **kwargs)
            for _, hosts in platforms.items():
                if any(host == "localhost" for host in hosts):
                    return
            func(*args, **kwargs)

        return platforms_wrapper

    return func_wrapper


def enable_for_family(family: str):
    def func_wrapper(func):
        @functools.wraps(func)
        def params_wrapper(*args, **kwargs):
            config: DeploymentConfig = _get_param_by_name("configurator", **kwargs)
            config.set_deployment_hosts(family)
            func(*args, **kwargs)

        return params_wrapper

    return func_wrapper


def perform_operation_on_platforms(platforms: PlatformCollection, operation: CallableOperation, *args) -> None:
    for platform, hosts in platforms.items():
        for address in hosts:
            operation(platform, address, *args)


def set_installer_download_params(config: DeploymentConfig) -> None:
    config.set_common_parameter(config.ENVIRONMENT_URL_KEY, HOST_SERVER_ADDRESS)
    config.set_common_parameter(config.PAAS_TOKEN_KEY, HOST_SERVER_TOKEN)
    config.set_common_parameter(config.VALIDATE_DOWNLOAD_CERTS_KEY, False)
    for platform in DeploymentPlatform:
        config.set_platform_parameter(platform, config.INSTALLER_ARCH_KEY, platform.arch())


def run_deployment(runner: DeploymentRunner, ignore_errors: bool = False) -> DeploymentResult:
    results = runner.run_deployment()
    logging.info("Deployment finished")
    for result in results:
        logging.debug(f"Exit code: {result.returncode}\nOutput: {result.stdout}, Error: {result.stderr}")

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
