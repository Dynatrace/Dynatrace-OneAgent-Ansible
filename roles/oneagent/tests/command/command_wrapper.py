from abc import abstractmethod
from pathlib import Path

from command.command_result import CommandResult


class CommandWrapper:
    @abstractmethod
    def get_file_content(self, address: str, file: Path) -> CommandResult:
        raise NotImplementedError

    @abstractmethod
    def file_exists(self, address: str, file: Path) -> CommandResult:
        raise NotImplementedError

    @abstractmethod
    def directory_exists(self, address: str, directory: Path) -> CommandResult:
        raise NotImplementedError

    @abstractmethod
    def create_directory(self, address: str, directory: Path) -> CommandResult:
        raise NotImplementedError

    @abstractmethod
    def run_command(self, address: str, command: str, *args: str) -> CommandResult:
        raise NotImplementedError
