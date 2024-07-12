import subprocess
from typing import List, Union

from util.test_data_types import CommandResult


def _get_command_prefix(address: str, user: str, password: str) -> List[str]:
    if address == "localhost":
        return []
    else:
        return ["sshpass", "-p", f"{password}", "ssh", "-o", "StrictHostKeyChecking=no", f"{user}@{address}"]


def _get_command_and_shell(address: str, user: str, password: str, command: str, *args: str) \
        -> [Union[List[str], str], bool]:
    prefix = _get_command_prefix(address, user, password)
    if not prefix:
        return " ".join([command, *args]), True
    return prefix + [command, *args], False


class UnixCommandExecutor:
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password

    def execute(self, address: str, command: str, *args: str) -> CommandResult:
        cmd, shell = _get_command_and_shell(address, self.user, self.password, command, *args)
        out = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=False, shell=shell
        )
        return CommandResult(out.returncode, out.stdout, out.stderr)


