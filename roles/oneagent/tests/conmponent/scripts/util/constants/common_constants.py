from pathlib import Path

# is cwd() correct?
COMPONENT_TEST_BASE = Path().cwd() / "test_dir"
TEST_DIRECTORY = COMPONENT_TEST_BASE / "working_dir"
RESOURCES_DIRECTORY = Path().cwd() / "resources"
INSTALLERS_DIRECTORY = COMPONENT_TEST_BASE / "installers"
SIGNATURE_FILE_NAME = "dt-root.cert.pem"

INSTALLER_PARTIAL_NAME = "Dynatrace-OneAgent"
INSTALLER_SYSTEM_NAME_TYPE_MAP = {"linux": "linux", "unix": "linux", "aix": "aix", "windows": "windows"}

HOST_SERVER_PORT = 8021
HOST_SERVER_ADDRESS = f"https://127.0.0.1:{HOST_SERVER_PORT}"
HOST_SERVER_TOKEN = "abcdefghijk1234567890"
