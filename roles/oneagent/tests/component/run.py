import argparse
import glob
import logging
import os
import shutil
import subprocess
import sys

from pathlib import Path
from typing import Any
from scripts.util.test_data_types import DeploymentPlatform
from scripts.util.constants.common_constants import (INSTALLER_CERTIFICATE_FILE_NAME, INSTALLER_PRIVATE_KEY_FILE_NAME,
                                                     INSTALLERS_RESOURCE_DIR, InstallerVersion)
from scripts.util.ssl_certificate_generator import SSLCertificateGenerator

USER_KEY = "user"
PASS_KEY = "password"

BASE_DIR = Path(__file__).resolve().parent
TEST_DIR = BASE_DIR / "test_dir"
LOG_DIR = TEST_DIR / "logs"
INSTALLERS_DEST_DIR = TEST_DIR / "installers"
SERVER_DEST_DIR = TEST_DIR / "server"
TEST_VARS = {"PYTHONPATH": "scripts/"}



class ServerWrapper(object):
    def __init__(self, proc: subprocess.Popen):
        self.proc = proc

    def __enter__(self):
        return self.proc

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.proc.terminate()
        save_file(self.proc.stdout, LOG_DIR / "server.log")


def get_env_vars() -> dict[str, str]:
    # This is required to pass current venv vars down to the subprocess for tests and server
    env_vars = os.environ.copy()
    env_vars.update(TEST_VARS)
    return env_vars


def save_file(data: list[str], path: Path) -> None:
    with path.open("w") as log:
        log.writelines(data)


def get_test_args(args: dict[str, Any]) -> list[str]:
    test_args = [f"--{USER_KEY}='{args[USER_KEY]}'", f"--{PASS_KEY}='{args[PASS_KEY]}'"]
    for platform in [p.value for p in DeploymentPlatform]:
        hosts = ','.join(args[platform])
        hosts and test_args.append(f"--{platform}={hosts}")
    return test_args


def run_test(test: str, test_args: list[str]) -> bool:
    test_name = Path(test).stem
    logging.info(f"Test: {test_name}")
    proc = subprocess.run([sys.executable, "-m", "pytest", "-o", "log_cli=true", test] + test_args, env=get_env_vars(), encoding="utf-8",
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    save_file(proc.stdout, LOG_DIR / f"{test_name}.log")
    result = proc.returncode == 0
    if result:
        logging.info("PASSED")
    else:
        logging.error(f"FAILED")
    return result


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
    return subprocess.Popen([sys.executable, server_path], env=get_env_vars(),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")


def get_file_content(path: Path) -> list[str]:
    with path.open("r") as f:
        return f.readlines()


def replace_tag(source: list[str], old: str, new: str) -> list[str]:
    return [line.replace(old, new) for line in source]


def sign_installer(installer: list[str]) -> list[str]:
    cmd = ["openssl", "cms", "-sign",
           "-signer", f"{INSTALLERS_DEST_DIR / INSTALLER_CERTIFICATE_FILE_NAME}",
           "-inkey", f"{INSTALLERS_DEST_DIR / INSTALLER_PRIVATE_KEY_FILE_NAME}"]

    proc = subprocess.run(cmd, input=f"{''.join(installer)}", encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        logging.error(f"Failed to sign installer: {proc.stdout}")
        sys.exit(1)

    signed_installer = proc.stdout.splitlines()
    delimiter = next(l for l in signed_installer if l.startswith("----"))
    index = signed_installer.index(delimiter)
    signed_installer = signed_installer[index + 1:]

    custom_delimiter = "----SIGNED-INSTALLER"
    return [ f"{l}\n" if not l.startswith(delimiter) else f"{l.replace(delimiter, custom_delimiter)}\n" for l in signed_installer]


def prepend(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line + '\n' + content)


def prepare_installers() -> None:
    logging.info("Preparing installers...")

    uninstall_template = get_file_content(INSTALLERS_RESOURCE_DIR / "uninstall.sh")
    uninstall_code = replace_tag(uninstall_template, "$", r"\$")

    oneagentctl_template = get_file_content(INSTALLERS_RESOURCE_DIR / "oneagentctl.sh")
    oneagentctl_code = replace_tag(oneagentctl_template, "$", r"\$")

    installer_partial_name = "Dynatrace-OneAgent-Linux"
    installer_template = get_file_content(INSTALLERS_RESOURCE_DIR / f"{installer_partial_name}.sh")
    installer_template = replace_tag(installer_template, "##UNINSTALL_CODE##", "".join(uninstall_code))
    installer_template = replace_tag(installer_template, "##ONEAGENTCTL_CODE##", "".join(oneagentctl_code))

    generator = SSLCertificateGenerator(
        country_name="US",
        state_name="California",
        locality_name="San Francisco",
        organization_name="Dynatrace",
        common_name="localhost"
    )
    generator.generate_and_save(f"{INSTALLERS_DEST_DIR / INSTALLER_PRIVATE_KEY_FILE_NAME}",
                                f"{INSTALLERS_DEST_DIR / INSTALLER_CERTIFICATE_FILE_NAME}")

    for version in InstallerVersion:
        installer_code = replace_tag(installer_template, "##VERSION##", version.value)
        installer_code = sign_installer(installer_code)
        save_file(installer_code, INSTALLERS_DEST_DIR / f"{installer_partial_name}-{version.value}.sh")

    prepend(INSTALLERS_DEST_DIR / f"{installer_partial_name}-{InstallerVersion.MALFORMED.value}.sh", "Malformed line")


def prepare_environment() -> None:
    logging.basicConfig(
        format="%(asctime)s [server] %(levelname)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO
    )
    shutil.rmtree(TEST_DIR, ignore_errors=True)
    os.makedirs(INSTALLERS_DEST_DIR, exist_ok=True)
    os.makedirs(SERVER_DEST_DIR, exist_ok=True)
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
