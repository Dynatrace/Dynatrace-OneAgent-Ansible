# Component tests
The tests are using mocked version of the OneAgent installer, which simulates its basic behavior - returning version, 
deploying `uninstall.sh` script and creating `oneagentctl`, used for configuring installation. 
The mocked installers are being created once the `run.py` is being executed.
The tests are adapted run on the same machine as main node. 
## Requirements
- Python 3.10+
- pip 21.0+
- virtualenv 20.0+
## Running tests
Upon downloading the collection
```commandline
# Install dependencies
$ pip install virtualenv

# Create virtual environment
$ python -m virtualenv venv && source venv/bin/activate

# Install requirements
$ pip install -r roles/oneagent/tests/component/resources/requirements.txt

# Download CA certificate
$ mkdir -p roles/oneagent/files && wget https://ca.dynatrace.com/dt-root.cert.pem -P roles/oneagent/files

# Build and install the collection
$ ansible-galaxy collection build . -vvv
$ ansible-galaxy collection install -vvv dynatrace-oneagent*

# Run tests (eg. For linux_x86 platform)
$ cd roles/oneagent/tests/component
$ python run.py --linux_x86=localhost
```