# PYTEST CONFIGURATION FILE
import logging

import pytest

import technology.constants as AnsibleConstants
import technology.util as AnsibleUtil

from command.platform_command_wrapper import PlatformCommandWrapper
from technology.config import AnsibleConfig
from technology.runner import AnsibleRunner
from util.common_utils import prepare_test_dirs
from util.test_data_types import DeploymentPlatform, PlatformCollection, DeploymentResult


USER_KEY = "user"
PASS_KEY = "password"

UTIL_KEY = "util"
RUNNER_KEY = "runner"
WRAPPER_KEY = "wrapper"
CONSTANTS_KEY = "constants"
PLATFORMS_KEY = "platforms"
CONFIGURATOR_KEY = "configurator"


@pytest.fixture(name="_set_up")
def set_up(runner, configurator) -> None:
    logging.info("Preparing test environment")
    prepare_test_dirs()
    configurator.prepare_test_environment()


@pytest.fixture(name="_tear_down")
def tear_down(runner, configurator) -> None:
    # Fixtures are executed one by one after injection
    # Yield prevents cleaning up environment before the actual test is executed
    yield
    logging.info("Cleaning up environment")
    configurator.clear_parameters_section()

    configurator.set_common_parameter(configurator.PACKAGE_STATE_KEY, "absent")

    results: DeploymentResult = runner.run_deployment()
    for result in results:
        if result.returncode != 0:
            logging.error("Failed to clean up environment, output: %s", result.stdout)

    configurator.clear_parameters_section()


def pytest_addoption(parser):
    parser.addoption(f"--{USER_KEY}", type=str, help="Name of the user", required=True)
    parser.addoption(f"--{PASS_KEY}", type=str, help="Password of the user", required=True)

    for platform in DeploymentPlatform:
        parser.addoption(
            f"--{platform.value}", type=str, nargs="+", default=[], help="List of IPs for specified platform"
        )


def pytest_configure():
    logging.basicConfig(
        format="%(asctime)s [deploymentTest] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG,
    )


def pytest_generate_tests(metafunc):
    options = vars(metafunc.config.option)
    for key in [USER_KEY, PASS_KEY]:
        if key in metafunc.fixturenames:
            metafunc.parametrize(key, [options[key]])

    user = options[USER_KEY]
    password = options[PASS_KEY]

    platforms = {}
    deployment_platforms = [e.value for e in DeploymentPlatform]
    for platform, hosts in options.items():
        if platform in deployment_platforms and hosts:
            platforms[DeploymentPlatform.from_str(platform)] = hosts

    wrapper = PlatformCommandWrapper(user, password)

    configurator, runner, util, constants = _create_technology_classes(user, password, platforms, wrapper)

    if CONFIGURATOR_KEY in metafunc.fixturenames:
        metafunc.parametrize(CONFIGURATOR_KEY, [configurator])

    if RUNNER_KEY in metafunc.fixturenames:
        metafunc.parametrize(RUNNER_KEY, [runner])

    if UTIL_KEY in metafunc.fixturenames:
        metafunc.parametrize(UTIL_KEY, [util])

    if CONSTANTS_KEY in metafunc.fixturenames:
        metafunc.parametrize(CONSTANTS_KEY, [constants])

    if PLATFORMS_KEY in metafunc.fixturenames:
        metafunc.parametrize(PLATFORMS_KEY, [platforms])

    if WRAPPER_KEY in metafunc.fixturenames:
        metafunc.parametrize(WRAPPER_KEY, [wrapper])


def _create_technology_classes(
    user: str, password: str, platforms: PlatformCollection, wrapper: PlatformCommandWrapper
):
    return AnsibleConfig(user, password, platforms), AnsibleRunner(user, password), AnsibleUtil, AnsibleConstants
