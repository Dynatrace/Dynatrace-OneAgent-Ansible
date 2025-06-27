# PYTEST CONFIGURATION FILE
import logging
import os
import shutil
import time
from collections.abc import Generator

import pytest
import requests
from pytest import FixtureRequest, Metafunc, Parser
from tests.ansible.config import AnsibleConfigurator
from tests.ansible.runner import AnsibleRunner
from tests.command.platform_command_wrapper import PlatformCommandWrapper
from tests.constants import (
    TEST_RUN_DIR_PATH,
    WORK_DIR_PATH,
    WORK_INSTALLERS_DIR_PATH,
    WORK_SERVER_DIR_PATH,
)
from tests.deployment.deployment_operations import (
    check_agent_state,
    perform_operation_on_platforms,
    prepare_test_dirs,
)
from tests.deployment.deployment_platform import (
    DeploymentPlatform,
    DeploymentResult,
    PlatformCollection,
)
from tests.deployment.installer_fetching import (
    download_installers,
    download_signature,
    generate_installers,
)
from tests.installer_server.server import run_server

# Command line options
USER_KEY = "user"
PASS_KEY = "password"
TENANT_KEY = "tenant"
TENANT_TOKEN_KEY = "tenant_token"
PRESERVE_INSTALLERS_KEY = "preserve_installers"

# Ini file configuration
CA_CERT_URL_KEY = "dynatrace_ca_cert_url"

RUNNER_KEY = "runner"
WRAPPER_KEY = "wrapper"
CONSTANTS_KEY = "constants"
PLATFORMS_KEY = "platforms"
CONFIGURATOR_KEY = "configurator"


def is_local_deployment(platforms: PlatformCollection) -> bool:
    return any("localhost" in hosts for hosts in platforms.values())


def parse_platforms_from_options(options: dict[str, list[str]]) -> PlatformCollection:
    platforms: PlatformCollection = {}
    deployment_platforms = [e.value for e in DeploymentPlatform]

    for key, hosts in options.items():
        if key in deployment_platforms and hosts:
            if "localhost" in hosts:
                return {DeploymentPlatform.from_str(key): hosts}
            platforms[DeploymentPlatform.from_str(key)] = hosts
    return platforms


def try_connect_to_server(url: str):
    try:
        response = requests.get(url, verify=False)
        logging.info("Installer server started successfully")
        return response
    except requests.ConnectionError:
        time.sleep(0.5)
        return None


def wait_for_server_or_fail(url: str, max_attempts: int = 10) -> bool:
    for _attempt in range(max_attempts):
        if try_connect_to_server(url) is not None:
            return True
    return False


@pytest.fixture(scope="session", autouse=True)
def create_test_directories(request: FixtureRequest) -> None:
    logging.info("Creating working directories for tests")
    if request.config.getoption(PRESERVE_INSTALLERS_KEY):
        logging.info("Installers will be preserved, no installers will be generated")
        shutil.rmtree(WORK_SERVER_DIR_PATH, ignore_errors=True)
        shutil.rmtree(WORK_DIR_PATH, ignore_errors=True)
    else:
        shutil.rmtree(TEST_RUN_DIR_PATH, ignore_errors=True)

    os.makedirs(WORK_INSTALLERS_DIR_PATH, exist_ok=True)
    os.makedirs(WORK_SERVER_DIR_PATH, exist_ok=True)
    os.makedirs(WORK_DIR_PATH, exist_ok=True)


@pytest.fixture(scope="session", autouse=True)
def prepare_installers(request: FixtureRequest) -> None:
    logging.info("Preparing installers...")
    tenant = request.config.getoption(TENANT_KEY)
    tenant_token = request.config.getoption(TENANT_TOKEN_KEY)
    preserve_installers = request.config.getoption(PRESERVE_INSTALLERS_KEY)
    cert_url = str(request.config.getini(CA_CERT_URL_KEY))

    if preserve_installers:
        logging.info("Skipping installers preparation...")
        return

    if is_local_deployment(request.config.platforms):
        logging.info("Generating installers...")
        if not generate_installers():
            pytest.exit("Generating installers failed")
    elif tenant and tenant_token:
        logging.info("Downloading installers and signature...")
        if not download_signature(cert_url) or not download_installers(tenant, tenant_token, request.config.platforms):
            pytest.exit("Downloading installers and signature failed")
    else:
        pytest.exit("No tenant or tenant token provided, cannot download installers")


@pytest.fixture(scope="session", autouse=True)
def installer_server_url() -> Generator[str, None, None]:
    port = 8021
    ipaddress = "127.0.0.1"
    url = f"https://{ipaddress}:{port}"

    logging.info("Running installer server on %s", url)

    server = run_server(ipaddress, port)
    for _unused in server:
        break

    if not wait_for_server_or_fail(url):
        pytest.exit("Failed to start installer server")

    yield url

    logging.info("Stopping installer server")
    for _unused in server:
        break
    logging.info("Installer server has stopped")


@pytest.fixture(autouse=True)
def handle_test_environment(
    request,
    runner: AnsibleRunner,
    configurator: AnsibleConfigurator,
    platforms: PlatformCollection,
    wrapper: PlatformCommandWrapper,
) -> Generator[None, None, None]:
    logging.info("Preparing test environment")
    prepare_test_dirs(WORK_DIR_PATH / request.module.__name__ / request.node.originalname)

    yield

    logging.info("Cleaning up environment")
    configurator.set_common_parameter(configurator.PACKAGE_STATE_KEY, "absent")

    results: DeploymentResult = runner.run_deployment(configurator)
    for result in results:
        if result.returncode != 0:
            logging.error("Failed to clean up environment, exit code: %d", result.returncode)

    logging.info("Check if agent is uninstalled")
    perform_operation_on_platforms(platforms, check_agent_state, wrapper, False)

    shutil.rmtree("/var/lib/dynatrace", ignore_errors=True)


def pytest_addoption(parser: Parser) -> None:
    parser.addini(CA_CERT_URL_KEY, type="string", help="Url to CA certificate for downloading installers")

    parser.addoption(f"--{USER_KEY}", type=str, help="Name of the user", required=False)
    parser.addoption(f"--{PASS_KEY}", type=str, help="Password of the user", required=False)
    parser.addoption(
        f"--{TENANT_KEY}",
        type=str,
        help="Tenant URL for downloading installer",
        required=False,
    )
    parser.addoption(
        f"--{TENANT_TOKEN_KEY}",
        type=str,
        help="API key for downloading installer",
        required=False,
    )
    parser.addoption(
        f"--{PRESERVE_INSTALLERS_KEY}",
        type=bool,
        default=False,
        help="Preserve installers after test run",
        required=False,
    )

    for platform in DeploymentPlatform:
        parser.addoption(
            f"--{platform.value}",
            type=str,
            nargs="+",
            default=[],
            help="List of IPs for specified platform",
        )


def pytest_configure(config) -> None:
    config.platforms = parse_platforms_from_options(vars(config.option))


def pytest_generate_tests(metafunc: Metafunc) -> None:
    options = vars(metafunc.config.option)
    for key in [USER_KEY, PASS_KEY]:
        if key in metafunc.fixturenames:
            metafunc.parametrize(key, [options[key]])

    user: str = options[USER_KEY]
    password: str = options[PASS_KEY]

    wrapper = PlatformCommandWrapper(user, password)
    configurator = AnsibleConfigurator(user, password, metafunc.config.platforms)
    runner = AnsibleRunner(WORK_DIR_PATH / metafunc.module.__name__ / metafunc.function.__name__, user, password)

    if CONFIGURATOR_KEY in metafunc.fixturenames:
        metafunc.parametrize(CONFIGURATOR_KEY, [configurator])

    if RUNNER_KEY in metafunc.fixturenames:
        metafunc.parametrize(RUNNER_KEY, [runner])

    if PLATFORMS_KEY in metafunc.fixturenames:
        metafunc.parametrize(PLATFORMS_KEY, [metafunc.config.platforms])

    if WRAPPER_KEY in metafunc.fixturenames:
        metafunc.parametrize(WRAPPER_KEY, [wrapper])


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_setup(item):
    config = item.config
    logging_plugin = config.pluginmanager.get_plugin("logging-plugin")
    logging_plugin.set_log_path(WORK_DIR_PATH / item._request.module.__name__ / item._request.node.originalname / "test.log")

    yield
