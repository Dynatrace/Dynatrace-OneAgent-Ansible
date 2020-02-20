# OneAgent-Ansible

This Ansible role installs [Dynatrace OneAgent](http://www.dynatrace.com) on Linux and Windows systems.

## Download

The role is available via:

- [Ansible Galaxy](https://galaxy.ansible.com/Dynatrace/OneAgent)
- [GitHub](https://github.com/dynatrace-acl/Dynatrace-OneAgent-Ansible)

## Description

This role downloads and installs the most recent version of the Dynatrace OneAgent for your Linux and Windows environments. Sign up for a [15-day free Dynatrace trial](https://www.dynatrace.com/trial/?vehicle_name=https://github.com/Dynatrace/Dynatrace-OneAgent-Ansible/) now!

## Requirements
To use this Role requires the following:
* __ansible >= 2.9.0__

__NOTE__: If attempting to `pip install` Ansible, it is recommended to use Python3.7. Using Python3.8 has shown stability issues and is not recommended at this time.

Testing and contributing to this Role, in addition to the above, requires the following:
* __VirtualBox >= 6.0.14__
* __ruby >= 2.6.5__
* __vagrant >= 2.2.6__
* __python ~= 3.7.5__

## Configuration

The following variables are _required_ and can be found in `defaults/main.yml`:

| Name | Default | Description
|-|-|-
| `dynatrace_environment_url` | `""` | URL of the target Dynatrace environment (SaaS or Managed)
| `dynatrace_paas_token` | `""` | The API Token retrieved from the "Deploy Dynatrace" installer page

The `dynatrace_environment_url` can take two values:
- **SaaS**: abc1234.live.dynatrace.com
- **Managed**: abc123.dynatrace-managed.com/e/1a2b3c4d-5e6f-6g7h-abcd-12ab34cd56ef

To retrieve the value for `dynatrace_paas_token`, do the following:
1. Select **Deploy Dynatrace** from the navigation menu.
2. Click the **Set up PaaS integration** button.
3. Copy the existing **InstallerDownload** token, or create and copy a new token.

## Example Playbook
```
- hosts: all
  roles:
    - role: Dynatrace.OneAgent
      dynatrace_environment_url: abc1234.live.dynatrace.com
      dynatrace_paas_token: ABcDeFgHIJKLMN12opqr
```

## Testing
[Test Kitchen](http://kitchen.ci) is used in combination with [InSpec](https://www.inspec.io/) to automatically test OneAgent deployments using this Ansible Role. By default, Test Kitchen uses [Vagrant](https://www.vagrantup.com/) to create virtual machines thru the [VirtualBox](https://www.virtualbox.org/) hypervisor. This requires that the tester's workstation has [VT-x](https://en.wikipedia.org/wiki/X86_virtualization#Intel_virtualization_.28VT-x.29) or [AMD-V](https://en.wikipedia.org/wiki/X86_virtualization#AMD_virtualization_.28AMD-V.29) virtualization enabled, as well as **at least 1 CPU and 2048MB of RAM available**.

To test modifications to this Role, follow the steps below:
1) Install Test Kitchen and dependencies:
    ```
    gem install bundler
    bundle install
    ```
2) Install Ansible and dependencies:
    ```
    pip install -r requirements.txt
    ```
3) Define required variables in `vars.yml` file. For example:
    ```
    ~$ cat vars.yml
    dynatrace_environment_url: abc1234.live.dynatrace.com
    dynatrace_paas_token: ABcDeFgHIJKLMN12opqr
    ```
4) Run all tests
    ```
    kitchen test
    ```

## License

Licensed under the MIT License. See the [LICENSE](https://github.com/dynatrace-acl/Dynatrace-OneAgent-Ansible/blob/master/LICENSE) file for details.
