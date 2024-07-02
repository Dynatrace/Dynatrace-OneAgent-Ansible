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


def save_log(out, log_path: str):
    with open(log_path, "w") as log:
        for line in out:
            log.write(line)


def run_tests():
    logging.info("Running tests...")

    test_path = "scripts/tests"
    for test in glob.glob(f"{test_path}/test_*.py"):
        proc = subprocess.run(["pytest", test], env=get_env_vars(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
        save_log(proc.stdout, f"{LOG_DIR}/{Path(test).stem}.log")


def run_server():
    logging.info("Running server...")
    server_path = Path("scripts") / "server" / "server.py"
    return subprocess.Popen(["python", server_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=get_env_vars(), encoding="utf-8")


def prepare_installers():
    logging.info("Preparing installers...")

    installer_partial_name = "Dynatrace-OneAgent-Linux"
    src_dir = Path("resources") / "installers"
    version_tag = "##VERSION##"

    installers = list(glob.glob(f"{src_dir}/*.sh"))
    assert len(installers) == 1, "Only one installer is supported"

    with open(installers[0], "r") as i:
        installer_template = i.readlines()
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
    save_log(server.stdout, f"{LOG_DIR}/server.log")


if __name__ == "__main__":
    main()
