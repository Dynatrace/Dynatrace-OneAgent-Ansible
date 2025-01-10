import shutil
from typing import Any

from ansible.constants import (
    ANSIBLE_CONNECTION_KEY,
    ANSIBLE_PASS_KEY,
    ANSIBLE_RESOURCE_DIR,
    ANSIBLE_USER_KEY,
    CREDENTIALS_FILE_NAME,
    HOSTS_TEMPLATE_FILE_NAME,
    INSTALLED_COLLECTIONS_DIR,
    INVENTORY_FILE,
    PLAYBOOK_FILE,
    PLAYBOOK_TEMPLATE_FILE_NAME,
    TEST_COLLECTIONS_DIR,
)
from util.common_utils import read_yaml_file, write_yaml_file
from util.constants.common_constants import TEST_DIRECTORY
from util.test_data_types import DeploymentPlatform, PlatformCollection


def _prepare_collection() -> None:
    shutil.rmtree(TEST_COLLECTIONS_DIR, ignore_errors=True)
    shutil.copytree(INSTALLED_COLLECTIONS_DIR, TEST_COLLECTIONS_DIR)


def _prepare_playbook_file() -> None:
    shutil.copy(
        str(ANSIBLE_RESOURCE_DIR / PLAYBOOK_TEMPLATE_FILE_NAME),
        str(TEST_DIRECTORY / PLAYBOOK_TEMPLATE_FILE_NAME),
    )


def _prepare_inventory_file(user: str, platforms: PlatformCollection) -> None:
    host_file = TEST_DIRECTORY / HOSTS_TEMPLATE_FILE_NAME
    shutil.copy(str(ANSIBLE_RESOURCE_DIR / HOSTS_TEMPLATE_FILE_NAME), str(host_file))
    data = read_yaml_file(INVENTORY_FILE)
    for platform, hosts in platforms.items():
        group_data = data["all"]["children"][platform.family()]["children"][platform.value]
        group_data["hosts"] = {k: None for k in hosts}
        group_data["vars"][ANSIBLE_USER_KEY] = user
        # TODO: Add condition to fail test if localhost is used with multiple platforms
        # We assume that localhost is used only with single platform
        if "localhost" in hosts:
            group_data = data["all"]["children"][platform.family()]["vars"]
            group_data[ANSIBLE_CONNECTION_KEY] = "local"
    write_yaml_file(INVENTORY_FILE, data)


def _prepare_credentials_file(user: str, password: str) -> None:
    credentials_file = TEST_DIRECTORY / CREDENTIALS_FILE_NAME
    shutil.copy(str(ANSIBLE_RESOURCE_DIR / CREDENTIALS_FILE_NAME), str(credentials_file))
    data = read_yaml_file(credentials_file)
    data[ANSIBLE_USER_KEY] = user
    data[ANSIBLE_PASS_KEY] = password
    write_yaml_file(credentials_file, data)


class AnsibleConfig:
    HOSTS_PARAM_KEY = "hosts"
    PARAM_SECTION_KEY = "vars"

    # Platform-agnostic
    ENVIRONMENT_URL_KEY = "oneagent_environment_url"
    INSTALLER_ARGS_KEY = "oneagent_install_args"
    INSTALLER_VERSION_KEY = "oneagent_version"
    PAAS_TOKEN_KEY = "oneagent_paas_token"
    PACKAGE_STATE_KEY = "oneagent_package_state"
    PRESERVE_INSTALLER_KEY = "oneagent_preserve_installer"
    VERIFY_SIGNATURE_KEY = "oneagent_verify_signature"

    # Internal parameters
    CA_CERT_DOWNLOAD_CERT_KEY = "oneagent_ca_cert_download_cert"
    CA_CERT_DOWNLOAD_URL_KEY = "oneagent_ca_cert_download_url"
    FORCE_CERT_DOWNLOAD_KEY = "oneagent_force_cert_download"
    INSTALLER_DOWNLOAD_CERT_KEY = "oneagent_installer_download_cert"
    VALIDATE_DOWNLOAD_CERTS_KEY = "oneagent_validate_certs"

    # Platform-specific
    DOWNLOAD_DIR_KEY = "oneagent_download_dir"
    INSTALLER_ARCH_KEY = "oneagent_installer_arch"
    INSTALLER_PLATFORM_ARGS_KEY = "oneagent_platform_install_args"
    LOCAL_INSTALLER_KEY = "oneagent_local_installer"

    def __init__(self, user: str, password: str, platforms: PlatformCollection):
        self.user = user
        self.password = password
        self.platforms = platforms

    def prepare_test_environment(self) -> None:
        _prepare_playbook_file()
        _prepare_inventory_file(self.user, self.platforms)
        _prepare_credentials_file(self.user, self.password)
        _prepare_collection()

    def set_common_parameter(self, key: str, value: Any) -> None:
        data = read_yaml_file(PLAYBOOK_FILE)
        data[0][AnsibleConfig.PARAM_SECTION_KEY][key] = value
        write_yaml_file(PLAYBOOK_FILE, data)

    def set_platform_parameter(self, platform: DeploymentPlatform, key: str, value: Any) -> None:
        data = read_yaml_file(INVENTORY_FILE)
        group_data = data["all"]["children"][platform.family()]["children"][platform.value]
        group_data[self.PARAM_SECTION_KEY][key] = value
        write_yaml_file(INVENTORY_FILE, data)

    def set_deployment_hosts(self, hosts: str) -> None:
        data = read_yaml_file(PLAYBOOK_FILE)
        data[0][self.HOSTS_PARAM_KEY] = hosts
        write_yaml_file(PLAYBOOK_FILE, data)

    def clear_parameters_section(self) -> None:
        data = read_yaml_file(PLAYBOOK_FILE)
        data[0][AnsibleConfig.PARAM_SECTION_KEY] = {}
        write_yaml_file(PLAYBOOK_FILE, data)
        data = read_yaml_file(INVENTORY_FILE)
        for platform in DeploymentPlatform:
            group_data = data["all"]["children"][platform.family()]["children"][platform.value]
            group_data[self.PARAM_SECTION_KEY] = {}
        write_yaml_file(INVENTORY_FILE, data)
