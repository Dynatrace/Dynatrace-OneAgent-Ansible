import logging

from tests.ansible.config import AnsibleConfigurator
from tests.ansible.runner import AnsibleRunner
from tests.command.platform_command_wrapper import PlatformCommandWrapper
from tests.deployment.deployment_operations import (
    run_deployment,
    set_installer_download_params,
)
from tests.deployment.deployment_platform import PlatformCollection


def parse_changed_tasks(ansible_output: str):
    excluded_tasks = [
        "dynatrace.oneagent.oneagent : Download OneAgent installer",
        "dynatrace.oneagent.oneagent : Install OneAgent"
    ]
    changed_tasks = []
    current_task = None

    for line in ansible_output.splitlines():
        if line.startswith("TASK [") and "]" in line:
            current_task = line.split("TASK [", 1)[1].split("]", 1)[0]

        if "changed:" in line and current_task:
            if current_task not in excluded_tasks:
                changed_tasks.append(current_task)

    return changed_tasks


def collect_changed_tasks_from_results(results):
    if not isinstance(results, (list, tuple)):
        results = [results]

    all_changed_tasks = []

    for i, res in enumerate(results):
        ansible_output = getattr(res, "stdout", "")
        if not isinstance(ansible_output, str):
            logging.warning("Unexpected stdout type in result[%d]: %s", i, type(ansible_output))
            continue

        changed_tasks = parse_changed_tasks(ansible_output)
        if changed_tasks:
            logging.warning("Changed tasks found in result[%d]: %s", i, changed_tasks)
            all_changed_tasks.extend([(i, task) for task in changed_tasks])

    return all_changed_tasks


def test_check_mode(
    runner: AnsibleRunner,
    configurator: AnsibleConfigurator,
    platforms: PlatformCollection,
    wrapper: PlatformCommandWrapper,
    installer_server_url: str,
):
    set_installer_download_params(configurator, installer_server_url)
    configurator.set_common_parameter(configurator.VALIDATE_DOWNLOAD_CERTS_KEY, False)
    configurator.set_common_parameter(configurator.PRESERVE_INSTALLER_KEY, True)

    logging.info("Running deployment with --check mode enabled")

    result = run_deployment(runner, configurator, check_mode=True)
    all_changed_tasks = collect_changed_tasks_from_results(result)

    assert not all_changed_tasks, f"Unexpected changed tasks found in check mode: {all_changed_tasks}"
