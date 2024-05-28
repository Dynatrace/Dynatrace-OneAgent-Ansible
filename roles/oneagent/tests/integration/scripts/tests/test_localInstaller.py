import logging

from util.common_utils import get_installers
from util.constants.unix_constants import UNIX_DEFAULT_DOWNLOAD_PATH
from util.constants.windows_constants import WINDOWS_DEFAULT_DOWNLOAD_PATH
from util.test_helpers import (
    check_agent_state,
    check_download_directory,
    perform_operation_on_platforms,
    run_deployment,
)


def test_local_installer(_set_up, runner, configurator, constants, platforms, wrapper, _tear_down):
    logging.info("Running local installer test")

    for platform, _ in platforms.items():
        installers_location = constants.LOCAL_INSTALLERS_LOCATION
        latest_installer_name = get_installers(platform.system(), platform.arch(), "latest")[-1]
        configurator.set_platform_parameter(
            platform, configurator.LOCAL_INSTALLER_KEY, f"{installers_location}/{latest_installer_name}"
        )

    run_deployment(runner)

    logging.info("Check if agent is installed")
    perform_operation_on_platforms(platforms, check_agent_state, wrapper, True)

    logging.info("Check if installer was removed")
    perform_operation_on_platforms(
        platforms, check_download_directory, wrapper, False, UNIX_DEFAULT_DOWNLOAD_PATH, WINDOWS_DEFAULT_DOWNLOAD_PATH
    )
