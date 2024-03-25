# PYTEST CONFIGURATION FILE
import logging
import os
import shutil
import socket
import requests
import time
from pathlib import Path
from typing import Any
from threading import Thread, Event

import pytest
from ansible.config import AnsibleConfig
from ansible.runner import AnsibleRunner
from command.platform_command_wrapper import PlatformCommandWrapper
from constants import (
    TEST_RUN_DIR_PATH,
    WORK_DIR_PATH,
    WORK_INSTALLERS_DIR_PATH,
    WORK_LOGS_DIR_PATH,
    WORK_SERVER_DIR_PATH,
)
from deployment.deployment_operations import (
    check_agent_state,
    perform_operation_on_platforms,
    prepare_test_dirs,
)
from deployment.deployment_platform import (
    DeploymentPlatform,
    DeploymentResult,
    PlatformCollection,
)
from deployment.installer_fetching import (
    download_installers,
    download_signature,
    generate_installers,
)
from installer_server.server import run_server

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
    return any("localhost" in hosts for platform, hosts in platforms.items())


def parse_platforms_from_options(options: dict[str, Any]) -> PlatformCollection:
    platforms: PlatformCollection = {}
    deployment_platforms = [e.value for e in DeploymentPlatform]

    for key, hosts in options.items():
        if key in deployment_platforms and hosts:
            if "localhost" in hosts:
                logging.info("Local deployment detected for %s, only this host will be used", key)
                return {DeploymentPlatform.from_str(key): hosts}
            platforms[DeploymentPlatform.from_str(key)] = hosts
    return platforms


def output_installer_server_log(proc):
    with Path(WORK_LOGS_DIR_PATH / "installer_server.log").open("a") as logfile:
        logfile.writelines(proc.stdout)
        logfile.writelines(proc.stderr)


def try_connect_to_server(url):
    try:
        response = requests.get(url, verify=False)
        logging.info("Installer server started successfully")
        return response
    except requests.ConnectionError:
        time.sleep(0.5)
        return None


def wait_for_server_or_fail(url, max_attempts=10):
    for attempt in range(max_attempts):
        result = try_connect_to_server(url)
        if result is not None:
            return True
    return False


@pytest.fixture(scope="session", autouse=True)
def create_test_directories(request) -> None:
    if request.config.getoption(PRESERVE_INSTALLERS_KEY):
        logging.info("Installers will be preserved, no installers will be generated")
        shutil.rmtree(WORK_SERVER_DIR_PATH, ignore_errors=True)
        shutil.rmtree(WORK_LOGS_DIR_PATH, ignore_errors=True)
        shutil.rmtree(WORK_DIR_PATH, ignore_errors=True)
    else:
        shutil.rmtree(TEST_RUN_DIR_PATH, ignore_errors=True)

    os.makedirs(WORK_INSTALLERS_DIR_PATH, exist_ok=True)
    os.makedirs(WORK_SERVER_DIR_PATH, exist_ok=True)
    os.makedirs(WORK_LOGS_DIR_PATH, exist_ok=True)


@pytest.fixture(scope="session", autouse=True)
def prepare_installers(request) -> None:
    logging.info("Preparing installers...")
    tenant = request.config.getoption(TENANT_KEY)
    tenant_token = request.config.getoption(TENANT_TOKEN_KEY)
    preserve_installers = request.config.getoption(PRESERVE_INSTALLERS_KEY)
    platforms = parse_platforms_from_options(vars(request.config.option))

    cert_url = request.config.getini(CA_CERT_URL_KEY)

    if preserve_installers:
        logging.info("Skipping installers preparation...")
        return

    if is_local_deployment(platforms):
        logging.info("Generating installers...")
        if not generate_installers():
            pytest.exit("Generating installers failed")
    elif tenant and tenant_token:
        logging.info("Downloading installers and signature...")
        if not download_signature(cert_url) or not download_installers(tenant, tenant_token, platforms):
            pytest.exit("Downloading installers and signature failed")
    else:
        pytest.exit("No tenant or tenant token provided, cannot download installers")


@pytest.fixture(scope="session", autouse=True)
def installer_server_url(request) -> None:
    port = 8021
    ipaddress = socket.gethostbyname(socket.gethostname())
    url = f"https://{ipaddress}:{port}"

    logging.info("Running installer server on %s...", url)

    stop_event = Event()
    server_thread = Thread(
        target=run_server, args=(ipaddress, port, WORK_LOGS_DIR_PATH / "installer_server.log", stop_event), daemon=True
    )
    server_thread.start()

    if not wait_for_server_or_fail(url):
        pytest.exit("Failed to start installer server")

    yield url

    logging.info("Stopping installer server...")
    stop_event.set()
    server_thread.join()


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


def pytest_addoption(parser) -> None:
    parser.addini(CA_CERT_URL_KEY, "Url to CA certificate for downloading installers")

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


def pytest_configure() -> None:
    logging.basicConfig(
        format="%(asctime)s [deploymentTest] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG,
    )


def pytest_generate_tests(metafunc) -> None:
    options = vars(metafunc.config.option)
    for key in [USER_KEY, PASS_KEY]:
        if key in metafunc.fixturenames:
            metafunc.parametrize(key, [options[key]])

    user = options[USER_KEY]
    password = options[PASS_KEY]
    platforms = parse_platforms_from_options(options)

    wrapper = PlatformCommandWrapper(user, password)
    configurator = AnsibleConfig(user, password, platforms)
    runner = AnsibleRunner(user, password)

    if CONFIGURATOR_KEY in metafunc.fixturenames:
        metafunc.parametrize(CONFIGURATOR_KEY, [configurator])

    if RUNNER_KEY in metafunc.fixturenames:
        metafunc.parametrize(RUNNER_KEY, [runner])

    if PLATFORMS_KEY in metafunc.fixturenames:
        metafunc.parametrize(PLATFORMS_KEY, [platforms])

    if WRAPPER_KEY in metafunc.fixturenames:
        metafunc.parametrize(WRAPPER_KEY, [wrapper])
