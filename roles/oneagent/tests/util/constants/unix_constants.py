from pathlib import Path

UNIX_ONEAGENTCTL_BIN_NAME = "oneagentctl"
UNIX_DEFAULT_INSTALL_PATH = Path("/opt") / "dynatrace" / "oneagent"
UNIX_DEFAULT_DOWNLOAD_PATH = Path("/tmp")
UNIX_ONEAGENTCTL_PATH = UNIX_DEFAULT_INSTALL_PATH / \
    "agent" / "tools" / UNIX_ONEAGENTCTL_BIN_NAME
