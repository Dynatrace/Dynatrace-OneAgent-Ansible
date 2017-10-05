# OneAgent-Ansible

This Ansible role installs [Dynatrace OneAgent](http://www.dynatrace.com) on Linux systems.

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
   ![Alt text](https://user-images.githubusercontent.com/23307837/31234263-bf223030-a9ee-11e7-94f8-69945b82e791.png)
4. For **Windows**
    - Rightclick on "Download agent.exe" button and select "Copy link address"
5. Paste the url as a value for the *oneagent_installer_script_url* variable in `defaults/main.yml`.

## Example Playbook

```
- hosts: all
  roles:
    - role: Dynatrace.OneAgent
      oneagent_installer_script_url: YOUR_ONEAGENT_INSTALLER_SCRIPT_URL
```

More in-depth examples can be found in the [examples](https://github.com/Dynatrace/Dynatrace-OneAgent-Ansible/tree/master/examples) folder.

## Testing

We use [Test Kitchen](http://kitchen.ci) to automatically test our automated deployments with [Serverspec](http://serverspec.org) and [RSpec](http://rspec.info/):

1) Install Test Kitchen and its dependencies from within the project's directory:

```
gem install bundler
bundle install
```

2) Run all tests

```
kitchen test
```

By default, we run our tests inside [Docker](https://www.docker.com/) containers as this considerably speeds up testing time (see `.kitchen.yml`).

## License

Licensed under the MIT License. See the [LICENSE](https://github.com/dynatrace/Dynatrace-OneAgent-Ansible/blob/master/LICENSE) file for details.
