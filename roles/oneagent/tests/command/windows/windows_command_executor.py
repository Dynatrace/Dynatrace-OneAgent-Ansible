import winrm
from tests.command.command_result import CommandResult


class WindowsCommandExecutor:
    def __init__(self, user: str, password: str):
        self.user: str = user
        self.password: str = password

    def execute(self, address: str, command: str, *args: str) -> CommandResult:
        session = winrm.Session(address, auth=(self.user, self.password))
        out = session.run_cmd(command, args)
        return CommandResult(out.status_code, out.std_out.decode("utf-8"), out.std_err.decode("utf-8"))
