import shutil
from typing import Any

from technology.ansible.constants import (
    PLAYBOOK_TEMPLATE_FILE_NAME,
    HOSTS_TEMPLATE_FILE_NAME,
    ANSIBLE_USER_KEY,
    ANSIBLE_CONNECTION_KEY,
    ANSIBLE_RESOURCE_DIR,
    COLLECTION_DIR,
    COLLECTION_NAME,
    PLAYBOOK_FILE,
    INVENTORY_FILE,
    CREDENTIALS_FILE_NAME,
    ANSIBLE_PASS_KEY,
)
from technology.deployment_config import DeploymentConfig
from util.common_utils import read_yaml_file, write_yaml_file
from util.constants.common_constants import TEST_DIRECTORY, INSTALLERS_DIRECTORY
from util.test_data_types import DeploymentPlatform, PlatformCollection


def _prepare_playbook_file() -> None:
    shutil.copy(
        str(ANSIBLE_RESOURCE_DIR / PLAYBOOK_TEMPLATE_FILE_NAME), str(TEST_DIRECTORY / PLAYBOOK_TEMPLATE_FILE_NAME)
    )


def _prepare_inventory_file(user: str, platforms: PlatformCollection) -> None:
    host_file = TEST_DIRECTORY / HOSTS_TEMPLATE_FILE_NAME
    shutil.copy(str(ANSIBLE_RESOURCE_DIR / HOSTS_TEMPLATE_FILE_NAME), str(host_file))
    data = read_yaml_file(INVENTORY_FILE)
    for platform, hosts in platforms.items():
        group_data = data["all"]["children"][platform.family()]["children"][platform.value]
        group_data["hosts"] = {k: None for k in hosts}
        # TODO: Replace so that both local and ssh connections can be used
        if "localhost" in hosts:
            group_data["vars"][ANSIBLE_CONNECTION_KEY] = "local"
        group_data["vars"][ANSIBLE_USER_KEY] = user
    write_yaml_file(INVENTORY_FILE, data)


def _prepare_credentials_file(user: str, password: str) -> None:
    credentials_file = TEST_DIRECTORY / CREDENTIALS_FILE_NAME
    shutil.copy(str(ANSIBLE_RESOURCE_DIR / CREDENTIALS_FILE_NAME), str(credentials_file))
    data = read_yaml_file(credentials_file)
    data[ANSIBLE_USER_KEY] = user
    data[ANSIBLE_PASS_KEY] = password
    write_yaml_file(credentials_file, data)


class AnsibleConfig(DeploymentConfig):
    PARAM_SECTION_KEY = "vars"
    HOSTS_PARAM_KEY = "hosts"

    # Platform-agnostic
    INSTALLER_VERSION_KEY = "oneagent_version"
    PACKAGE_STATE_KEY = "oneagent_package_state"
    VERIFY_SIGNATURE_KEY = "oneagent_verify_signature"
    PRESERVE_INSTALLER_KEY = "oneagent_preserve_installer"
    ENVIRONMENT_URL_KEY = "oneagent_environment_url"
    VALIDATE_DOWNLOAD_CERTS_KEY = "oneagent_validate_certs"
    PAAS_TOKEN_KEY = "oneagent_paas_token"
    INSTALLER_ARGS_KEY = "oneagent_install_args"

    # Platform-specific
    DOWNLOAD_DIR_KEY = "oneagent_download_dir"
    LOCAL_INSTALLER_KEY = "oneagent_local_installer"
    INSTALLER_ARCH_KEY = "oneagent_installer_arch"
    INSTALLER_PLATFORM_ARGS_KEY = "oneagent_platform_install_args"

    def __init__(self, user: str, password: str, platforms: PlatformCollection):
        self.user = user
        self.password = password
        self.platforms = platforms

    def prepare_test_environment(self) -> None:
        _prepare_playbook_file()
        _prepare_inventory_file(self.user, self.platforms)
        _prepare_credentials_file(self.user, self.password)

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
