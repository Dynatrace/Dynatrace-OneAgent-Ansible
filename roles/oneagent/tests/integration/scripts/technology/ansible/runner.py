import subprocess

from technology.ansible.constants import HOSTS_TEMPLATE_FILE_NAME, PLAYBOOK_TEMPLATE_FILE_NAME
from technology.deployment_runner import DeploymentRunner, DeploymentResult
from util.test_data_types import CommandResult


class AnsibleRunner(DeploymentRunner):
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password

    def run_deployment(self) -> DeploymentResult:
        res = subprocess.run(
            ["ansible-playbook", "-i", HOSTS_TEMPLATE_FILE_NAME, PLAYBOOK_TEMPLATE_FILE_NAME],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
        )
        return [CommandResult(res.returncode, res.stdout, res.stderr)]
