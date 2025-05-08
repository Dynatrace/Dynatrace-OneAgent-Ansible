from typing import Any

from tests.constants import (
    ANSIBLE_CONNECTION_KEY,
    ANSIBLE_PASS_KEY,
    ANSIBLE_RESOURCES_DIR_PATH,
    ANSIBLE_USER_KEY,
    CREDENTIALS_FILE_NAME,
    HOSTS_TEMPLATE_FILE_NAME,
    PLAYBOOK_TEMPLATE_FILE_NAME
)
from tests.deployment.deployment_platform import DeploymentPlatform, PlatformCollection
from tests.resources.file_operations import read_yaml_file, write_yaml_file


class AnsibleConfigurator:
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
        self.playbook = read_yaml_file(ANSIBLE_RESOURCES_DIR_PATH / PLAYBOOK_TEMPLATE_FILE_NAME)
        self.inventory = read_yaml_file(ANSIBLE_RESOURCES_DIR_PATH / HOSTS_TEMPLATE_FILE_NAME)
        self._prepare_inventory(self.user, self.platforms)
        self.credentials = read_yaml_file(ANSIBLE_RESOURCES_DIR_PATH / CREDENTIALS_FILE_NAME)
        self._prepare_credentials(self.user, self.password)

    def _prepare_inventory(self, user: str, platforms: PlatformCollection) -> None:
        for platform, hosts in platforms.items():
            group_data = self.inventory["all"]["children"][platform.family()]["children"][platform.value]
            group_data["hosts"] = {k: None for k in hosts}
            group_data["vars"][ANSIBLE_USER_KEY] = user
            # TODO: Add condition to fail test if localhost is used with multiple platforms
            # We assume that localhost is used only with single platform
            if "localhost" in hosts:
                group_data = self.inventory["all"]["children"][platform.family()]["vars"]
                group_data[ANSIBLE_CONNECTION_KEY] = "local"

    def _prepare_credentials(self, user: str, password: str) -> None:
        self.credentials[ANSIBLE_USER_KEY] = user
        self.credentials[ANSIBLE_PASS_KEY] = password

    def set_common_parameter(self, key: str, value: Any) -> None:
        self.playbook[0][AnsibleConfigurator.PARAM_SECTION_KEY][key] = value

    def set_platform_parameter(self, platform: DeploymentPlatform, key: str, value: Any) -> None:
        group_data = self.inventory["all"]["children"][platform.family()]["children"][platform.value]
        group_data[self.PARAM_SECTION_KEY][key] = value

    def set_deployment_hosts(self, hosts: str) -> None:
        self.playbook[0][self.HOSTS_PARAM_KEY] = hosts

    def create_playbook_file(self, path: str) -> None:
        write_yaml_file(path, self.playbook)

    def create_inventory_file(self, path: str) -> None:
        write_yaml_file(path, self.inventory)

    def create_credentials_file(self, path: str) -> None:
        write_yaml_file(path, self.credentials)
