#!/bin/bash -eu

# This file simulates the basic behavior of the uninstall.sh script

set -e

main() {
	rm -rf /opt/dynatrace
}

##################
## SCRIPT START ##
##################

main
