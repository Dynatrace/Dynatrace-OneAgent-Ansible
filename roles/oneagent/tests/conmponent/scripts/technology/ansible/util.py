from typing import Dict

from technology.ansible.constants import ERROR_MESSAGES_FILE
from util.common_utils import read_yaml_file


def parse_error_messages_file() -> Dict[str, str]:
    return read_yaml_file(ERROR_MESSAGES_FILE)
