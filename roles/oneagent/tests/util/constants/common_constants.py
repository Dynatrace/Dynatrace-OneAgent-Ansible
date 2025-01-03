from enum import Enum
from pathlib import Path

# TODO: is cwd() correct?
COMPONENT_TEST_BASE = Path().cwd() / "test_dir"
INSTALLERS_DIRECTORY = COMPONENT_TEST_BASE / "installers"
RESOURCES_DIRECTORY = Path(__file__).resolve().parent.parent.parent / "resources"
INSTALLERS_RESOURCE_DIR = RESOURCES_DIRECTORY / "installers"
LOG_DIRECTORY = COMPONENT_TEST_BASE / "logs"
SERVER_DIRECTORY = COMPONENT_TEST_BASE / "server"
TEST_DIRECTORY = COMPONENT_TEST_BASE / "working_dir"

INSTALLER_CERTIFICATE_FILE_NAME = "dt-root.cert.pem"
INSTALLER_PRIVATE_KEY_FILE_NAME = "dt-root.key"
SERVER_CERTIFICATE_FILE_NAME = "server.pem"
SERVER_PRIVATE_KEY_FILE_NAME = "server.key"

INSTALLER_PARTIAL_NAME = "Dynatrace-OneAgent"
INSTALLER_SYSTEM_NAME_TYPE_MAP = {"linux": "linux", "unix": "linux", "aix": "aix", "windows": "windows"}

INSTALLER_SERVER_TOKEN = "abcdefghijk1234567890"


class InstallerVersion(Enum):
    OLD = "1.199.0.20241008-150308"
    LATEST = "1.300.0.20241008-150308"
