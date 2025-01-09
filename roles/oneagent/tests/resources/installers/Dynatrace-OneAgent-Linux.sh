#!/bin/bash -eu

# This script acts as a self contained installer of the procuct

set -e

readonly DEFAULT_INSTALL_DIR="/opt/dynatrace/oneagent"
readonly INSTALLER_VERSION="##VERSION##"
readonly DEPLOYMENT_CONF_PATH="/var/lib/dynatrace/oneagent/agent/config"

readonly UNINSTALL_SCRIPT="uninstall.sh"
UNINSTALL_CODE="$(cat <<-ENDUNINSTALL
##UNINSTALL_CODE##
ENDUNINSTALL
)"
readonly UNINSTALL_CODE

readonly ONEAGENTCTL_BIN="oneagentctl"
ONEAGENTCTL_CODE="$(cat <<-ENDCTL
##ONEAGENTCTL_CODE##
ENDCTL
)"
readonly ONEAGENTCTL_CODE

CTL_PARAMS=
INSTALL_DIR="${DEFAULT_INSTALL_DIR}"

parseParams() {
	while [ $# -gt 0 ]; do
		local param="${1}"
		if [ "${param}" = "--version" ]; then
			printf "%s\n" "${INSTALLER_VERSION}"
			exit 0
		elif [ "${param}" = "INSTALL_PATH" ]; then
			INSTALL_DIR="$(printf "%s" "${param}" | cut -d "=" -f "2-")"
		elif printf "%s" "${param}" | grep -q -- "--set"; then
			CTL_PARAMS="${CTL_PARAMS} ${1}"
		fi
		shift
	done
}

uninstall() {
	local uninstallScript="${INSTALL_DIR}/agent/${UNINSTALL_SCRIPT}"
	if [ -f "${uninstallScript}" ]; then
		"${uninstallScript}"
	fi
}

deployOneagentCtl() {
	local ONEAGENTCTL_DIR="${INSTALL_DIR}/agent/tools"
	mkdir -p "${ONEAGENTCTL_DIR}"
	mkdir -p "${DEPLOYMENT_CONF_PATH}"
	printf '%s' "${ONEAGENTCTL_CODE}" > "${ONEAGENTCTL_DIR}/${ONEAGENTCTL_BIN}"
	chmod +x "${ONEAGENTCTL_DIR}/${ONEAGENTCTL_BIN}"
}

deployUninstallScript() {
	local UNINSTALL_DIR="${INSTALL_DIR}/agent"
	mkdir -p "${UNINSTALL_DIR}"
	printf '%s' "${UNINSTALL_CODE}" > "${UNINSTALL_DIR}/${UNINSTALL_SCRIPT}"
	chmod +x "${UNINSTALL_DIR}/${UNINSTALL_SCRIPT}"
}

applyConfig() {
	# shellcheck disable=SC2086
	"${INSTALL_DIR}/agent/tools/${ONEAGENTCTL_BIN}" ${CTL_PARAMS}
}

main() {
	parseParams "$@"
	uninstall
	deployOneagentCtl
	deployUninstallScript
	applyConfig
	exit 0
}

##################
## SCRIPT START ##
##################

main "$@"
