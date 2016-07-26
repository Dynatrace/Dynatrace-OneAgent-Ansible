# OneAgent-Ansible

This Ansible role installs [Dynatrace OneAgent](http://www.dynatrace.com) on Linux systems.

## Download

The role is available via:

- [Ansible Galaxy](https://galaxy.ansible.com/Dynatrace/OneAgent)
- [GitHub](https://github.com/dynatrace/Dynatrace-OneAgent-Ansible)

## Description

This role downloads and installs the most recent version of Dynatrace OneAgent in your Linux environment. Sign up for a [30-day free Dynatrace trial](http://www.dynatrace.com) now!

## Role Variables

As defined in ```defaults/main.yml```:

| Name                                | Default | Description
|-------------------------------------|---------|------------
| *dynatrace_oneagent_environment_id* |         | Your Dynatrace environment id.
| *dynatrace_oneagent_tenant_token*   |         | Your Dynatrace tenant token.

## Example Playbook

```
- hosts: all
  roles:
    - role: Dynatrace.OneAgent
      dynatrace_oneagent_environment_id: 123
      dynatrace_oneagent_tenant_token: abc
```

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