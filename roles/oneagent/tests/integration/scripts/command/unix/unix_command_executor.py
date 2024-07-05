import subprocess
from typing import List

from util.test_data_types import CommandResult


def _getCommandPrefix(address: str, user: str, password: str) -> List[str]:
    if address == "localhost":
        return []
    else:
        return ["sshpass", "-p", f"{password}", "ssh", "-o", "StrictHostKeyChecking=no", f"{user}@{address}"]

class UnixCommandExecutor:
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password

    def execute(self, address: str, command: str, *args: str) -> CommandResult:
        prefix = _getCommandPrefix(address, self.user, self.password)
        cmd = prefix + [command, *args]
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=False)
        return CommandResult(out.returncode, out.stdout, out.stderr)


