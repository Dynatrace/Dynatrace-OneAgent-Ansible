import subprocess
from pathlib import Path

from tests.command.command_result import CommandResult
from tests.command.command_wrapper import CommandWrapper
from typing_extensions import override


class UnixCommandWrapper(CommandWrapper):
    def __init__(self, user: str, password: str):
        self.password: str = password

    def _execute(self, address: str, command: str, *args: str) -> CommandResult:
        out = subprocess.run(
            " ".join([command, *args]),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
            shell=True,
        )
        return CommandResult(out.returncode, out.stdout, out.stderr)

    @override
    def get_file_content(self, address: str, file: Path) -> CommandResult:
        return self._execute(address, "cat", str(file))

    @override
    def file_exists(self, address: str, file: Path) -> CommandResult:
        return self._execute(address, "test", "-f", str(file))

    @override
    def directory_exists(self, address: str, directory: Path) -> CommandResult:
        return self._execute(address, "test", "-d", str(directory))

    @override
    def create_directory(self, address: str, directory: Path) -> CommandResult:
        return self._execute(address, "mkdir", "-p", str(directory))

    @override
    def run_command(self, address: str, command: str, *args: str) -> CommandResult:
        return self._execute(address, f"echo {self.password} | sudo -S {command}", *args)
