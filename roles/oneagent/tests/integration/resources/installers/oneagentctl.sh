#!/bin/bash

# This file simulates deployment functionalities of oneagentctl binary, used to configure installation.

readonly DIR_NAME="$(dirname "${0}")"
readonly INSTALLER_VERSION="##VERSION##"
readonly DEPLOYMENT_CONF_PATH="/var/lib/dynatrace/oneagent/agent/config"

cutVariable() {
	local variable="${1}"
	local delimiter="${2}"
	local fields="${3}"
	printf "%s" "${variable}" | cut -d "${delimiter}" -f "${fields}"
}

saveToConfig() {
	while [ $# -gt 0 ]; do
			local setter="$(cutVariable "${1}" "=" 1)"
			local setterType="$(cutVariable "${setter}" "-" "5-")"
			local value="$(cutVariable "${1}" "=" "2-")"
			local setterFile="${DEPLOYMENT_CONF_PATH}/${setterType}"
			printf '%s\n' "${value}" >>"${setterFile}"
			echo "${1} Set ${setterType} to ${value}" >> "${DIR_NAME}/output"
			shift
	done
}

readFromConfig() {
	local getterType="$(cutVariable "${1}" "-" "5-")"

	if [ "${getterType}" = "properties" ]; then
		getterType="property"
	fi
	getterType="$(cutVariable "${getterType}" "s" "1")"
	cat "${DEPLOYMENT_CONF_PATH}/${getterType}"
}

main() {
	if [ "${1}" = '--version' ]; then
		printf '%s\n' "${INSTALLER_VERSION}"
	elif printf "%s" "${1}" | grep -q "get"; then
		readFromConfig ${1}
	elif printf "%s" "${1}" | grep -q "set"; then
		saveToConfig "$@"
	fi
}

##################
## SCRIPT START ##
##################

main "$@"
