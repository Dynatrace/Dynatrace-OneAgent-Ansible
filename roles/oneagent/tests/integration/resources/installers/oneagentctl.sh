#!/bin/sh

readonly INSTALLER_VERSION='##VERSION##'
readonly DEPLOYMENT_CONF_PATH='/var/lib/dynatrace/oneagent/agent/config'

saveToConfig() {
	;
}

readFromConfig() {
	;
}

main() {
	if [ "${1}" = '--version' ]; then
		printf '%s\n' "${INSTALLER_VERSION}"
		return 0
	elif printf "%s" "${1}" | grep -q "--get-"; then
		readFromConfig
	elif printf "%s" "${1}" | grep -q "--set-"; then
		saveToConfig
	fi
}

##################
## SCRIPT START ##
##################

main "$@"

}