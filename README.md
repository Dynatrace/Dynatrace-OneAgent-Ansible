# Dynatrace OneAgent Ansible collection

Ansible collection for deploying Dynatrace OneAgent.

## Description

The Dynatrace OneAgent Ansible collection is a collection consisting of a single role that handles the installation and
configuration of OneAgent and ensures the OneAgent service remains in a running state.

## Requirements

- Ansible >= 2.15.0
- pywinrm >= 0.4.3 (Windows only)

## Installation

Before using this collection, you need to install it with the Ansible Galaxy command-line tool:

```
ansible-galaxy collection install dynatrace.oneagent
```

You can also include it in a requirements.yml file and install it with ansible-galaxy collection install -r
requirements.yml, using the format:

```yaml
collections:
  - name: dynatrace.oneagent
```

Note that if you install any collections from Ansible Galaxy, they will not be upgraded automatically when you upgrade
the Ansible package.
To upgrade the collection to the latest available version, run the following command:

```
ansible-galaxy collection install dynatrace.oneagent --upgrade
```

You can also install a specific version of the collection, for example, if you need to downgrade when something is
broken in the latest version (please report an issue in this repository). Use the following syntax to install version
1.0.0:

```
ansible-galaxy collection install dynatrace.oneagent:==1.0.0
```

See [using Ansible collections](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html) for more details.

## Use Cases

See [OneAgent role README](roles/oneagent/README.md) for more details.

## Testing

The collection was tested against Ansible sanity tests and component tests. The latter runs regular deployment with
the installer and checks veriety of installation scenarios.
See [OneAgent role tests README](roles/oneagent/tests/README.md) for more details.

## Support

You can submit a support request [here](https://www.dynatrace.com/support/contact-support).

## Release Notes and Roadmap

For release notes see [CHANGELOG](CHANGELOG.md).

## Related Information

See more on https://docs.dynatrace.com/docs/shortlink/oneagent-ansible.

## License Information

This Ansible collection is published under Apache 2.0 license. See [LICENSE](LICENSE) for more details.
