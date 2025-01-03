import logging
from pathlib import Path, PureWindowsPath

from ansible.constants import TECH_NAME
from command.platform_command_wrapper import PlatformCommandWrapper
from util.common_utils import get_oneagentctl_path, get_platform_argument
from util.constants.common_constants import INSTALLER_SERVER_TOKEN
from util.test_data_types import DeploymentPlatform, DeploymentResult
from util.test_helpers import (
    check_agent_state,
    check_download_directory,
    perform_operation_on_platforms,
    run_deployment,
    set_installer_download_params,
)

UNIX_DOWNLOAD_PATH = Path("/tmp/dyna")
WINDOWS_DOWNLOAD_PATH = PureWindowsPath("C:\\tmp\\dyna")

TECH_NAME_KEY = "orchestration_tech"
TECH_VERSION_KEY = "tech_version"
TECH_SCRIPT_VERSION_KEY = "script_version"

CTL_OPTION_GET_HOST_TAGS = "--get-host-tags"
CTL_OPTION_SET_HOST_TAG = "--set-host-tag"

CTL_OPTION_GET_HOST_PROPERTIES = "--get-host-properties"
CTL_OPTION_SET_HOST_PROPERTY = "--set-host-property"


def _assert_oneagentctl_getter(
    platform: DeploymentPlatform,
    address: str,
    wrapper: PlatformCommandWrapper,
    ctl_param: str,
    expected_values: set[str],
):
    oneagentctl = f"{get_oneagentctl_path(platform)}"
    result = wrapper.run_command(platform, address, oneagentctl, ctl_param)
    assert result.returncode == 0
    assert expected_values == set(result.stdout.strip().splitlines())


def _check_install_args(
    platform: DeploymentPlatform,
    address: str,
    wrapper: PlatformCommandWrapper,
    ansible: str,
) -> None:
    logging.debug("Platform: %s, IP: %s", platform, address)

    oneagentctl = f"{get_oneagentctl_path(platform)}"
    metadata = wrapper.run_command(platform, address, oneagentctl, "--get-deployment-metadata")
    assert metadata.returncode == 0

    params = dict(kv.split("=") for kv in metadata.stdout.strip().splitlines())

    assert params[TECH_VERSION_KEY] is not None
    assert params[TECH_SCRIPT_VERSION_KEY] is not None
    assert params[TECH_NAME_KEY] is not None and params[TECH_NAME_KEY] == ansible


def _check_config_args(
    platform: DeploymentPlatform,
    address: str,
    wrapper: PlatformCommandWrapper,
    expected_tags: set[str],
    expected_properties: set[str],
):
    logging.debug("Platform: %s, IP: %s", platform, address)

    _assert_oneagentctl_getter(platform, address, wrapper, CTL_OPTION_GET_HOST_TAGS, expected_tags)
    _assert_oneagentctl_getter(platform, address, wrapper, CTL_OPTION_GET_HOST_PROPERTIES, expected_properties)


def _check_output_for_secrets(result: DeploymentResult, installer_server_url) -> None:
    for out in result:
        assert INSTALLER_SERVER_TOKEN not in out.stdout
        assert installer_server_url not in out.stderr


def test_basic_installation(runner, configurator, platforms, wrapper, installer_server_url):
    logging.info("Running basic installation test")

    dummy_common_tag = "dummy_common_tag"
    dummy_platform_tag = "dummy_platform_tag"
    dummy_common_property = "dummy_common_key=dummy_common_value"
    dummy_platform_property = "dummy_platform_key=dummy_platform_value"

    set_installer_download_params(configurator, installer_server_url)
    configurator.set_common_parameter(configurator.VALIDATE_DOWNLOAD_CERTS_KEY, False)
    configurator.set_common_parameter(configurator.PRESERVE_INSTALLER_KEY, True)
    configurator.set_common_parameter(
        configurator.INSTALLER_ARGS_KEY,
        [
            f"{CTL_OPTION_SET_HOST_TAG}={dummy_common_tag}",
            f"{CTL_OPTION_SET_HOST_PROPERTY}={dummy_common_property}",
        ],
    )

    for platform, hosts in platforms.items():
        download_dir: Path = get_platform_argument(platform, UNIX_DOWNLOAD_PATH, WINDOWS_DOWNLOAD_PATH)
        configurator.set_platform_parameter(platform, configurator.DOWNLOAD_DIR_KEY, str(download_dir))
        configurator.set_common_parameter(
            configurator.INSTALLER_PLATFORM_ARGS_KEY,
            [
                f"{CTL_OPTION_SET_HOST_TAG}={dummy_platform_tag}",
                f"{CTL_OPTION_SET_HOST_PROPERTY}={dummy_platform_property}",
            ],
        )

    result = run_deployment(runner)

    logging.info("Check if output contains secrets")
    _check_output_for_secrets(result, installer_server_url)

    logging.info("Check if agent is installed")
    perform_operation_on_platforms(platforms, check_agent_state, wrapper, True)

    logging.info("Check if installer was downloaded to correct place and preserved")
    perform_operation_on_platforms(
        platforms,
        check_download_directory,
        wrapper,
        True,
        UNIX_DOWNLOAD_PATH,
        WINDOWS_DOWNLOAD_PATH,
    )

    logging.info("Check if config args were applied correctly")
    perform_operation_on_platforms(
        platforms,
        _check_config_args,
        wrapper,
        {dummy_common_tag, dummy_platform_tag},
        {dummy_common_property, dummy_platform_property},
    )

    logging.info("Check if installer args were passed correctly")
    perform_operation_on_platforms(platforms, _check_install_args, wrapper, TECH_NAME)
