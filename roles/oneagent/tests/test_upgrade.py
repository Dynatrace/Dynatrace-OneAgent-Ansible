import logging
import re

from tests.ansible.config import AnsibleConfigurator
from tests.ansible.runner import AnsibleRunner
from tests.command.platform_command_wrapper import PlatformCommandWrapper
from tests.deployment.deployment_operations import (
    check_agent_state,
    get_installers,
    get_oneagentctl_path,
    perform_operation_on_platforms,
    run_deployment,
    set_installer_download_params,
)
from tests.deployment.deployment_platform import DeploymentPlatform, PlatformCollection, DeploymentResult


def _get_versions_for_platforms(platforms: PlatformCollection, latest: bool) -> dict[DeploymentPlatform, str]:
    versions: dict[DeploymentPlatform, str] = {}
    for platform in platforms:
        installers = get_installers(platform.system(), platform.arch())
        versioned_installer = installers[-1 if latest else 0]
        versions[platform] = re.search(r"\d.\d+.\d+.\d+-\d+", str(versioned_installer)).group()
    return versions


def _check_agent_version(
    platform: DeploymentPlatform,
    address: str,
    wrapper: PlatformCommandWrapper,
    versions: dict[DeploymentPlatform, str],
) -> None:
    installed_version = wrapper.run_command(platform, address, f"{get_oneagentctl_path(platform)}", "--version")
    assert installed_version.stdout.strip() == versions[platform]


def test_upgrade(
    runner: AnsibleRunner,
    configurator: AnsibleConfigurator,
    platforms: PlatformCollection,
    wrapper: PlatformCommandWrapper,
    installer_server_url: str,
):
    logging.info("Running upgrade test")

    set_installer_download_params(configurator, installer_server_url)
    configurator.set_common_parameter(configurator.VALIDATE_DOWNLOAD_CERTS_KEY, False)

    old_versions = _get_versions_for_platforms(platforms, False)
    for platform, version in old_versions.items():
        configurator.set_platform_parameter(platform, configurator.INSTALLER_VERSION_KEY, version)

    _unused = run_deployment(runner)

    logging.info("Check if agent is installed")
    perform_operation_on_platforms(platforms, check_agent_state, wrapper, True)

    logging.info("Check if agent has proper version")
    perform_operation_on_platforms(platforms, _check_agent_version, wrapper, old_versions)

    configurator.set_common_parameter(configurator.INSTALLER_VERSION_KEY, "latest")

     _unused = run_deployment(runner)

    logging.info("Check if agent is installed")
    perform_operation_on_platforms(platforms, check_agent_state, wrapper, True)

    logging.info("Check if agent has proper version")
    new_versions = _get_versions_for_platforms(platforms, True)
    perform_operation_on_platforms(platforms, _check_agent_version, wrapper, new_versions)
