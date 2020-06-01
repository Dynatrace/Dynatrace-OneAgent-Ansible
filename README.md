Ansible Role: Dynatrace OneAgent
================

This ansible role deploys the Dynatrace OneAgent on Linux and Windows Operating Systems with different available configurations and ensures the OneAgent service maintains a running state. It provides the tasks to interact with the various OneAgent configuration files.

**Note:** This role is still in active development. There may be unidentified issues and the role variables may change as development continues.

Requirements
------------

To use this Role requires the following:

* ansible >= 2.9.0

You will then need to supply the role with two critical pieces of information:

* The environment URL: **Managed** `https://{your-domain}/e/{your-environment-id}` |  **SaaS** `https://{your-environment-id}.live.dynatrace.com`
* The [PaaS token] of your environment for downloading the OneAgent installer

Refer to the customize OneAgent installation documentation on [Dynatrace Supported Operating Systems]
This role uses the Dynatrace deployment API for downloading the installer for each supported OS. See [Deployment API]

Installation
------------

**Ansible Galaxy**

Use `ansible-galaxy install dynatrace.oneagent` to install the latest stable release of the role on your system.

**Git**

Use `git clone https://github.com/Dynatrace/Dynatrace-OneAgent-Ansible.git` to pull the latest edge commit of the role from GitHub.

Role variables
--------------

The following variables are available in `defaults/main/` and can be overriden:

| Name | Default | Description
|-|-|-
| `dynatrace_environment_url` | `""` | URL of the target Dynatrace environment (SaaS or Managed)
| `dynatrace_paas_token` | `""` | The API Token retrieved from the "Deploy Dynatrace" installer page
| `dynatrace_oneagent_version` | `"latest"` | The required version of the OneAgent in 1.155.275.20181112-084458 format
| `dynatrace_oneagent_download_dir` | `Linux: /tmp/ Windows: C:\Windows\Temp\` | Dynatrace OneAgent installer file download directory
| `dynatrace_oneagent_install_args` | `APP_LOG_CONTENT_ACCESS=1 INFRA_ONLY=0` | Dynatrace OneAgent install parameters defined as a list of items
| `dynatrace_oneagent_host_tags` | `""` | Values to automatically add tags to a host, should contain a list of strings or key/value pairs. Spaces are used to separate tag values.
| `dynatrace_oneagent_host_metadata` | `""` | Values to automatically add metadata to a host, should contain a list of strings or key/value pairs. Spaces are used to separate metadata values.
| `dynatrace_oneagent_hostname` | `""` | Overrides an automatically detected host name.
| `dynatrace_oneagent_state:` | `"started"` | Set initial oneagent state. Recommended values: `started` or `stopped`
| `dynatrace_oneagent_restart_state` | `"restarted"` | Set oneagent state when configuration changes are made. Recommended values: `restarted` or `reloaded`
| `dynatrace_oneagent_package_state` | `"present"` | oneagent package state; use `present` to make sure it's installed, or `latest`
| `dynatrace_oneagent_package_download_validate_certs` | `yes` | oneagent package download using secure https; use `no` to skip tls verification

Example Playbook
----------------

Most basic OneAgent installation using a SAAS tenant

```bash
---
- hosts: all
  become: true
  roles:
    - role: Dynatrace.OneAgent
  vars:
    dynatrace_environment_url: {your-environment-id}.live.dynatrace.com
    dynatrace_paas_token: {your-paas-token}
```

OneAgent installation using a managed tenant with a specific version. The required version of the OneAgent must be in 1.155.275.20181112-084458 format. See [Deployment API - GET available versions of OneAgent]

```bash
---
- hosts: all
  become: true
  roles:
    - role: Dynatrace.OneAgent
  vars:
    dynatrace_environment_url: {your-domain}/e/{your-environment-id}
    dynatrace_paas_token: {your-paas-token}
    dynatrace_oneagent_version: 1.189.99.20200317-150951
```

Advanced configuration - Download OneAgent installer to a custom directory with additional OneAgent install parameters should be defined as follows (will override default install args):

```bash
---
- hosts: all
  become: true
  roles:
    - role: Dynatrace.OneAgent
  vars:
    dynatrace_environment_url: {your-environment-id}.live.dynatrace.com
    dynatrace_paas_token: {your-paas-token}
    dynatrace_oneagent_download_dir: /home/user1/
    dynatrace_oneagent_install_args:
      APP_LOG_CONTENT_ACCESS: 1
      INFRA_ONLY: 0
      HOST_GROUP: CENTOS_VM
      INSTALL_PATH: /var/
```

Setting tags, metadata and custom hostname

```bash
---
- hosts: all
  become: true
  roles:
    - role: Dynatrace.OneAgent
  vars:
    dynatrace_environment_url: {your-environment-id}.live.dynatrace.com
    dynatrace_paas_token: {your-paas-token}
    dynatrace_oneagent_host_tags: TestHost Gdansk role=fallback
    dynatrace_oneagent_host_metadata: Environment=Prod Organization=D1P Owner=john.doe@dynatrace.com Support=https://www.dynatrace.com/support
    dynatrace_oneagent_hostname: ansible.host.vm
```

__NOTE:__ On Windows, the `become: yes` option is not needed and will fail as it is not supported. Since windows paths are different than a traditional Linux system, review [Path Formatting for Windows] to avoid issues during install.

Testing
-------

Testing and contributing to this ansible role requires the following:

* ansible >= 2.9.0
* VirtualBox >= 6.0.14
* ruby >= 2.6.5
* vagrant >= 2.2.6
* python ~= 3.7.4

[Test Kitchen] is used in combination with [InSpec] to automatically test OneAgent deployments using this Ansible Role. By default, Test Kitchen uses [Vagrant] to create virtual machines thru the [VirtualBox] hypervisor. This requires that the tester's workstation has [VT-x] or [AMD-V] virtualization enabled, as well as **at least 1 CPU and 2048MB of RAM available**.

To test modifications to this Role, follow the steps below:

1) Install Test Kitchen and dependencies:

    ```bash
    gem install bundler
    bundle install
    ```

2) Install Ansible and dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3) Define required variables in `vars.yml` file. For example:

    ```bash
    ~$ cat vars.yml
    dynatrace_environment_url: {your-environment-id}.live.dynatrace.com
    dynatrace_paas_token: {your-paas-token}
    ```

4) Run all tests

    ```bash
    kitchen test
    ```

License
-------

Licensed under the MIT License. See the [LICENSE] file for details.

Author Information
------------------

Dynatrace Autonomous Cloud Enablement team (ACE): [ace@dynatrace.com]

[Dynatrace Supported Operating Systems]:https://www.dynatrace.com/support/help/technology-support/operating-systems/
[PAAS token]: https://www.dynatrace.com/support/help/technology-support/cloud-platforms/kubernetes/other-deployments-and-configurations/deploy-oneagent-on-kubernetes-for-application-only-monitoring/#expand-1548how-to-get-your-paas-token
[Deployment API]: https://www.dynatrace.com/support/help/extend-dynatrace/dynatrace-api/environment-api/deployment/
[Deployment API - GET available versions of OneAgent]: https://www.dynatrace.com/support/help/extend-dynatrace/dynatrace-api/environment-api/deployment/oneagent/get-available-versions/
[Path Formatting for Windows]: https://docs.ansible.com/ansible/latest/user_guide/windows_usage.html#path-formatting-for-windows
[Test Kitchen]: http://kitchen.ci
[InSpec]: https://www.inspec.io/
[Vagrant]: https://www.vagrantup.com/
[VirtualBox]: https://www.virtualbox.org/
[VT-x]: https://en.wikipedia.org/wiki/X86_virtualization#Intel_virtualization_.28VT-x.29
[AMD-V]: https://en.wikipedia.org/wiki/X86_virtualization#AMD_virtualization_.28AMD-V.29
[LICENSE]: https://github.com/dynatrace-acl/Dynatrace-OneAgent-Ansible/blob/master/LICENSE
[ace@dynatrace.com]: mailto:ace@dynatrace.com
