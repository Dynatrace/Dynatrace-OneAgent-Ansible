import logging
import subprocess

from tests.command.command_result import CommandResult
from tests.constants import (
    CREDENTIALS_FILE_NAME,
    HOSTS_TEMPLATE_FILE_NAME,
    PLAYBOOK_TEMPLATE_FILE_NAME,
    WORK_DIR_PATH,
)
from tests.deployment.deployment_platform import DeploymentResult


class AnsibleRunner:
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password

    def run_deployment(self) -> DeploymentResult:
        with open(WORK_DIR_PATH / PLAYBOOK_TEMPLATE_FILE_NAME, "r") as f:
            logging.debug("Running playbook (%s):\n%s", PLAYBOOK_TEMPLATE_FILE_NAME, f.read())

        with open(WORK_DIR_PATH / HOSTS_TEMPLATE_FILE_NAME, "r") as f:
            logging.debug("Inventory file (%s):\n%s", HOSTS_TEMPLATE_FILE_NAME, f.read())

        with open(WORK_DIR_PATH / CREDENTIALS_FILE_NAME, "r") as f:
            logging.debug("Credentials file (%s):\n%s", CREDENTIALS_FILE_NAME, f.read())

        res = subprocess.run(
            [
                "ansible-playbook",
                "-i",
                WORK_DIR_PATH / HOSTS_TEMPLATE_FILE_NAME,
                WORK_DIR_PATH / PLAYBOOK_TEMPLATE_FILE_NAME,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
        )
        return [CommandResult(res.returncode, res.stdout, res.stderr)]
