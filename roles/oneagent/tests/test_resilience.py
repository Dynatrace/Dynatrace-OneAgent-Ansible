import logging
import re

import pytest
from ansible.constants import ERROR_MESSAGES_FILE, FAILED_DEPLOYMENT_EXIT_CODE, TEST_SIGNATURE_FILE, VARIABLE_PREFIX
from util.common_utils import read_yaml_file
from util.test_data_types import DeploymentResult
from util.test_helpers import enable_for_system_family, run_deployment, set_installer_download_params

DOWNLOAD_DIR_CONTAINS_SPACES_KEY = "download_dir_contains_spaces"
DOWNLOAD_FAILED_KEY = "failed_download"
INSTALL_DIR_CONTAINS_SPACES_KEY = "install_dir_contains_spaces"
LOCAL_INSTALLER_NOT_AVAILABLE_KEY = "missing_local_installer"
MISSING_DOWNLOAD_DIRECTORY_KEY = "missing_download_dir"
MISSING_REQUIRED_PARAMETERS_KEY = "missing_mandatory_params"
MULTIPLE_INSTALL_PATH_KEY = "multiple_install_dir"
SIGNATURE_VERIFICATION_FAILED_KEY = "signature_verification_failed"
UNKNOWN_ARCHITECTURE_KEY = "unknown_arch"
VERSION_LOWER_THAN_INSTALLED_KEY = "version_lower_than_installed"
VERSION_PARAMETER_TOO_LOW_KEY = "version_lower_than_minimal"


def _parse_error_messages_file() -> dict[str, str]:
    return read_yaml_file(ERROR_MESSAGES_FILE)


def _prepare_test_data(data: dict[str, str]) -> dict[str, str]:
    parsed_data = {}
    for key, value in data.items():
        key = key.strip().removeprefix(VARIABLE_PREFIX)
        value = value.strip().strip('"')
        value = value.replace("(", "\\(").replace(")", "\\)")
        parsed_data[key] = re.sub("%\\w", ".*", value)
    return parsed_data


@pytest.fixture
def _error_messages() -> dict[str, str]:
    return _prepare_test_data(_parse_error_messages_file())


def _check_deployment_failure(results: DeploymentResult, expected_message: str, expected_code: int) -> None:
    logging.info("Check if installation failed")
    for result in results:
        assert result.returncode == expected_code

    logging.info("Check if output contains proper error message")
    for result in results:
        assert re.search(expected_message, result.stdout + result.stderr)


def test_invalid_required_parameters(_error_messages, runner, configurator, installer_server_url):
    logging.info("Running missing required parameters test")

    logging.debug("Removing required parameter - direct download scenario")
    set_installer_download_params(configurator, installer_server_url)
    configurator.set_common_parameter(configurator.ENVIRONMENT_URL_KEY, "")

    _check_deployment_failure(
        run_deployment(runner, True),
        _error_messages[MISSING_REQUIRED_PARAMETERS_KEY],
        FAILED_DEPLOYMENT_EXIT_CODE,
    )


def test_invalid_architecture(_error_messages, runner, configurator, installer_server_url):
    logging.info("Running invalid architecture test")

    set_installer_download_params(configurator, installer_server_url)
    configurator.set_common_parameter(configurator.INSTALLER_ARCH_KEY, "unknown_arch")

    _check_deployment_failure(
        run_deployment(runner, True),
        _error_messages[UNKNOWN_ARCHITECTURE_KEY],
        FAILED_DEPLOYMENT_EXIT_CODE,
    )


def test_missing_local_installer(_error_messages, runner, configurator):
    logging.info("Running missing local installer test")

    configurator.set_common_parameter(configurator.LOCAL_INSTALLER_KEY, "non_existing_installer")

    _check_deployment_failure(
        run_deployment(runner, True),
        _error_messages[LOCAL_INSTALLER_NOT_AVAILABLE_KEY],
        FAILED_DEPLOYMENT_EXIT_CODE,
    )


@enable_for_system_family(family="unix")
def test_directories_contain_spaces(_error_messages, runner, configurator, platforms, installer_server_url):
    logging.info("Running directories contain spaces test")

    logging.debug("Space in directory path - INSTALL_PATH scenario")
    set_installer_download_params(configurator, installer_server_url)
    installer_args = ["INSTALL_PATH=/path with spaces"]
    configurator.set_common_parameter(configurator.INSTALLER_ARGS_KEY, installer_args)

    _check_deployment_failure(
        run_deployment(runner, True),
        _error_messages[INSTALL_DIR_CONTAINS_SPACES_KEY],
        FAILED_DEPLOYMENT_EXIT_CODE,
    )

    logging.debug("Space in directory path - download dir scenario")
    configurator.clear_parameters_section()
    set_installer_download_params(configurator, installer_server_url)
    configurator.set_common_parameter(configurator.DOWNLOAD_DIR_KEY, "/path with spaces")

    _check_deployment_failure(
        run_deployment(runner, True),
        _error_messages[DOWNLOAD_DIR_CONTAINS_SPACES_KEY],
        FAILED_DEPLOYMENT_EXIT_CODE,
    )


def test_version_parameter_too_low(_error_messages, runner, configurator, installer_server_url):
    logging.info("Running version parameter too low test")

    set_installer_download_params(configurator, installer_server_url)
    configurator.set_common_parameter(configurator.INSTALLER_VERSION_KEY, "0.0.0")

    _check_deployment_failure(
        run_deployment(runner, True),
        _error_messages[VERSION_PARAMETER_TOO_LOW_KEY],
        FAILED_DEPLOYMENT_EXIT_CODE,
    )


def test_multiple_install_path_arguments(_error_messages, runner, configurator, installer_server_url):
    logging.info("Running multiple install path arguments test")

    set_installer_download_params(configurator, installer_server_url)
    configurator.set_common_parameter(configurator.INSTALLER_ARGS_KEY, ["INSTALL_PATH=/path1"])
    configurator.set_common_parameter(configurator.INSTALLER_PLATFORM_ARGS_KEY, ["INSTALL_PATH=/path2"])

    _check_deployment_failure(
        run_deployment(runner, True),
        _error_messages[MULTIPLE_INSTALL_PATH_KEY],
        FAILED_DEPLOYMENT_EXIT_CODE,
    )


def test_failed_download(_error_messages, runner, configurator, installer_server_url):
    logging.info("Running failed download test")

    set_installer_download_params(configurator, installer_server_url)
    configurator.set_common_parameter(configurator.ENVIRONMENT_URL_KEY, "0.0.0.0")

    _check_deployment_failure(
        run_deployment(runner, True),
        _error_messages[DOWNLOAD_FAILED_KEY],
        FAILED_DEPLOYMENT_EXIT_CODE,
    )


# noinspection PyUnusedLocal
@enable_for_system_family(family="unix")
def test_failed_signature_verification(_error_messages, runner, configurator, platforms, installer_server_url):
    logging.info("Running failed signature verification test")

    set_installer_download_params(configurator, installer_server_url)
    configurator.set_common_parameter(configurator.FORCE_CERT_DOWNLOAD_KEY, False)
    configurator.set_common_parameter(configurator.INSTALLER_VERSION_KEY, "latest")

    with TEST_SIGNATURE_FILE.open("w") as signature:
        signature.write("break signature by writing some text")

    universal_message = _error_messages.get(SIGNATURE_VERIFICATION_FAILED_KEY)
    _check_deployment_failure(run_deployment(runner, True), universal_message, FAILED_DEPLOYMENT_EXIT_CODE)
