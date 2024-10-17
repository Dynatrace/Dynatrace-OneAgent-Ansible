# PYTEST CONFIGURATION FILE
import logging
import pytest
import shutil
import subprocess
import sys
import os
from pathlib import Path

import technology.constants as AnsibleConstants
import technology.util as AnsibleUtil

from command.platform_command_wrapper import PlatformCommandWrapper
from technology.config import AnsibleConfig
from technology.runner import AnsibleRunner
from util.common_utils import prepare_test_dirs
from util.test_data_types import DeploymentPlatform, PlatformCollection, DeploymentResult
from util.test_helpers import check_agent_state, perform_operation_on_platforms
from util.constants.common_constants import (TEST_DIRECTORY, INSTALLERS_DIRECTORY, INSTALLER_CERTIFICATE_FILE_NAME,
                                             INSTALLER_PRIVATE_KEY_FILE_NAME, INSTALLERS_RESOURCE_DIR,
                                             COMPONENT_TEST_BASE, SERVER_DIRECTORY, LOG_DIRECTORY, InstallerVersion)
from util.ssl_certificate_generator import SSLCertificateGenerator



USER_KEY = "user"
PASS_KEY = "password"

UTIL_KEY = "util"
RUNNER_KEY = "runner"
WRAPPER_KEY = "wrapper"
CONSTANTS_KEY = "constants"
PLATFORMS_KEY = "platforms"
CONFIGURATOR_KEY = "configurator"


@pytest.fixture(scope="session", autouse=True)
def create_test_directories() -> None:
    shutil.rmtree(COMPONENT_TEST_BASE, ignore_errors=True)
    os.makedirs(INSTALLERS_DIRECTORY, exist_ok=True)
    os.makedirs(SERVER_DIRECTORY, exist_ok=True)
    os.makedirs(LOG_DIRECTORY, exist_ok=True)


def get_file_content(path: Path) -> list[str]:
    with path.open("r") as f:
        return f.readlines()


def replace_tag(source: list[str], old: str, new: str) -> list[str]:
    return [line.replace(old, new) for line in source]


def sign_installer(installer: list[str]) -> list[str]:
    cmd = ["openssl", "cms", "-sign",
           "-signer", f"{INSTALLERS_DIRECTORY / INSTALLER_CERTIFICATE_FILE_NAME}",
           "-inkey", f"{INSTALLERS_DIRECTORY / INSTALLER_PRIVATE_KEY_FILE_NAME}"]

    proc = subprocess.run(cmd, input=f"{''.join(installer)}", encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        logging.error(f"Failed to sign installer: {proc.stdout}")
        sys.exit(1)

    signed_installer = proc.stdout.splitlines()
    delimiter = next(l for l in signed_installer if l.startswith("----"))
    index = signed_installer.index(delimiter)
    signed_installer = signed_installer[index + 1:]

    custom_delimiter = "----SIGNED-INSTALLER"
    return [ f"{l}\n" if not l.startswith(delimiter) else f"{l.replace(delimiter, custom_delimiter)}\n" for l in signed_installer]


def prepend(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line + '\n' + content)


def save_file(data: list[str], path: Path) -> None:
    with path.open("w") as log:
        log.writelines(data)

@pytest.fixture(scope="session", autouse=True)
def prepare_installers() -> None:
    logging.info("Preparing installers...")

    uninstall_template = get_file_content(INSTALLERS_RESOURCE_DIR / "uninstall.sh")
    uninstall_code = replace_tag(uninstall_template, "$", r"\$")

    oneagentctl_template = get_file_content(INSTALLERS_RESOURCE_DIR / "oneagentctl.sh")
    oneagentctl_code = replace_tag(oneagentctl_template, "$", r"\$")

    installer_partial_name = "Dynatrace-OneAgent-Linux"
    installer_template = get_file_content(INSTALLERS_RESOURCE_DIR / f"{installer_partial_name}.sh")
    installer_template = replace_tag(installer_template, "##UNINSTALL_CODE##", "".join(uninstall_code))
    installer_template = replace_tag(installer_template, "##ONEAGENTCTL_CODE##", "".join(oneagentctl_code))

    generator = SSLCertificateGenerator(
        country_name="US",
        state_name="California",
        locality_name="San Francisco",
        organization_name="Dynatrace",
        common_name="localhost"
    )
    generator.generate_and_save(f"{INSTALLERS_DIRECTORY / INSTALLER_PRIVATE_KEY_FILE_NAME}",
                                f"{INSTALLERS_DIRECTORY / INSTALLER_CERTIFICATE_FILE_NAME}")

    for version in InstallerVersion:
        installer_code = replace_tag(installer_template, "##VERSION##", version.value)
        installer_code = sign_installer(installer_code)
        save_file(installer_code, INSTALLERS_DIRECTORY / f"{installer_partial_name}-{version.value}.sh")

    prepend(INSTALLERS_DIRECTORY / f"{installer_partial_name}-{InstallerVersion.MALFORMED.value}.sh", "Malformed line")


@pytest.fixture(scope="session", autouse=True)
def run_server(request) -> subprocess.Popen:
    logging.info(f"Running server...")
    proc = subprocess.Popen([sys.executable, "-m", "server"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", env={"PYTHONPATH": f"{Path(__file__).resolve().parent}"})

    yield

    proc.terminate()
    with Path(LOG_DIRECTORY / "server.log").open("a") as log:
        log.writelines(proc.stdout)


@pytest.fixture(autouse=True)
def handle_test_environment(runner, configurator, platforms, wrapper) -> None:
    logging.info("Preparing test environment")
    prepare_test_dirs()
    configurator.prepare_test_environment()

    yield

    logging.info("Cleaning up environment")
    configurator.clear_parameters_section()

    configurator.set_common_parameter(configurator.PACKAGE_STATE_KEY, "absent")

    logging.info("Check if agent is uninstalled")
    perform_operation_on_platforms(platforms, check_agent_state, wrapper, False)

    results: DeploymentResult = runner.run_deployment()
    for result in results:
        if result.returncode != 0:
            logging.error("Failed to clean up environment, output: %s", result.stdout)

    shutil.rmtree("/var/lib/dynatrace", ignore_errors=True)

    configurator.clear_parameters_section()


def pytest_addoption(parser):
    parser.addoption(f"--{USER_KEY}", type=str, help="Name of the user", required=False)
    parser.addoption(f"--{PASS_KEY}", type=str, help="Password of the user", required=False)

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
