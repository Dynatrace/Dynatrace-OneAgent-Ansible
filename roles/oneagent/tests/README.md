# Component tests
The tests support two types of deployment:
- local  - the tests are run on the same Unix machine as main node;
- remote - the tests are run on a remote Windows machine;
Currently, there is no option to mix these two types of deployment and the tests must be run for one platform at a time.
For local deployment, the tests are using mocked version of the OneAgent installer, which simulates its basic behavior -
returning version, deploying `uninstall.sh` script and creating `oneagentctl`, used for configuring installation.
For remote deployment, regular OneAgent installers are used, which are downloaded from the Dynatrace environment during
the tests.

## Requirements
- Python 3.10+
- pip 21.0+
- venv 20.0+
- 
## Running tests
Upon downloading the collection

```commandline
# Install dependencies
$ apt-get install -y python3-venv python3-pip sshpass

# Create virtual environment
$ python -m venv venv
$ source venv/bin/activate

# Install requirements
$ pip install -r roles/oneagent/tests/requirements.txt

# Build and install the collection
$ mkdir -p roles/oneagent/files && wget https://ca.dynatrace.com/dt-root.cert.pem -P roles/oneagent/files
$ ansible-galaxy collection build . -vvv
$ sudo bash -c "source venv/bin/activate && ansible-galaxy collection install -vvv dynatrace-oneagent*"

# Run tests for linux_x86 platform on local machine
$ sudo bash -c "source venv/bin/activate && pytest roles/oneagent/tests --linux_x86=localhost"

# Run tests with regular installer on remote Windows machine
$ sudo bash -c "source venv/bin/activate && pytest roles/oneagent/tests --user=<USER> --password=<password> \
--tenant=https://abc123456.com --tenant_token=<TOKEN> --windows_x86=<IP>"
```
