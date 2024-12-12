from pathlib import Path

WINDOWS_ONEAGENTCTL_BIN_NAME = "oneagentctl.exe"
WINDOWS_DEFAULT_INSTALL_PATH = Path(
    "C:\\Program Files") / "dynatrace" / "oneagent"
WINDOWS_DEFAULT_DOWNLOAD_PATH = Path("%TEMP%")
WINDOWS_ONEAGENTCTL_PATH = WINDOWS_DEFAULT_INSTALL_PATH / \
    "agent" / "tools" / WINDOWS_ONEAGENTCTL_BIN_NAME
