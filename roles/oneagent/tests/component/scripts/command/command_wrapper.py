from abc import abstractmethod
from pathlib import Path

from util.test_data_types import CommandResult


class CommandWrapper:
    @abstractmethod
    def get_file_content(self, address: str, file: Path) -> CommandResult:
        pass

    @abstractmethod
    def file_exists(self, address: str, file: Path) -> CommandResult:
        pass

    @abstractmethod
    def directory_exists(self, address: str, directory: Path) -> CommandResult:
        pass

    @abstractmethod
    def create_directory(self, address: str, directory: Path) -> CommandResult:
        pass

    @abstractmethod
    def run_command(self, address: str, command: str, *args: str) -> CommandResult:
        pass
