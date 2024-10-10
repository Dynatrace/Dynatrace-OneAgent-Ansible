import subprocess
import logging

from technology.constants import HOSTS_TEMPLATE_FILE_NAME, PLAYBOOK_TEMPLATE_FILE_NAME, CREDENTIALS_FILE_NAME
from technology.deployment_runner import DeploymentRunner, DeploymentResult
from util.test_data_types import CommandResult


class AnsibleRunner(DeploymentRunner):
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password

    def run_deployment(self) -> DeploymentResult:
        with open(PLAYBOOK_TEMPLATE_FILE_NAME, 'r') as f:
            logging.debug(f"Running playbook ({PLAYBOOK_TEMPLATE_FILE_NAME}):\n{f.read()}")

        with open(HOSTS_TEMPLATE_FILE_NAME, 'r') as f:
            logging.debug(f"Inventory file ({HOSTS_TEMPLATE_FILE_NAME}):\n{f.read()}")

        with open(CREDENTIALS_FILE_NAME, 'r') as f:
            logging.debug(f"Credentials file ({CREDENTIALS_FILE_NAME}):\n{f.read()}")

        res = subprocess.run(
            ["ansible-playbook", "-i", HOSTS_TEMPLATE_FILE_NAME, PLAYBOOK_TEMPLATE_FILE_NAME],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
        )
        return [CommandResult(res.returncode, res.stdout, res.stderr)]
