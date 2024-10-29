import logging
import re

from command.platform_command_wrapper import PlatformCommandWrapper
from util.common_utils import get_oneagentctl_path, get_installers
from util.test_data_types import DeploymentPlatform, PlatformCollection
from util.test_helpers import (
    check_agent_state,
    perform_operation_on_platforms,
    set_installer_download_params,
    run_deployment,
)
from util.constants.common_constants import InstallerVersion


def _check_agent_version(
    platform: DeploymentPlatform, address: str, wrapper: PlatformCommandWrapper, version:  str) -> None:
    installed_version = wrapper.run_command(platform, address, f"{get_oneagentctl_path(platform)}", "--version")
    assert installed_version.stdout.strip() == version


def test_upgrade(runner, configurator, platforms, wrapper, installer_server_url):
    logging.info("Running upgrade test")

    set_installer_download_params(configurator, installer_server_url)
    configurator.set_common_parameter(configurator.VALIDATE_DOWNLOAD_CERTS_KEY, False)

    for platform in platforms:
        configurator.set_platform_parameter(platform, configurator.INSTALLER_VERSION_KEY, InstallerVersion.OLD.value)

    run_deployment(runner)

    logging.info("Check if agent is installed")
    perform_operation_on_platforms(platforms, check_agent_state, wrapper, True)

    logging.info("Check if agent has proper version")
    perform_operation_on_platforms(platforms, _check_agent_version, wrapper, InstallerVersion.OLD.value)

    configurator.set_common_parameter(configurator.INSTALLER_VERSION_KEY, "latest")

    run_deployment(runner)

    logging.info("Check if agent is installed")
    perform_operation_on_platforms(platforms, check_agent_state, wrapper, True)

    logging.info("Check if agent has proper version")
    perform_operation_on_platforms(platforms, _check_agent_version, wrapper, InstallerVersion.LATEST.value)
