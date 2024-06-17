# Dynatrace OneAgent collection
In its current state, the collection consists of a single role that deploys Dynatrace OneAgent on Linux and Windows operating systems using dedicated configuration and ensures the OneAgent service maintains a running state.

## Requirements
### General
* Ansible >= 2.15.0
### Windows
* pywinrm >= 0.4.1

## Setup
`pip install -r requirements.txt`

## Build
`ansible-galaxy collection build .`

## Installation
To install the latest stable release of the collection on your system, call:

`ansible-galaxy collection install dynatrace.oneagent`

To install the locally built collection on your system, call:

`ansible-galaxy collection install dynatrace-oneagent-<version>.tar.gz`

## License
Licensed under the MIT License.

## Support
In case of difficulties, contact our [SUPPORT].

[SUPPORT]: https://www.dynatrace.com/support/contact-support/
