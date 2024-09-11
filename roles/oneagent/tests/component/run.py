import argparse
import glob
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime

from pathlib import Path
from typing import Any
from scripts.util.test_data_types import DeploymentPlatform

USER_KEY = "user"
PASS_KEY = "password"

BASE_DIR = Path(__file__).resolve().parent
TEST_DIR = BASE_DIR / "test_dir"
LOG_DIR = TEST_DIR / "logs"
INSTALLERS_DIR = TEST_DIR / "installers"
TEST_VARS = {"PYTHONPATH": "scripts/"}


class ServerWrapper(object):
    def __init__(self, proc: subprocess.Popen):
        self.proc = proc

    def __enter__(self):
        return self.proc

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.proc.terminate()
        save_log(self.proc.stdout, LOG_DIR / "server.log")


def get_env_vars() -> dict[str, str]:
    # This is required to pass current venv vars down to the subprocess for tests and server
    env_vars = os.environ.copy()
    env_vars.update(TEST_VARS)
    return env_vars


def save_log(out, log_path: Path) -> None:
    with log_path.open("w") as log:
        for line in out:
            log.write(line)


def get_test_args(args: dict[str, Any]) -> list[str]:
    test_args = [f"--{USER_KEY}='{args[USER_KEY]}'", f"--{PASS_KEY}='{args[PASS_KEY]}'"]
    for platform in [p.value for p in DeploymentPlatform]:
        hosts = ','.join(args[platform])
        hosts and test_args.append(f"--{platform}={hosts}")
    return test_args


def run_test(test: str, test_args: list[str]) -> bool:
    test_name = Path(test).stem
    logging.info(f"Test: {test_name}")
    proc = subprocess.run(["pytest", test] + test_args, env=get_env_vars(), encoding="utf-8",
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    save_log(proc.stdout, LOG_DIR / f"{test_name}.log")
    success = proc.returncode == 0
    logging.info("PASSED" if success else "FAILED")
    return success


def run_all_tests(args: dict[str, Any]) -> bool:
    logging.info("Running tests...")

    test_path = "scripts/tests"
    test_args = get_test_args(args)
    tests_failed = False

    for test in glob.glob(f"{test_path}/test_*.py"):
        if not run_test(test, test_args):
            tests_failed = True

    return tests_failed


def run_server() -> subprocess.Popen:
    logging.info("Running server...")
    server_path = BASE_DIR / "scripts" / "server" / "server.py"
    return subprocess.Popen(["python", server_path], env=get_env_vars(),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")


def get_file_content(path: Path) -> list[str]:
    with path.open("r") as f:
        return f.readlines()


def replace_tag(source: list[str], old: str, new: str) -> list[str]:
    return [line.replace(old, new) for line in source]


def prepare_installers() -> None:
    logging.info("Preparing installers...")

    oneagentctl_bin_name = "oneagentctl.sh"
    uninstall_script_name = "uninstall.sh"
    installer_partial_name = "Dynatrace-OneAgent-Linux"

    version_tag = "##VERSION##"
    uninstall_code_tag = "##UNINSTALL_CODE##"
    oneagentctl_code_tag = "##ONEAGENTCTL_CODE##"

    resource_dir = BASE_DIR / "resources" / "installers"

    uninstall_template = get_file_content(resource_dir / uninstall_script_name)
    uninstall_code = replace_tag(uninstall_template, "$", r"\$")

    oneagentctl_template = get_file_content(resource_dir / oneagentctl_bin_name)
    oneagentctl_code = replace_tag(oneagentctl_template, "$", r"\$")

    installer_template = get_file_content(resource_dir / f"{installer_partial_name}.sh")
    installer_template = replace_tag(installer_template, uninstall_code_tag, "".join(uninstall_code))
    installer_template = replace_tag(installer_template, oneagentctl_code_tag, "".join(oneagentctl_code))

    timestamp = '{:%Y%m%d-%H%M%S}'.format(datetime.now())
    # Minimal supported version is 1.199
    for version in ["1.199.0", "1.300.0"]:
        full_version = f"{version}.{timestamp}"
        installer_code = replace_tag(installer_template, version_tag, full_version)
        with open(INSTALLERS_DIR / f"{installer_partial_name}-{full_version}.sh", "w") as f:
            f.writelines(installer_code)


def prepare_environment() -> None:
    logging.basicConfig(
        format="%(asctime)s [server] %(levelname)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO
    )
    shutil.rmtree(TEST_DIR, ignore_errors=True)
    os.makedirs(INSTALLERS_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    prepare_installers()


def parse_args() -> dict[str, Any]:
    parser = argparse.ArgumentParser(
        description="Run component tests for OneAgent role. If any of specified platform contains"
                    " 'localhost' as an IP address, the script will perform tests on the local machine."
                    " In such case, user and password arguments can be empty"
    )

    parser.add_argument(f"--{USER_KEY}", type=str, help="User for remote hosts", default="")
    parser.add_argument(f"--{PASS_KEY}", type=str, help="Password for remote hosts user", default="")

    for platform in DeploymentPlatform:
        parser.add_argument(
            f"--{platform.value}", type=str, nargs="+", default=[], help="List of IPs for specified platform"
        )

    return vars(parser.parse_args())


def main() -> bool:
    args = parse_args()
    prepare_environment()
    with ServerWrapper(run_server()):
        result = run_all_tests(args)
    return result


if __name__ == "__main__":
    sys.exit(main())
