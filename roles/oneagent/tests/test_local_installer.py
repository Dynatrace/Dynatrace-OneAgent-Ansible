import logging

from ansible.config import AnsibleConfigurator
from ansible.runner import AnsibleRunner
from command.platform_command_wrapper import PlatformCommandWrapper
from constants import (
    UNIX_DOWNLOAD_DIR_PATH,
    WINDOWS_DOWNLOAD_DIR_PATH,
    WORK_INSTALLERS_DIR_PATH,
)
from deployment.deployment_operations import (
    check_agent_state,
    check_download_directory,
    enable_for_system_family,
    get_installers,
    perform_operation_on_platforms,
    run_deployment,
    set_ca_cert_download_params,
)
from deployment.deployment_platform import DeploymentPlatform, PlatformCollection


def test_local_installer(
    runner: AnsibleRunner,
    configurator: AnsibleConfigurator,
    platforms: PlatformCollection,
    wrapper: PlatformCommandWrapper,
    installer_server_url: str,
):
    set_ca_cert_download_params(configurator, installer_server_url)

    for platform in platforms:
        installers_location = WORK_INSTALLERS_DIR_PATH
        latest_installer_name = get_installers(platform.system(), platform.arch(), "latest")[-1]
        configurator.set_platform_parameter(
            platform,
            configurator.LOCAL_INSTALLER_KEY,
            f"{installers_location}/{latest_installer_name}",
        )

    _unused = run_deployment(runner, configurator)

    logging.info("Check if agent is installed")
    perform_operation_on_platforms(platforms, check_agent_state, wrapper, True)

    logging.info("Check if installer was removed")
    perform_operation_on_platforms(
        platforms,
        check_download_directory,
        wrapper,
        False,
        UNIX_DOWNLOAD_DIR_PATH,
        WINDOWS_DOWNLOAD_DIR_PATH,
    )


@enable_for_system_family(family="windows")
def test_windows_installer_directory_is_private(
    runner: AnsibleRunner,
    configurator: AnsibleConfigurator,
    platforms: PlatformCollection,
    wrapper: PlatformCommandWrapper,
    installer_server_url: str,
):
    # The preserved scratch directory is the one the installer was staged in and executed from,
    # so its DACL and owner show whether a standard user could have read, planted or swapped anything
    windows_hosts = platforms[DeploymentPlatform.WINDOWS_X86]

    set_ca_cert_download_params(configurator, installer_server_url)
    configurator.set_common_parameter(configurator.PRESERVE_INSTALLER_KEY, True)
    configurator.set_platform_parameter(
        DeploymentPlatform.WINDOWS_X86, configurator.DOWNLOAD_DIR_KEY, str(WINDOWS_DOWNLOAD_DIR_PATH)
    )
    latest_installer_name = get_installers("windows", "x86", "latest")[-1]
    configurator.set_platform_parameter(
        DeploymentPlatform.WINDOWS_X86,
        configurator.LOCAL_INSTALLER_KEY,
        f"{WORK_INSTALLERS_DIR_PATH}/{latest_installer_name}",
    )

    _unused = run_deployment(runner, configurator)

    logging.info("Check if agent is installed")
    perform_operation_on_platforms({DeploymentPlatform.WINDOWS_X86: windows_hosts}, check_agent_state, wrapper, True)

    logging.info("Check if installer was preserved in the scratch directory")
    perform_operation_on_platforms(
        {DeploymentPlatform.WINDOWS_X86: windows_hosts},
        check_download_directory,
        wrapper,
        True,
        UNIX_DOWNLOAD_DIR_PATH,
        WINDOWS_DOWNLOAD_DIR_PATH,
    )

    logging.info("Check if only SYSTEM and Administrators can access the scratch directory and the installer")
    for address in windows_hosts:
        result = wrapper.windows_command_wrapper.check_private_directories(
            address, WINDOWS_DOWNLOAD_DIR_PATH / "dynatrace-oneagent-*"
        )
        assert result.returncode == 0, result.stdout
