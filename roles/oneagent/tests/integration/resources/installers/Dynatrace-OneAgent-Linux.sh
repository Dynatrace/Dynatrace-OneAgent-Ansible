#!/bin/sh

readonly INSTALLER_VERSION='##VERSION##'

readonly UNINSTALL_DIR='/opt/dynatrace/oneagent/agent'
readonly UNINSTALL_SCRIPT='uninstall.sh'
readonly UNINSTALL_CODE="$(cat <<-ENDUNINSTALL
##UNINSTALL_CODE##
ENDUNINSTALL
)"

readonly ONEAGENTCTL_BIN='oneagentctl'
readonly ONEAGENTCTL_DIR='/opt/dynatrace/oneagent/agent/tools'
readonly ONEAGENTCTL_CODE="$(cat <<-ENDCTL
##ONEAGENTCTL_CODE##
ENDCTL
)"

deployOneagentCtl() {
	mkdir -p "${ONEAGENTCTL_DIR}"
	printf '%s' "${ONEAGENTCTL_CODE}" > "${ONEAGENTCTL_DIR}/${ONEAGENTCTL_BIN}"
	chmod +x "${ONEAGENTCTL_DIR}/${ONEAGENTCTL_BIN}"
}

deployUninstallScript() {
	mkdir -p "${UNINSTALL_DIR}"
	printf '%s' "${UNINSTALL_CODE}" > "${UNINSTALL_DIR}/${UNINSTALL_SCRIPT}"
	chmod +x "${UNINSTALL_DIR}/${UNINSTALL_SCRIPT}"
}

main() {
	if [ "${1}" = '--version' ]; then
		printf '%s\n' "${INSTALLER_VERSION}"
		return 0
	else
		deployOneagentCtl
		deployUninstallScript
	fi
}

##################
## SCRIPT START ##
##################

main "$@"
