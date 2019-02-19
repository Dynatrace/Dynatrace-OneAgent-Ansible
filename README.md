# OneAgent-Ansible
Based on original role by Dynatrace

This Ansible role installs [Dynatrace OneAgent](http://www.dynatrace.com) on Linux systems.

## Quick Start
Requirements:
- Python 3.7.0
- ansible 2.7.6
- molecule 2.19.0
- docker-py 1.10.6
- clone the repo

Steps:
- install [Python 3](https://www.python.org/downloads/)
```
pip install ansible
pip install molecule
pip install docker-py
```

# go to root folder and run:
```
$ molecule test
...test output will follow
```

## Download

The role is available via:

- [Ansible Galaxy](https://galaxy.ansible.com/Dynatrace/OneAgent)
- [GitHub](https://github.com/dynatrace/Dynatrace-OneAgent-Ansible)

## Description

This role downloads and installs the most recent version of Dynatrace OneAgent in your Linux environment. Sign up for a [15-day free Dynatrace trial](https://www.dynatrace.com/trial/?vehicle_name=https://github.com/Dynatrace/Dynatrace-OneAgent-Ansible/) now!

## Configuration

Please edit below role variable(s) defined in ```defaults/main.yml```:

| Name                                   | Default            | Description
|----------------------------------------|--------------------|------------
| *oneagent_installer_script_url*        |                    | Url presented in the command on the Dynatrace OneAgent installation page

You can get your url by following these steps:

1. Select **Deploy Dynatrace** from the navigation menu.
2. Click the **Start installation** button.
3.  For **Linux**
   - Locate your `oneagent_installer_script_url`, as shown below.
   ![Alt text](https://raw.githubusercontent.com/Dynatrace/Dynatrace-OneAgent-Ansible/images/url_script_screenshot.png)
4. For **Windows**
    - Rightclick on "Download agent.exe" button and select "Copy link address"
5. Paste the url as a value for the *oneagent_installer_script_url* variable in `defaults/main.yml`.

### Previous versions

If you’ve been using automated scripts or deployment via YAML utilizing the TENANT, SERVER, TENANT_TOKEN command line arguments, you’ll find that the new approach is fully transparent and no changes are required.

## Example Playbook

```
- hosts: all
  roles:
    - role: Dynatrace.OneAgent
      oneagent_installer_script_url: YOUR_ONEAGENT_INSTALLER_SCRIPT_URL
```

More in-depth examples can be found in the [examples](https://github.com/Dynatrace/Dynatrace-OneAgent-Ansible/tree/master/examples) folder.

## Testing

We use [Molecule](https://molecule.readthedocs.io/en/latest/) to automatically test our automated deployments with [Test Infra](https://testinfra.readthedocs.io/en/latest/) and [Python3](https://docs.python.org/3/):

1) Install Molecule and its dependencies from within the project's directory:

```
pip install ansible
pip install molecule
pip install docker-py
```

2) Run all tests

```
molecule test
```

By default, we run our tests using [Vagrant](https://www.vagrantup.com/) provisioning tool (see `molecule.yml`) since installation OneAgent on [Docker](https://www.docker.com/) containers is possible only by running Docker command -> [see our blog article](https://www.dynatrace.com/blog/new-docker-image-leverages-bootstrapper-download-oneagent-installer/).

*Please note, that running tests using Vagrant provisioning on virtual machine or cloud instance may cause serious difficulties since [VT-x](https://en.wikipedia.org/wiki/X86_virtualization#Intel_virtualization_.28VT-x.29) or [AMD-V](https://en.wikipedia.org/wiki/X86_virtualization#AMD_virtualization_.28AMD-V.29) virtualization can't be nested.*

## License

Licensed under the MIT License. See the [LICENSE](https://github.com/dynatrace/Dynatrace-OneAgent-Ansible/blob/master/LICENSE) file for details.
