# Component tests
The tests are using mocked version of the OneAgent installer, which simulates its basic behavior - returning version, 
deploying `uninstall.sh` script and creating `oneagentctl`, used for configuring installation. The tests can run on 
the same machine as main node.

## Requirements
- Python 3.10+
- pip 21.0+
- venv 20.0+
- 
## Running tests
Upon downloading the collection

```commandline
# Install dependencies
$ apt-get install -y python3-venv python3-pip

# Create virtual environment
$ python -m venv venv
$ source venv/bin/activate

# Install requirements
$ pip install -r roles/oneagent/tests/requirements.txt

# Build and install the collection
$ ansible-galaxy collection build . -vvv
$ sudo bash -c "source venv/bin/activate && ansible-galaxy collection install -vvv dynatrace-oneagent*"

# Run tests (eg. For linux_x86 platform)
$ sudo bash -c "source venv/bin/activate && pytest roles/oneagent/tests --linux_x86=localhost"
```
