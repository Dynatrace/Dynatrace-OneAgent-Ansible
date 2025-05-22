import logging
import subprocess
import os

from tests.ansible.config import AnsibleConfigurator
from tests.command.command_result import CommandResult
from tests.constants import CREDENTIALS_FILE_NAME, HOSTS_TEMPLATE_FILE_NAME, PLAYBOOK_TEMPLATE_FILE_NAME
from tests.deployment.deployment_platform import DeploymentResult


class AnsibleRunner:
    def __init__(self, work_dir: str, user: str, password: str):
        self.work_dir = work_dir
        self.user = user
        self.password = password
        self.run_index = 0

    def _generate_file_name(self, file_name: str, new_extension: str = None) -> str:
        base_name, extension = os.path.splitext(file_name)
        if new_extension is not None:
            extension = new_extension
        return f"{base_name}_{self.run_index}{extension}"

    def run_deployment(self, configurator: AnsibleConfigurator, check_mode: bool = False) -> DeploymentResult:
        playbook_file_path = self._generate_file_name(PLAYBOOK_TEMPLATE_FILE_NAME)
        inventory_file_path = self._generate_file_name(HOSTS_TEMPLATE_FILE_NAME)
        log_file_path = self.work_dir / self._generate_file_name(PLAYBOOK_TEMPLATE_FILE_NAME, ".log")
        self.run_index += 1

        configurator.create_playbook_file(self.work_dir / playbook_file_path)
        configurator.create_inventory_file(self.work_dir / inventory_file_path)
        configurator.create_credentials_file(self.work_dir / CREDENTIALS_FILE_NAME)

        commandline = [
            "ansible-playbook",
            "-i",
            inventory_file_path,
            playbook_file_path,
        ]
        if check_mode:
            commandline.append("--check")

        logging.info("Running '%s' in '%s'. ", " ".join(commandline), self.work_dir)

        res = subprocess.run(
            commandline,
            cwd=self.work_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
        )

        logging.info("Deployment finished")

        with log_file_path.open("w") as config:
            logging.info("Saving log to '%s'", log_file_path)
            config.write(res.stdout + res.stderr)

        return [CommandResult(res.returncode, res.stdout, res.stderr)]
