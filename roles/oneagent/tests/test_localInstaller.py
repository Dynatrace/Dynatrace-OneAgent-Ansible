import logging

from ansible.constants import LOCAL_INSTALLERS_LOCATION
from util.common_utils import get_installers
from util.constants.unix_constants import UNIX_DEFAULT_DOWNLOAD_PATH
from util.constants.windows_constants import WINDOWS_DEFAULT_DOWNLOAD_PATH
from util.test_helpers import (
    check_agent_state,
    check_download_directory,
    perform_operation_on_platforms,
    run_deployment,
    set_ca_cert_download_params,
)


def test_local_installer(runner, configurator, platforms, wrapper, installer_server_url):
    logging.info("Running local installer test")

    set_ca_cert_download_params(configurator, installer_server_url)

    for platform, hosts in platforms.items():
        installers_location = LOCAL_INSTALLERS_LOCATION
        latest_installer_name = get_installers(platform.system(), platform.arch(), "latest")[-1]
        configurator.set_platform_parameter(
            platform,
            configurator.LOCAL_INSTALLER_KEY,
            f"{installers_location}/{latest_installer_name}",
        )

    run_deployment(runner)

    logging.info("Check if agent is installed")
    perform_operation_on_platforms(platforms, check_agent_state, wrapper, True)

    logging.info("Check if installer was removed")
    perform_operation_on_platforms(
        platforms,
        check_download_directory,
        wrapper,
        False,
        UNIX_DEFAULT_DOWNLOAD_PATH,
        WINDOWS_DEFAULT_DOWNLOAD_PATH,
    )
