# OneAgent-Ansible

This Ansible role installs [Dynatrace OneAgent](http://www.dynatrace.com) on Linux and Windows systems.

## Download

The role is available via:

- [Ansible Galaxy](https://galaxy.ansible.com/Dynatrace/OneAgent)
- [GitHub](https://github.com/dynatrace-acl/Dynatrace-OneAgent-Ansible)

## Description

This role downloads and installs the most recent version of the Dynatrace OneAgent for your Linux and Windows environments. Sign up for a [15-day free Dynatrace trial](https://www.dynatrace.com/trial/?vehicle_name=https://github.com/Dynatrace/Dynatrace-OneAgent-Ansible/) now!

## Configuration

The following variables are _required_ and can be found in `defaults/main.yml`:

| Name | Default | Description
|-|-|-
| `dynatrace_environment_url` | `""` | URL of the target Dynatrace environment (SaaS or Managed)
| `dynatrace_api_token` | `""` | The API Token retrieved from the "Deploy Dynatrace" installer page

The `dynatrace_environment_url` can take two values:
- **SaaS**: abc1234.live.dynatrace.com
- **Managed**: abc123.dynatrace-managed.com/e/1a2b3c4d-5e6f-6g7h-abcd-12ab34cd56ef

To retrieve the proper `dynatrace_api_token`, do the following:
1. Select **Deploy Dynatrace** from the navigation menu.
2. Click the **Start installation** button.
3. Select **Linux** from the available platforms (even if you are installing on Windows).
4. Copy the value of the `Api-Token` key in the installer script URL.

## Example Playbook
```
- hosts: all
  roles:
    - role: Dynatrace.OneAgent
      dynatrace_environment_url: abc1234.live.dynatrace.com
      dynatrace_api_token: ABcDeFgHIJKLMN12opqr
```

## Testing
[Test Kitchen](http://kitchen.ci) is used in combination with [InSpec](https://www.inspec.io/) to automatically test OneAgent deployments using this Ansible Role. By default, Test Kitchen uses [Vagrant](https://www.vagrantup.com/) to create virtual machines thru the [VirtualBox](https://www.virtualbox.org/) hypervisor. This requires that the tester's workstation has [VT-x](https://en.wikipedia.org/wiki/X86_virtualization#Intel_virtualization_.28VT-x.29) or [AMD-V](https://en.wikipedia.org/wiki/X86_virtualization#AMD_virtualization_.28AMD-V.29) virtualization enabled, as well as **at least 1 CPU and 2048MB of RAM available**.

For installing Test Kitchen, **Ruby 2.6.5** is recommended. Testing also requires that Ansible be installed locally on the tester's workstation. This Role was developed using **Ansible 2.9.0** with **Python 3.7.5**.

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
3) Run all tests
    ```
    kitchen test
    ```

## License

Licensed under the MIT License. See the [LICENSE](https://github.com/dynatrace-acl/Dynatrace-OneAgent-Ansible/blob/master/LICENSE) file for details.
