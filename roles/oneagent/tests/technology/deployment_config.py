from abc import ABC, abstractmethod
from typing import Any

from util.constant_key import constant_key
from util.test_data_types import DeploymentPlatform


class DeploymentConfig(ABC):
    @abstractmethod
    def prepare_test_environment(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_common_parameter(self, key: str, value: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_platform_parameter(self, platform: DeploymentPlatform, key: str, value: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_deployment_hosts(self, hosts: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def clear_parameters_section(self) -> None:
        raise NotImplementedError

    # C0103: Method name doesn't conform to snake_case naming style (invalid-name)
    # E0213: Method should have "self" as first argument (no-self-argument)
    # pylint: disable=C0103,E0213
    @constant_key
    def INSTALLER_ARGS_KEY(cls):
        raise NotImplementedError

    @constant_key
    def DOWNLOAD_DIR_KEY(cls):
        raise NotImplementedError

    @constant_key
    def INSTALLER_VERSION_KEY(cls):
        raise NotImplementedError

    @constant_key
    def PACKAGE_STATE_KEY(cls):
        raise NotImplementedError

    @constant_key
    def LOCAL_INSTALLER_KEY(cls):
        raise NotImplementedError

    @constant_key
    def PRESERVE_INSTALLER_KEY(cls):
        raise NotImplementedError

    @constant_key
    def ENVIRONMENT_URL_KEY(cls):
        raise NotImplementedError

    @constant_key
    def PAAS_TOKEN_KEY(cls):
        raise NotImplementedError

    @constant_key
    def VALIDATE_DOWNLOAD_CERTS_KEY(cls):
        raise NotImplementedError

    @constant_key
    def VERIFY_SIGNATURE_KEY(cls):
        raise NotImplementedError

    @constant_key
    def INSTALLER_ARCH_KEY(cls):
        raise NotImplementedError

    @constant_key
    def INSTALLER_PLATFORM_ARGS_KEY(cls):
        raise NotImplementedError
