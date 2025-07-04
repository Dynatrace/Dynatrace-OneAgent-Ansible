# Component tests

The tests support two types of deployment:

- local - the tests are run on the same Unix machine as main node;
- remote - the tests are run on a remote Windows (Unix is not supported at the moment) machine;
  Currently, there is no option to mix these two types of deployment and the tests must be run for one platform at a time.

## Remote deployment

For remote deployment, regular OneAgent installers are used, which are downloaded from the Dynatrace environment during
the tests. To use this type of deployment, the following parameters must be provided:

- `--user` - username for the remote machine;
- `--password` - password for the remote machine;
- `--tenant` - The environment URL from which the installer will be downloaded, in form of `https://abc123456.com`;
- `--tenant_token` - Token for downloading the installer, generated in Deployment UI;
- `--windows_x86=<IP>` - IP address of the remote Windows machine;
  Failing to provide any of these parameters will result in failure.

## Local deployment

For local deployment, the tests are using mocked version of the OneAgent installer, which simulates its basic behavior -
returning version, deploying `uninstall.sh` script and creating `oneagentctl`, used for configuring installation.
To use this type of deployment, the only required parameter is `--linux_x86=localhost`. In case, multiple platforms for
local deployment are specified or any other platforms is used along with local one, only the first local platform is used.

## Requirements

- Python 3.10+
- pip 21.0+
- venv 20.0+

## Running tests

### Preparing test environment

Upon downloading the collection

```console
# Install dependencies
$ apt-get install -y python3-venv python3-pip sshpass

# Create virtual environment
$ python -m venv venv && source venv/bin/activate

# Install requirements
$ pip install -r roles/oneagent/tests/requirements.txt

# Install ansible (any supported version, for more details see: https://endoflife.date/api/v1/products/ansible/)
$ pip install ansible

# Build and install the collection
$ mkdir -p roles/oneagent/files && wget https://ca.dynatrace.com/dt-root.cert.pem -P roles/oneagent/files
$ ansible-galaxy collection build . -vvvf
$ sudo bash -c "source venv/bin/activate && ansible-galaxy collection install -vvvf dynatrace-oneagent*"
```

### Running tests locally and remotely

Running tests with regular manner requires one of the following commands:

```console
# Run tests for any platform (except from Windows) on local machine
$ sudo bash -c "source venv/bin/activate && pytest roles/oneagent/tests --linux_x86=localhost"

# Run tests with regular installer on remote Windows machine
$ sudo bash -c "source venv/bin/activate && pytest roles/oneagent/tests --user=<USER> --password=<password> \
--tenant=https://abc123456.com --tenant_token=<TOKEN> --windows_x86=<IP>"
```
