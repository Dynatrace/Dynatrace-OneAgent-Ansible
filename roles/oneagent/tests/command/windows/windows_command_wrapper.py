from pathlib import Path

from command.command_wrapper import CommandWrapper
from command.windows.windows_command_executor import WindowsCommandExecutor
from util.test_data_types import CommandResult


class WindowsCommandWrapper(CommandWrapper):
    def __init__(self, user: str, password: str):
        self.executor = WindowsCommandExecutor(user, password)

    def get_file_content(self, address: str, file: Path) -> CommandResult:
        return self.executor.execute(address, "type", str(file))

    def file_exists(self, address: str, file: Path) -> CommandResult:
        # Windows needs double quoting for passing paths
        # containing spaces, single quotes don't work
        return self.executor.execute(address, f'if exist "{file}" (exit 0) else (exit 1)')

    def directory_exists(self, address: str, directory: Path) -> CommandResult:
        return self.executor.execute(address, f'if exist "{directory}\\*" (exit 0) else (exit 1)')

    def _run_directory_creation_command(self, address: str, directory: Path) -> CommandResult:
        result = CommandResult(0, "", "")
        if self.directory_exists(address, directory).returncode == 1:
            result = self.executor.execute(address, "md", str(directory))

        return result

    def create_directory(self, address: str, directory: Path) -> CommandResult:
        for parent in list(directory.parents)[::-1][1::]:
            result = self._run_directory_creation_command(address, parent)
            if result.returncode != 0:
                return result
        return self._run_directory_creation_command(address, directory)

    def run_command(self, address: str, command: str, *args: str) -> CommandResult:
        return self.executor.execute(address, f'"{command}"', *args)
