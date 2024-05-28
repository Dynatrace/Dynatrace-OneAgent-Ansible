from pathlib import Path

from command.command_wrapper import CommandWrapper
from command.unix.unix_command_executor import UnixCommandExecutor
from util.test_data_types import CommandResult


class UnixCommandWrapper(CommandWrapper):
    def __init__(self, user: str, password: str):
        self.password = password
        self.executor = UnixCommandExecutor(user, password)

    def get_file_content(self, address: str, file: Path) -> CommandResult:
        return self.executor.execute(address, "cat", str(file))

    def file_exists(self, address: str, file: Path) -> CommandResult:
        return self.executor.execute(address, "test", "-f", str(file))

    def directory_exists(self, address: str, directory: Path) -> CommandResult:
        return self.executor.execute(address, "test", "-d", str(directory))

    def create_directory(self, address: str, directory: Path) -> CommandResult:
        return self.executor.execute(address, "mkdir", "-p", str(directory))

    def run_command(self, address: str, command: str, *args: str) -> CommandResult:
        return self.executor.execute(address, f"echo {self.password} | sudo -S {command}", *args)
