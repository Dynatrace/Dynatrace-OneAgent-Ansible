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
    get_installers,
    perform_operation_on_platforms,
    run_deployment,
    set_ca_cert_download_params,
)
from deployment.deployment_platform import PlatformCollection


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
