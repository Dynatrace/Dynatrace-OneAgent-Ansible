import logging
from pathlib import Path

from tests.ansible.config import AnsibleConfigurator
from tests.ansible.runner import AnsibleRunner
from tests.command.platform_command_wrapper import PlatformCommandWrapper
from tests.constants import (
    INSTALLER_SERVER_TOKEN,
    UNIX_DOWNLOAD_DIR_PATH,
    WINDOWS_DOWNLOAD_DIR_PATH,
)
from tests.deployment.deployment_operations import (
    check_agent_state,
    check_download_directory,
    get_oneagentctl_path,
    select_by_platform,
    perform_operation_on_platforms,
    run_deployment,
    set_installer_download_params,
)
from tests.deployment.deployment_platform import (
    DeploymentPlatform,
    DeploymentResult,
    PlatformCollection,
)


def test_basic_installation(
    runner: AnsibleRunner,
    configurator: AnsibleConfigurator,
    platforms: PlatformCollection,
    wrapper: PlatformCommandWrapper,
    installer_server_url: str,
):
    logging.info("Running basic installation test")

    set_installer_download_params(configurator, installer_server_url)
    configurator.set_common_parameter(configurator.VALIDATE_DOWNLOAD_CERTS_KEY, False)
    configurator.set_common_parameter(configurator.PRESERVE_INSTALLER_KEY, True)
    configurator.set_common_parameter(
        configurator.INSTALLER_ARGS_KEY,
        [
            f"{CTL_OPTION_SET_HOST_TAG}={dummy_common_tag}",
            f"{CTL_OPTION_SET_HOST_PROPERTY}={dummy_common_property}",
        ],
    )

    result = run_check_mode(runner, check_mode=True)

    logging.info("Running Check Mode / Dry Run check")

    for result in results:
        changed_tasks = re.findall(r'changed=(\d+)', result.stdout)

        if changed_tasks:
            changed_count = sum(map(int, changed_tasks))
            if changed_count > 0:
                assert change_count == 0, f"Playbook would change {changed_count} tasks"

    return results
