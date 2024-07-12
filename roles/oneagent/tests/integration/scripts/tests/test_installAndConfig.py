import logging
from pathlib import Path, PureWindowsPath
from typing import Set

from command.platform_command_wrapper import PlatformCommandWrapper
from util.common_utils import get_oneagentctl_path, get_platform_argument
from util.constants.common_constants import HOST_SERVER_ADDRESS, HOST_SERVER_TOKEN
from util.test_data_types import DeploymentPlatform, DeploymentResult
from util.test_helpers import (
    check_agent_state,
    check_download_directory,
    set_installer_download_params,
    perform_operation_on_platforms,
    run_deployment,
)

UNIX_DOWNLOAD_PATH = Path("/tmp/dyna")
WINDOWS_DOWNLOAD_PATH = PureWindowsPath("C:\\tmp\\dyna")

TECH_NAME_KEY = "orchestration_tech"
TECH_VERSION_KEY = "tech_version"
TECH_SCRIPT_VERSION_KEY = "script_version"

INSTALLER_TAG = "install_tag"
INSTALLER_PROPERTY = "install_prop1=install_1"
PLATFORM_TAG = "platform_install_tag"
PLATFORM_PROPERTY = "platform_install_property"
CONFIG_INSTALL_TAG = "config_install_tag"
CONFIG_INSTALL_PROPERTY = "install_prop2=config_install_prop"
CONFIG_INTENDED_TAG = "config_intended_tag"
CONFIG_INTENDED_PROPERTY = "install_prop2=config_intended_prop"

CTL_TAGS_GETTER = "--get-host-tags"
CTL_PROPERTIES_GETTER = "--get-host-properties"

INSTALLER_ARGS = [f'--set-host-tag="{INSTALLER_TAG}"', f'--set-host-property="{INSTALLER_PROPERTY}"']
INSTALLER_PLATFORM_ARGS = [f'--set-host-tag="{PLATFORM_TAG}"', f'--set-host-property="{PLATFORM_PROPERTY}"']
CONFIG_INSTALL_ARGS = [f'--set-host-tag="{CONFIG_INSTALL_TAG}"', f'--set-host-property="{CONFIG_INSTALL_PROPERTY}"']
CONFIG_INTENDED_ARGS = [f'--set-host-tag="{CONFIG_INTENDED_TAG}"', f'--set-host-property="{CONFIG_INTENDED_PROPERTY}"']


def _assert_oneagentctl_getter(
    platform: DeploymentPlatform,
    address: str,
    wrapper: PlatformCommandWrapper,
    ctl_param: str,
    expected_values: Set[str],
):
    oneagentctl = f"{get_oneagentctl_path(platform)}"
    tags = wrapper.run_command(platform, address, oneagentctl, ctl_param)
    assert tags.returncode == 0 and expected_values == set(tags.stdout.strip().splitlines())


def _check_install_args(
    platform: DeploymentPlatform, address: str, wrapper: PlatformCommandWrapper, technology: str
) -> None:
    logging.debug("Platform: %s, IP: %s", platform, address)

    _assert_oneagentctl_getter(platform, address, wrapper, CTL_TAGS_GETTER, {INSTALLER_TAG, PLATFORM_TAG})
    _assert_oneagentctl_getter(
        platform, address, wrapper, CTL_PROPERTIES_GETTER, {INSTALLER_PROPERTY, PLATFORM_PROPERTY}
    )

    oneagentctl = f"{get_oneagentctl_path(platform)}"
    metadata = wrapper.run_command(platform, address, oneagentctl, "--get-deployment-metadata")
    assert metadata.returncode == 0

    params = dict(kv.split("=") for kv in metadata.stdout.strip().splitlines())
    assert params[TECH_VERSION_KEY] is not None
    assert params[TECH_SCRIPT_VERSION_KEY] is not None
    assert params[TECH_NAME_KEY] is not None and params[TECH_NAME_KEY] == technology


def _check_config_args(platform: DeploymentPlatform, address: str, wrapper: PlatformCommandWrapper, expected_tags: Set[str],
                       expected_properties: Set[str]):
    logging.debug("Platform: %s, IP: %s", platform, address)

    _assert_oneagentctl_getter(platform, address, wrapper, CTL_TAGS_GETTER, expected_tags)
    _assert_oneagentctl_getter(platform, address, wrapper, CTL_PROPERTIES_GETTER, expected_properties)


# noinspection PyUnusedLocal
def _check_output_for_secrets(result: DeploymentResult) -> None:
    for out in result:
        assert HOST_SERVER_TOKEN not in out.stdout
        assert HOST_SERVER_ADDRESS not in out.stderr


def test_basic_installation(_set_up, runner, configurator, constants, platforms, wrapper):
    logging.info("Running basic installation test")

    set_installer_download_params(configurator) 
    configurator.set_common_parameter(configurator.PRESERVE_INSTALLER_KEY, True)
    configurator.set_common_parameter(configurator.INSTALLER_ARGS_KEY, INSTALLER_ARGS)
    configurator.set_common_parameter(configurator.VERIFY_SIGNATURE_KEY, False)

    for platform, _ in platforms.items():
        download_dir: Path = get_platform_argument(platform, UNIX_DOWNLOAD_PATH, WINDOWS_DOWNLOAD_PATH)
        configurator.set_platform_parameter(platform, configurator.DOWNLOAD_DIR_KEY, str(download_dir))
        configurator.set_platform_parameter(platform, configurator.INSTALLER_PLATFORM_ARGS_KEY, INSTALLER_PLATFORM_ARGS)

    result = run_deployment(runner)

    logging.info("Check if output contains secrets")
    _check_output_for_secrets(result)

    logging.info("Check if agent is installed")
    perform_operation_on_platforms(platforms, check_agent_state, wrapper, True)

    logging.info("Check if installer was downloaded to correct place and preserved")
    perform_operation_on_platforms(
        platforms, check_download_directory, wrapper, True, UNIX_DOWNLOAD_PATH, WINDOWS_DOWNLOAD_PATH
    )

    logging.info("Check if installer args were passed correctly")
    perform_operation_on_platforms(platforms, _check_install_args, wrapper, constants.TECH_NAME)


def test_oneagentctl_installation_config(_set_up, runner, configurator, platforms, wrapper):
    logging.info("Running oneagentctl config test")

    configurator.clear_parameters_section()
    set_installer_download_params(configurator)
    configurator.set_common_parameter(configurator.INSTALLER_ARGS_KEY, CONFIG_INSTALL_ARGS)
    configurator.set_common_parameter(configurator.VERIFY_SIGNATURE_KEY, False)

    run_deployment(runner)

    logging.info("Check if config args were applied correctly")
    expected_tags = {INSTALLER_TAG, PLATFORM_TAG, CONFIG_INSTALL_TAG}
    expected_properties = {PLATFORM_PROPERTY, CONFIG_INSTALL_PROPERTY, INSTALLER_PROPERTY}
    perform_operation_on_platforms(platforms, _check_config_args, wrapper, expected_tags, expected_properties)


# noinspection PyUnusedLocal
def test_oneagentctl_intended_config(_set_up, runner, configurator, platforms, wrapper):
    logging.info("Running oneagentctl config test")

    configurator.clear_parameters_section()
    configurator.set_common_parameter(configurator.INSTALLER_ARGS_KEY, CONFIG_INTENDED_ARGS)
    configurator.set_common_parameter(configurator.VERIFY_SIGNATURE_KEY, False)

    run_deployment(runner)

    logging.info("Check if config args were applied correctly")
    expected_tags = {INSTALLER_TAG, PLATFORM_TAG, CONFIG_INSTALL_TAG, CONFIG_INTENDED_TAG}
    expected_properties = {PLATFORM_PROPERTY, CONFIG_INTENDED_PROPERTY, INSTALLER_PROPERTY}

    perform_operation_on_platforms(platforms, _check_config_args, wrapper, expected_tags, expected_properties)

#
# def test_uninstall(_set_up, runner, configurator, platforms, wrapper):
#     logging.info("Running uninstall test")
#
#     configurator.set_common_parameter(configurator.PACKAGE_STATE_KEY, "absent")
#
#     run_deployment(runner)
#
#     logging.info("Check if agent is uninstalled")
#     perform_operation_on_platforms(platforms, check_agent_state, wrapper, False)
