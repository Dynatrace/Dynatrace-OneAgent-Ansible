#!/bin/sh

readonly INSTALLER_VERSION='##VERSION##'
readonly ONEAGENTCTL_BIN='oneagentctl'
readonly ONEAGENTCTL_DIR='/opt/dynatrace/oneagent/agent/tools'

deployOneagentCtl() {
	mkdir -p "${ONEAGENTCTL_DIR}"
	# Separate ctl logic
	chmod +x "${ONEAGENTCTL_DIR}/${ONEAGENTCTL_BIN}"
}

main() {
	deployOneagentCtl
}

##################
## SCRIPT START ##
##################

main "$@"
