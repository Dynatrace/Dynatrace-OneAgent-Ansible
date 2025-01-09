#!/usr/bin/env bash

# This script simulates deployment functionalities of oneagentctl binary, used to configure installation.

set -eu

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
		# example command: --set-host-property=TENANT=tenant1
		# setter: --set-host-property
		local setter
		setter="$(cutVariable "${1}" "=" 1)"

		# setterType: property
		local setterType
		setterType="$(cutVariable "${setter}" "-" "5-")"

		# value: TENANT=tenant1
		local value
		value="$(cutVariable "${1}" "=" "2-")"

		# property: TENANT
		local property
		property="$(cutVariable "${value}" "=" "1")"

		local setterFile="${DEPLOYMENT_CONF_PATH}/${setterType}"
		if grep -q "${property}" "${setterFile}"; then
			sed -i "s/${property}.*/${value}/" "${setterFile}"
		else
			printf '%s\n' "${value}" >>"${setterFile}"
		fi

		shift
	done
}

readFromConfig() {
	local getterType
	getterType="$(cutVariable "${1}" "-" "5-")"

	if [ "${getterType}" = "properties" ]; then
		getterType="property"
	fi

	getterType="$(cutVariable "${getterType}" "s" "1")"
	cat "${DEPLOYMENT_CONF_PATH}/${getterType}"
}

main() {
	if [ "${1}" = '--version' ]; then
		printf '%s\n' "${INSTALLER_VERSION}"
	elif printf "%s" "${1}" | grep -q "^--get"; then
		readFromConfig "${1}"
	elif printf "%s" "${1}" | grep -q "^--set"; then
		saveToConfig "$@"
	fi
}

##################
## SCRIPT START ##
##################

main "$@"
