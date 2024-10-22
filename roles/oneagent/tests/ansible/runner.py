import subprocess
import logging

from ansible.constants import HOSTS_TEMPLATE_FILE_NAME, PLAYBOOK_TEMPLATE_FILE_NAME, CREDENTIALS_FILE_NAME, TEST_DIRECTORY
from util.test_data_types import CommandResult, DeploymentResult


class AnsibleRunner:
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password

    def run_deployment(self) -> DeploymentResult:
        with open(TEST_DIRECTORY / PLAYBOOK_TEMPLATE_FILE_NAME, 'r') as f:
            logging.debug(f"Running playbook ({PLAYBOOK_TEMPLATE_FILE_NAME}):\n{f.read()}")

        with open(TEST_DIRECTORY / HOSTS_TEMPLATE_FILE_NAME, 'r') as f:
            logging.debug(f"Inventory file ({HOSTS_TEMPLATE_FILE_NAME}):\n{f.read()}")

        with open(TEST_DIRECTORY / CREDENTIALS_FILE_NAME, 'r') as f:
            logging.debug(f"Credentials file ({CREDENTIALS_FILE_NAME}):\n{f.read()}")

        res = subprocess.run(
            ["ansible-playbook", "-i", TEST_DIRECTORY / HOSTS_TEMPLATE_FILE_NAME, TEST_DIRECTORY / PLAYBOOK_TEMPLATE_FILE_NAME],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
        )
        return [CommandResult(res.returncode, res.stdout, res.stderr)]