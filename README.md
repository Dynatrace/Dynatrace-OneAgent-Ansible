[![Build Status](https://travis-ci.org/redoceantechnology/Dynatrace-OneAgent-Ansible.svg?branch=development)](https://travis-ci.org/redoceantechnology/Dynatrace-OneAgent-Ansible)
# OneAgent-Ansible
 Fork of https://github.com/Dynatrace/Dynatrace-OneAgent-Ansible

This Ansible role installs [Dynatrace OneAgent](http://www.dynatrace.com) on the following Linux systems:
- Amazon ami,
- Centos 7,
- Centos 6 - not tested
- Solaris - not tested
- Windows server - not tested
- Ubuntu - not tested

## Quick Start
Requirements:
- Python 3.7.0
- ansible 2.7.6
- molecule 2.19.0
- docker-py 1.10.6
- clone the repo

Steps:
- install [Python 3](https://www.python.org/downloads/)
- install requirements
with pip either use the requirements file:
```
pip install -r requirements.tx
```
Or individually
```
pip install ansible
pip install molecule
pip install docker-py
```

# Run Tests
Navigate to root folder and run:
```
$ molecule test
...test output will follow
```

# Dev Usage
You can use molecule during development as well.
Same Molecule configuration can spawn virtual hosts or docker containers on which to run ansible playbooks against.

Use create to instruct molecule to launch an instance of the defined driver e.g virtualbox, vagrant, docker.
```
molecule create
```

The create command includes the prepare statement if a prepare.yml is set.
```
molecule prepare
```

TDD run verify to run tests. They should fail.
```
molecule verify
```

Runs the playbook against the instance.
```
molecule converge
```

Tests should now pass.
```
molecule verify
```

## Download
The role is available via:

- TODO: [Ansible Galaxy]()
- [GitHub](https://github.com/redoceantechnology/Dynatrace-OneAgent-Ansible.git)

## Description
This role downloads and installs the most recent version of Dynatrace OneAgent in your Linux environment.

## Configuration
All variables are defined in ```defualts/main.yml```
Playbook vars can override the above.
And can also be called using tags: ```$ ansible-playbook playbook.yml -vvv --tags "config, uninstall"```
Important values in  ```defaults/main.yml```:

- oneagent_installer_script_url: url to download one agent from. Use inventory vars for environment specific urls.
- uninstall_dynatrace_oneagent: defualts to False. Set this to true as well the config and uninstall tag to roll back the installation.
e.g: ```$ ansible-playbook playbook.yml -vvv --tags "config, uninstall```

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

You can also edit the installer path although this simply creates a symlink to /opt/dynatrace
*Installation under custom path or with /opt being a symlink when SELinux is enabled requires semanage to be available for the purpose of assigning persistent security contexts to Dynatrace OneAgent files and directories.*

## Example Playbook
```
- hosts: all
  roles:
    - role: Dynatrace.OneAgent
      oneagent_installer_script_url: YOUR_ONEAGENT_INSTALLER_SCRIPT_URL
      uninstall_dynatrace_oneagent: False
```

More in-depth examples can be found in the [examples](https://github.com/redoceantechnology/Dynatrace-OneAgent-Ansible/tree/master/examples) folder.

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

TODO: Setup [Vagrant](https://www.vagrantup.com/) to use for docker tests.
Provisioning for docker since installation OneAgent on [Docker](https://www.docker.com/) containers is possible only by running Docker command -> [see our the Dynatrace blog article](https://www.dynatrace.com/blog/new-docker-image-leverages-bootstrapper-download-oneagent-installer/).

*Please note, that running tests using Vagrant provisioning on virtual machine or cloud instance may cause serious difficulties since [VT-x](https://en.wikipedia.org/wiki/X86_virtualization#Intel_virtualization_.28VT-x.29) or [AMD-V](https://en.wikipedia.org/wiki/X86_virtualization#AMD_virtualization_.28AMD-V.29) virtualization can't be nested.*


## License

Licensed under the MIT License. See the [LICENSE](https://github.com/redoceantechnology/Dynatrace-OneAgent-Ansible/blob/master/LICENSE) file for details.
