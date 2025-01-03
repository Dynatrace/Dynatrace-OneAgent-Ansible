import winrm
from util.test_data_types import CommandResult


class WindowsCommandExecutor:
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password

    def execute(self, address: str, command: str, *args: str) -> CommandResult:
        session = winrm.Session(address, auth=(self.user, self.password))
        out = session.run_cmd(command, args)
        return CommandResult(out.status_code, out.std_out.decode("utf-8"), out.std_err.decode("utf-8"))
