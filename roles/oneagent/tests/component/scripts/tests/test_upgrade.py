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


def _get_versions_for_platforms(platforms: PlatformCollection, latest: bool) -> dict[DeploymentPlatform, str]:
    versions: dict[DeploymentPlatform, str] = {}
    for platform, _ in platforms.items():
        installers = get_installers(platform.system(), platform.arch())
        versioned_installer = installers[-1 if latest else 0]
        versions[platform] = re.search(r"\d.\d+.\d+.\d+-\d+", str(versioned_installer)).group()
    return versions


def _check_agent_version(
    platform: DeploymentPlatform, address: str, wrapper: PlatformCommandWrapper, versions: dict[DeploymentPlatform, str]
) -> None:
    installed_version = wrapper.run_command(platform, address, f"{get_oneagentctl_path(platform)}", "--version")
    assert installed_version.stdout.strip() == versions[platform]


def test_versioned_installation(_set_up, runner, configurator, platforms, wrapper):
    logging.info("Running versioned installation test")

    set_installer_download_params(configurator)
    configurator.set_common_parameter(configurator.VERIFY_SIGNATURE_KEY, False)

    versions = _get_versions_for_platforms(platforms, False)
    for platform, version in versions.items():
        configurator.set_platform_parameter(platform, configurator.INSTALLER_VERSION_KEY, version)

    run_deployment(runner)

    logging.info("Check if agent is installed")
    perform_operation_on_platforms(platforms, check_agent_state, wrapper, True)

    logging.info("Check if agent has proper version")
    perform_operation_on_platforms(platforms, _check_agent_version, wrapper, versions)


def test_upgrade(_set_up, runner, configurator, platforms, wrapper, _tear_down):
    logging.info("Running upgrade test")

    configurator.clear_parameters_section()
    set_installer_download_params(configurator)
    configurator.set_common_parameter(configurator.INSTALLER_VERSION_KEY, "latest")
    configurator.set_common_parameter(configurator.VERIFY_SIGNATURE_KEY, False)

    versions = _get_versions_for_platforms(platforms, True)

    run_deployment(runner)

    logging.info("Check if agent is installed")
    perform_operation_on_platforms(platforms, check_agent_state, wrapper, True)

    logging.info("Check if agent has proper version")
    perform_operation_on_platforms(platforms, _check_agent_version, wrapper, versions)
