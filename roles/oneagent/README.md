# OneAgent role

## Requirements

- OneAgent version 1.199+.
- Script access to the OneAgent installer file. You can either:
  - configure the script to download the installer directly from your Dynatrace environment,
  - download it yourself and upload it to the primary node.

### Direct download from your environment

The script utilizes [Deployment API] to download a platform-specific installer to the target machine.
You will need to supply the role with information required to authenticate the API call in your environment:

- The environment URL:
  - **SaaS**: `https://{your-environment-id}.live.dynatrace.com`
  - **Managed**: `https://{your-domain}/e/{your-environment-id}`
- The [PaaS token] of your environment

### Local installer

Use the Dynatrace UI to download OneAgent and upload it to the primary node. The script copies the installer to target machines during execution.
Note that Windows, Linux, and AIX require their dedicated installers. Original installer names indicate the target platform. If you need to change the installer names, make sure the script can distinguish them.
If you don't specify the installer, the script attempts to use the direct download.

### Configure existing installation

The role is capable of configuring existing installation by utilizing `oneagentctl`.
There are 2 ways of applying configuration:

- In case the Agent in the same or lower version is installed on specified host already, the script
  uses provided installation parameters and runs `oneagentctl` with them, skipping installation procedure.
- In case no `environment_url`, `paas_token` and `local_installer` parameters are provided,
  the script runs `oneagentctl` with provided parameters directly.

For full list of suitable parameters, see [OneAgent configuration via command-line interface].

## Variables

The following variables are available in `defaults/main/` and can be overridden:

| Name                             | Default                                                                    | Description                                                                                                                                                 |
| -------------------------------- | -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `oneagent_environment_url`       | `-`                                                                        | The URL of the target Dynatrace environment (see [Direct download from your environment](#direct-download-from-your-environment)).                          |
| `oneagent_paas_token`            | `-`                                                                        | The [PaaS Token] retrieved from the "Deploy Dynatrace" installer page.                                                                                      |
| `oneagent_local_installer`       | `-`                                                                        | The Path to OneAgent installer stored on the main node.                                                                                                     |
| `oneagent_installer_arch`        | `-`                                                                        | Specifies the OneAgent installer architecture.                                                                                                              |
| `oneagent_version`               | `latest`                                                                   | The required version of the OneAgent in the `1.199.247.20200714-111723` format. See [Deployment API - GET available versions of OneAgent] for more details. |
| `oneagent_download_dir`          | Linux: `$TEMP` or `/tmp`</br>Windows: `%TEMP%` or `C:\Windows\Temp`        | Installer download directory. For Linux and AIX, the directory must not contain spaces. Will be created if it does not exist.                               |
| `oneagent_install_args`          | `-` Dynatrace OneAgent installation parameters defined as a list of items. |
| `oneagent_platform_install_args` | `-`                                                                        | Additional list of platform-specific installation parameters, appended to `oneagent_install_args' when run on a respective platform.                        |
| `oneagent_preserve_installer`    | `false`                                                                    | Preserve installers on secondary machines after deployment.                                                                                                 |
| `oneagent_package_state`         | `present`                                                                  | OneAgent package state; use `present` or `latest` to make sure it's installed, or `absent` in order to uninstall.                                           |
| `oneagent_reboot_host`           | `false`                                                                    | Reboot the secondary machine after OneAgent installation                                                                                                    |
| `oneagent_verify_signature`      | `true`                                                                     | Verifies installer's signature (available only on AIX/Linux platforms)                                                                                      |
| `oneagent_reboot_timeout`        | `3600`                                                                     | Set the timeout for rebooting secondary machine in seconds                                                                                                  |

For more information, see customize OneAgent installation documentation for [Linux], [Windows], and [AIX].

## Examples

You can find example playbooks in the `examples` directory within the role. The directory contains the following: -`local_installer` - basic configuration with local installers. -`advanced_config` - showing advanced configuration with a custom install path and download directory. -`oneagentctl_config` - showing bare configuration with oneagentctl.

Additionally, each directory contains inventory file with basic hosts configuration for playbooks.

**NOTE:** For multi-platform Windows, Linux or AIX deployment, you must specify the `become: true` option for proper machines group in the inventory file.
On Windows, `become: true` option is not supported.
Since Windows paths are different compared to a traditional Linux system, review [Path Formatting for Windows] to avoid issues during install.

## Logging

The logs produced by ansible can be collected into a single file located on the managed node instead of printing them to STDOUT.
Log output will still be printed to the STDOUT.
There are several ways to achieve that using ansible's configuration setting:

- Set `ANSIBLE_LOG_PATH` environment variable containing path to the log file before executing a playbook with the role.
- Specify `log_path` variable in the `[default]` section of ansible's [configuration settings file].

The verbosity of the logs can be controlled with the command line option `-v`.
Repeating the option multiple times gets maximal verbosity up to the connection debugging level: `-vvvv`.

[PaaS token]: https://www.dynatrace.com/support/help/shortlink/token#paas-token-
[Deployment API]: https://www.dynatrace.com/support/help/shortlink/api-deployment
[Deployment API - GET available versions of OneAgent]: https://www.dynatrace.com/support/help/shortlink/api-deployment-get-versions
[Path Formatting for Windows]: https://docs.ansible.com/ansible/latest/user_guide/windows_usage.html#path-formatting-for-windows
[Windows]: https://www.dynatrace.com/support/help/shortlink/windows-custom-installation
[Linux]: https://www.dynatrace.com/support/help/shortlink/linux-custom-installation
[AIX]: https://www.dynatrace.com/support/help/shortlink/aix-custom-installation
[configuration settings file]: https://docs.ansible.com/ansible/latest/reference_appendices/general_precedence.html#configuration-settings
