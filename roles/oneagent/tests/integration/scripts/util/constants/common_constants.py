import os
from pathlib import Path

# Currently the base is `integration` directory
INTEGRATION_TEST_BASE = Path().cwd()
TEST_DIRECTORY = INTEGRATION_TEST_BASE / "test_dir"
RESOURCES_DIRECTORY = INTEGRATION_TEST_BASE / "resources"
INSTALLERS_DIRECTORY = TEST_DIRECTORY / "installers"
SIGNATURE_FILE_NAME = "dt-root.cert.pem"

INSTALLER_PARTIAL_NAME = "Dynatrace-OneAgent"
INSTALLER_SYSTEM_NAME_TYPE_MAP = {"linux": "linux", "unix": "linux", "aix": "aix", "windows": "windows"}

HOST_SERVER_PORT = 8021
HOST_SERVER_ADDRESS = f"https://127.0.0.1:{HOST_SERVER_PORT}"
HOST_SERVER_TOKEN = "abcdefghijk1234567890"
