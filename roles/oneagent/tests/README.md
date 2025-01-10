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
-

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

# Build and install the collection
$ mkdir -p roles/oneagent/files && wget https://ca.dynatrace.com/dt-root.cert.pem -P roles/oneagent/files
$ ansible-galaxy collection build . -vvv
$ sudo bash -c "source venv/bin/activate && ansible-galaxy collection install -vvv dynatrace-oneagent*"
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

There is also an option to run tests with placed-in installers using `--preserve-installers` switch.
In this mode, the test environment won't be fully cleaned. It requires that both installers differs in version and have
the naming schema from tenant, e.g. `Dynatrace-OneAgent-Linux-1.301.0.sh`, `Dynatrace-OneAgent-Linux-arm-1.302.0.sh`.
Also, the installers certificate must be downloaded for successful run. </br>
You can refer to [this documentation](https://docs.dynatrace.com/docs/shortlink/api-deployment-get-versions) on how to
list available installers.
For downloading the specific version of the OneAgent, visit
[this documentation](https://docs.dynatrace.com/docs/shortlink/api-deployment-get-oneagent-version). </br>
To run tests in this mode, download 2 versions of installers you want along with the certificate and place them in
`test_dir/installers` directory. Then, you can run the tests.

```console
# Create directory `test_dir/installers` and place the installers and certificate in it
$ mkdir -p test_dir/installers
$ cp /path/and/name/of/both/installers test_dir/installers
$ wget https://ca.dynatrace.com/dt-root.cert.pem -P test_dir/installers

# Run tests on local machine
$ sudo bash -c "source venv/bin/activate && pytest roles/oneagent/tests --linux_x86=localhost --preserve_installers"
```
