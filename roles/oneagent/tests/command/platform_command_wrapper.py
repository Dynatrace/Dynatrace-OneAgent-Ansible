from pathlib import Path

from command.command_wrapper import CommandWrapper
from command.unix.unix_command_wrapper import UnixCommandWrapper
from command.windows.windows_command_wrapper import WindowsCommandWrapper
from util.test_data_types import CommandResult, DeploymentPlatform


class PlatformCommandWrapper:
    def __init__(self, user: str, password: str):
        self.unix_command_wrapper = UnixCommandWrapper(user, password)
        self.windows_command_wrapper = WindowsCommandWrapper(user, password)

    def _get_command_wrapper(self, platform: DeploymentPlatform) -> CommandWrapper:
        if platform == DeploymentPlatform.WINDOWS_X86:
            return self.windows_command_wrapper
        return self.unix_command_wrapper

    def get_file_content(self, platform: DeploymentPlatform, address: str, file: Path) -> CommandResult:
        return self._get_command_wrapper(platform).get_file_content(address, file)

    def file_exists(self, platform: DeploymentPlatform, address: str, file: Path) -> CommandResult:
        return self._get_command_wrapper(platform).file_exists(address, file)

    def directory_exists(self, platform: DeploymentPlatform, address: str, directory: Path) -> CommandResult:
        return self._get_command_wrapper(platform).directory_exists(address, directory)

    def create_directory(self, platform: DeploymentPlatform, address: str, directory: Path) -> CommandResult:
        return self._get_command_wrapper(platform).create_directory(address, directory)

    def run_command(self, platform: DeploymentPlatform, address: str, command: str, *args: str) -> CommandResult:
        return self._get_command_wrapper(platform).run_command(address, command, *args)
