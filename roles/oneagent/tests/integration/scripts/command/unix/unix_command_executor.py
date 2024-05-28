import subprocess

from util.test_data_types import CommandResult


class UnixCommandExecutor:
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password

    def execute(self, address: str, command: str, *args: str) -> CommandResult:
        cmd = [
            "sshpass",
            "-p",
            f"{self.password}",
            "ssh",
            "-o StrictHostKeyChecking=no",
            f"{self.user}@{address}",
            command,
            *args,
        ]
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=False)
        return CommandResult(out.returncode, out.stdout, out.stderr)
