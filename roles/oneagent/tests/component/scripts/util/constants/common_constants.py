from pathlib import Path

# TODO: is cwd() correct?
COMPONENT_TEST_BASE = Path().cwd() / "test_dir"
TEST_DIRECTORY = COMPONENT_TEST_BASE / "working_dir"
RESOURCES_DIRECTORY = Path().cwd() / "resources"
INSTALLERS_DIRECTORY = COMPONENT_TEST_BASE / "installers"
INSTALLERS_RESOURCE_DIR = RESOURCES_DIRECTORY / "installers"
SIGNATURE_FILE_NAME = "dt-root.cert.pem"

INSTALLER_PARTIAL_NAME = "Dynatrace-OneAgent"
INSTALLER_SYSTEM_NAME_TYPE_MAP = {"linux": "linux", "unix": "linux", "aix": "aix", "windows": "windows"}

HOST_SERVER_PORT = 8021
HOST_SERVER_ADDRESS = f"https://127.0.0.1:{HOST_SERVER_PORT}"
HOST_SERVER_TOKEN = "abcdefghijk1234567890"

class InstallerVersion(Enum):
    OLD = "1.199.0.20241008-150308"
    MALFORMED = "1.259.0.20241008-150308"
    LATEST = "1.300.0.20241008-150308"