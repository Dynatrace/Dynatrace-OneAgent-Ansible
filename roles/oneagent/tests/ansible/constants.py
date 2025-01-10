from pathlib import Path

from util.constants.common_constants import (
    INSTALLER_CERTIFICATE_FILE_NAME,
    INSTALLERS_DIRECTORY,
    RESOURCES_DIRECTORY,
    TEST_DIRECTORY,
)

# Internal
COLLECTION_NAME = "oneagent"
COLLECTION_NAMESPACE = "dynatrace"
ROLE_NAME = "oneagent"

TECH_NAME = "Ansible"

ANSIBLE_USER_KEY = "ansible_user"
ANSIBLE_PASS_KEY = "ansible_password"
ANSIBLE_CONNECTION_KEY = "ansible_connection"

HOSTS_TEMPLATE_FILE_NAME = "hosts.yml"
CREDENTIALS_FILE_NAME = "credentials.yml"
PLAYBOOK_TEMPLATE_FILE_NAME = "oneagent.yml"

ANSIBLE_RESOURCE_DIR = RESOURCES_DIRECTORY / "ansible"

# As tests needs to be run as root and the default install location for collection is non-root based,
# we need to get the script's user home dir to access installed collection.
# Parents[-3] for __file__ will return "/home/<user>"
INSTALLED_COLLECTIONS_DIR = Path.home() / ".ansible" / "collections"
NAMESPACE_DIR = INSTALLED_COLLECTIONS_DIR / "ansible_collections" / COLLECTION_NAMESPACE
ROLE_DIR = NAMESPACE_DIR / COLLECTION_NAME / "roles" / ROLE_NAME

PLAYBOOK_FILE = TEST_DIRECTORY / PLAYBOOK_TEMPLATE_FILE_NAME
INVENTORY_FILE = TEST_DIRECTORY / HOSTS_TEMPLATE_FILE_NAME
TEST_COLLECTIONS_DIR = TEST_DIRECTORY / "collections"
TEST_SIGNATURE_FILE = (
    TEST_COLLECTIONS_DIR
    / "ansible_collections"
    / COLLECTION_NAMESPACE
    / COLLECTION_NAME
    / "roles"
    / ROLE_NAME
    / "files"
    / INSTALLER_CERTIFICATE_FILE_NAME
)

# Public
LOCAL_INSTALLERS_LOCATION = INSTALLERS_DIRECTORY
ERROR_MESSAGES_FILE = ROLE_DIR / "vars" / "messages.yml"
INSTALLER_SIGNATURE_FILE = ROLE_DIR / "files" / INSTALLER_CERTIFICATE_FILE_NAME

FAILED_DEPLOYMENT_EXIT_CODE = 2
SUCCESSFUL_DEPLOYMENT_EXIT_CODE = 0
VARIABLE_PREFIX = f"{COLLECTION_NAME}_"
