import glob
import logging
import os
import shutil
import subprocess

from pathlib import Path

TEST_DIR = Path("test_dir")
LOG_DIR = TEST_DIR / "logs"
INSTALLERS_DIR = TEST_DIR / "installers"
TEST_VARS = {"PYTHONPATH": "scripts/"}


def get_env_vars():
    env_vars = os.environ.copy()
    env_vars.update(TEST_VARS)
    return env_vars


def save_log(out, log_path: Path):
    with open(log_path, "w") as log:
        for line in out:
            log.write(line)


def run_tests():
    logging.info("Running tests...")

    test_path = "scripts/tests"
    for test in glob.glob(f"{test_path}/test_i*.py"):
        test_name = Path(test).stem
        proc = subprocess.run(["pytest", test, "--user=''", "--password=''", "--linux_x86=localhost"],
                              env=get_env_vars(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
        save_log(proc.stdout, LOG_DIR / f"{test_name}.log")


def run_server():
    logging.info("Running server...")
    server_path = Path("scripts") / "server" / "server.py"
    return subprocess.Popen(["python", server_path], env=get_env_vars(),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")


def get_file_content(path: Path):
    with open(path, "r") as f:
        return f.readlines()


def prepare_installers():
    logging.info("Preparing installers...")

    # TODO: remove SH once oneagentctl in ready
    oneagentctl_bin_name = "oneagentctl.sh"
    uninstall_script_name = "uninstall.sh"
    installer_partial_name = "Dynatrace-OneAgent-Linux"

    version_tag = "##VERSION##"
    uninstall_code_tag = "##UNINSTALL_CODE##"
    oneagentctl_code_tag = "##ONEAGENTCTL_CODE##"

    resource_dir = Path("resources") / "installers"

    uninstall_code = get_file_content(resource_dir / uninstall_script_name)
    uninstall_code = [line.replace("$", r"\$") for line in uninstall_code]

    oneagentctl_code = get_file_content(resource_dir / oneagentctl_bin_name)
    oneagentctl_code = [line.replace("$", r"\$") for line in oneagentctl_code]

    installer_template = get_file_content(resource_dir / f"{installer_partial_name}.sh")
    installer_template = [line.replace(uninstall_code_tag, "".join(uninstall_code)) for line in installer_template]
    installer_template = [line.replace(oneagentctl_code_tag, "".join(oneagentctl_code)) for line in installer_template]

    for ver in ["1.0.0", "2.0.0"]:
        versioned_installer = [line.replace(version_tag, ver) for line in installer_template]
        with open(INSTALLERS_DIR / f"{installer_partial_name}-{ver}.sh", "w") as f:
            f.writelines(versioned_installer)


def prepare_environment():
    shutil.rmtree(TEST_DIR, ignore_errors=True)
    os.makedirs(INSTALLERS_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    prepare_installers()


def main():
    prepare_environment()
    server = run_server()
    run_tests()

    server.terminate()
    save_log(server.stdout, LOG_DIR / "server.log")


if __name__ == "__main__":
    main()
